using System;
using System.Collections.Generic;

namespace qlthuvien_vip.Models.DTOs
{
    public class DashboardResponseDto
    {
        /// <summary>
        /// Tổng doanh thu thực tế đã thu tiền (Không bị tính dư do loại trừ đơn COD chưa giao)
        /// </summary>
        public decimal TotalRevenue { get; set; }

        /// <summary>
        /// Doanh thu thực tế đã thu (bằng TotalRevenue)
        /// </summary>
        public decimal CollectedRevenue { get; set; }

        /// <summary>
        /// Giá trị các đơn hàng đang xử lý chưa thu tiền (Đơn COD đang xác nhận/xử lý/giao hàng)
        /// </summary>
        public decimal PendingRevenue { get; set; }

        /// <summary>
        /// Giá trị các đơn hàng đang xử lý (Alias của PendingRevenue)
        /// </summary>
        public decimal ProcessingOrdersValue { get; set; }

        /// <summary>
        /// Tổng giá trị tiềm năng = Doanh thu đã thu + Giá trị đơn đang xử lý
        /// </summary>
        public decimal PotentialRevenue { get; set; }

        public int TotalOrders { get; set; }

        public int TotalCustomers { get; set; }

        public List<BestSellingProductDto> BestSellingProducts { get; set; } = new List<BestSellingProductDto>();

        public List<LowStockProductDto> LowStockProducts { get; set; } = new List<LowStockProductDto>();

        public DailyRevenueStatistic? DailyRevenue { get; set; }
    }

    public class BestSellingProductDto
    {
        public long ProductId { get; set; }

        public string Title { get; set; } = null!;

        public int QuantitySold { get; set; }

        public decimal TotalRevenue { get; set; }
    }

    public class LowStockProductDto
    {
        public long ProductId { get; set; }

        public string Title { get; set; } = null!;

        public int StockQuantity { get; set; }

        public int HoldQuantity { get; set; }
    }

    public class DailyRevenueStatistic
    {
        public DateTime Date { get; set; }

        /// <summary>
        /// Doanh thu thực tế đã thu trong ngày
        /// </summary>
        public decimal Revenue { get; set; }

        /// <summary>
        /// Giá trị các đơn đang xử lý phát sinh trong ngày
        /// </summary>
        public decimal PendingRevenue { get; set; }

        public int OrderCount { get; set; }
    }

    public class AiChatRequestDto
    {
        public string Message { get; set; } = null!;

        public string? ApiKey { get; set; }

        /// <summary>
        /// Lọc giá tối thiểu (tùy chọn)
        /// </summary>
        public decimal? MinPrice { get; set; }

        /// <summary>
        /// Lọc giá tối đa (tùy chọn)
        /// </summary>
        public decimal? MaxPrice { get; set; }

        /// <summary>
        /// Chỉ gợi ý sách còn hàng trong kho (mặc định true)
        /// </summary>
        public bool? InStockOnly { get; set; } = true;

        /// <summary>
        /// Lọc theo thể loại sách (tùy chọn)
        /// </summary>
        public string? Category { get; set; }
    }

    public class AiChatResponseDto
    {
        public string Response { get; set; } = null!;

        public DateTime? Timestamp { get; set; }

        public List<ProductResponseDto>? RelatedProducts { get; set; }

        /// <summary>
        /// Nguồn trả lời: "Gemini AI (Realtime)" hoặc "Smart Fallback (Local Engine)"
        /// </summary>
        public string? Source { get; set; }

        /// <summary>
        /// True nếu được sinh từ dịch vụ AI thật (Gemini/OpenAI), False nếu dùng mẫu trả lời tích hợp sẵn
        /// </summary>
        public bool IsRealAi { get; set; }
    }
}
