from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
base=Path(r'D:\QL dự án nhóm');out=base/'output';work=base/'work'
s=(work/'build_doc.py').read_text(encoding='utf-8-sig')
exec(s[s.index('doc=Document();'):s.index("p('BÁO CÁO THỰC HÀNH'")])
doc=Document(out/'QLDA_Nhom11_Lab.docx')
# Complete proposed charter controls without changing source facts.
for para in doc.paragraphs:
 if para.text.startswith('Lớp:'):
  para.text='Lớp: nhóm bổ sung'
 if para.text.startswith('Thành viên:'):
  para.text='Thành viên: TV1, TV2, TV3, TV4, TV5, TV6\nMã phân công tạm thời; thay bằng họ tên trước khi nộp.'
 for old,new in {
  'Ngân sách, ngày khởi động, người duyệt và quyết định phạm vi.':'Xác nhận dự toán đề xuất, ngày khởi động, người duyệt và quyết định phạm vi.',
  'Ngày, ngân sách, tên người phụ trách và xác nhận quyết định.':'Xác nhận ngày, dự toán đề xuất, tên người phụ trách và các quyết định.',
  'Chưa được xác định trong dữ liệu dự án; cần dự toán và phê duyệt riêng':'Nguồn chưa có ngân sách. Dự toán đề xuất bổ sung: 29.325.000 đồng, chưa được phê duyệt.',
 }.items():
  if old in para.text:para.text=para.text.replace(old,new)
for t in doc.tables:
 for row in t.rows:
  for cell in row.cells:
   for para in cell.paragraphs:
    if 'Chưa được xác định trong dữ liệu dự án; cần dự toán và phê duyệt riêng' in para.text:
     para.text='Nguồn chưa có ngân sách. Dự toán đề xuất: 29.325.000 đồng, chưa được phê duyệt.'
