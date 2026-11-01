using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Logging;
using qlthuvien_vip.Models;
using qlthuvien_vip.Models.DTOs;
using qlthuvien_vip.Services.Interfaces;

namespace qlthuvien_vip.Services.Implementations
{
    public class BookContentService : IBookContentService
    {
        private readonly IWebHostEnvironment _env;
        private readonly ILogger<BookContentService> _logger;
        private readonly string _contentDirectory;

        public BookContentService(IWebHostEnvironment env, ILogger<BookContentService> logger)
        {
            _env = env;
            _logger = logger;
            _contentDirectory = Path.Combine(_env.ContentRootPath, "Data", "BookContents");
            if (!Directory.Exists(_contentDirectory))
            {
                Directory.CreateDirectory(_contentDirectory);
            }
        }

        public async Task<BookContentResult> GetBookContentAsync(Product product)
        {
            if (product == null)
            {
                return new BookContentResult
                {
                    Excerpt = "Nội dung đang được cập nhật...",
                    PreviewChapters = new List<BookChapterDto>(),
                    FullChapters = new List<BookChapterDto>()
                };
            }

            // 1. Kiểm tra xem có file nội dung riêng được lưu theo ProductId hoặc Isbn không
            var customContent = await LoadCustomContentFromFileAsync(product.ProductId, product.Isbn);
            if (customContent != null)
            {
                customContent.IsFullBook = true;
                customContent.ContentType = "Custom";
                customContent.ContentNote = "Nội dung sách điện tử trọn vẹn chính thức.";
                return customContent;
            }

            // 2. Tra cứu trong kho nội dung thực tế biên soạn riêng cho từng đầu sách nổi tiếng
            var curatedContent = GetCuratedBookContent(product);
            if (curatedContent != null)
            {
                curatedContent.IsFullBook = false;
                curatedContent.ContentType = "Curated";
                curatedContent.ContentNote = "Lưu ý: Đây là bản tóm tắt và trích đoạn biên soạn chuyên sâu của sách. Bản số hóa toàn văn trọn vẹn đang được nhà xuất bản cập nhật.";
                return curatedContent;
            }

            // 3. Tự động sinh nội dung chuyên sâu theo thể loại và mô tả thực tế của cuốn sách
            var generatedContent = GenerateCategorySpecificBookContent(product);
            generatedContent.IsFullBook = false;
            generatedContent.ContentType = "Generated";
            generatedContent.ContentNote = "Lưu ý: Đây là bản giới thiệu và trích đoạn tóm tắt biên soạn theo thể loại. Bản số hóa toàn văn trọn vẹn đang được cập nhật.";
            return generatedContent;
        }

        public async Task<bool> SaveCustomBookContentAsync(long productId, string excerpt, List<BookChapterDto> chapters)
        {
            try
            {
                var filePath = Path.Combine(_contentDirectory, $"{productId}.json");
                var data = new BookContentResult
                {
                    Excerpt = excerpt,
                    FullChapters = chapters,
                    PreviewChapters = chapters.Where(c => c.IsPreview || c.ChapterNumber == 1).ToList(),
                    TotalPages = chapters.Count * 8,
                    TotalPreviewPages = 4,
                    IsFullBook = true,
                    ContentType = "Custom",
                    ContentNote = "Nội dung sách điện tử trọn vẹn chính thức."
                };

                var json = JsonSerializer.Serialize(data, new JsonSerializerOptions { WriteIndented = true });
                await File.WriteAllTextAsync(filePath, json);
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Lỗi khi lưu nội dung sách cho ProductId = {ProductId}", productId);
                return false;
            }
        }

