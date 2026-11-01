using System.Collections.Generic;
using System.Threading.Tasks;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;

namespace qlthuvien_vip.Services.Interfaces
{
    public class BookContentResult
    {
        public string Excerpt { get; set; } = null!;
        public List<BookChapterDto> PreviewChapters { get; set; } = new List<BookChapterDto>();
        public List<BookChapterDto> FullChapters { get; set; } = new List<BookChapterDto>();
        public int TotalPages { get; set; } = 10;
        public int TotalPreviewPages { get; set; } = 3;

        /// <summary>
        /// True nếu là sách đã nhập nội dung riêng đầy đủ, false nếu là bản tóm tắt/biên soạn hoặc sinh theo thể loại
        /// </summary>
        public bool IsFullBook { get; set; } = false;

        /// <summary>
        /// Custom (Bản trọn vẹn), Curated (Biên soạn/Tóm tắt), Generated (Theo thể loại)
        /// </summary>
        public string ContentType { get; set; } = "Curated";

        /// <summary>
        /// Ghi chú minh bạch về nguồn và tính hoàn chỉnh của nội dung
        /// </summary>
        public string ContentNote { get; set; } = string.Empty;
    }

    public class UpdateBookContentRequestDto
    {
        public string Excerpt { get; set; } = null!;
        public List<BookChapterDto> Chapters { get; set; } = new List<BookChapterDto>();
    }

    public interface IBookContentService
    {
        Task<BookContentResult> GetBookContentAsync(Product product);
        Task<bool> SaveCustomBookContentAsync(long productId, string excerpt, List<BookChapterDto> chapters);
    }
}
