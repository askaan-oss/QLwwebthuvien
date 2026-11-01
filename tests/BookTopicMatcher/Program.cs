using qlthuvien_vip.Services.Implementations;
var cases = new[] {
    ("Tôi muốn sách về tài chính", "Cha giàu cha nghèo", "Kinh tế", "Quản lý tiền và đầu tư", true),
    ("sach ve tai chinh", "Cha giàu cha nghèo", "Kinh tế", "Quản lý tiền và đầu tư", true),
    ("Tôi muốn sách về tài chính", "Nhà giả kim", "Văn học", "Hành trình theo đuổi ước mơ", false),
    ("sách thiếu nhi", "Hoàng tử bé", "Thiếu nhi", "Một câu chuyện", true),
    ("sách thiên văn lượng tử", "Nhà giả kim", "Văn học", "Hành trình ước mơ", false),
    ("tìm Nhà giả kim", "Nhà giả kim", "Văn học", "Hành trình ước mơ", true)
};
foreach (var (q,title,category,description,expected) in cases)
    if ((BookTopicMatcher.Score(q,title,null,category,description)>0)!=expected) throw new Exception(q+" -> "+title);
Console.WriteLine("6 topic matching checks passed.");