        private async Task<BookContentResult?> LoadCustomContentFromFileAsync(long productId, string? isbn)
        {
            try
            {
                string filePath = Path.Combine(_contentDirectory, $"{productId}.json");
                if (!File.Exists(filePath) && !string.IsNullOrWhiteSpace(isbn))
                {
                    filePath = Path.Combine(_contentDirectory, $"{isbn}.json");
                }

                if (File.Exists(filePath))
                {
                    var json = await File.ReadAllTextAsync(filePath);
                    return JsonSerializer.Deserialize<BookContentResult>(json, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Không thể đọc file nội dung sách cho ID {ProductId}", productId);
            }
            return null;
        }

        private BookContentResult? GetCuratedBookContent(Product p)
        {
            var titleLower = (p.Title ?? "").ToLowerInvariant();

            // 1. NHÀ GIẢ KIM (THE ALCHEMIST)
            if (titleLower.Contains("nhà giả kim") || titleLower.Contains("the alchemist"))
            {
                var excerpt = 
@"Cậu bé tên là Santiago. Trời vừa chập tối khi cậu cùng đàn cừu đến một nhà thờ cổ đổ nát. Mái nhà thờ đã sập từ lâu và một cây dâu tằm khổng lồ mọc ngay tại vị trí trước kia từng là phòng thánh.

Cậu quyết định qua đêm ở đó. Cậu lùa lũ cừu qua cánh cổng gỗ xiêu vẹo rồi chặn lại bằng mấy thanh gỗ để chúng khỏi đi lạc trong đêm. Vùng này không có chó sói, nhưng thỉnh thoảng vẫn có con cừu đi lạc và cậu phải mất cả ngày hôm sau mới tìm lại được.

Cậu trải chiếc áo choàng len xuống sàn đá, dùng cuốn sách vừa đọc xong làm gối kê đầu rồi nằm xuống, tự nhủ từ nay phải đọc những cuốn dày hơn để có gối êm hơn và đọc được lâu hơn.

Khi thức dậy, trời vẫn còn tối mịt. Nhìn lên trần nhà, qua những thanh rầm đã mục nát, cậu thấy những vì sao lấp lánh qua kẽ lá dâu tằm. Cậu lại vừa mơ thấy giấc mơ giống hệt tuần trước, và một lần nữa cậu lại thức giấc trước khi giấc mơ đi đến hồi kết. Trong giấc mơ, một đứa trẻ xuất hiện, dắt tay cậu đến chân Kim Tự Tháp Ai Cập và bảo: 'Nếu bạn đến đây, bạn sẽ tìm thấy một kho báu bí mật'...

'Khi bạn khao khát một điều gì đó, cả vũ trụ sẽ hợp lực giúp bạn đạt được điều đó.'";

                var chapters = new List<BookChapterDto>
                {
                    new BookChapterDto
                    {
                        ChapterNumber = 1,
                        Title = "Chương 1: Chàng chăn cừu và Giấc mơ Kim Tự Tháp",
                        Content = excerpt + @"

Santiago yêu quý đàn cừu của mình, nhưng trong thâm tâm cậu luôn khát khao được đi khắp thế gian. Cậu đã từ bỏ ý định trở thành linh mục mà cha mẹ mong muốn để trở thành người chăn cừu tại xứ Andalusia nắng gió. Cậu nhận ra rằng đàn cừu chỉ quan tâm đến nước uống và cỏ tươi, chúng chưa từng bận tâm đến những vùng đất mới hay những điều kỳ diệu của cuộc sống.

Ngày hôm sau, Santiago quyết định đến thị trấn Tarifa để nhờ một bà lão người Digan giải mã giấc mơ kỳ lạ. Bà lão nhìn vào lòng bàn tay cậu, khấn vái và nói: 'Giấc mơ này thuộc về ngôn ngữ của thế giới. Hãy đi đến Kim Tự Tháp Ai Cập, ở đó có kho báu đang chờ đợi cậu'. Cậu bé nghi ngờ và quyết định quay lại với đàn cừu, nghĩ rằng những giấc mơ chỉ là ảo ảnh hão huyền.",
                        IsPreview = true
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 2,
                        Title = "Chương 2: Cuộc gặp gỡ Vua xứ Salem & Hai viên đá Urim - Thummim",
                        Content = 
@"Ngồi tại quảng trường Tarifa ngắm nhìn dòng người qua lại, một ông già lạ mặt tiến đến bắt chuyện với Santiago. Ông mặc áo choàng trắng, ánh mắt toát lên sự thông thái kỳ lạ. Ông tự xưng là Melchizedek, Vua xứ Salem.

Ông nói với cậu về 'Vận mệnh cuộc đời' - điều mà mỗi con người luôn muốn thực hiện từ thuở thiếu thời. Nhưng theo thời gian, một lực lượng bí ẩn dần thuyết phục ta rằng việc hiện thực hóa ước mơ là bất khả thi.

'Bí quyết của hạnh phúc là biết chiêm ngưỡng mọi vẻ đẹp kỳ vĩ của thế gian mà không bao giờ làm đổ hai giọt dầu trên chiếc muỗng.'

Trước khi chia tay, vị vua trao cho cậu hai viên đá: viên trắng Thummim mang nghĩa 'Không' và viên đen Urim mang nghĩa 'Có', dặn cậu chỉ dùng khi không thể tự mình đọc các dấu hiệu của vũ trụ. Santiago bán đàn cừu, cầm số tiền vàng và bước lên con tàu hướng về bờ biển châu Phi, chính thức khởi đầu chuyến phiêu lưu vĩ đại.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 3,
                        Title = "Chương 3: Cửa hàng pha lê Tangier & Băng qua Sa mạc Sahara",
                        Content = 
@"Đặt chân đến Tangier, Santiago nhanh chóng bị một kẻ lừa đảo lấy sạch tiền bạc. Trắng tay tại một vùng đất xa lạ với ngôn ngữ Ả Rập cậu không hiểu, cậu đã không gục ngã trong tuyệt vọng.

Cậu đến làm việc cho một ông chủ tiệm pha lê trên đồi cao. Bằng sự sáng tạo và chăm chỉ, cậu lau sạch từng chiếc cốc, dựng quầy trà giải khát phục vụ người leo đồi, giúp tiệm pha lê phát đạt chưa từng thấy. Sau gần một năm tích lũy, cậu đủ tiền mua lại đàn cừu gấp đôi, nhưng cậu quyết định tiếp tục hành trình tới Kim Tự Tháp.

Cậu gia nhập đoàn lữ hành gồm hàng trăm người và lạc đà băng qua sa mạc Sahara mênh mông. Tại đây, cậu gặp một chàng trai người Anh say mê thuật giả kim, luôn vùi đầu vào những cuốn sách cổ dày cộp. Santiago học cách lắng nghe ngôn ngữ của sa mạc, của gió cát và sự thinh lặng vô tận.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 4,
                        Title = "Chương 4: Ốc đảo Al-Fayoum, Nàng Fatima & Nhà Giả Kim",
                        Content = 
@"Tại ốc đảo Al-Fayoum xanh tươi giữa lòng sa mạc, chiến tranh giữa các bộ tộc bùng nổ khiến đoàn lữ hành phải tạm dừng chân. Bên giếng nước ốc đảo, Santiago đã gặp Fatima - một cô gái sa mạc với đôi mắt đen láy. Ngay khoảnh khắc ánh mắt họ chạm nhau, cậu nhận ra Tình Yêu chính là ngôn ngữ thuần khiết nhất của Trái Đất.

Fatima không giữ chân cậu. Nàng bảo: 'Em là một người phụ nữ sa mạc. Sa mạc cướp đi những người đàn ông của chúng em và đôi khi không trả lại. Nhưng nếu em là một phần vận mệnh của anh, một ngày nào đó anh sẽ quay trở về'.

Sau khi cảnh báo tù trưởng về điềm báo chim ưng và cứu ốc đảo khỏi cuộc tập kích, Santiago được gặp Nhà Giả Kim thực sự. Cưỡi trên lưng ngựa trắng, Nhà Giả Kim dẫn đường cho cậu vượt qua những vùng đất hiểm trở nhất hướng về Kim Tự Tháp, dạy cậu cách lắng nghe tiếng nói của chính trái tim mình: 'Trái tim sợ phải đau khổ còn tồi tệ hơn chính sự đau khổ'.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 5,
                        Title = "Lời kết: Kho báu dưới cội cây dâu tằm",
                        Content = 
@"Đến chân Kim Tự Tháp Ai Cập hùng vĩ dưới ánh trăng, Santiago quỳ xuống khóc vì xúc động. Nơi giọt nước mắt cậu rơi xuống, một con bọ hung - biểu tượng của Chúa trời - bò qua. Cậu bắt đầu đào bới trong đêm.

Một toán cướp sa mạc đi ngang qua, thấy cậu đào đất liền bắt giữ, đánh đập và cướp sạch số vàng cuối cùng của cậu. Khi thấy cậu không còn gì ngoài những vết thương, tên thủ lĩnh bọn cướp cười khinh bỉ nói: 'Đừng có ngu ngốc tin vào những giấc mơ. Hai năm trước ta cũng từng mơ thấy một nhà thờ cổ đổ nát ở Tây Ban Nha, nơi có cây dâu tằm mọc trong phòng thánh, và dưới rễ cây chôn giấu một hòm vàng. Nhưng ta đâu có điên mà băng qua cả sa mạc chỉ vì một giấc mơ!'

Bọn cướp bỏ đi. Santiago đứng dậy, nhìn lên những Kim Tự Tháp đang mỉm cười trong gió đêm. Cậu bật cười trong niềm hạnh phúc vô biên: Cậu đã biết kho báu thực sự nằm ở đâu.

Santiago trở về Andalusia, đến ngôi nhà thờ cổ đổ nát năm xưa. Dưới gốc cây dâu tằm, lưỡi xẻng của cậu chạm vào một rương vàng bạc, châu báu cổ xưa của người Tây Ban Nha. Gió phương Đông thổi qua, mang theo mùi hương quen thuộc và nụ hôn của nàng Fatima. Cậu mỉm cười thì thầm: 'Fatima, anh về với em đây!'",
                        IsPreview = false
                    }
                };

                return new BookContentResult
                {
                    Excerpt = excerpt,
                    PreviewChapters = chapters.Where(c => c.IsPreview).ToList(),
                    FullChapters = chapters,
                    TotalPages = 240,
                    TotalPreviewPages = 25
                };
            }

            // 2. ĐẮC NHÂN TÂM (HOW TO WIN FRIENDS AND INFLUENCE PEOPLE)
            if (titleLower.Contains("đắc nhân tâm") || titleLower.Contains("how to win friends"))
            {
                var excerpt = 
@"Vào ngày 7 tháng 5 năm 1931, thành phố New York chứng kiến một cuộc vây bắt tội phạm kịch tính chưa từng có trong lịch sử. Sau nhiều tuần theo dấu, 150 cảnh sát và thám tử bao vây căn hộ tầng áp mái của tên sát thủ máu lạnh khét tiếng Francis 'Two-Gun' Crowley trên đại lộ West End.

Hơi cay được xịt vào phòng, tiếng súng máy nổ vang rền suốt hai giờ đồng hồ. Núp sau chiếc ghế bọc nệm dày, Crowley vẫn điên cuồng nổ súng chống trả. Trong lúc đạn bay xối xả, hắn đã viết một bức thư gửi cho mọi người: 'Dưới lớp áo này là một trái tim mệt mỏi, nhưng nhân từ – một trái tim không hề muốn làm hại bất cứ ai'.

Crowley là kẻ sẵn sàng bắn chết một viên cảnh sát chỉ vì người đó yêu cầu hắn xuất trình bằng lái xe. Thế nhưng, trong tâm thức sâu kín nhất, hắn vẫn tự coi mình là một người nhân từ vô tội!

Nếu một kẻ cướp giết người man rợ như Crowley còn không bao giờ tự trách mình, thì những người bình thường chúng ta tiếp xúc hàng ngày sẽ nghĩ gì khi bị bạn phê phán?

NGUYÊN TẮC VÀNG SỐ 1: Không chỉ trích, oán trách hay than phiền. Muốn lấy mật, đừng phá tổ ong!";

                var chapters = new List<BookChapterDto>
                {
                    new BookChapterDto
                    {
                        ChapterNumber = 1,
                        Title = "Chương 1: Muốn lấy mật, đừng phá tổ ong - Nghệ thuật không chỉ trích",
                        Content = excerpt + @"

Chỉ trích là một hành động nguy hiểm vì nó làm tổn thương lòng tự trọng quý giá của con người, gây tổn hại đến ý thức về tầm quan trọng của họ và khơi dậy sự phẫn nộ thù hằn. Sự chỉ trích giống như chim bồ câu đưa thư: chúng luôn quay trở về nơi xuất phát.

Tổng thống Abraham Lincoln từng là một người rất thích viết thư châm biếm và đả kích đối thủ chính trị. Nhưng sau trận thách đấu suýt chết bằng kiếm vì một bức thư chỉ trích thâm độc, Lincoln đã thay đổi hoàn toàn. Trong suốt cuộc Nội chiến đẫm máu, khi các tướng lĩnh dưới quyền liên tiếp mắc sai lầm ngớ ngẩn, câu nói nổi tiếng của ông luôn là: 'Đừng phán xét người khác nếu bạn không muốn bị phán xét'.

Thay vì lên án người khác, chúng ta hãy cố gắng thấu hiểu họ. Hãy tìm hiểu vì sao họ lại hành động như vậy. Điều đó đem lại thiện chí, lòng khoan dung và nhân ái hơn nhiều so với những lời trách cứ cay nghiệt.",
                        IsPreview = true
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 2,
                        Title = "Chương 2: Bí mật lớn nhất trong phép giao tiếp - Khen ngợi thành thật",
                        Content = 
@"Chỉ có một cách duy nhất trên cõi đời này để khiến một người làm bất cứ điều gì: đó là làm cho người đó MUỐN làm điều đó.

Nhà triết học John Dewey từng nhấn mạnh rằng: Động lực sâu xa nhất trong bản chất con người là 'khát khao được cảm thấy mình quan trọng'. William James nói: 'Nguyên lý sâu sắc nhất của bản tính loài người là sự khao khát được tán thưởng'.

Charles Schwab - người từng được triệu phú thép Andrew Carnegie trả mức lương kỷ lục một triệu đô-la mỗi năm - chia sẻ bí quyết thành công lớn nhất của mình:
'Khả năng lớn nhất của tôi là khơi dậy lòng nhiệt tình ở nhân viên. Cách tốt nhất để phát triển những đức tính tốt nhất ở một con người là sự công nhận và khuyến khích. Không có điều gì làm thui chột hoài bão của con người nhanh bằng sự chỉ trích từ cấp trên'.

Hãy phân biệt rõ ràng giữa 'LỜI KHEN CHÂN THÀNH' và 'SỰ NỊNH HÓT GIẢ DỐI'. Lời khen xuất phát từ trái tim, không vụ lợi và khách quan; còn lời nịnh hót xuất phát từ đầu lưỡi, ích kỷ và giả tạo. Hãy bắt đầu nhìn thấy những điểm tốt đẹp ở người khác và bày tỏ sự tán thưởng chân thành ngay hôm nay.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 3,
                        Title = "Chương 3: Khơi gợi ở người khác một ý muốn tha thiết",
                        Content = 
@"Mỗi mùa hè tôi đều đi câu cá ở vùng Maine. Cá nhân tôi rất thích ăn dâu tây dầm kem, nhưng kỳ lạ thay, lũ cá dưới hồ lại chỉ thích ăn giun. Vì vậy, khi đi câu, tôi không móc dâu tây dầm kem vào lưỡi câu. Tôi móc vào đó một con sâu hoặc một con cào cào và nhử: 'Này cá, mày có thích món này không?'

Tại sao trong đối nhân xử thế chúng ta lại không dùng lẽ thường giản dị ấy?

Bạn quan tâm đến những gì bạn muốn. Đó là bản năng muôn thuở. Nhưng không một ai khác quan tâm đến điều bạn muốn cả! Mọi người đều chỉ quan tâm đến điều HỌ muốn. Vì vậy, cách duy nhất trên thế gian này để thuyết phục người khác là hãy nói về điều HỌ muốn và chỉ cho họ cách để đạt được điều đó.

Henry Ford từng đưa ra lời khuyên sâu sắc bậc nhất về nghệ thuật thành công: 'Nếu có bất kỳ bí quyết thành công nào, thì nó nằm ở khả năng đặt mình vào vị trí của người khác và nhìn nhận vấn đề từ góc độ của họ cũng như từ góc độ của chính mình'.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 4,
                        Title = "Chương 4: Thành thật quan tâm và Lắng nghe người khác",
                        Content = 
@"Bạn có thể kết bạn được nhiều hơn trong hai tháng bằng cách thực sự quan tâm đến người khác, so với hai năm bạn cố gắng làm cho người khác quan tâm đến bạn.

Con chó là con vật duy nhất không cần phải làm việc kiếm sống: gà phải đẻ trứng, bò phải cho sữa, chim phải bắt sâu; còn chó kiếm sống chỉ bằng cách trao tặng tình yêu thương vô điều kiện và sự trung thành tận tụy cho chủ nhân.

Hãy nhớ rằng: Tên của một người là âm thanh êm đềm và quan trọng nhất đối với họ trong bất kỳ ngôn ngữ nào. Hãy nhớ tên người đối thoại, mỉm cười rạng rỡ và trở thành một người biết lắng nghe chăm chú.

Những người nói chuyện cuốn hút nhất thường không phải là những người nói nhiều nhất, mà là những người biết lắng nghe chăm chú nhất và khuyến khích người khác nói về chính bản thân họ.",
                        IsPreview = false
                    }
                };

                return new BookContentResult
                {
                    Excerpt = excerpt,
                    PreviewChapters = chapters.Where(c => c.IsPreview).ToList(),
                    FullChapters = chapters,
                    TotalPages = 320,
                    TotalPreviewPages = 35
                };
            }

            // 3. CLEAN CODE - MÃ SẠCH (ROBERT C. MARTIN)
            if (titleLower.Contains("clean code") || titleLower.Contains("mã sạch"))
            {
                var excerpt = 
@"Bạn đang đọc cuốn sách này vì hai lý do: thứ nhất, bạn là một lập trình viên; thứ hai, bạn muốn trở thành một lập trình viên giỏi hơn. Tốt lắm, bởi vì ngành công nghiệp phần mềm của chúng ta đang rất cần những lập trình viên giỏi hơn.

Bạn đã bao giờ bị cản trở bởi một đoạn mã tồi tệ (bad code) chưa? Nếu bạn là lập trình viên có thâm niên trên một năm, bạn chắc chắn đã từng bị những đống code rác rưởi kìm hãm bước chân hàng trăm lần. Chúng ta gọi đó là hiện tượng 'sa lầy' (wading). Bạn cố gắng lội qua đống mã nguồn lộn xộn, nơi từng hàm phình to hàng nghìn dòng, biến đặt tên tùy tiện 'd', 'temp', 'flag', và bất kỳ thay đổi nhỏ nào cũng làm sập ba hệ thống con khác.

Tại sao các lập trình viên lại viết code tồi? Thường là vì họ nói: 'Tôi phải làm cho kịp deadline, tôi sẽ quay lại dọn dẹp sau'.

Nhưng bạn biết định luật LeBlanc nói gì không?
'LATER EQUALS NEVER' – 'LẦN SAU ĐỒNG NGHĨA VỚI KHÔNG BAO GIỜ'.

Quy tắc Hướng đạo sinh (The Boy Scout Rule): Luôn để lại bãi trại sạch sẽ hơn lúc bạn mới đến. Mỗi lần commit code, hãy làm cho mã nguồn sạch hơn một chút so với trước khi bạn checkout.";

                var chapters = new List<BookChapterDto>
                {
                    new BookChapterDto
                    {
                        ChapterNumber = 1,
                        Title = "Chương 1: Mã sạch là gì? & Định luật LeBlanc",
                        Content = excerpt + @"

Bjarne Stroustrup - cha đẻ ngôn ngữ C++ - định nghĩa: 'Tôi thích code của mình thanh lịch và hiệu quả. Logic phải đơn giản, thẳng thắn để bọ (bug) khó lòng ẩn nấp. Mã sạch chỉ làm một việc duy nhất và làm nó thật tốt.'

Grady Booch - tác giả cuốn Phân tích và Thiết kế Hướng đối tượng - nhận xét: 'Mã sạch đơn giản và trực diện. Nó đọc giống như một áng văn xuôi trau chuốt.'

Michael Feathers - tác giả sách Working Effectively with Legacy Code: 'Mã sạch luôn trông như thể nó được viết bởi một người rất quan tâm đến nó. Không có điểm nào hiển nhiên có thể cải thiện thêm.'

Viết mã sạch cũng giống như vẽ một bức tranh nghệ thuật. Biết phân biệt tranh đẹp và tranh xấu không có nghĩa là bạn biết vẽ tranh. Bạn cần rèn luyện 'cảm quan về mã' (code-sense) qua từng ngày để nhận diện mùi hôi của mã (code smells) và biến nó thành những dòng lệnh tinh tế.",
                        IsPreview = true
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 2,
                        Title = "Chương 2: Ý nghĩa của Tên gọi (Meaningful Names)",
                        Content = 
@"Tên gọi xuất hiện ở khắp mọi nơi trong phần mềm: chúng ta đặt tên cho biến, hàm, tham số, lớp, gói, file mã nguồn... Vì làm việc với tên gọi liên tục, hãy biến việc đặt tên thành một nghệ thuật:

1. TÊN PHẢI THỂ HIỆN RÕ Ý ĐỊNH (Intent-Revealing):
Nếu một cái tên cần thêm một dòng chú thích để giải thích nó làm gì, thì cái tên đó đã thất bại.
Thay vì: int d; // elapsed time in days
Hãy viết: int elapsedTimeInDays; int daysSinceCreation; int fileAgeInDays;

2. TRÁNH GÂY HIỂU LẦM (Avoid Disinformation):
Không đặt tên một biến là accountList trừ khi nó thực sự là một List (hãy dùng accountGroup hoặc accounts). Tránh dùng các ký tự dễ nhầm lẫn như chữ 'l' thường và số '1', hoặc chữ 'O' hoa và số '0'.

3. TẠO SỰ KHÁC BIỆT CÓ Ý NGHĨA (Make Meaningful Distinctions):
Đừng dùng các từ vô nghĩa như Info, Data, The, Variable vào tên gọi. Ví dụ giữa ProductInfo và ProductData, bạn có phân biệt được chúng khác nhau ở chỗ nào không?

4. TÊN CÓ THỂ PHÁT ÂM VÀ TÌM KIẾM ĐƯỢC:
Hãy đặt tên để bạn có thể trao đổi tự nhiên trong cuộc họp với đồng nghiệp thay vì đánh vần từng ký tự viết tắt kỳ dị.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 3,
                        Title = "Chương 3: Viết Hàm (Functions) - Ngắn gọn và Đơn nhiệm",
                        Content = 
@"Quy tắc số 1 của hàm: CHÚNG PHẢI NGẮN.
Quy tắc số 2 của hàm: CHÚNG PHẢI NGẮN HƠN NỮA!

Hàm của bạn hiếm khi nên dài quá 20 dòng. Một hàm lý tưởng chỉ nên dài từ 4 đến 10 dòng mã.

NGUYÊN TẮC ĐƠN NHIỆM (Single Responsibility Principle):
Một hàm chỉ nên làm MỘT VIỆC DUY NHẤT. Nó phải làm việc đó thật tốt, và CHỈ LÀM VIỆC ĐÓ MÀ THÔI.

Làm sao để biết một hàm đang làm nhiều hơn một việc? Nếu bạn có thể trích xuất (extract) một hàm khác từ nó với một cái tên không chỉ đơn thuần là việc thuật lại quá trình thực thi, thì hàm ban đầu đang làm nhiều hơn một việc.

SỐ LƯỢNG THAM SỐ CỦA HÀM:
Số lượng tham số lý tưởng của một hàm là 0 (niladic). Kế đến là 1 tham số (monadic), sau đó là 2 tham số (dyadic). Nên tránh tối đa các hàm có 3 tham số trở lên (triadic hoặc polyadic). Nếu hàm cần quá nhiều tham số, hãy đóng gói chúng thành một Object riêng biệt.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 4,
                        Title = "Chương 4: Xử lý Lỗi & Kiểm thử Đơn vị (Unit Tests)",
                        Content = 
@"Xử lý lỗi là điều cần thiết, nhưng nếu xử lý lỗi làm lu mờ logic chính của mã nguồn thì đó là một thiết kế tồi.

1. Hãy sử dụng Ngoại lệ (Exceptions) thay vì trả về Mã lỗi (Error codes). Khi trả về mã lỗi, bạn buộc người gọi hàm phải kiểm tra lỗi ngay lập tức, làm phân mảnh luồng xử lý. Ngoại lệ tách biệt luồng nghiệp vụ chính khỏi luồng xử lý tình huống bất thường.

2. ĐỪNG TRẢ VỀ NULL!
Khi bạn trả về null từ một hàm, bạn đang tạo ra việc làm cho chính mình và gieo mầm mống cho lỗi huyền thoại NullPointerException (hoặc NullReferenceException). Thay vì trả về null, hãy xem xét trả về một Empty Collection, một Optional/Nullable hợp lệ, hoặc sử dụng Special Case Object.

3. BA ĐỊNH LUẬT CỦA TDD (Test-Driven Development):
- Bạn không được viết mã sản phẩm (production code) cho đến khi đã viết một bài test thất bại.
- Bạn không được viết nhiều hơn một bài test đơn vị vừa đủ để thất bại.
- Bạn không được viết nhiều hơn mã sản phẩm vừa đủ để vượt qua bài test thất bại đó.
Code sạch đi đôi với bài test sạch. Không có bài test tự động đáng tin cậy, bạn sẽ không bao giờ dám tự tin tái cấu trúc (refactor) hệ thống.",
                        IsPreview = false
                    }
                };

                return new BookContentResult
                {
                    Excerpt = excerpt,
                    PreviewChapters = chapters.Where(c => c.IsPreview).ToList(),
                    FullChapters = chapters,
                    TotalPages = 464,
                    TotalPreviewPages = 45
                };
            }

            // 4. CHA GIÀU CHA NGHÈO (RICH DAD POOR DAD)
            if (titleLower.Contains("cha giàu cha nghèo") || titleLower.Contains("rich dad poor dad"))
            {
                var excerpt = 
@"Tôi có hai người cha: một người giàu và một người nghèo. Một người cha có học thức cao, bằng tiến sĩ, hoàn thành khóa học bốn năm đại học chỉ trong hai năm. Người cha kia chưa bao giờ học hết lớp tám.

Cả hai người đều thành công trong sự nghiệp và làm việc chăm chỉ suốt đời. Cả hai đều có thu nhập đáng kể. Nhưng một người luôn phải vật lộn với vấn đề tài chính cho đến cuối đời; còn người kia trở thành một trong những người giàu nhất bang Hawaii. Một người để lại hàng chục triệu đô-la cho gia đình và các tổ chức từ thiện; người kia chỉ để lại những hóa đơn nợ nần chưa thanh toán.

Cả hai người đều đưa ra những lời khuyên sâu sắc cho tôi, nhưng lời khuyên của họ hoàn toàn trái ngược nhau:
- Người cha có học thức khuyên: 'Ráng học cho giỏi, lấy điểm cao để sau này tìm được một công việc an toàn, ổn định với mức lương cao'.
- Người cha giàu dạy: 'Ráng học cho giỏi để biết cách xây dựng một công ty và thuê những người giỏi nhất làm việc cho con'.

BÀI HỌC SỐ 1: Người nghèo và tầng lớp trung lưu làm việc vì tiền bạc. Người giàu buộc tiền bạc phải làm việc cho chính mình!";

                var chapters = new List<BookChapterDto>
                {
                    new BookChapterDto
                    {
                        ChapterNumber = 1,
                        Title = "Chương 1: Bài học số 1 - Người giàu không làm việc vì tiền",
                        Content = excerpt + @"

Khi tôi 9 tuổi, tôi và người bạn thân Mike quyết định tìm cách kiếm tiền. Người cha giàu của Mike đã dạy chúng tôi bài học đầu tiên không phải qua những bài giảng lý thuyết khô khan, mà bằng trải nghiệm thực tế. Ông trả cho chúng tôi 10 xu một giờ để dọn dẹp cửa hàng tạp hóa của ông vào sáng thứ Bảy – một mức lương rẻ mạt ngay cả vào năm 1956.

Sau vài tuần tức giận vì bị bóc lột, tôi đến gặp ông để đòi tăng lương hoặc nghỉ việc. Người cha giàu mỉm cười nói: 'Chào mừng con đến với trường học thực tế. Hầu hết mọi người để nỗi sợ hãi và lòng tham chi phối cuộc đời họ. Khi không có tiền, nỗi sợ không có tiền thôi thúc họ thức dậy đi làm. Khi nhận được tiền lương, lòng tham và ham muốn thôi thúc họ tiêu xài vào những thứ xa xỉ, và rồi cái bẫy Chuột chạy vòng quanh (Rat Race) khép lại'.

Người giàu thoát khỏi cái bẫy đó bằng cách làm chủ cảm xúc, học cách nhìn thấy những cơ hội mà người khác bỏ qua và tạo ra các tài sản sinh dòng tiền thụ động.",
                        IsPreview = true
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 2,
                        Title = "Chương 2: Bài học số 2 - Tại sao phải dạy con về Tài chính?",
                        Content = 
@"Quy tắc số một và duy nhất quan trọng nhất để làm giàu là: BẠN PHẢI BIẾT SỰ KHÁC NHAU GIỮA TÀI SẢN VÀ TIÊU SẢN, VÀ LUÔN MUA TÀI SẢN.

Định nghĩa tài chính đơn giản của Người cha giàu:
- TÀI SẢN (Asset): Là thứ bỏ tiền vào túi của bạn (ví dụ: bất động sản cho thuê, cổ phiếu chia cổ tức, bản quyền sở hữu trí tuệ, doanh nghiệp tự vận hành).
- TIÊU SẢN (Liability): Là thứ rút tiền ra khỏi túi của bạn (ví dụ: xe cộ hao mòn, các món nợ thẻ tín dụng, những tiện nghi xa xỉ đắt đỏ).

Ngôi nhà bạn đang ở có phải là tài sản không? Người cha nghèo nói: 'Nhà là tài sản lớn nhất của tôi'. Người cha giàu nói: 'Ngôi nhà là một tiêu sản, vì mỗi tháng nó rút tiền ra khỏi túi bạn qua thuế nhà đất, bảo hiểm, tiền lãi vay ngân hàng và chi phí bảo trì'. Nếu bạn muốn mua một ngôi nhà lớn hơn, trước tiên hãy mua những tài sản tạo ra dòng tiền đủ để thanh toán cho ngôi nhà đó!",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 3,
                        Title = "Chương 3: Hãy nghĩ đến công việc kinh doanh của chính mình",
                        Content = 
@"Ray Kroc - người sáng lập đế chế nhượng quyền McDonald's - từng hỏi một nhóm sinh viên MBA đại học Texas: 'Các bạn có biết tôi kinh doanh ngành nghề gì không?'
Tất cả sinh viên đều cười: 'Ai mà không biết ông bán bánh hamburger!'

Ray Kroc lắc đầu: 'Không, kinh doanh cốt lõi của tôi không phải là bánh hamburger. Công việc kinh doanh thực sự của tôi là BẤT ĐỘNG SẢN'. Ông hiểu rằng mỗi cửa hàng McDonald's nhượng quyền đều tọa lạc tại những góc phố đắc địa nhất, sầm uất nhất trên toàn cầu.

Người giàu tập trung xây dựng cột tài sản của chính họ, trong khi người bình thường dành cả cuộc đời để làm giàu cho người chủ doanh nghiệp, làm giàu cho chính phủ qua các khoản thuế và làm giàu cho ngân hàng qua các khoản vay thế chấp.",
                        IsPreview = false
                    },
                    new BookChapterDto
                    {
                        ChapterNumber = 4,
                        Title = "Chương 4: Vượt qua các Chướng ngại vật & Bắt đầu hành động",
                        Content = 
@"Sự khác biệt căn bản giữa người giàu và người nghèo không nằm ở học vấn, mà nằm ở cách họ xử lý NỖI SỢ HÃI.

Năm chướng ngại vật lớn nhất trên con đường tự do tài chính:
1. Nỗi sợ mất tiền: Người nghèo sợ thất bại đến mức không dám thử; người giàu xem thất bại là bài học kinh nghiệm quý giá.
2. Sự hoài nghi: Tiếng nói nội tâm tiêu cực và những lời bàn lùi của đám đông.
3. Sự lười biếng: Cách chữa trị sự lười biếng hiệu quả nhất là một chút lòng tham lành mạnh – khao khát một cuộc sống tốt đẹp hơn cho bản thân và gia đình.
4. Thói quen xấu: Hãy trả cho bản thân mình đầu tiên trước khi trả cho các chủ nợ và hóa đơn.
5. Sự kiêu ngạo: Những gì bạn biết giúp bạn kiếm tiền, những gì bạn không biết làm bạn mất tiền. Hãy luôn giữ tinh thần khiêm nhường học hỏi.",
                        IsPreview = false
                    }
                };

                return new BookContentResult
                {
                    Excerpt = excerpt,
                    PreviewChapters = chapters.Where(c => c.IsPreview).ToList(),
                    FullChapters = chapters,
                    TotalPages = 280,
                    TotalPreviewPages = 30
                };
            }

            return null;
        }

        private BookContentResult GenerateCategorySpecificBookContent(Product p)
        {
            var category = p.Category ?? "Sách chọn lọc";
            var desc = !string.IsNullOrWhiteSpace(p.Description) 
                ? p.Description 
                : $"Tác phẩm nổi tiếng '{p.Title}' do tác giả {p.Author ?? "nhiều tác giả"} biên soạn.";

            string excerpt = $"[Trích đoạn tác phẩm '{p.Title}']\n\n" +
                             $"{desc}\n\n" +
                             $"\"Mỗi trang sách được lật mở là một cánh cửa bước vào thế giới tri thức mới. Dưới ngòi bút tinh tế của {p.Author ?? "tác giả"}, tác phẩm mang đến cho bạn đọc những góc nhìn đa chiều, sâu sắc và đầy sức thuyết phục về chủ đề {category}.\"\n\n" +
                             $"[Đọc thử miễn phí]: Để thấu hiểu trọn vẹn bản chất của vấn đề, độc giả cần nắm vững các nguyên lý cốt lõi được xây dựng từ những bài học thực tế...";

            var chapters = new List<BookChapterDto>
            {
                new BookChapterDto
                {
                    ChapterNumber = 1,
                    Title = $"Chương 1: Khởi nguồn & Bối cảnh tác phẩm ({p.Title})",
                    Content = excerpt + $"\n\nTrong chương đầu tiên này, tác phẩm tập trung làm rõ bối cảnh ra đời và những câu hỏi then chốt mà độc giả đang tìm kiếm lời giải đáp. Với văn phong mạch lạc và lập luận chặt chẽ, cuốn sách mở ra lộ trình tiếp cận toàn diện cho bất kỳ ai muốn nắm vững lĩnh vực {category}.",
                    IsPreview = true
                },
                new BookChapterDto
                {
                    ChapterNumber = 2,
                    Title = "Chương 2: Phân tích Chuyên sâu & Hệ thống Lý thuyết",
                    Content = $"Trích đoạn & Phân tích Chương 2 của '{p.Title}':\n\nĐi sâu vào bản chất của {category}, chương này trình bày các phân tích thực chứng, so sánh các mô hình tiếp cận hiện đại và chỉ ra những sai lầm phổ biến mà đa số người mới bắt đầu thường mắc phải. Tác giả {p.Author ?? ""} đưa ra các dẫn chứng thuyết phục giúp bạn đọc củng cố tư duy nền tảng vững chắc.",
                    IsPreview = false
                },
                new BookChapterDto
                {
                    ChapterNumber = 3,
                    Title = "Chương 3: Chiến lược Ứng dụng & Giải pháp Thực tiễn",
                    Content = $"Trích đoạn & Phân tích Chương 3 của '{p.Title}':\n\nLý thuyết chỉ thực sự có giá trị khi được chuyển hóa thành hành động cụ thể. Trong chương này, tác phẩm cung cấp bộ công cụ, quy trình từng bước và các phương pháp ứng dụng thực tiễn để giải quyết những thách thức thực tế trong đời sống và công việc.",
                    IsPreview = false
                },
                new BookChapterDto
                {
                    ChapterNumber = 4,
                    Title = "Chương 4: Tổng kết & Định hướng Tương lai",
                    Content = $"Trích lược Chương 4 của '{p.Title}':\n\nĐúc kết toàn bộ thông điệp cốt lõi của tác phẩm, chương kết thúc đưa ra những bài học trường tồn cùng thời gian và những gợi mở cho chặng đường phát triển tiếp theo. Cảm ơn quý độc giả đã đồng hành cùng tác phẩm '{p.Title}'.",
                    IsPreview = false
                }
            };

            return new BookContentResult
            {
                Excerpt = excerpt,
                PreviewChapters = chapters.Where(c => c.IsPreview).ToList(),
                FullChapters = chapters,
                TotalPages = 150,
                TotalPreviewPages = 15
            };
        }
    }
}
