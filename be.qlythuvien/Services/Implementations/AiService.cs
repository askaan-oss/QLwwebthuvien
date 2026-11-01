using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Services.Implementations
{
    public class AiService : IAiService
    {
        private readonly AppDbContext _context;
        private readonly IConfiguration _configuration;
        private readonly HttpClient _httpClient;
        private readonly ILogger<AiService> _logger;

        public AiService(
            AppDbContext context,
            IConfiguration configuration,
            HttpClient httpClient,
            ILogger<AiService> logger)
        {
            _context = context;
            _configuration = configuration;
            _httpClient = httpClient;
            _logger = logger;
        }

        public async Task<AiChatResponseDto> ChatAsync(string message, string? clientApiKey = null)
        {
            return await ChatAsync(new AiChatRequestDto
            {
                Message = message,
                ApiKey = clientApiKey,
                InStockOnly = true
            });
        }

        public async Task<AiChatResponseDto> ChatAsync(AiChatRequestDto request)
        {
            var cleanMessage = request.Message.Trim();
            var lowerMessage = cleanMessage.ToLower();

            // 1. Phân tích ngữ nghĩa để tự động trích xuất các điều kiện lọc giá từ nội dung tin nhắn nếu DTO chưa truyền
            decimal? minPrice = request.MinPrice;
            decimal? maxPrice = request.MaxPrice;
            bool inStockOnly = request.InStockOnly ?? true;
            string? category = request.Category?.Trim().ToLower();

            // Regex trích xuất yêu cầu giá tiếng Việt:
            // "dưới 100k", "< 100k", "dưới 150000", "nhỏ hơn 200k"
            var underMatch = System.Text.RegularExpressions.Regex.Match(lowerMessage, @"(?:dưới|<|nhỏ hơn|ít hơn)\s*(\d+(?:[.,]\d+)?)\s*(k|nghìn|ngàn|tr|triệu|đ|vnd)?");
            if (underMatch.Success && !maxPrice.HasValue)
            {
                if (decimal.TryParse(underMatch.Groups[1].Value.Replace(",", "."), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var val))
                {
                    string unit = underMatch.Groups[2].Value;
                    if (unit.Contains("k") || unit.Contains("nghìn") || unit.Contains("ngàn") || val < 1000) val *= 1000m;
                    else if (unit.Contains("tr") || unit.Contains("triệu")) val *= 1000000m;
                    maxPrice = val;
                }
            }

            // "trên 100k", "> 100k", "từ 100k"
            var overMatch = System.Text.RegularExpressions.Regex.Match(lowerMessage, @"(?:trên|>|lớn hơn|từ)\s*(\d+(?:[.,]\d+)?)\s*(k|nghìn|ngàn|tr|triệu|đ|vnd)?");
            if (overMatch.Success && !minPrice.HasValue)
            {
                if (decimal.TryParse(overMatch.Groups[1].Value.Replace(",", "."), System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out var val))
                {
                    string unit = overMatch.Groups[2].Value;
                    if (unit.Contains("k") || unit.Contains("nghìn") || unit.Contains("ngàn") || val < 1000) val *= 1000m;
                    else if (unit.Contains("tr") || unit.Contains("triệu")) val *= 1000000m;
                    minPrice = val;
                }
            }

            // Nếu người dùng hỏi "giá rẻ" hoặc "rẻ" mà chưa có maxPrice -> mặc định gợi ý sách dưới 150.000 VNĐ
            if ((lowerMessage.Contains("giá rẻ") || lowerMessage.Contains("sách rẻ") || lowerMessage.Contains("hạt dẻ")) && !maxPrice.HasValue)
            {
                maxPrice = 150000m;
            }

            // Chuẩn hóa và bảo vệ tính hợp lệ của bộ lọc giá
            if (minPrice.HasValue && minPrice.Value < 0) minPrice = 0;
            if (maxPrice.HasValue && maxPrice.Value < 0) maxPrice = null;
            if (minPrice.HasValue && maxPrice.HasValue && minPrice.Value > maxPrice.Value)
            {
                (minPrice, maxPrice) = (maxPrice, minPrice);
            }

            // 2. Tìm kiếm sách từ cơ sở dữ liệu có áp dụng toàn bộ bộ lọc
            var query = _context.Products
                .Where(p => p.IsActive == true)
                .AsNoTracking();

            // Lọc tồn kho khả dụng (chỉ lấy sách còn hàng)
            if (inStockOnly)
            {
                query = query.Where(p => p.StockQuantity > 0 && (p.StockQuantity - p.HoldQuantity) > 0);
            }

            // Lọc theo khoảng giá
            if (minPrice.HasValue)
            {
                query = query.Where(p => p.Price >= minPrice.Value);
            }
            if (maxPrice.HasValue)
            {
                query = query.Where(p => p.Price <= maxPrice.Value);
            }

            // Lọc theo thể loại
            if (!string.IsNullOrWhiteSpace(category))
            {
                query = query.Where(p => p.Category != null && p.Category.ToLower().Contains(category));
            }

            // Rank meaningful topics instead of falling back to unrelated high-stock books.
            var candidates = await query.ToListAsync();
            var matchedProducts = candidates
                .Select(p => new { Product = p, Score = BookTopicMatcher.Score(cleanMessage, p.Title, p.Author, p.Category, p.Description) })
                .Where(p => p.Score > 0)
                .OrderByDescending(p => p.Score)
                .ThenBy(p => p.Product.ProductId)
                .Take(6)
                .Select(p => p.Product)
                .ToList();

            var productDtos = matchedProducts.Select(p => new ProductResponseDto
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
            }).ToList();

            // 3. Gọi AI Service sử dụng API Key lưu tập trung tại BE (Gemini) kèm ràng buộc ngữ cảnh
            var (aiResponseText, isRealAi, source) = matchedProducts.Count == 0
                ? ("Chưa tìm thấy sách phù hợp với chủ đề và mức giá bạn yêu cầu trong kho hiện tại. Bạn có thể thử tên sách, tác giả hoặc chủ đề cụ thể hơn.", false, "Catalog search")
                : await CallAiApiAsync(cleanMessage, matchedProducts, request.ApiKey);

            return new AiChatResponseDto
            {
                Response = aiResponseText,
                Timestamp = DateTime.UtcNow,
                RelatedProducts = productDtos,
                Source = source,
                IsRealAi = isRealAi
            };
        }

        private async Task<(string text, bool isRealAi, string source)> CallAiApiAsync(
            string userMessage, 
            List<Product> availableBooks,
            string? clientApiKey = null)
        {
            // Lấy API key từ client (nếu có), hoặc cấu hình backend (không để lộ ra client), hoặc biến môi trường
            var apiKey = !string.IsNullOrWhiteSpace(clientApiKey)
                ? clientApiKey.Trim()
                : (_configuration["Ai:ApiKey"] 
                   ?? _configuration["Ai:GeminiApiKey"] 
                   ?? Environment.GetEnvironmentVariable("GEMINI_API_KEY"));

            var provider = _configuration["Ai:Provider"] ?? "Gemini";
            var model = _configuration["Ai:Model"] ?? "gemini-1.5-flash";

            // Xây dựng danh sách sách ngữ cảnh
            var booksContext = string.Join("\n", availableBooks.Select(b =>
                $"- [Mã: {b.ProductId}] '{b.Title}' | Tác giả: {b.Author ?? "Chưa rõ"} | Thể loại: {b.Category ?? "Chung"} | Giá: {b.Price:N0}đ | Tồn kho: {b.StockQuantity} | Tóm tắt: {b.Description}"));

            var prompt = $@"Bạn là trợ lý AI chuyên viên tư vấn sách tận tâm và am hiểu của Nhà sách Bookstore.
Dưới đây là danh sách sách hiện có tại nhà sách:
{booksContext}

Yêu cầu của khách hàng: ""{userMessage}""

Nhiệm vụ của bạn:
1. Trả lời thân thiện, lịch sự, nhiệt tình bằng tiếng Việt.
2. Gợi ý cụ thể các cuốn sách phù hợp nhất từ danh sách trên (nêu rõ tên sách, tác giả, giá bán và lý do cuốn sách này phù hợp với sở thích hoặc nhu cầu của khách hàng).
3. Nếu không có cuốn sách nào khớp hoàn toàn, hãy giới thiệu các cuốn sách nổi bật hiện có trong danh sách trên và đưa ra lời khuyên hữu ích cho người đọc.";

            // Nếu có API key hợp lệ của Gemini
            if (!string.IsNullOrWhiteSpace(apiKey) && apiKey.Length > 15 && provider.Equals("Gemini", StringComparison.OrdinalIgnoreCase))
            {
                try
                {
                    var geminiUrl = $"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={apiKey}";
                    var requestBody = new
                    {
                        contents = new[]
                        {
                            new
                            {
                                parts = new[]
                                {
                                    new { text = prompt }
                                }
                            }
                        },
                        generationConfig = new
                        {
                            temperature = 0.7,
                            maxOutputTokens = 800
                        }
                    };

                    var content = new StringContent(JsonSerializer.Serialize(requestBody), Encoding.UTF8, "application/json");
                    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(15));
                    var httpResponse = await _httpClient.PostAsync(geminiUrl, content, cts.Token);

                    if (httpResponse.IsSuccessStatusCode)
                    {
                        var responseJson = await httpResponse.Content.ReadAsStringAsync();
                        using var doc = JsonDocument.Parse(responseJson);
                        if (doc.RootElement.TryGetProperty("candidates", out var candidates) &&
                            candidates.GetArrayLength() > 0 &&
                            candidates[0].TryGetProperty("content", out var contentElem) &&
                            contentElem.TryGetProperty("parts", out var parts) &&
                            parts.GetArrayLength() > 0 &&
                            parts[0].TryGetProperty("text", out var textElem))
                        {
                            var text = textElem.GetString();
                            if (!string.IsNullOrWhiteSpace(text))
                            {
                                return (text.Trim(), true, $"Gemini AI ({model})");
                            }
                        }
                    }
                    else
                    {
                        var err = await httpResponse.Content.ReadAsStringAsync();
                        _logger.LogWarning("Gemini API gọi không thành công. Mã trạng thái: {StatusCode}, Chi tiết: {Error}", httpResponse.StatusCode, err);
                    }
                }
                catch (OperationCanceledException)
                {
                    _logger.LogWarning("Gọi external AI API bị timeout sau 15 giây, tự động chuyển sang chế độ tư vấn tích hợp.");
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Lỗi khi gọi external AI API, chuyển sang chế độ tư vấn tích hợp.");
                }
            }
            else
            {
                _logger.LogInformation("Ai:ApiKey chưa được cấu hình. Hệ thống sử dụng mẫu tư vấn thông minh tích hợp.");
            }

            // Fallback: Chế độ tư vấn thông minh tích hợp (khi chưa cấu hình khóa ngoài hoặc offline)
            var fallback = GenerateSmartFallbackResponse(userMessage, availableBooks);
            return (fallback, false, "Smart Fallback (Local Engine)");
        }

        private string GenerateSmartFallbackResponse(string userMessage, List<Product> books)
        {
            var sb = new StringBuilder();
            sb.AppendLine($"Xin chào quý khách! Cảm ơn bạn đã quan tâm đến kho sách của Bookstore về chủ đề \"{userMessage}\".");
            sb.AppendLine();

            if (books.Any())
            {
                sb.AppendLine("Dựa trên tìm kiếm và sở thích của bạn, tôi xin gợi ý những tựa sách rất phù hợp đang có sẵn tại cửa hàng:");
                sb.AppendLine();

                int idx = 1;
                foreach (var book in books)
                {
                    sb.AppendLine($"{idx}. **{book.Title}**");
                    if (!string.IsNullOrWhiteSpace(book.Author))
                        sb.AppendLine($"   - Tác giả: {book.Author}");
                    if (!string.IsNullOrWhiteSpace(book.Category))
                        sb.AppendLine($"   - Thể loại: {book.Category}");
                    sb.AppendLine($"   - Giá ưu đãi: {book.Price:N0} VNĐ (Còn {book.StockQuantity} cuốn)");
                    if (!string.IsNullOrWhiteSpace(book.Description))
                    {
                        var shortDesc = book.Description.Length > 120 
                            ? book.Description.Substring(0, 120) + "..." 
                            : book.Description;
                        sb.AppendLine($"   - Giới thiệu: {shortDesc}");
                    }
                    sb.AppendLine();
                    idx++;
                }

                sb.AppendLine("Bạn có thể thêm trực tiếp các tựa sách trên vào Giỏ hàng hoặc đặt mua ngay hôm nay để nhận ưu đãi vận chuyển tốt nhất nhé!");
            }
            else
            {
                sb.AppendLine("Hiện tại cửa hàng chưa có tựa sách hoàn toàn trùng khớp với từ khóa này. Bạn có thể thử tìm kiếm với tên tác giả, thể loại khác hoặc liên hệ bộ phận hỗ trợ để chúng tôi đặt thêm sách cho bạn!");
            }

            return sb.ToString().TrimEnd();
        }
    }
}
