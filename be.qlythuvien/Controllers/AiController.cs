using System;
using System.Linq;
using System.Net;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Configuration;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Controllers
{
    internal class SafeRateLimitBucket
    {
        public DateTime WindowEndUtc { get; set; }
        public int RequestCount { get; set; }
        public object SyncLock { get; } = new object();
    }

    [ApiController]
    [Route("api/[controller]")]
    public class AiController : ControllerBase
    {
        private readonly IAiService _aiService;
        private readonly IMemoryCache _cache;
        private readonly IConfiguration _configuration;

        public AiController(IAiService aiService, IMemoryCache cache, IConfiguration configuration)
        {
            _aiService = aiService;
            _cache = cache;
            _configuration = configuration;
        }

        /// <summary>
        /// API AI tư vấn sách dựa trên nhu cầu, sở thích của khách hàng và tìm sách liên quan từ cơ sở dữ liệu.
        /// Có giới hạn độ dài tin nhắn (2 - 500 ký tự) và giới hạn tần suất gọi an toàn (tối đa 10 lượt / phút).
        /// Xác thực IP bảo mật qua Trusted Proxy để ngăn chặn tuyệt đối việc vượt qua Rate Limit bằng fake header.
        /// </summary>
        [HttpPost("chat")]
        [AllowAnonymous]
        [ProducesResponseType(typeof(ApiResponse<AiChatResponseDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status429TooManyRequests)]
        public async Task<IActionResult> Chat([FromBody] AiChatRequestDto request)
        {
            // 1. Kiểm tra tính hợp lệ và giới hạn độ dài tin nhắn
            if (request == null || string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Nội dung tin nhắn tư vấn không được để trống."));
            }

            var cleanMessage = request.Message.Trim();

            if (cleanMessage.Length < 2)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Nội dung tin nhắn tư vấn quá ngắn. Vui lòng nhập tối thiểu 2 ký tự."));
            }

            if (cleanMessage.Length > 500)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Nội dung tin nhắn tư vấn vượt quá giới hạn cho phép (tối đa 500 ký tự). Vui lòng rút gọn nội dung."));
            }

            if (request.MinPrice.HasValue && request.MinPrice.Value < 0)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Giá tối thiểu không được là số âm."));
            }

            if (request.MaxPrice.HasValue && request.MaxPrice.Value < 0)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Giá tối đa không được là số âm."));
            }

            // 2. Xác định định danh Client một cách AN TOÀN (chống giả mạo IP qua header X-Forwarded-For)
            var clientId = ResolveClientIdentifier();
            const int maxRequestsPerMinute = 10;
            var rateLimitCacheKey = $"SafeRateLimit_Ai_{clientId}";

            // Lấy hoặc tạo bucket trong bộ nhớ
            var bucket = _cache.GetOrCreate(rateLimitCacheKey, entry =>
            {
                entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(2);
                return new SafeRateLimitBucket
                {
                    WindowEndUtc = DateTime.UtcNow.AddMinutes(1),
                    RequestCount = 0
                };
            })!;

            int secondsRemaining = 60;
            bool isRateLimitExceeded = false;
            int remainingRequests = 0;

            lock (bucket.SyncLock)
            {
                var nowUtc = DateTime.UtcNow;

                // Nếu cửa sổ 60s hiện tại đã hết hạn -> khởi tạo chu kỳ mới
                if (nowUtc >= bucket.WindowEndUtc)
                {
                    bucket.WindowEndUtc = nowUtc.AddMinutes(1);
                    bucket.RequestCount = 0;
                }

                secondsRemaining = Math.Max(1, (int)Math.Ceiling((bucket.WindowEndUtc - nowUtc).TotalSeconds));

                if (bucket.RequestCount >= maxRequestsPerMinute)
                {
                    isRateLimitExceeded = true;
                    remainingRequests = 0;
                }
                else
                {
                    bucket.RequestCount++;
                    remainingRequests = Math.Max(0, maxRequestsPerMinute - bucket.RequestCount);
                }
            }

            // Thêm headers Rate-Limit chuẩn HTTP
            Response.Headers["X-RateLimit-Limit"] = maxRequestsPerMinute.ToString();
            Response.Headers["X-RateLimit-Remaining"] = remainingRequests.ToString();
            Response.Headers["X-RateLimit-Reset"] = secondsRemaining.ToString();

            if (isRateLimitExceeded)
            {
                Response.Headers["Retry-After"] = secondsRemaining.ToString();
                return StatusCode(StatusCodes.Status429TooManyRequests,
                    ApiResponse<string>.ErrorResponse($"Bạn đã gửi yêu cầu quá nhanh (vượt quá {maxRequestsPerMinute} lượt/phút). Vui lòng thử lại sau {secondsRemaining} giây."));
            }

            // 3. Xử lý tư vấn AI
            var result = await _aiService.ChatAsync(request);

            return Ok(ApiResponse<AiChatResponseDto>.SuccessResponse(result, "Tư vấn sách thành công."));
        }

        /// <summary>
        /// Xác định Client IP an toàn:
        /// - Nếu đã đăng nhập: Dùng UserId làm định danh.
        /// - Nếu là khách vãng lai: Kiểm tra IP kết nối vật lý (RemoteIpAddress).
        ///   CHỈ tin tưởng header X-Forwarded-For / X-Real-IP nếu kết nối đến từ Proxy tin cậy (Localhost, Docker network, reverse proxy cấu hình).
        ///   Nếu kết nối trực tiếp, TUYỆT ĐỐI BỎ QUA mọi header IP do người gọi tự gửi để chống bypass rate limit.
        /// </summary>
        private string ResolveClientIdentifier()
        {
            // 1. Người dùng đã đăng nhập có JWT
            var customerIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value
                               ?? User.FindFirst("sub")?.Value;

            if (!string.IsNullOrWhiteSpace(customerIdClaim))
            {
                return $"user_{customerIdClaim}";
            }

            // 2. Khách vãng lai: Lấy IP kết nối socket thực tế
            var remoteIp = HttpContext.Connection.RemoteIpAddress;
            if (remoteIp == null)
            {
                return "ip_unknown";
            }

            bool isTrustedProxy = IsTrustedProxyIp(remoteIp);

            // Chỉ khi kết nối đến từ Proxy tin cậy, mới trích xuất Client IP từ header
            if (isTrustedProxy)
            {
                var forwardedHeader = HttpContext.Request.Headers["X-Forwarded-For"].FirstOrDefault();
                if (!string.IsNullOrWhiteSpace(forwardedHeader))
                {
                    var clientIpCandidate = forwardedHeader.Split(',')[0].Trim();
                    if (IPAddress.TryParse(clientIpCandidate, out var parsedIp))
                    {
                        return $"ip_{parsedIp}";
                    }
                }

                var realIpHeader = HttpContext.Request.Headers["X-Real-IP"].FirstOrDefault();
                if (!string.IsNullOrWhiteSpace(realIpHeader) && IPAddress.TryParse(realIpHeader.Trim(), out var parsedRealIp))
                {
                    return $"ip_{parsedRealIp}";
                }
            }

            // Kết nối trực tiếp hoặc không phải Proxy tin cậy -> dùng chính IP kết nối vật lý, kẻ tấn công không thể spoof
            return $"ip_{remoteIp}";
        }

        private bool IsTrustedProxyIp(IPAddress ip)
        {
var ipString = ip.ToString();
            var configuredTrusted = _configuration.GetSection("Ai:TrustedProxies").Get<string[]>() ?? Array.Empty<string>();
            return configuredTrusted.Any(t => string.Equals(t?.Trim(), ipString, StringComparison.OrdinalIgnoreCase));
        }
    }
}
