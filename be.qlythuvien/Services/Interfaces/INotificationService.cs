using System.Collections.Generic;
using System.Threading.Tasks;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;

namespace qlthuvien_vip.Services.Interfaces
{
    public interface INotificationService
    {
        /// <summary>
        /// Lấy danh sách thông báo của khách hàng
        /// </summary>
        Task<List<NotificationResponseDto>> GetCustomerNotificationsAsync(long customerId, bool? isRead = null);

        /// <summary>
        /// Đánh dấu một thông báo là đã đọc
        /// </summary>
        Task<NotificationResponseDto?> MarkAsReadAsync(long notificationId, long customerId);

        /// <summary>
        /// Đánh dấu tất cả thông báo của khách hàng là đã đọc
        /// </summary>
        Task<int> MarkAllAsReadAsync(long customerId);

        /// <summary>
        /// Xóa thông báo
        /// </summary>
        Task<bool> DeleteNotificationAsync(long notificationId, long customerId);

        /// <summary>
        /// Tự động tạo thông báo khi có sự kiện (đặt hàng, cập nhật đơn hàng, thanh toán, v.v.)
        /// </summary>
        Task<NotificationResponseDto> CreateNotificationAsync(long? customerId, string title, string message, string? type = null);

        /// <summary>
        /// Gửi thông báo đến tất cả người dùng thuộc các vai trò cụ thể (ví dụ Staff, Manager, Admin)
        /// </summary>
        Task CreateNotificationForRolesAsync(IEnumerable<string> roles, string title, string message, string? type = null);

        /// <summary>
        /// Kiểm tra và tự động gửi cảnh báo tồn kho thấp cho các tài khoản Manager và Admin
        /// </summary>
        Task CheckAndNotifyLowStockAsync(IEnumerable<Product> products, int threshold = 10);

        /// <summary>
        /// Quét toàn bộ kho sách trong cơ sở dữ liệu và gửi cảnh báo tồn kho thấp cho Manager và Admin
        /// </summary>
        Task<int> CheckAndNotifyAllLowStockAsync(int threshold = 10);

        /// <summary>
        /// Reset bộ đệm cảnh báo tồn kho thấp cho sản phẩm khi đã được nhập thêm hàng
        /// </summary>
        void ResetLowStockCooldown(long productId);
    }
}
