using System.Collections.Generic;
using System.Security.Claims;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class NotificationsController : ControllerBase
    {
        private readonly INotificationService _notificationService;

        public NotificationsController(INotificationService notificationService)
        {
            _notificationService = notificationService;
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

        /// <summary>
        /// Lấy danh sách thông báo của khách hàng, có thể lọc theo trạng thái đã đọc (isRead)
        /// </summary>
        [HttpGet]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<List<NotificationResponseDto>>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status401Unauthorized)]
        public async Task<IActionResult> GetNotifications([FromQuery] bool? isRead)
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin người dùng."));
            }

            var notifications = await _notificationService.GetCustomerNotificationsAsync(customerId.Value, isRead);
            return Ok(ApiResponse<List<NotificationResponseDto>>.SuccessResponse(notifications, "Lấy danh sách thông báo thành công."));
        }

        /// <summary>
        /// Đánh dấu một thông báo là đã đọc
        /// </summary>
        [HttpPut("{id}/read")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<NotificationResponseDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status401Unauthorized)]
        public async Task<IActionResult> MarkAsRead(long id)
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin người dùng."));
            }

            var notification = await _notificationService.MarkAsReadAsync(id, customerId.Value);
            if (notification == null)
            {
                return NotFound(ApiResponse<string>.ErrorResponse("Không tìm thấy thông báo hoặc bạn không có quyền truy cập."));
            }

            return Ok(ApiResponse<NotificationResponseDto>.SuccessResponse(notification, "Đánh dấu thông báo đã đọc thành công."));
        }

        /// <summary>
        /// Đánh dấu tất cả thông báo là đã đọc
        /// </summary>
        [HttpPut("mark-all-read")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status401Unauthorized)]
        public async Task<IActionResult> MarkAllAsRead()
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin người dùng."));
            }

            int count = await _notificationService.MarkAllAsReadAsync(customerId.Value);
            return Ok(ApiResponse<string>.SuccessResponse($"Đã đánh dấu {count} thông báo là đã đọc.", "Thành công."));
        }

        /// <summary>
        /// Xóa một thông báo
        /// </summary>
        [HttpDelete("{id}")]
        [Authorize]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status401Unauthorized)]
        public async Task<IActionResult> DeleteNotification(long id)
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin người dùng."));
            }

            bool deleted = await _notificationService.DeleteNotificationAsync(id, customerId.Value);
            if (!deleted)
            {
                return NotFound(ApiResponse<string>.ErrorResponse("Không tìm thấy thông báo cần xóa."));
            }

            return Ok(ApiResponse<string>.SuccessResponse("", "Xóa thông báo thành công."));
        }

        /// <summary>
        /// [Admin/Manager Only] Tạo thông báo thủ công cho khách hàng
        /// </summary>
        [HttpPost("create")]
        [Authorize(Roles = "Admin,Manager")]
        [ProducesResponseType(typeof(ApiResponse<NotificationResponseDto>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> CreateNotification([FromBody] CreateNotificationDto dto)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(ApiResponse<string>.ErrorResponse("Dữ liệu gửi lên không hợp lệ."));
            }

            var notification = await _notificationService.CreateNotificationAsync(
                dto.CustomerId,
                dto.Title,
                dto.Message,
                dto.Type);

            return Ok(ApiResponse<NotificationResponseDto>.SuccessResponse(notification, "Tạo thông báo thành công."));
        }

        /// <summary>
        /// [Admin/Manager/Staff] Chủ động quét toàn bộ kho sách và gửi cảnh báo tồn kho thấp cho Quản lý & Nhân viên
        /// </summary>
        [HttpPost("check-low-stock")]
        [Authorize(Roles = "Admin,Manager,Staff")]
        [ProducesResponseType(typeof(ApiResponse<string>), StatusCodes.Status200OK)]
        public async Task<IActionResult> TriggerLowStockCheck([FromQuery] int threshold = 10)
        {
            int count = await _notificationService.CheckAndNotifyAllLowStockAsync(threshold);
            string msg = count > 0 
                ? $"Đã phát hiện và gửi cảnh báo cho {count} sản phẩm có tồn kho thấp (ngưỡng: {threshold})."
                : $"Tất cả sản phẩm đều đảm bảo lượng tồn kho an toàn (ngưỡng: {threshold}).";
            return Ok(ApiResponse<string>.SuccessResponse(count.ToString(), msg));
        }

        /// <summary>
        /// [Admin/Manager/Staff] Lấy danh sách thông báo điều hành hệ thống (đơn hàng mới, tồn kho thấp, thanh toán)
        /// </summary>
        [HttpGet("system")]
        [Authorize(Roles = "Admin,Manager,Staff")]
        [ProducesResponseType(typeof(ApiResponse<List<NotificationResponseDto>>), StatusCodes.Status200OK)]
        public async Task<IActionResult> GetSystemNotifications([FromQuery] bool? isRead)
        {
            var customerId = GetCurrentCustomerId();
            if (!customerId.HasValue)
            {
                return Unauthorized(ApiResponse<string>.ErrorResponse("Không tìm thấy thông tin tài khoản nhân viên/quản lý."));
            }

            var notifications = await _notificationService.GetCustomerNotificationsAsync(customerId.Value, isRead);
            return Ok(ApiResponse<List<NotificationResponseDto>>.SuccessResponse(notifications, "Lấy danh sách thông báo điều hành thành công."));
        }
    }
}
