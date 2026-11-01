using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Memory;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Services.Implementations
{
    public class NotificationService : INotificationService
    {
        private readonly AppDbContext _context;
        private readonly IMemoryCache _cache;

        public NotificationService(AppDbContext context, IMemoryCache cache)
        {
            _context = context;
            _cache = cache;
        }

        public async Task<List<NotificationResponseDto>> GetCustomerNotificationsAsync(long customerId, bool? isRead = null)
        {
            var query = _context.Notifications
                .Where(n => n.CustomerId == customerId)
                .AsNoTracking();

            if (isRead.HasValue)
            {
                query = query.Where(n => n.IsRead == isRead.Value);
            }

            return await query
                .OrderByDescending(n => n.CreatedAt)
                .Select(n => new NotificationResponseDto
                {
                    NotificationId = n.NotificationId,
                    Title = n.Title,
                    Message = n.Message,
                    Type = n.Type,
                    IsRead = n.IsRead,
                    CreatedAt = n.CreatedAt,
                    ReadAt = n.ReadAt
                })
                .ToListAsync();
        }

        public async Task<NotificationResponseDto?> MarkAsReadAsync(long notificationId, long customerId)
        {
            var notification = await _context.Notifications
                .FirstOrDefaultAsync(n => n.NotificationId == notificationId && n.CustomerId == customerId);

            if (notification == null)
            {
                return null;
            }

            notification.IsRead = true;
            notification.ReadAt = DateTime.UtcNow;

            _context.Notifications.Update(notification);
            await _context.SaveChangesAsync();

            return new NotificationResponseDto
            {
                NotificationId = notification.NotificationId,
                Title = notification.Title,
                Message = notification.Message,
                Type = notification.Type,
                IsRead = notification.IsRead,
                CreatedAt = notification.CreatedAt,
                ReadAt = notification.ReadAt
            };
        }

        public async Task<int> MarkAllAsReadAsync(long customerId)
        {
            var notifications = await _context.Notifications
                .Where(n => n.CustomerId == customerId && !n.IsRead)
                .ToListAsync();

            if (!notifications.Any())
            {
                return 0;
            }

            var now = DateTime.UtcNow;
            foreach (var n in notifications)
            {
                n.IsRead = true;
                n.ReadAt = now;
            }

            _context.Notifications.UpdateRange(notifications);
            await _context.SaveChangesAsync();

            return notifications.Count;
        }

        public async Task<bool> DeleteNotificationAsync(long notificationId, long customerId)
        {
            var notification = await _context.Notifications
                .FirstOrDefaultAsync(n => n.NotificationId == notificationId && n.CustomerId == customerId);

            if (notification == null)
            {
                return false;
            }

            _context.Notifications.Remove(notification);
            await _context.SaveChangesAsync();
            return true;
        }

        public async Task<NotificationResponseDto> CreateNotificationAsync(long? customerId, string title, string message, string? type = null)
        {
            var notification = new Notification
            {
                CustomerId = customerId,
                Title = title,
                Message = message,
                Type = type,
                IsRead = false,
                CreatedAt = DateTime.UtcNow
            };

            await _context.Notifications.AddAsync(notification);
            await _context.SaveChangesAsync();

            return new NotificationResponseDto
            {
                NotificationId = notification.NotificationId,
                Title = notification.Title,
                Message = notification.Message,
                Type = notification.Type,
                IsRead = notification.IsRead,
                CreatedAt = notification.CreatedAt,
                ReadAt = notification.ReadAt
            };
        }

        public async Task CreateNotificationForRolesAsync(IEnumerable<string> roles, string title, string message, string? type = null)
        {
            var roleList = roles.Where(r => !string.IsNullOrWhiteSpace(r))
                                .Select(r => r.Trim().ToLower())
                                .ToList();
            if (!roleList.Any()) return;

            var targetRecipientIds = await _context.Customers
                .Where(c => c.Role != null && 
                            (c.IsActive == null || c.IsActive == true) &&
                            roleList.Contains(c.Role.ToLower()))
                .Select(c => c.CustomerId)
                .Distinct()
                .ToListAsync();

            if (!targetRecipientIds.Any()) return;

            var now = DateTime.UtcNow;
            var notifications = targetRecipientIds.Select(id => new Notification
            {
                CustomerId = id,
                Title = title,
                Message = message,
                Type = type,
                IsRead = false,
                CreatedAt = now
            }).ToList();

            await _context.Notifications.AddRangeAsync(notifications);
            await _context.SaveChangesAsync();
        }

        /// <summary>
        /// Kiểm tra và thông báo tồn kho thấp CÓ CƠ CHẾ CHỐNG TRÙNG LẶP TRIỆT ĐỂ:
        /// - Chống spam thông báo mỗi lần checkout hoặc quét kho
        /// - Chỉ thông báo 1 lần duy nhất trong chu kỳ 24h hoặc khi vừa xuống ngưỡng
        /// </summary>
        public async Task CheckAndNotifyLowStockAsync(IEnumerable<Product> products, int threshold = 10)
        {
            if (products == null) return;

            var lowStockCandidates = products
                .Where(p => p != null && (p.StockQuantity <= threshold || (p.StockQuantity - p.HoldQuantity) <= threshold))
                .DistinctBy(p => p.ProductId)
                .ToList();

            if (!lowStockCandidates.Any()) return;

            var now = DateTime.UtcNow;
            var recentCutoff = now.AddHours(-24);

            // 1. Chống trùng lặp nhanh cấp bộ nhớ Cache
            var productsToNotify = new List<Product>();
            foreach (var p in lowStockCandidates)
            {
                var cacheKey = $"LowStockCooldown_{p.ProductId}";
                if (_cache.TryGetValue(cacheKey, out _))
                {
                    continue; // Đã cảnh báo trong 24 giờ gần nhất, bỏ qua
                }
                productsToNotify.Add(p);
            }

            if (!productsToNotify.Any()) return;

            // 2. Chống trùng lặp cấp cơ sở dữ liệu (Database check)
            var recentMessages = await _context.Notifications
                .Where(n => n.Type == "inventory" && n.CreatedAt >= recentCutoff)
                .Select(n => n.Message)
                .ToListAsync();

            var trulyNewProducts = new List<Product>();
            foreach (var p in productsToNotify)
            {
                var identifier = $"(Mã: {p.ProductId})";
                if (recentMessages.Any(m => m.Contains(identifier)))
                {
                    // Đã có cảnh báo trong 24h qua, ghi nhớ vào cache để không quét lại DB
                    _cache.Set($"LowStockCooldown_{p.ProductId}", true, TimeSpan.FromHours(24));
                    continue;
                }
                trulyNewProducts.Add(p);
            }

            if (!trulyNewProducts.Any()) return;

            // Lấy danh sách Quản lý (Manager), Quản trị viên (Admin) và Nhân viên (Staff)
            var staffRoles = new[] { "manager", "admin", "staff" };
            var managers = await _context.Customers
                .Where(c => c.Role != null && 
                            (c.IsActive == null || c.IsActive == true) &&
                            staffRoles.Contains(c.Role.ToLower()))
                .Select(c => c.CustomerId)
                .Distinct()
                .ToListAsync();

            if (!managers.Any()) return;

            var notifications = new List<Notification>();

            foreach (var product in trulyNewProducts)
            {
                int remaining = Math.Max(0, product.StockQuantity - product.HoldQuantity);
                foreach (var managerId in managers)
                {
                    notifications.Add(new Notification
                    {
                        CustomerId = managerId,
                        Title = "Cảnh báo tồn kho thấp",
                        Message = $"Sách '{product.Title}' (Mã: {product.ProductId}) hiện chỉ còn {remaining} cuốn khả dụng trong kho (tổng tồn: {product.StockQuantity}, ngưỡng: {threshold}). Vui lòng kiểm tra và nhập thêm hàng.",
                        Type = "inventory",
                        IsRead = false,
                        CreatedAt = now
                    });
                }

                // Kích hoạt cooldown 24 giờ cho sản phẩm này
                _cache.Set($"LowStockCooldown_{product.ProductId}", true, TimeSpan.FromHours(24));
            }

            if (notifications.Any())
            {
                await _context.Notifications.AddRangeAsync(notifications);
                await _context.SaveChangesAsync();
            }
        }

        public async Task<int> CheckAndNotifyAllLowStockAsync(int threshold = 10)
        {
            var lowStockProducts = await _context.Products
                .Where(p => p.IsActive == true && (p.StockQuantity <= threshold || (p.StockQuantity - p.HoldQuantity) <= threshold))
                .ToListAsync();

            if (!lowStockProducts.Any()) return 0;

            await CheckAndNotifyLowStockAsync(lowStockProducts, threshold);
            return lowStockProducts.Count;
        }

        public void ResetLowStockCooldown(long productId)
        {
            _cache.Remove($"LowStockCooldown_{productId}");
        }
    }
}
