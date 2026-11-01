using System;
using System.ComponentModel.DataAnnotations;

namespace qlthuvien_vip.Models.DTOs
{
    public class CreateProductDto
    {
        [Required(ErrorMessage = "Tên sản phẩm không được để trống")]
        [MaxLength(255, ErrorMessage = "Tên sản phẩm tối đa 255 ký tự")]
        public string Title { get; set; } = null!;

        [MaxLength(255, ErrorMessage = "Tên tác giả tối đa 255 ký tự")]
        public string? Author { get; set; }

        [MaxLength(255, ErrorMessage = "Tên nhà xuất bản tối đa 255 ký tự")]
        public string? Publisher { get; set; }

        [MaxLength(50, ErrorMessage = "Mã ISBN tối đa 50 ký tự")]
        public string? Isbn { get; set; }

        [MaxLength(100, ErrorMessage = "Thể loại tối đa 100 ký tự")]
        public string? Category { get; set; }

        [Required(ErrorMessage = "Giá sản phẩm không được để trống")]
        [Range(0, double.MaxValue, ErrorMessage = "Giá sản phẩm phải lớn hơn hoặc bằng 0")]
        public decimal Price { get; set; }

        [Required(ErrorMessage = "Số lượng tồn kho không được để trống")]
        [Range(0, int.MaxValue, ErrorMessage = "Số lượng tồn kho phải lớn hơn hoặc bằng 0")]
        public int StockQuantity { get; set; }

        public string? Description { get; set; }

        [MaxLength(500, ErrorMessage = "Đường dẫn ảnh tối đa 500 ký tự")]
        public string? ImageUrl { get; set; }

        public bool IsActive { get; set; } = true;
    }

    public class UpdateProductDto
    {
        [Required(ErrorMessage = "Tên sản phẩm không được để trống")]
        [MaxLength(255, ErrorMessage = "Tên sản phẩm tối đa 255 ký tự")]
        public string Title { get; set; } = null!;

        [MaxLength(255, ErrorMessage = "Tên tác giả tối đa 255 ký tự")]
        public string? Author { get; set; }

        [MaxLength(255, ErrorMessage = "Tên nhà xuất bản tối đa 255 ký tự")]
        public string? Publisher { get; set; }

        [MaxLength(50, ErrorMessage = "Mã ISBN tối đa 50 ký tự")]
        public string? Isbn { get; set; }

        [MaxLength(100, ErrorMessage = "Thể loại tối đa 100 ký tự")]
        public string? Category { get; set; }

        [Required(ErrorMessage = "Giá sản phẩm không được để trống")]
        [Range(0, double.MaxValue, ErrorMessage = "Giá sản phẩm phải lớn hơn hoặc bằng 0")]
        public decimal Price { get; set; }

        [Required(ErrorMessage = "Số lượng tồn kho không được để trống")]
        [Range(0, int.MaxValue, ErrorMessage = "Số lượng tồn kho phải lớn hơn hoặc bằng 0")]
        public int StockQuantity { get; set; }

        public string? Description { get; set; }

        [MaxLength(500, ErrorMessage = "Đường dẫn ảnh tối đa 500 ký tự")]
        public string? ImageUrl { get; set; }

        public bool IsActive { get; set; } = true;
    }

    public class ProductResponseDto
    {
        public long ProductId { get; set; }
        public string Title { get; set; } = null!;
        public string? Author { get; set; }
        public string? Publisher { get; set; }
        public string? Isbn { get; set; }
        public string? Category { get; set; }
        public decimal Price { get; set; }
        public int StockQuantity { get; set; }
        public string? Description { get; set; }
        public string? ImageUrl { get; set; }
        public bool? IsActive { get; set; }
        public DateTime? CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
    }

    public class PagedResult<T>
    {
        public IEnumerable<T> Items { get; set; } = new List<T>();
        public int TotalItems { get; set; }
        public int Page { get; set; }
        public int PageSize { get; set; }
        public int TotalPages { get; set; }
        public bool HasPreviousPage => Page > 1;
        public bool HasNextPage => Page < TotalPages;
    }

    public class BookChapterDto
    {
        public int ChapterNumber { get; set; }
        public string Title { get; set; } = null!;
        public string Content { get; set; } = null!;
        public bool IsPreview { get; set; }
    }

    public class ProductPreviewDto
    {
        public long ProductId { get; set; }
        public string Title { get; set; } = null!;
        public string? Author { get; set; }
        public string? Publisher { get; set; }
        public string? Category { get; set; }
        public decimal Price { get; set; }
        public string? ImageUrl { get; set; }
        public string? Description { get; set; }
        public bool IsPurchased { get; set; }
        public bool CanReadFull { get; set; }
        public int TotalPreviewPages { get; set; }

        /// <summary>
        /// Đoạn trích đọc thử riêng của từng cuốn sách (Khớp hoàn toàn với FE đọc d.excerpt)
        /// </summary>
        public string Excerpt { get; set; } = null!;

        /// <summary>
        /// Tương thích ngược với BE cũ
        /// </summary>
        public string PreviewContent { get; set; } = null!;

        public List<BookChapterDto> PreviewChapters { get; set; } = new List<BookChapterDto>();
        public bool IsFullBook { get; set; }
        public string? ContentNote { get; set; }
        public string Message { get; set; } = null!;

        /// <summary>
        /// Đường link mở giao diện đọc toàn bộ sách sau khi mua
        /// </summary>
        public string ReaderUrl { get; set; } = null!;
    }

    public class ProductEbookDto
    {
        public long ProductId { get; set; }
        public string Title { get; set; } = null!;
        public string? Author { get; set; }
        public string? Publisher { get; set; }
        public string? Category { get; set; }
        public string? ImageUrl { get; set; }
        public bool IsUnlocked { get; set; }
        public bool IsFullBook { get; set; }
        public string? ContentNote { get; set; }
        public long? OrderId { get; set; }
        public DateTime? PurchasedAt { get; set; }
        public string FullContent { get; set; } = null!;
        public List<BookChapterDto> Chapters { get; set; } = new List<BookChapterDto>();
        public string Message { get; set; } = null!;

        /// <summary>
        /// Đường link mở giao diện đọc toàn bộ sách sau khi mua
        /// </summary>
        public string ReaderUrl { get; set; } = null!;
    }

    public class CheckPurchaseResponseDto
    {
        public long ProductId { get; set; }
        public string Title { get; set; } = null!;
        public bool IsPurchased { get; set; }
        public long? OrderId { get; set; }
        public string? OrderStatus { get; set; }
        public DateTime? PurchasedAt { get; set; }
        public bool CanReadEbook { get; set; }
    }
}
