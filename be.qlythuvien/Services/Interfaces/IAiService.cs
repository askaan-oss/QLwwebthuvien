using System.Threading.Tasks;
using qlthuvien_vip.Models.DTOs;

namespace qlthuvien_vip.Services.Interfaces
{
    public interface IAiService
    {
        /// <summary>
        /// Xử lý tin nhắn tư vấn sách của khách hàng và tìm sách liên quan từ cơ sở dữ liệu.
        /// API key được lấy từ cấu hình Backend hoặc truyền từ client (nếu có).
        /// </summary>
        Task<AiChatResponseDto> ChatAsync(string message, string? clientApiKey = null);

        /// <summary>
        /// Xử lý tin nhắn tư vấn sách kèm các bộ lọc giá, tồn kho, thể loại.
        /// </summary>
        Task<AiChatResponseDto> ChatAsync(AiChatRequestDto request);
    }
}
