using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Services.Implementations
{
    public class DashboardService : IDashboardService
    {
        private readonly AppDbContext _context;

        public DashboardService(AppDbContext context)
        {
            _context = context;
        }

        public async Task<DashboardResponseDto> GetDashboardStatsAsync(
            DateTime? fromDate,
            DateTime? toDate,
            int topProducts = 5,
            int lowStockThreshold = 10)
        {
            // Mặc định 30 ngày gần nhất nếu không truyền
            if (!fromDate.HasValue)
                fromDate = DateTime.UtcNow.AddDays(-30);
            else
                fromDate = fromDate.Value.Date;

            if (!toDate.HasValue)
            {
                toDate = DateTime.UtcNow;
            }
            else
            {
                // Khi FE truyền toDate dạng ngày (yyyy-MM-dd với giờ 00:00:00),
                // cần lấy trọn vẹn đến cuối ngày (23:59:59.999) để không bỏ sót các giao dịch phát sinh sau 00:00
                toDate = toDate.Value.Date.AddDays(1).AddTicks(-1);
            }

            // Các trạng thái đơn hủy/thất bại cần loại trừ triệt để khỏi doanh thu và thống kê
            var invalidStatuses = new[] { "CANCELLED", "EXPIRED", "RETURNED" };

            // Điều kiện đơn hàng hợp lệ chưa bị hủy
            var baseOrdersQuery = _context.Orders
                .Where(o => o.CreatedAt >= fromDate && o.CreatedAt <= toDate &&
                            o.OrderStatus != null &&
                            !invalidStatuses.Contains(o.OrderStatus.ToUpper()));

            // 1. Phân loại chuẩn xác:
            // - ĐƠN ĐÃ THU TIỀN THỰC TẾ (Collected):
            //   + Đơn thanh toán trực tuyến (VNPAY, Momo, Banking...): đã PAID, DELIVERED, COMPLETED hoặc có Transaction SUCCESS
            //   + Đơn COD: CHỈ TÍNH KHI ĐÃ GIAO HÀNG THÀNH CÔNG (DELIVERED, COMPLETED) hoặc Transaction SUCCESS. Tuyệt đối không tính COD đang xử lý/giao hàng.
            var collectedOrdersQuery = baseOrdersQuery.Where(o =>
                (o.PaymentMethod != null && o.PaymentMethod.ToUpper() == "COD" &&
                    (o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                     o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))
                ||
                ((o.PaymentMethod == null || o.PaymentMethod.ToUpper() != "COD") &&
                    (o.OrderStatus.ToUpper() == "PAID" || o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                     o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS"))));

            // - ĐƠN ĐANG XỬ LÝ CHƯA THU TIỀN (Pending / Processing):
            //   Bao gồm đơn COD đang PENDING, CONFIRMED, PROCESSING, SHIPPING (chưa thu tiền thực tế)
            var pendingOrdersQuery = baseOrdersQuery.Where(o =>
                !((o.PaymentMethod != null && o.PaymentMethod.ToUpper() == "COD" &&
                    (o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                     o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))
                ||
                ((o.PaymentMethod == null || o.PaymentMethod.ToUpper() != "COD") &&
                    (o.OrderStatus.ToUpper() == "PAID" || o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                     o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))));

            // Tính tổng doanh thu thực thu (không còn bị tính dư do loại bỏ COD chưa giao)
            var collectedRevenue = await collectedOrdersQuery.SumAsync(o => o.TotalAmount);

            // Tính giá trị các đơn hàng đang xử lý chưa thu tiền
            var pendingRevenue = await pendingOrdersQuery.SumAsync(o => o.TotalAmount);

            // 2. Thống kê tổng số đơn hàng hợp lệ
            var totalOrders = await baseOrdersQuery.CountAsync();

            // 3. Thống kê tổng số khách hàng thực tế (loại bỏ Admin/Manager/Staff)
            var excludedRoles = new[] { "ADMIN", "MANAGER", "STAFF" };
            var totalCustomers = await _context.Customers
                .Where(c => (c.Role == null || !excludedRoles.Contains(c.Role.ToUpper())) &&
                            (c.IsActive == null || c.IsActive == true))
                .CountAsync();

            // 4. Danh sách sách bán chạy nhất:
            // CHỈ TÍNH TỪ CÁC ĐƠN HÀNG ĐÃ THU TIỀN HOẶC GIAO THÀNH CÔNG (tránh đơn ảo/đơn COD chưa thanh toán)
            var bestSellingProducts = await _context.OrderItems
                .Where(oi => oi.Order.CreatedAt >= fromDate &&
                             oi.Order.CreatedAt <= toDate &&
                             oi.Order.OrderStatus != null &&
                             !invalidStatuses.Contains(oi.Order.OrderStatus.ToUpper()) &&
                             ((oi.Order.PaymentMethod != null && oi.Order.PaymentMethod.ToUpper() == "COD" &&
                               (oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED" ||
                                oi.Order.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))
                              ||
                              ((oi.Order.PaymentMethod == null || oi.Order.PaymentMethod.ToUpper() != "COD") &&
                               (oi.Order.OrderStatus.ToUpper() == "PAID" || oi.Order.OrderStatus.ToUpper() == "DELIVERED" || oi.Order.OrderStatus.ToUpper() == "COMPLETED" ||
                                oi.Order.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))))
                .GroupBy(oi => new { oi.ProductId, Title = oi.Product != null ? oi.Product.Title : "Sách #" + oi.ProductId })
                .Select(g => new BestSellingProductDto
                {
                    ProductId = g.Key.ProductId,
                    Title = g.Key.Title,
                    QuantitySold = g.Sum(oi => oi.Quantity),
                    TotalRevenue = g.Sum(oi => oi.Subtotal)
                })
                .OrderByDescending(p => p.QuantitySold)
                .Take(topProducts)
                .ToListAsync();

            // 5. Danh sách sách tồn kho thấp
            var lowStockProducts = await _context.Products
                .Where(p => (p.StockQuantity <= lowStockThreshold || (p.StockQuantity - p.HoldQuantity) <= lowStockThreshold) && p.IsActive == true)
                .Select(p => new LowStockProductDto
                {
                    ProductId = p.ProductId,
                    Title = p.Title,
                    StockQuantity = p.StockQuantity,
                    HoldQuantity = p.HoldQuantity
                })
                .OrderBy(p => p.StockQuantity)
                .ToListAsync();

            // 6. Doanh thu theo ngày hôm nay / ngày gần nhất trong khoảng (Tách doanh thu đã thu và giá trị đang xử lý)
            var startOfLastDate = toDate.Value.Date;
            var endOfLastDate = startOfLastDate.AddDays(1);

            var dailyOrders = await _context.Orders
                .Where(o => o.CreatedAt.HasValue &&
                            o.CreatedAt.Value >= startOfLastDate &&
                            o.CreatedAt.Value < endOfLastDate &&
                            o.OrderStatus != null &&
                            !invalidStatuses.Contains(o.OrderStatus.ToUpper()))
                .Include(o => o.PaymentTransactions)
                .AsNoTracking()
                .ToListAsync();

            DailyRevenueStatistic? dailyRevenue = null;
            if (dailyOrders.Any())
            {
                var dailyCollected = dailyOrders
                    .Where(o => (o.PaymentMethod != null && o.PaymentMethod.ToUpper() == "COD" &&
                                 (o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                                  o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))
                                ||
                                ((o.PaymentMethod == null || o.PaymentMethod.ToUpper() != "COD") &&
                                 (o.OrderStatus.ToUpper() == "PAID" || o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                                  o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS"))))
                    .Sum(o => o.TotalAmount);

                var dailyPending = dailyOrders
                    .Where(o => !((o.PaymentMethod != null && o.PaymentMethod.ToUpper() == "COD" &&
                                  (o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                                   o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))
                                 ||
                                 ((o.PaymentMethod == null || o.PaymentMethod.ToUpper() != "COD") &&
                                  (o.OrderStatus.ToUpper() == "PAID" || o.OrderStatus.ToUpper() == "DELIVERED" || o.OrderStatus.ToUpper() == "COMPLETED" ||
                                   o.PaymentTransactions.Any(pt => pt.PaymentStatus == "SUCCESS")))))
                    .Sum(o => o.TotalAmount);

                dailyRevenue = new DailyRevenueStatistic
                {
                    Date = startOfLastDate,
                    Revenue = dailyCollected,
                    PendingRevenue = dailyPending,
                    OrderCount = dailyOrders.Count
                };
            }

            return new DashboardResponseDto
            {
                TotalRevenue = collectedRevenue, // Doanh thu thực tế đã thu, không tính khống đơn COD đang xử lý
                CollectedRevenue = collectedRevenue,
                PendingRevenue = pendingRevenue,
                ProcessingOrdersValue = pendingRevenue,
                PotentialRevenue = collectedRevenue + pendingRevenue,
                TotalOrders = totalOrders,
                TotalCustomers = totalCustomers,
                BestSellingProducts = bestSellingProducts,
                LowStockProducts = lowStockProducts,
                DailyRevenue = dailyRevenue
            };
        }
    }
}
