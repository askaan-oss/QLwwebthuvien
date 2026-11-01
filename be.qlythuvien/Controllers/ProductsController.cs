using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ProductsController : ControllerBase
    {
        private readonly AppDbContext _context;
        private readonly INotificationService _notificationService;
        private readonly IBookContentService _bookContentService;
        private readonly IConfiguration _configuration;
        private readonly ITokenBlacklistService _blacklistService;

        public ProductsController(
            AppDbContext context, 
            INotificationService notificationService,
            IBookContentService bookContentService,
            IConfiguration configuration,
            ITokenBlacklistService blacklistService)
        {
            _context = context;
            _notificationService = notificationService;
            _bookContentService = bookContentService;
            _configuration = configuration;
            _blacklistService = blacklistService;
        }

        private long? GetCurrentCustomerId()
        {
            var claim = User.FindFirst(ClaimTypes.NameIdentifier) ?? User.FindFirst("sub");
            if (claim != null && long.TryParse(claim.Value, out var customerId))
            {
                return customerId;
            }
            return null;
        }

        private bool IsStaffOrHigher()
        {
            var roleClaim = User.FindFirst(ClaimTypes.Role)?.Value;
            return roleClaim != null && new[] { "admin", "manager", "staff" }.Contains(roleClaim.Trim().ToLower());
        }

        /// <summary>
        /// Tìm kiếm sách theo từ khóa (Tên sách, Tác giả, ISBN), lọc theo giá, thể loại và phân trang đầy đủ (trả về totalCount, totalPages cho FE).
        /// Public cho phép Khách hàng xem.
        /// </summary>
        [HttpGet]
        [AllowAnonymous]
        [ProducesResponseType(typeof(ApiResponse<PagedResult<ProductResponseDto>>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetAll(
            [FromQuery] string? search,
            [FromQuery] string? category,
            [FromQuery] decimal? minPrice,
            [FromQuery] decimal? maxPrice,
            [FromQuery] bool? isActive = true,
            [FromQuery] int page = 1,
            [FromQuery] int pageSize = 10)
        {
            if (page < 1) page = 1;
            if (pageSize < 1) pageSize = 10;
            if (pageSize > 100) pageSize = 100;

            var query = _context.Products.AsNoTracking().AsQueryable();

            if (isActive.HasValue)
            {
                query = query.Where(p => p.IsActive == isActive.Value);
            }

            if (!string.IsNullOrWhiteSpace(category))
            {
                query = query.Where(p => p.Category != null && p.Category.ToLower() == category.Trim().ToLower());
            }

            if (minPrice.HasValue)
            {
                query = query.Where(p => p.Price >= minPrice.Value);
            }

            if (maxPrice.HasValue)
            {
                query = query.Where(p => p.Price <= maxPrice.Value);
            }

            if (!string.IsNullOrWhiteSpace(search))
            {
                string keyword = search.Trim().ToLower();
                query = query.Where(p => p.Title.ToLower().Contains(keyword) ||
                                         (p.Author != null && p.Author.ToLower().Contains(keyword)) ||
                                         (p.Isbn != null && p.Isbn.ToLower().Contains(keyword)));
            }

            int totalCount = await query.CountAsync();
            int totalPages = (int)Math.Ceiling((double)totalCount / pageSize);

            var products = await query
                .OrderByDescending(p => p.CreatedAt)
                .Skip((page - 1) * pageSize)
                .Take(pageSize)
                .Select(p => MapToResponseDto(p))
                .ToListAsync();

            var pagedResult = new PagedResult<ProductResponseDto>
            {
                Items = products,
                TotalItems = totalCount,
                Page = page,
                PageSize = pageSize,
                TotalPages = totalPages
            };

            return Ok(ApiResponse<PagedResult<ProductResponseDto>>.SuccessResponse(pagedResult, "Lấy danh sách sách thành công."));
        }

        /// <summary>
        /// Xem chi tiết sách gồm: Tên, Tác giả, NXB, Giá bán, Mô tả, Số lượng tồn kho, Hình ảnh.
        /// Public cho phép Khách hàng xem.
        /// </summary>
        [HttpGet("{id}")]
        [AllowAnonymous]
        [ProducesResponseType(typeof(ApiResponse<ProductResponseDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        public async Task<IActionResult> GetById(long id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            return Ok(ApiResponse<ProductResponseDto>.SuccessResponse(MapToResponseDto(product), "Lấy thông tin chi tiết sách thành công."));
        }

        /// <summary>
        /// API Đọc thử sách (Preview): Cho phép độc giả đọc thử chương mẫu / 10-20% nội dung sách miễn phí.
        /// Tự động kiểm tra quyền sở hữu nếu đã đăng nhập (đã mua sách thì có quyền đọc toàn bộ).
        /// </summary>
        /// <summary>
        /// API Đọc thử sách (Preview): Cho phép độc giả đọc thử trích đoạn thật riêng của từng cuốn sách.
        /// Đảm bảo trả trường `excerpt` (khớp hoàn toàn với FE đọc d.excerpt) và `previewContent` tương thích ngược.
        /// Kèm đường dẫn readerUrl để mở giao diện đọc trực quan.
        /// </summary>
        [HttpGet("{id}/preview")]
        [AllowAnonymous]
        [ProducesResponseType(typeof(ApiResponse<ProductPreviewDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        public async Task<IActionResult> GetPreview(long id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            bool isPurchased = false;
            var customerId = GetCurrentCustomerId();

            if (customerId.HasValue)
            {
                isPurchased = await _context.OrderItems
                    .AnyAsync(oi => oi.ProductId == id &&
                                    oi.Order.CustomerId == customerId.Value &&
                                    oi.Order.OrderStatus != null &&
                                    !new[] { "CANCELLED", "EXPIRED", "RETURNED", "PENDING_PAYMENT", "PENDING_CONFIRMATION" }.Contains(oi.Order.OrderStatus.ToUpper()) &&
                                    ((oi.Order.PaymentMethod == "COD" && (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED")) ||
                                     (oi.Order.PaymentMethod != "COD" && (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "PROCESSING" || oi.Order.OrderStatus.ToUpper() == "SHIPPING" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED"))));
            }

            bool canReadFull = isPurchased || IsStaffOrHigher() || product.Price == 0;
            
            // Lấy nội dung thật riêng biệt cho từng cuốn sách từ BookContentService
            var bookContent = await _bookContentService.GetBookContentAsync(product);

            var previewDto = new ProductPreviewDto
            {
                ProductId = product.ProductId,
                Title = product.Title,
                Author = product.Author,
                Publisher = product.Publisher,
                Category = product.Category,
                Price = product.Price,
                ImageUrl = product.ImageUrl,
                Description = product.Description,
                IsPurchased = isPurchased,
                CanReadFull = canReadFull,
                TotalPreviewPages = bookContent.TotalPreviewPages,
                Excerpt = bookContent.Excerpt, // Khớp với FE line 140 đọc d.excerpt
                PreviewContent = bookContent.Excerpt, // Tương thích ngược
                PreviewChapters = bookContent.PreviewChapters,
                IsFullBook = bookContent.IsFullBook,
                ContentNote = bookContent.ContentNote,
                ReaderUrl = $"/api/Products/{id}/reader",
                Message = canReadFull 
                    ? (bookContent.IsFullBook
                        ? "Bạn đã mua cuốn sách này hoặc có quyền truy cập toàn diện. Bạn có thể đọc toàn bộ sách tại giao diện /api/Products/" + id + "/reader hoặc API /api/Products/" + id + "/read."
                        : "Bạn có quyền truy cập. Hệ thống đang hiển thị bản tóm tắt/biên soạn; bản toàn văn trọn vẹn đang được cập nhật.")
                    : "Đây là nội dung đọc thử trích đoạn miễn phí. Quý khách vui lòng đặt mua sách để mở khóa toàn bộ nội dung Ebook!"
            };

            return Ok(ApiResponse<ProductPreviewDto>.SuccessResponse(previewDto, "Lấy nội dung đọc thử sách thành công."));
        }

        /// <summary>
        /// API Đọc trọn vẹn Ebook sau khi mua sách: Yêu cầu đăng nhập, kiểm tra đơn hàng đã thanh toán thành công.
        /// Trả về 403 Forbidden nếu chưa mua sách.
        /// </summary>
        [HttpGet("{id}/read")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<ProductEbookDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status403Forbidden)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        public async Task<IActionResult> ReadFullEbook(long id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin tài khoản người dùng."));
            }

            bool isStaff = IsStaffOrHigher();

            var purchaseInfo = await _context.OrderItems
                .Where(oi => oi.ProductId == id &&
                             oi.Order.CustomerId == customerId.Value &&
                             oi.Order.OrderStatus != null &&
                             !new[] { "CANCELLED", "EXPIRED", "RETURNED", "PENDING_PAYMENT", "PENDING_CONFIRMATION" }.Contains(oi.Order.OrderStatus.ToUpper()) &&
                             ((oi.Order.PaymentMethod == "COD" && (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED")) ||
                              (oi.Order.PaymentMethod != "COD" && (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "PROCESSING" || oi.Order.OrderStatus.ToUpper() == "SHIPPING" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED"))))
                .OrderByDescending(oi => oi.Order.CreatedAt)
                .Select(oi => new { oi.OrderId, oi.Order.CreatedAt })
                .FirstOrDefaultAsync();

            bool hasAccess = isStaff || purchaseInfo != null || product.Price == 0;

            if (!hasAccess)
            {
                return StatusCode(StatusCodes.Status403Forbidden, 
                    ApiResponse<string>.ErrorResponse($"Bạn chưa mua cuốn sách '{product.Title}' hoặc đơn hàng chưa hoàn tất thanh toán. Vui lòng mua sách để mở khóa và đọc toàn bộ nội dung Ebook."));
            }

            // Lấy toàn bộ các chương thật của cuốn sách
            var bookContent = await _bookContentService.GetBookContentAsync(product);
            var chapters = bookContent.FullChapters;
            var fullContent = string.Join("\n\n----------------------------------------\n\n", chapters.Select(c => $"### {c.Title}\n\n{c.Content}"));

            var ebookDto = new ProductEbookDto
            {
                ProductId = product.ProductId,
                Title = product.Title,
                Author = product.Author,
                Publisher = product.Publisher,
                Category = product.Category,
                ImageUrl = product.ImageUrl,
                IsUnlocked = true,
                IsFullBook = bookContent.IsFullBook,
                ContentNote = bookContent.ContentNote,
                OrderId = purchaseInfo?.OrderId,
                PurchasedAt = purchaseInfo?.CreatedAt,
                FullContent = fullContent,
                Chapters = chapters,
                ReaderUrl = $"/api/Products/{id}/reader",
                Message = bookContent.IsFullBook
                    ? "Chào mừng quý độc giả! Bạn đã mở khóa trọn vẹn Ebook này. Chúc bạn có những phút giây đọc sách bổ ích!"
                    : "Chào mừng quý độc giả! Bạn đã mở khóa đọc sách. Lưu ý: Đây là bản tóm tắt & trích đoạn biên soạn của sách; bản số hóa toàn văn đang được cập nhật."
            };

            return Ok(ApiResponse<ProductEbookDto>.SuccessResponse(ebookDto, "Mở khóa nội dung Ebook thành công."));
        }

        /// <summary>
        /// Giao diện Web Reader đọc toàn bộ sách sau mua (Ebook Viewer giao diện cao cấp tích hợp ngay tại Backend).
        /// Hỗ trợ đọc thử hoặc đọc trọn vẹn nếu đã mua sách, có chế độ sáng/tối/sepia, chỉnh font size và chuyển chương.
        /// </summary>
        [HttpGet("{id}/reader")]
        [HttpGet("{id}/read-view")]
        [AllowAnonymous]
        public async Task<IActionResult> GetReaderView(long id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound("Không tìm thấy sách yêu cầu.");
            }

            long? customerId = GetCurrentCustomerId();
            bool isStaff = IsStaffOrHigher();

            bool isPurchased = false;
            if (customerId.HasValue)
            {
                isPurchased = await _context.OrderItems
                    .AnyAsync(oi => oi.ProductId == id &&
                                    oi.Order.CustomerId == customerId.Value &&
                                    oi.Order.OrderStatus != null &&
                                    !new[] { "CANCELLED", "EXPIRED", "RETURNED", "PENDING_PAYMENT", "PENDING_CONFIRMATION" }.Contains(oi.Order.OrderStatus.ToUpper()) &&
                                    ((oi.Order.PaymentMethod == "COD" && (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED")) ||
                                     (oi.Order.PaymentMethod != "COD" && (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "PROCESSING" || oi.Order.OrderStatus.ToUpper() == "SHIPPING" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED"))));
            }

            bool canReadFull = isPurchased || isStaff || product.Price == 0;
            var bookContent = await _bookContentService.GetBookContentAsync(product);
            var displayChapters = canReadFull ? bookContent.FullChapters : bookContent.PreviewChapters;

            string badgeText;
            string badgeStyle;
            if (canReadFull)
            {
                if (bookContent.IsFullBook)
                {
                    badgeText = "BẢN ĐỌC TRỌN VẸN";
                    badgeStyle = "background: #dcfce7; color: #15803d;";
                }
                else
                {
                    badgeText = "BẢN BIÊN SOẠN / TÓM TẮT";
                    badgeStyle = "background: #fef3c7; color: #b45309;";
                }
            }
            else
            {
                badgeText = "BẢN ĐỌC THỬ MIỄN PHÍ";
                badgeStyle = "background: var(--accent-bg); color: var(--primary-color);";
            }

            var chaptersJson = System.Text.Json.JsonSerializer.Serialize(displayChapters);
            var excerptHtml = System.Net.WebUtility.HtmlEncode(bookContent.Excerpt).Replace("\n", "<br/>");

            var html = $@"<!DOCTYPE html>
<html lang=""vi"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>{System.Net.WebUtility.HtmlEncode(product.Title)} - Ebook Reader</title>
    <link rel=""preconnect"" href=""https://fonts.googleapis.com"">
    <link rel=""preconnect"" href=""https://fonts.gstatic.com"" crossorigin>
    <link href=""https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"" rel=""stylesheet"">
    <style>
        :root {{
            --bg-color: #f8fafc;
            --surface-color: #ffffff;
            --text-color: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            --accent-bg: #eff6ff;
            --font-reader: 'Merriweather', Georgia, serif;
            --font-ui: 'Plus Jakarta Sans', system-ui, sans-serif;
            --reader-font-size: 18px;
            --reader-line-height: 1.85;
        }}
        body.theme-dark {{
            --bg-color: #0f172a;
            --surface-color: #1e293b;
            --text-color: #f1f5f9;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --primary-color: #3b82f6;
            --accent-bg: #1e3a8a33;
        }}
        body.theme-sepia {{
            --bg-color: #fbf0d9;
            --surface-color: #f4e8ce;
            --text-color: #433422;
            --text-muted: #79664f;
            --border-color: #e5d5b7;
            --primary-color: #92400e;
            --accent-bg: #faeed4;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-ui);
            transition: background 0.3s, color 0.3s;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        header {{
            position: sticky;
            top: 0;
            background: var(--surface-color);
            border-bottom: 1px solid var(--border-color);
            padding: 0.75rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 50;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .header-title {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .book-badge {{
            background: var(--accent-bg);
            color: var(--primary-color);
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .controls {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .btn {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 0.45rem 0.85rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.2s;
        }}
        .btn:hover {{ background: var(--accent-bg); border-color: var(--primary-color); }}
        .btn-primary {{
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }}
        .btn-primary:hover {{ background: var(--primary-hover); }}
        .container {{
            max-width: 860px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            flex: 1;
            width: 100%;
        }}
        .reader-card {{
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 3rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        }}
        .chapter-header {{
            margin-bottom: 2.5rem;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }}
        .chapter-title {{
            font-size: 1.85rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: var(--text-color);
        }}
        .chapter-meta {{
            font-size: 0.875rem;
            color: var(--text-muted);
        }}
        .chapter-content {{
            font-family: var(--font-reader);
            font-size: var(--reader-font-size);
            line-height: var(--reader-line-height);
            color: var(--text-color);
            white-space: pre-wrap;
            word-break: break-word;
        }}
        .reader-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-color);
        }}
        .locked-banner {{
            background: linear-gradient(135deg, #1e293b, #0f172a);
            color: #ffffff;
            border-radius: 1rem;
            padding: 2.5rem;
            text-align: center;
            margin-top: 2rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        .locked-banner h3 {{ font-size: 1.5rem; margin-bottom: 0.75rem; color: #f8fafc; }}
        .locked-banner p {{ color: #cbd5e1; margin-bottom: 1.5rem; font-size: 0.95rem; }}
        .modal-overlay {{
            position: fixed; inset: 0; background: rgba(0,0,0,0.5);
            display: none; align-items: center; justify-content: center; z-index: 100;
        }}
        .modal-card {{
            background: var(--surface-color); border: 1px solid var(--border-color);
            border-radius: 1rem; width: 90%; max-width: 500px; max-height: 80vh;
            overflow-y: auto; padding: 1.5rem;
        }}
        .toc-item {{
            padding: 0.75rem 1rem; border-radius: 0.5rem; cursor: pointer;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 0.35rem; transition: background 0.15s;
        }}
        .toc-item:hover {{ background: var(--accent-bg); }}
        .toc-item.active {{ background: var(--accent-bg); color: var(--primary-color); font-weight: 600; }}
        @media (max-width: 640px) {{
            .reader-card {{ padding: 1.5rem; }}
            .chapter-title {{ font-size: 1.4rem; }}
            header {{ padding: 0.5rem 1rem; }}
        }}
    </style>
</head>
<body class=""theme-light"">
    <header>
        <div class=""header-title"">
            <div>
                <h1 style=""font-size: 1.1rem; font-weight: 700;"">{System.Net.WebUtility.HtmlEncode(product.Title)}</h1>
                <p style=""font-size: 0.8rem; color: var(--text-muted);"">{System.Net.WebUtility.HtmlEncode(product.Author ?? "Tác giả")} • {System.Net.WebUtility.HtmlEncode(product.Category ?? "Sách")}</p>
            </div>
            <span class=""book-badge"" style=""{badgeStyle}"">{badgeText}</span>
        </div>
        <div class=""controls"">
            <button class=""btn"" onclick=""openTocModal()"">☰ Mục lục</button>
            <button class=""btn"" onclick=""toggleTheme()"" id=""btnTheme"" title=""Đổi màu nền"">🌓 Chế độ đọc</button>
            <button class=""btn"" onclick=""changeFontSize(-1)"" title=""Thu nhỏ chữ"">A-</button>
            <button class=""btn"" onclick=""changeFontSize(1)"" title=""Phóng to chữ"">A+</button>
        </div>
    </header>

    <div class=""container"">
        <main class=""reader-card"">
            {(!bookContent.IsFullBook ? $@"
            <div style=""background: rgba(245, 158, 11, 0.08); border-left: 4px solid #f59e0b; padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: var(--text-color);"">
                <strong>📌 Lưu ý về nội dung:</strong> {System.Net.WebUtility.HtmlEncode(bookContent.ContentNote)}
            </div>" : "")}

            <div class=""chapter-header"">
                <h2 class=""chapter-title"" id=""chapterTitle"">Đang tải chương...</h2>
                <div class=""chapter-meta"" id=""chapterMeta"">Đang chuẩn bị trang sách...</div>
            </div>

            <div class=""chapter-content"" id=""chapterContent"">Đang kết nối thư viện...</div>

            <div class=""reader-nav"">
                <button class=""btn"" id=""btnPrev"" onclick=""navigateChapter(-1)"">⬅ Chương trước</button>
                <span id=""pageIndicator"" style=""font-size: 0.875rem; color: var(--text-muted);"">Chương 1 / 1</span>
                <button class=""btn"" id=""btnNext"" onclick=""navigateChapter(1)"">Chương sau ➡</button>
            </div>
        </main>

        {(!canReadFull ? $@"
        <div class=""locked-banner"">
            <h3>🔒 Bạn vừa đọc xong trích đoạn đọc thử miễn phí</h3>
            <p>Cuốn sách '<strong>{System.Net.WebUtility.HtmlEncode(product.Title)}</strong>' chứa trọn vẹn những kiến thức sâu sắc nhất. Hãy đặt mua ngay với giá chỉ <strong>{product.Price:N0} đ</strong> để mở khóa các chương sách tiếp theo!</p>
            <a href=""/"" class=""btn btn-primary"" style=""padding: 0.75rem 1.75rem; font-size: 1rem;"">🛒 Mua sách ngay để mở khóa</a>
        </div>" : "")}
    </div>

    <div class=""modal-overlay"" id=""tocModal"" onclick=""closeTocModal(event)"">
        <div class=""modal-card"" onclick=""event.stopPropagation()"">
            <div style=""display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;"">
                <h3 style=""font-size: 1.15rem; font-weight: 700;"">Mục lục sách</h3>
                <button class=""btn"" onclick=""closeTocModal()"">✕</button>
            </div>
            <div id=""tocList""></div>
        </div>
    </div>

    <script>
        const chapters = {chaptersJson};
        const isFullBook = {bookContent.IsFullBook.ToString().ToLower()};
        let currentChapterIndex = 0;
        let themes = ['theme-light', 'theme-sepia', 'theme-dark'];
        let currentThemeIndex = 0;
        let fontSize = 18;

        function renderChapter(index) {{
            if (!chapters || chapters.length === 0) return;
            if (index < 0) index = 0;
            if (index >= chapters.length) index = chapters.length - 1;
            currentChapterIndex = index;

            const ch = chapters[index];
            document.getElementById('chapterTitle').textContent = ch.Title || ('Chương ' + ch.ChapterNumber);
            const typeLabel = ch.IsPreview ? ' (Đọc thử miễn phí)' : (isFullBook ? ' (Trọn vẹn)' : ' (Bản trích lược/tóm tắt)');
            document.getElementById('chapterMeta').textContent = 'Chương ' + (index + 1) + ' trong tổng số ' + chapters.length + ' chương' + typeLabel;
            document.getElementById('chapterContent').textContent = ch.Content || '';
            document.getElementById('pageIndicator').textContent = 'Chương ' + (index + 1) + ' / ' + chapters.length;

            document.getElementById('btnPrev').disabled = (index === 0);
            document.getElementById('btnNext').disabled = (index === chapters.length - 1);

            window.scrollTo({{ top: 0, behavior: 'smooth' }});
            renderTocList();
        }}

        function navigateChapter(delta) {{
            renderChapter(currentChapterIndex + delta);
        }}

        function toggleTheme() {{
            currentThemeIndex = (currentThemeIndex + 1) % themes.length;
            document.body.className = themes[currentThemeIndex];
        }}

        function changeFontSize(delta) {{
            fontSize = Math.min(26, Math.max(14, fontSize + delta));
            document.documentElement.style.setProperty('--reader-font-size', fontSize + 'px');
        }}

        function openTocModal() {{
            renderTocList();
            document.getElementById('tocModal').style.display = 'flex';
        }}

        function closeTocModal() {{
            document.getElementById('tocModal').style.display = 'none';
        }}

        function renderTocList() {{
            const list = document.getElementById('tocList');
            list.innerHTML = '';
            chapters.forEach((ch, idx) => {{
                const item = document.createElement('div');
                item.className = 'toc-item' + (idx === currentChapterIndex ? ' active' : '');
                const title = document.createElement('span');
                title.textContent = ch.Title || ('Chương ' + ch.ChapterNumber);
                const badge = document.createElement('span');
                badge.textContent = ch.IsPreview ? 'Miễn phí' : (isFullBook ? 'Đầy đủ' : 'Tóm tắt');
                item.append(title, badge);
                item.onclick = () => {{
                    renderChapter(idx);
                    closeTocModal();
                }};
                list.appendChild(item);
            }});
        }}

        // Khởi động
        renderChapter(0);
    </script>
</body>
</html>";

            return Content(html, "text/html; charset=utf-8");
        }

        /// <summary>
        /// API Cập nhật nội dung sách thật (Dành cho Quản trị viên, Quản lý, Nhân viên)
        /// Cho phép nhập trích đoạn đọc thử thật và các chương đầy đủ thật cho bất kỳ cuốn sách nào.
        /// </summary>
        [HttpPut("{id}/content")]
        [Authorize(Roles = "Admin,Manager,Staff")]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> UpdateBookContent(long id, [FromBody] UpdateBookContentRequestDto request)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            if (request == null || string.IsNullOrWhiteSpace(request.Excerpt) || request.Chapters == null || !request.Chapters.Any())
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Vui lòng cung cấp đầy đủ đoạn trích đọc thử và ít nhất 1 chương sách."));
            }

            var saved = await _bookContentService.SaveCustomBookContentAsync(id, request.Excerpt, request.Chapters);
            if (!saved)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, 
                    ApiResponse<string>.ErrorResponse("Lỗi khi lưu trữ nội dung sách vào hệ thống."));
            }

            return Ok(ApiResponse<string>.SuccessResponse($"Cập nhật nội dung sách thật cho '{product.Title}' thành công."));
        }

        /// <summary>
        /// Alias API đọc Ebook (/api/Products/{id}/ebook)
        /// </summary>
        [HttpGet("{id}/ebook")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<ProductEbookDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> ReadEbookAlias(long id)
        {
            return await ReadFullEbook(id);
        }

        /// <summary>
        /// API kiểm tra xem người dùng hiện tại đã mua cuốn sách này hay chưa
        /// </summary>
        [HttpGet("{id}/check-purchase")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<CheckPurchaseResponseDto>), StatusCodes.Status200OK)]
        public async Task<IActionResult> CheckPurchase(long id)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Chưa đăng nhập."));
            }

            var purchaseInfo = await _context.OrderItems
                .Where(oi => oi.ProductId == id &&
                             oi.Order.CustomerId == customerId.Value &&
                             oi.Order.OrderStatus != null &&
                             !new[] { "CANCELLED", "EXPIRED", "RETURNED", "PENDING_PAYMENT", "PENDING_CONFIRMATION" }.Contains(oi.Order.OrderStatus.ToUpper()) &&
                             ((oi.Order.PaymentMethod == "COD" && (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED")) ||
                              (oi.Order.PaymentMethod != "COD" && (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "PROCESSING" || oi.Order.OrderStatus.ToUpper() == "SHIPPING" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED"))))
                .OrderByDescending(oi => oi.Order.CreatedAt)
                .Select(oi => new { oi.OrderId, oi.Order.CreatedAt, oi.Order.OrderStatus })
                .FirstOrDefaultAsync();

            bool isPurchased = purchaseInfo != null;
            bool canRead = isPurchased || IsStaffOrHigher() || product.Price == 0;

            var result = new CheckPurchaseResponseDto
            {
                ProductId = id,
                Title = product.Title,
                IsPurchased = isPurchased,
                OrderId = purchaseInfo?.OrderId,
                OrderStatus = purchaseInfo?.OrderStatus,
                PurchasedAt = purchaseInfo?.CreatedAt,
                CanReadEbook = canRead
            };

            return Ok(ApiResponse<CheckPurchaseResponseDto>.SuccessResponse(result, "Kiểm tra quyền đọc sách thành công."));
        }

        /// <summary>
        /// Lấy danh sách tất cả các tựa Ebook mà khách hàng đã mua và có quyền đọc
        /// </summary>
        [HttpGet("my-ebooks")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<List<ProductResponseDto>>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetMyPurchasedEbooks()
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Chưa đăng nhập."));
            }

            var purchasedProductIds = await _context.OrderItems
                .Where(oi => oi.Order.CustomerId == customerId.Value &&
                             oi.Order.OrderStatus != null &&
                             !new[] { "CANCELLED", "EXPIRED", "RETURNED", "PENDING_PAYMENT", "PENDING_CONFIRMATION" }.Contains(oi.Order.OrderStatus.ToUpper()) &&
                             ((oi.Order.PaymentMethod == "COD" && (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED")) ||
                              (oi.Order.PaymentMethod != "COD" && (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "PROCESSING" || oi.Order.OrderStatus.ToUpper() == "SHIPPING" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED"))))
                .Select(oi => oi.ProductId)
                .Distinct()
                .ToListAsync();

            var products = await _context.Products
                .Where(p => purchasedProductIds.Contains(p.ProductId))
                .Select(p => MapToResponseDto(p))
                .ToListAsync();

            return Ok(ApiResponse<List<ProductResponseDto>>.SuccessResponse(products, "Lấy danh sách Ebook đã sở hữu thành công."));
        }

        /// <summary>
        /// Thêm sản phẩm sách mới (Admin hoặc Quản lý - Manager)
        /// </summary>
        [HttpPost]
        [Authorize(Roles = "Admin,Manager")]
        [ProducesResponseType(typeof(ApiResponse<ProductResponseDto>), StatusCodes.Status201Created)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status403Forbidden)]
        public async Task<IActionResult> Create([FromBody] CreateProductDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Dữ liệu gửi lên không hợp lệ."));
            }

            if (!string.IsNullOrWhiteSpace(dto.Isbn))
            {
                bool isbnExists = await _context.Products.AnyAsync(p => p.Isbn == dto.Isbn.Trim());
                if (isbnExists)
                {
                    return BadRequest(ApiResponse<string>.ErrorResponse("Mã ISBN này đã tồn tại trong hệ thống."));
                }
            }

            var product = new Product
            {
                Title = dto.Title.Trim(),
                Author = dto.Author?.Trim(),
                Publisher = dto.Publisher?.Trim(),
                Isbn = dto.Isbn?.Trim(),
                Category = dto.Category?.Trim(),
                Price = dto.Price,
                StockQuantity = dto.StockQuantity,
                HoldQuantity = 0,
                Description = dto.Description?.Trim(),
                ImageUrl = dto.ImageUrl?.Trim(),
                IsActive = dto.IsActive,
                CreatedAt = DateTime.UtcNow,
                UpdatedAt = DateTime.UtcNow
            };

            await _context.Products.AddAsync(product);
            await _context.SaveChangesAsync();

            var responseDto = MapToResponseDto(product);
            return CreatedAtAction(nameof(GetById), new { id = product.ProductId }, ApiResponse<ProductResponseDto>.SuccessResponse(responseDto, "Thêm sản phẩm sách mới thành công!"));
        }

        /// <summary>
        /// Cập nhật thông tin sách (Admin hoặc Quản lý - Manager)
        /// </summary>
        [HttpPut("{id}")]
        [Authorize(Roles = "Admin,Manager")]
        [ProducesResponseType(typeof(ApiResponse<ProductResponseDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        public async Task<IActionResult> Update(long id, [FromBody] UpdateProductDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Dữ liệu gửi lên không hợp lệ."));
            }

            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            if (!string.IsNullOrWhiteSpace(dto.Isbn) && dto.Isbn.Trim() != product.Isbn)
            {
                bool isbnExists = await _context.Products.AnyAsync(p => p.Isbn == dto.Isbn.Trim() && p.ProductId != id);
                if (isbnExists)
                {
                    return BadRequest(ApiResponse<string>.ErrorResponse("Mã ISBN này đã được sử dụng bởi sản phẩm khác."));
                }
            }

            product.Title = dto.Title.Trim();
            product.Author = dto.Author?.Trim();
            product.Publisher = dto.Publisher?.Trim();
            product.Isbn = dto.Isbn?.Trim();
            product.Category = dto.Category?.Trim();
            product.Price = dto.Price;
            product.StockQuantity = dto.StockQuantity;
            product.Description = dto.Description?.Trim();
            product.ImageUrl = dto.ImageUrl?.Trim();
            product.IsActive = dto.IsActive;
            product.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            // Nếu số lượng tồn kho sau cập nhật thấp hơn hoặc bằng ngưỡng, cảnh báo tới Quản lý
            if ((product.StockQuantity - product.HoldQuantity) <= 10)
            {
                await _notificationService.CheckAndNotifyLowStockAsync(new[] { product });
            }
            else
            {
                // Khi sách được nhập thêm hàng vượt ngưỡng an toàn, reset cooldown để sẵn sàng cảnh báo cho chu kỳ sau
                _notificationService.ResetLowStockCooldown(product.ProductId);
            }

            return Ok(ApiResponse<ProductResponseDto>.SuccessResponse(MapToResponseDto(product), "Cập nhật sản phẩm sách thành công!"));
        }

        /// <summary>
        /// Xóa sản phẩm sách (Admin hoặc Quản lý - Manager)
        /// </summary>
        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin,Manager")]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        public async Task<IActionResult> Delete(long id, [FromQuery] bool hardDelete = false)
        {
            var product = await _context.Products.FindAsync(id);
            if (product == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse($"Không tìm thấy sản phẩm có ID = {id}."));
            }

            if (hardDelete)
            {
                bool hasOrderItems = await _context.OrderItems.AnyAsync(oi => oi.ProductId == id);
                if (hasOrderItems)
                {
                    product.IsActive = false;
                    product.UpdatedAt = DateTime.UtcNow;
                    await _context.SaveChangesAsync();
                    return Ok(ApiResponse<string>.SuccessResponse("Sản phẩm đã phát sinh đơn hàng nên không thể xóa vĩnh viễn. Đã tự động chuyển sang trạng thái ngưng kinh doanh."));
                }

                var cartItems = await _context.CartItems.Where(ci => ci.ProductId == id).ToListAsync();
                if (cartItems.Any())
                {
                    _context.CartItems.RemoveRange(cartItems);
                }

                _context.Products.Remove(product);
                await _context.SaveChangesAsync();
                return Ok(ApiResponse<string>.SuccessResponse("Đã xóa vĩnh viễn sản phẩm khỏi hệ thống."));
            }

            product.IsActive = false;
            product.UpdatedAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();
            return Ok(ApiResponse<string>.SuccessResponse("Đã ngưng kinh doanh sản phẩm này (xóa mềm thành công)."));
        }

        private static List<BookChapterDto> GenerateBookPreviewChapters(Product p)
        {
            return new List<BookChapterDto>
            {
                new BookChapterDto
                {
                    ChapterNumber = 1,
                    Title = "Chương 1: Khởi đầu hành trình",
                    Content = $"Chào mừng bạn đến với tác phẩm '{p.Title}'. " +
                              (string.IsNullOrWhiteSpace(p.Description) 
                                ? "Đây là chương mở đầu giới thiệu về bối cảnh, nhân vật và những bài học đầu tiên."
                                : p.Description) + 
                              "\n\n[Trích đoạn đọc thử]: Mọi sự khởi đầu đều bắt đầu từ một ước mơ và lòng dũng cảm. Đừng bao giờ từ bỏ hành trình khám phá tri thức của chính mình...\n\n(Hết phần đọc thử chương 1. Quý khách vui lòng mua sách để tiếp tục các chương sau).",
                    IsPreview = true
                }
            };
        }

        private static List<BookChapterDto> GenerateFullBookChapters(Product p)
        {
            return new List<BookChapterDto>
            {
                new BookChapterDto
                {
                    ChapterNumber = 1,
                    Title = "Chương 1: Khởi đầu và Khám phá",
                    Content = $"Nội dung trọn vẹn Chương 1 của tác phẩm '{p.Title}'. " +
                              (string.IsNullOrWhiteSpace(p.Description) ? "Giới thiệu nền tảng tri thức và bài học quan trọng." : p.Description) +
                              "\n\nTrong hành trình này, điều cốt lõi nhất không nằm ở đích đến mà ở sự chuyển hóa trong nhận thức của bạn qua từng trang sách.",
                    IsPreview = false
                },
                new BookChapterDto
                {
                    ChapterNumber = 2,
                    Title = "Chương 2: Thử thách và Đột phá",
                    Content = $"Nội dung trọn vẹn Chương 2 của '{p.Title}'. Đối diện với nghịch cảnh là cơ hội tốt nhất để rèn giũa bản lĩnh và tư duy độc lập. Hãy luôn kiên trì với mục tiêu đã chọn.",
                    IsPreview = false
                },
                new BookChapterDto
                {
                    ChapterNumber = 3,
                    Title = "Chương 3: Ứng dụng thực tiễn & Thành tựu",
                    Content = $"Nội dung trọn vẹn Chương 3 của '{p.Title}'. Biến kiến thức thành hành động thực tế là chìa khóa mở ra cánh cửa thành công và thịnh vượng.",
                    IsPreview = false
                },
                new BookChapterDto
                {
                    ChapterNumber = 4,
                    Title = "Lời kết: Chân trời mới",
                    Content = $"Lời kết cho cuốn sách '{p.Title}'. Cảm ơn bạn đã đồng hành trọn vẹn cùng tác phẩm. Chúc bạn gặt hái được nhiều giá trị và ứng dụng hiệu quả vào cuộc sống!",
                    IsPreview = false
                }
            };
        }

        private static ProductResponseDto MapToResponseDto(Product p)
        {
            return new ProductResponseDto
            {
                ProductId = p.ProductId,
                Title = p.Title,
                Author = p.Author,
                Publisher = p.Publisher,
                Isbn = p.Isbn,
                Category = p.Category,
                Price = p.Price,
                StockQuantity = p.StockQuantity,
                Description = p.Description,
                ImageUrl = p.ImageUrl,
                IsActive = p.IsActive,
                CreatedAt = p.CreatedAt,
                UpdatedAt = p.UpdatedAt
            };
        }
    }
}