body=doc._element.body
before=set(body)
page('2 Mốc và dự toán đề xuất')
p('Các mốc dưới đây lấy từ lịch CPM cơ sở 37,02 ngày, dùng để nhóm chốt kế hoạch. Tuần quy đổi theo 5 ngày làm việc, chưa gắn ngày tháng. Phần mô tả sản phẩm tuần 1–4 của tài liệu nguồn vẫn được giữ riêng; chưa có dữ liệu để coi các sản phẩm đó là đã đạt mốc thực tế.')
table(['Mốc bàn giao','Kết thúc ngày','Tuần dự kiến'],[
['Yêu cầu','3,00','1'],['UI/UX, database và đặc tả API','9,17','2'],['Sách và tìm kiếm','13,34','3'],['Frontend khách hàng','19,34','4'],['Luồng đơn hàng và thanh toán','23,51','5'],['Bản tích hợp','26,51','6'],['Kiểm thử và sửa lỗi','33,85','7'],['Triển khai và nghiệm thu','37,02','8']],[10.3,3.6,3.5])
h('Dự toán để nhóm xem xét')
p('Quy đổi giờ công nhằm minh họa quản lý chi phí của bài thực hành, không phải khoản lương đã chi hoặc báo giá thị trường. Giả định 496 giờ theo WBS, đơn giá quy đổi 50.000 đồng/giờ. Toàn bộ quản lý, phát triển, kiểm thử và bàn giao đã nằm trong giờ WBS nên không cộng thêm lần nữa.')
table(['Khoản mục','Cách tính và giả định','Đồng'],[
['Công sức dự án','496 giờ × 50.000 đồng/giờ','24.800.000'],['Môi trường triển khai','Khoản giả định cho 8 tuần, cần báo giá','1.200.000'],['Công cụ và dịch vụ thử nghiệm','Khoản giả định, chưa xác nhận nhà cung cấp','500.000'],['Dự phòng rủi ro minh họa','Theo tổng EMV nguồn, cần rà lại mức đủ dùng','2.825.000'],['Tổng dự toán đề xuất','Chưa được phê duyệt','29.325.000']],[5,8.2,4.2])
p('EMV là tổn thất kỳ vọng, không phải bảo đảm dự phòng đủ cho mọi rủi ro. Nhóm cần thống nhất dự phòng bổ sung nếu nhiều rủi ro xảy ra cùng lúc. Mọi chi phí phát sinh, thuế hoặc dịch vụ chạy thật chưa có báo giá phải được xét trước cam kết.')
h('Kiểm soát thay đổi')
p('TV1 tiếp nhận yêu cầu thay đổi, ghi lý do và ảnh hưởng đến WBS, lịch, chi phí và tiêu chí nghiệm thu. Nhóm cùng giảng viên hoặc đại diện nghiệp vụ được chỉ định chấp thuận trước khi đưa vào Sprint. Dùng cùng phiên bản yêu cầu và API giữa frontend, backend và tester.')
new=[node for node in body if node not in before and node.tag!=qn('w:sectPr')]
target=next(p._p for p in doc.paragraphs if p.text=='3 Sơ đồ WBS')
# Insert before the existing page break that starts the WBS section.
prev=target.getprevious()
anchor=prev if prev is not None and prev.xpath('.//w:br') else target
for node in new:anchor.addprevious(node)
page('10 Nhật ký cuộc trao đổi thực tế')
p('Ngày lập: 28/09/2026. Nhật ký này ghi các yêu cầu có trong cuộc trao đổi với trợ lý, không được dùng thay cho ảnh hoặc lịch sử Claude Project chưa được cung cấp.')
table(['Yêu cầu người dùng','Kết quả xử lý','Kiểm tra hoặc giới hạn'],[
['làm ra work cho tôi','Soạn báo cáo theo khung lab đã gửi.','Bản đầu dùng tình huống EduReg của đề.'],
['QLDA_Nhom11_EduReg','Điền Nhóm 11 và tên file theo quy ước.','Chưa có tên cá nhân hoặc lớp.'],
['lấy cái này làm dữ liệu này','Chuyển báo cáo sang website bán hàng và thanh toán cho thư viện theo báo cáo tuần 1–4.','Giữ nguyên tính chất minh họa của Actual và EMV.'],
['sao tôi thấy yêu cầu nộp nhiều mà','Rà bộ nộp, bổ sung Excel và bảng đối chiếu các yêu cầu.','Phát hiện file Excel còn thiếu trong lần giao trước.'],
['làm cho xong nốt đi','Hoàn thiện bộ tài liệu, dự toán đề xuất, mốc, nhật ký và kiểm tra công thức.','Minh chứng cá nhân và ảnh Project cần lấy từ nhóm.']
],[4.8,6.3,6.3])
h('Kiểm tra đã thực hiện')
p('Đối chiếu các hoạt động A–Q với nguồn; tính lại CPM cơ sở và tối ưu; xác nhận tổng EMV; kiểm tra WBS đủ ba cấp và giờ công từng gói trong khoảng 8–80; kiểm tra công thức thay đổi theo đầu vào. Sau tối ưu, phát hiện thêm đường găng qua F do F và G cùng dài 3 ngày, và cập nhật giải thích trong báo cáo.')
h('Phần nhóm tự kiểm tra')
p('Người kiểm tra: ................................  Ngày: ................................\nKết quả kiểm tra trên Excel: ................................................................\nCác ước lượng hoặc phạm vi đã điều chỉnh: ............................................\nHai rủi ro nhóm tự bổ sung: ................................................................\nKết luận của nhóm sau phản biện: ........................................................')
for para in doc.paragraphs:
 if para.text.endswith('9  PERT ba điểm và đối chiếu bộ nộp'):
  para.add_run('\n10  Nhật ký cuộc trao đổi thực tế')
# Prevent table rows splitting across pages and keep headings readable.
for t in doc.tables:
 for row in t.rows:
  pr=row._tr.get_or_add_trPr()
  el=OxmlElement('w:cantSplit');pr.append(el)
  for c in row.cells:
   for para in c.paragraphs:
    para.paragraph_format.keep_with_next=False
doc.core_properties.title='Báo cáo thực hành Nhóm 11 dự án website bán hàng và thanh toán cho thư viện'
doc.core_properties.subject='Charter WBS PERT CPM Gantt quản lý rủi ro và phản biện'
doc.save(out/'QLDA_Nhom11_Lab.docx')
print('Report finalized')
