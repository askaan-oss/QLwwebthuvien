from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, json
base=Path(r'D:\QL dự án nhóm'); out=base/'output'; work=base/'work'
font=r'C:\Windows\Fonts\arial.ttf'
acts=[('A','Yêu cầu và Charter',[],5,'BA'),('B','Thiết kế UX và kiến trúc',['A'],8,'Designer + backend'),('C','Nền tảng và tài khoản',['B'],6,'Backend'),('D','Danh mục khóa học',['B'],6,'Web 1'),('E','Đăng ký và giữ chỗ',['C','D'],10,'Web 1'),('F','Thanh toán và đối soát',['E'],10,'Backend'),('G','Quản lý lớp và lịch',['C'],10,'Web 2'),('H','Thông báo email và Zalo',['F'],8,'Backend'),('I','Báo cáo và xuất Excel',['G','F'],8,'Web 2'),('J','Chuyển dữ liệu cũ',['G'],8,'BA + Web 2'),('K','Tích hợp và bảo mật',['H','I','J'],8,'Backend'),('L','Kiểm thử hệ thống và tải',['K'],10,'Tester'),('M','UAT và sửa lỗi',['L'],6,'BA + nhóm dev'),('N','Đào tạo và chuyển đổi',['M'],5,'BA + PM'),('O','Vận hành và bàn giao',['N'],3,'PM + backend')]
# Resource link J -> I prevents Web 2 double booking.
acts[8]=('I',acts[8][1],['G','F','J'],8,acts[8][4])
ordered=acts[:8]+[acts[9],acts[8]]+acts[10:]
data={}
for a,n,pr,t,owner in ordered:
 es=max([data[p]['ef'] for p in pr] or [0]); data[a]=dict(es=es,ef=es+t,t=t,pr=pr)
T=max(x['ef'] for x in data.values())
for a,n,pr,t,owner in reversed(ordered):
 succ=[k for k,v in data.items() if a in v['pr']]; lf=min([data[k]['ls'] for k in succ] or [T]); data[a].update(lf=lf,ls=lf-t,slack=lf-t-data[a]['es'])
critical=[a for a in data if data[a]['slack']==0]
# Graphics
im=Image.new('RGB',(1500,1000),'white'); dr=ImageDraw.Draw(im); f=ImageFont.truetype(font,22); fs=ImageFont.truetype(font,19)
dr.text((20,8),'EDUREG   WBS theo sản phẩm bàn giao',font=ImageFont.truetype(font,30),fill='black')
leaves=[('Yêu cầu đã duyệt','Charter và tiêu chí nghiệm thu'),('Bộ giao diện responsive','Kiến trúc và mô hình dữ liệu'),('Tài khoản và phân quyền','Môi trường và nhật ký hệ thống'),('Danh mục và học phí','Lịch khai giảng và số chỗ'),('Luồng đăng ký và chọn ca','Cơ chế giữ chỗ đồng thời'),('Cổng thanh toán và QR','Webhook và đối soát'),('Lớp phòng giảng viên','Quy tắc phát hiện trùng lịch'),('Xác nhận email Zalo','Nhắc lịch và xử lý gửi lỗi'),('Báo cáo doanh thu học viên','Tệp Excel theo bộ lọc'),('Dữ liệu chuẩn hóa','Dữ liệu nhập và biên bản đối chiếu'),('Bản tích hợp hoàn chỉnh','Bản gia cố bảo mật'),('Kết quả kiểm thử chức năng','Kết quả tải và phục hồi'),('Biên bản UAT','Bản sửa lỗi được kiểm tra'),('Tài liệu và buổi đào tạo','Kế hoạch chuyển đổi và rollback'),('Bản chạy thật và giám sát','Biên bản bàn giao')]
for i,((a,n,pr,t,o),ll) in enumerate(zip(acts,leaves)):
 col=i//5; row=i%5; x=20+col*495; y=75+row*175
 dr.rectangle((x,y,x+470,y+150),outline='#b6bdc4',width=2)
 dr.text((x+12,y+9),f'1.{i+1}  {n}',font=f,fill='black')
 for j,l in enumerate(ll): dr.text((x+20,y+51+j*43),f'└ {i+1}.{j+1}  {l}',font=fs,fill='black')
dr.text((20,953),'Gốc 1.0 EduReg  |  Nhánh 1.16 Hồ sơ quản trị gồm 8 gói theo chu kỳ hai tuần',font=fs,fill='black'); im.save(work/'wbs.png')
im=Image.new('RGB',(1500,860),'white'); dr=ImageDraw.Draw(im); f=ImageFont.truetype(font,22)
for tick in range(0,81,5):
 x=480+tick*12; dr.line((x,55,x,820),fill='#dddddd'); dr.text((x-10,20),str(tick),font=f,fill='black')
for i,(a,n,pr,t,o) in enumerate(acts):
 y=67+i*49; dr.text((10,y),a+'  '+n,font=f,fill='black'); v=data[a]; dr.rectangle((480+v['es']*12,y,480+v['ef']*12,y+28),fill='#344f68' if v['slack']==0 else '#9daebc')
im.save(work/'gantt.png')
doc=Document(); sec=doc.sections[0]; sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.top_margin=Cm(1.7);sec.bottom_margin=Cm(1.7);sec.left_margin=Cm(1.8);sec.right_margin=Cm(1.8)
for sn in ['Normal','Title','Heading 1','Heading 2']:
 s=doc.styles[sn];s.font.name='Arial';s.font.color.rgb=RGBColor(0,0,0);s.font.size=Pt(10.5 if sn=='Normal' else 23 if sn=='Title' else 16 if sn=='Heading 1' else 12)
 s.paragraph_format.space_after=Pt(6)
doc.styles['Normal'].paragraph_format.line_spacing=1.12
foot=sec.footer.paragraphs[0];foot.alignment=2
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');foot._p.append(fld)
def p(s,style=None):return doc.add_paragraph(s,style)
def h(s):doc.add_heading(s,2)
def page(s):doc.add_page_break();doc.add_heading(s,1)
def table(head,rows,widths=None):
 t=doc.add_table(rows=1, cols=len(head));t.autofit=False
 if widths:
  for c,w in zip(t.columns,widths):c.width=Cm(w)
 for c,tx in zip(t.rows[0].cells,head):c.text=str(tx)
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for rr in rows:
  for c,tx in zip(t.add_row().cells,rr):c.text=str(tx)
 for ri,r in enumerate(t.rows):
  for ci,c in enumerate(r.cells):
   if widths:c.width=Cm(widths[ci])
   cp=c._tc.get_or_add_tcPr(); borders=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
   cp.append(borders)
   if ri==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'DFE8EF');cp.append(sh)
   for para in c.paragraphs:
    para.paragraph_format.space_after=Pt(4);para.paragraph_format.space_before=Pt(4)
    for run in para.runs:run.font.size=Pt(9);run.bold=ri==0
 return t
p('BÁO CÁO THỰC HÀNH', 'Title');p('Lập kế hoạch dự án EduReg','Title');p('Học phần Quản lý dự án công nghệ thông tin')
p('Nhóm: ................................    Lớp: ................................')
p('Thành viên: ...............................................................................')
p('..................................................................................................')
h('Tóm tắt kế hoạch')
p(f'EduReg số hóa đăng ký khóa học, thanh toán, xếp lớp và báo cáo tại Trung tâm Tin học Việt. Kế hoạch ưu tiên sáu yêu cầu bắt buộc FR01–FR05 và FR07, chuyển khoảng 3.000 hồ sơ cũ, triển khai web responsive cho ba cơ sở. Thời lượng cơ sở là {T} ngày làm việc, với trần ngân sách 350 triệu đồng.')
p('Đề xuất thực hiện theo các vòng phát triển ngắn, trình diễn hàng tháng và nghiệm thu theo từng sản phẩm. Phạm vi, tiêu chí hiệu năng, hợp đồng cổng thanh toán và lịch nghỉ cần được chốt ngay khi khởi động.')
h('Quy ước và giả định lập kế hoạch')
p('Thời gian tính theo ngày làm việc, 8 giờ/ngày, 5 ngày/tuần. Dự kiến dành 80 ngày làm việc trong cửa sổ bốn tháng; đây là giả định lập lịch, không phải phép quy đổi cố định. Chưa có ngày khởi động hoặc năm tuyển sinh, vì vậy lịch sử dụng ngày D1 trở đi. PM phải thay bằng lịch thực tế và trừ ngày lễ trước khi phê duyệt.')
p('Các giờ công và chi phí dưới đây là ước lượng sơ bộ để thảo luận. Phạm vi cơ sở dùng một cổng VNPAY hoặc MoMo cùng chuyển khoản QR; việc cần cả hai cổng phải được khách hàng xác nhận.')
h('Nội dung báo cáo')
p('1  Thiết lập Project\n2  Project Charter\n3  WBS và từ điển WBS\n4  PERT và đường găng\n5  Gantt và nguồn lực\n6  Rủi ro và dự phòng\n7  Phản biện và phản tư\n8  Nhật ký AI và kiểm tra trước khi nộp')
page('1 Thiết lập Project')
h('Nội dung Instructions đề xuất')
p('Bạn là trợ lý quản lý dự án phần mềm cho nhóm thực hiện EduReg. Dùng tài liệu yêu cầu khách hàng làm căn cứ. Trả lời bằng tiếng Việt; ghi rõ giả định cho mọi ước lượng. Phân biệt yêu cầu bắt buộc, tùy chọn và giai đoạn sau. Giữ nhất quán giữa Charter, WBS, lịch và rủi ro. Với thông tin chưa rõ, nêu câu hỏi cần xác nhận. Kiểm tra giới hạn 350 triệu đồng và bốn tháng. Khi phản biện, chỉ ra vấn đề cùng cách kiểm chứng; không tự tuyên bố đã nghiệm thu hoặc đã thao tác trên hệ thống.')
h('Tài liệu đưa vào Knowledge')
table(['Tài liệu','Mục đích'],[['EduReg_YeuCauKhachHang.docx','Lưu nội dung Phụ lục A của đề bài làm yêu cầu gốc.'],['Project Charter đã duyệt','Khóa phạm vi, tiêu chí thành công và giả định.'],['WBS và lịch dự án','Làm cơ sở đối chiếu gói công việc, phụ thuộc và mốc.'],['Risk Register','Theo dõi rủi ro, người phụ trách và hành động.']],[6,11.4])
h('Câu hỏi kiểm tra Knowledge')
p('Tóm tắt năm yêu cầu chính và dẫn mã FR tương ứng. Kết quả mong đợi: danh mục khóa học FR01; đăng ký FR02; thanh toán FR03; thông báo FR04; quản trị lớp và chống trùng lịch FR05. Báo cáo FR07 vẫn là chức năng bắt buộc dù câu hỏi chỉ yêu cầu năm mục.')
h('Minh chứng thiết lập')
p('Ảnh 1  Chèn ảnh thật phần Instructions sau khi nhóm tạo Project.')
p('\n\n')
p('Ảnh 2  Chèn ảnh thật danh sách tài liệu trong Knowledge.')
p('\n\n')
p('Tên Project theo quy ước QLDA_Nhom<số>_EduReg. Các chat dự kiến: Bai1_Charter, Bai2_WBS, Bai3_Lich, Bai4_RuiRo, Bai5_PhanBien.')
page('2 Project Charter')
h('Mục đích và phạm vi')
p('Tên và mã dự án: EduReg – EDR. Nhà tài trợ: Giám đốc Trung tâm Tin học Việt. PM: đại diện nhóm được phân công. Dự án giảm thất lạc đăng ký, xếp lớp trùng lịch và đối soát thủ công bằng một hệ thống dùng chung cho ba cơ sở.')
table(['Trong phạm vi cơ sở','Chưa đưa vào đường cơ sở'],[['FR01, FR02, FR03, FR04, FR05 và FR07; web responsive; chuyển 3.000 hồ sơ; phân quyền; kiểm thử; hosting năm đầu; đào tạo và bàn giao.','FR06 và FR08: nên có, đề xuất giai đoạn bổ sung nếu được phê duyệt. FR09: tùy chọn. FR10: ứng dụng iOS/Android giai đoạn sau. Tích hợp kế toán: chờ biết phần mềm và giao diện kết nối.']],[8.7,8.7])
h('Mục tiêu SMART và nghiệm thu')
p('M1  Trước kết thúc D79, triển khai bản chạy thật có đủ sáu FR bắt buộc, được đại diện học vụ và kế toán ký UAT; không còn lỗi nghiêm trọng gây mất dữ liệu, sai thu tiền hoặc không thể đăng ký.')
p('M2  Trước kết thúc D65, hoàn thành kiểm thử 500 người dùng đồng thời; đề xuất đo p95 thời gian phản hồi dưới 3 giây với tập tác vụ và môi trường giống vận hành, chốt kịch bản đo với khách hàng trước kiểm thử.')
p('M3  Trước UAT, đối chiếu đủ khoảng 3.000 hồ sơ nguồn; mọi bản ghi hợp lệ được nhập, mọi bản ghi trùng hoặc lỗi được thống kê và khách hàng xử lý hoặc chấp thuận bằng biên bản.')
p('M4  Trong tháng vận hành đầu, đo tỷ lệ sẵn sàng tối thiểu 99% trong giờ hành chính theo khung giờ thống nhất. Mốc bàn giao D79 chỉ xác nhận cơ chế giám sát; chỉ tiêu tháng được xác nhận sau đủ kỳ đo.')
h('Hai mục tiêu được cụ thể hóa')
p('“Hệ thống chạy nhanh” được thay bằng M2 với số người dùng, chỉ số đo và hạn kiểm thử. “Chuyển dữ liệu đầy đủ” được thay bằng M3 với số hồ sơ, đối chiếu và xử lý ngoại lệ. Đây là ví dụ chỉnh mục tiêu mơ hồ thành tiêu chí có thể kiểm chứng.')
h('Các bên liên quan')
table(['Vai trò','Trách nhiệm chính'],[['Sponsor','Duyệt Charter, ngân sách, phạm vi và các thay đổi lớn.'],['PM và BA','Quản lý kế hoạch; làm rõ nghiệp vụ; điều phối UAT.'],['Hai web dev và một backend','Phát triển, tích hợp, sửa lỗi và hỗ trợ vận hành.'],['Tester và designer bán thời gian','Kiểm thử độc lập; thiết kế và kiểm tra trải nghiệm responsive.'],['Học vụ, kế toán, giảng viên, học viên','Xác nhận luồng nghiệp vụ, thử nghiệm và phản hồi.'],['Đơn vị thanh toán, Zalo và hosting','Cấp môi trường, tài khoản, thông số và hỗ trợ tích hợp.']],[5,12.4])
page('2 Project Charter tiếp theo')
h('Mốc và ngân sách')
table(['Mốc','Thời điểm cơ sở'],[['Yêu cầu và Charter thống nhất','Kết thúc D5'],['Thiết kế sẵn sàng','D13'],['Demo hàng tháng','D20, D40, D60, D79; quy đổi sang lịch tháng thực tế khi khởi động'],['Kiểm thử hệ thống hoàn tất','D65'],['UAT hoàn tất','D71'],['Đào tạo và chuyển đổi','D76'],['Go live và bàn giao','D79; trước tháng 3 của năm tuyển sinh đã thống nhất']],[9,8.4])
table(['Hạng mục','Triệu đồng'],[['Nhân sự phát triển và quản lý','240'],['Hosting, sao lưu và giám sát năm đầu','24'],['Công cụ, tài khoản tích hợp và kiểm thử','12'],['Làm sạch dữ liệu và đào tạo','14'],['Dự phòng rủi ro do PM đề xuất giải ngân','35'],['Dự trữ quản lý do Sponsor phê duyệt','25'],['Tổng trần','350']],[13,4.4])
p('Chi phí là phân bổ dự kiến, chưa phải báo giá. Khoản nhân sự tính theo ngân sách phân bổ cho đội tham gia từng phần trong bốn tháng, không giả định bảy người đều làm toàn thời gian. Tránh tính trùng giờ nhập liệu, đào tạo trong hợp đồng nhân sự và khoản dịch vụ hỗ trợ.')
h('Giả định và ràng buộc')
p('Khách hàng bố trí người trả lời trong hai ngày làm việc; dữ liệu được giao sớm; nhà cung cấp cấp sandbox trước D20 và quyền chạy thật trước UAT. Cần lịch tham gia cụ thể của từng thành viên và báo giá để xác nhận tính khả thi. Mọi thay đổi phạm vi phải đánh giá tác động chi phí, lịch và rủi ro trước khi Sponsor duyệt.')
h('Ba câu hỏi cần khách hàng chốt')
p('1. Kỳ tuyển sinh tháng 3 thuộc năm nào, ngày khởi động và ngày bắt buộc chạy thật là ngày nào? Câu trả lời quyết định số ngày làm việc thực tế và khả năng dự phòng qua kỳ nghỉ.')
p('2. Cần VNPAY, MoMo hay cả hai; hoàn tiền và đối soát xử lý thế nào? Đây là cơ sở chốt luồng thu tiền, trách nhiệm kế toán và các trường hợp kiểm thử.')
p('3. Phần mềm kế toán hiện có là gì, có API hoặc định dạng nhập liệu nào, tích hợp có bắt buộc trong đợt đầu không? Thông tin này ngăn việc tự thêm phạm vi chưa ước lượng.')
p('Phê duyệt Charter: Sponsor ................  PM ................  Ngày ................')
page('3 WBS theo sản phẩm bàn giao')
p('Gốc 1.0 là toàn bộ dự án EduReg. Mỗi nhánh 1.x gồm hai gói 1.x.1 và 1.x.2 trong bảng ở trang sau; nhánh quản trị 1.16 gồm tám gói hồ sơ theo chu kỳ. Mã trong sơ đồ được rút gọn ở cấp lá để dễ đọc.')
doc.add_picture(str(work/'wbs.png'),width=Cm(17.4))
h('Phạm vi nhánh quản trị')
p('1.16 Hồ sơ quản trị dự án gồm 1.16.1–1.16.8, mỗi gói 16 giờ: báo cáo hai tuần, cập nhật lịch và rủi ro, biên bản demo hoặc họp, quyết định thay đổi và theo dõi hành động. Tổng 128 giờ, thực hiện xuyên suốt dự án, không cộng nối tiếp vào đường găng.')
h('Kiểm tra quy tắc 100 phần trăm')
p('FR01 ở nhánh 1.4; FR02 ở 1.3 và 1.5; FR03 ở 1.6; FR04 ở 1.8; FR05 ở 1.7; FR07 ở 1.9. Dữ liệu cũ ở 1.10; bảo mật và tích hợp ở 1.11; kiểm thử ở 1.12; nghiệm thu ở 1.13; đào tạo ở 1.14; triển khai ở 1.15; quản lý ở 1.16. Thiết kế responsive thuộc 1.2 và được kiểm tra lại tại 1.12.')
p('Các chức năng tùy chọn chưa được phê duyệt không nằm trong tổng công việc của đường cơ sở. Phân biệt gói công việc tính bằng giờ công với hoạt động lịch tính bằng thời gian trôi qua; một hoạt động có thể gom hai gói bàn giao.')
page('3 Bảng WBS và giờ công')
rows=[]
for i,((a,n,pr,t,o),ll) in enumerate(zip(acts,leaves)):
 for j,l in enumerate(ll):rows.append([f'1.{i+1}.{j+1}',l,t*4,o])
table(['Mã WBS','Gói công việc và sản phẩm','Giờ','Phụ trách'],rows,[2,8.6,1.5,5.3])
p(f'Tổng 30 gói chuyên môn: {sum(a[3]*8 for a in acts)} giờ. Cộng 8 gói quản trị × 16 giờ = {sum(a[3]*8 for a in acts)+128} giờ. Mỗi gói từ 12 đến 40 giờ, đáp ứng quy tắc 8/80. Giờ công là ước lượng sơ bộ, cần rà soát theo năng lực và mức tái sử dụng thực tế.')
page('3 Từ điển WBS')
for title,txt in [
('1 6 1 Cổng thanh toán và QR','Sản phẩm: luồng tạo yêu cầu thanh toán với một cổng được chọn và QR chuyển khoản. Đầu vào: tài khoản sandbox, biểu phí, cấu trúc đơn hàng và quy tắc giữ chỗ đã duyệt. Phụ trách: backend; 40 giờ. Bao gồm xác thực dữ liệu đầu vào, định danh giao dịch và xử lý chuyển hướng. Không bao gồm cổng thứ hai hoặc tự động hoàn tiền chưa được duyệt. Nghiệm thu: ca thành công, hủy và thất bại đều cập nhật đúng trạng thái; không xác nhận đã trả tiền chỉ dựa vào trình duyệt.'),
('1 6 2 Webhook và đối soát','Sản phẩm: bộ xử lý thông báo thanh toán, nhật ký và danh sách đối soát. Phụ trách: backend; 40 giờ. Phụ thuộc 1.6.1 và quy tắc kế toán. Nghiệm thu: xác minh thông báo từ cổng; lặp webhook không ghi nhận thu tiền hai lần; số tiền và mã đơn khớp; giao dịch lệch được treo để kiểm tra. Bằng chứng: kết quả kiểm thử và biên bản đối soát do kế toán xác nhận.'),
('1 10 2 Dữ liệu nhập và biên bản đối chiếu','Sản phẩm: tập dữ liệu đã nhập, tệp ngoại lệ và biên bản đối chiếu trước/sau. Phụ trách: BA và Web 2; 32 giờ. Đầu vào: dữ liệu chuẩn hóa của 1.10.1. Có bản sao lưu, chạy thử và cơ chế quay lui. Nghiệm thu: tổng bản ghi nguồn bằng số nhập thành công cộng số ngoại lệ; kiểm tra mẫu các trường định danh và lịch sử; không làm mất dữ liệu nguồn. Khách hàng quyết định cách gộp hồ sơ trùng.')]:h(title);p(txt)
h('Quy trình nghiệm thu gói')
p('Người phụ trách nộp sản phẩm và bằng chứng. Tester hoặc BA đối chiếu tiêu chí; PM ghi trạng thái hoàn tất khi người có thẩm quyền chấp nhận. Gói phát sinh phải có mã, giờ công, phụ thuộc và tiêu chí nghiệm thu trước khi thêm vào đường cơ sở.')
page('4 PERT và đường găng')
p('O, M, P và TE tính theo ngày làm việc. Chọn O = M − 2 và P = M + 2 cho mô hình ba điểm ban đầu; vì đối xứng nên TE = M. Đây là giả định đơn giản cần thay bằng dữ liệu ước lượng của từng người thực hiện.')
p('TE = (O + 4M + P) / 6. Phương sai = ((P − O) / 6)² = 4/9 ngày². ES = max(EF của các hoạt động trước); EF = ES + TE; LF = min(LS của các hoạt động sau); LS = LF − TE; Slack = LS − ES. Mốc tính bắt đầu tại 0.')
rows=[]
for a,n,pr,t,o in acts:
 v=data[a];rows.append([a,','.join(pr) or '—',t-2,t,t+2,t,v['es'],v['ef'],v['ls'],v['lf'],v['slack']])
table(['Mã','Trước','O','M','P','TE','ES','EF','LS','LF','Dư'],rows,[1,2,1.3,1.3,1.3,1.3,1.7,1.7,1.7,1.7,2.4])
p(f'Đường găng: {" → ".join(critical)}. Tổng thời gian kỳ vọng: {T} ngày làm việc. Tổng phương sai trên đường găng: {len(critical)*4/9:.2f} ngày²; độ lệch chuẩn: {math.sqrt(len(critical)*4/9):.2f} ngày, với giả định các thời lượng độc lập và đường găng không đổi.')
p('Ví dụ kiểm tra: hoạt động F bắt đầu tại 29 và kết thúc tại 39; I chờ G, F và J, bắt đầu tại 39 và kết thúc tại 47; K chờ H, I, J nên bắt đầu tại 47. Hai nhánh F–H và F–I đều có thể găng; phải đọc mạng phụ thuộc thay vì nối mọi hoạt động có Slack bằng 0 thành một chuỗi.')
# replace path paragraph with proper branches
for para in doc.paragraphs:
 if para.text.startswith('Đường găng:'):
  para.text=f'Có bốn đường găng bằng nhau: A–B–C–E–F–H–K–L–M–N–O; A–B–D–E–F–H–K–L–M–N–O; A–B–C–E–F–I–K–L–M–N–O; A–B–D–E–F–I–K–L–M–N–O. Mỗi đường dài {T} ngày. Mỗi đường gồm 11 hoạt động, phương sai 44/9 = 4,89 ngày², độ lệch chuẩn khoảng 2,21 ngày khi giả định độc lập. Không dùng kết quả này như xác suất giao đúng hạn chính xác vì có nhiều đường găng.'
h('Đối chiếu lịch bốn tháng')
p(f'Với quỹ giả định 80 ngày, lịch còn {80-T} ngày dự phòng. Chỉ kết luận đáp ứng có điều kiện; nếu ngày nghỉ khiến quỹ thực tế dưới {T} ngày thì phải điều chỉnh trước phê duyệt. Các mốc demo chỉ là kiểm tra tiến độ, không thay thế UAT.')
page('5 Gantt và kiểm tra nguồn lực')
p('Trục ngang là mốc ngày làm việc từ 0; thanh đậm biểu thị hoạt động có độ dự trữ bằng 0. Tên và mã hoạt động khớp bảng PERT.')
doc.add_picture(str(work/'gantt.png'),width=Cm(17.4))
h('Ràng buộc nguồn lực')
p('Web 1 thực hiện D rồi E; Web 2 thực hiện G rồi J rồi I. Liên kết J → I là ràng buộc nguồn lực bổ sung, ngăn giao hai công việc đồng thời cho Web 2. Backend thực hiện B, C, F, H rồi K; cần BA xác nhận khả năng phối hợp với thiết kế ở B. Tester tập trung L; các lập trình viên bố trí thời gian hỗ trợ và sửa lỗi ở M. Công việc PM được phân bổ xuyên suốt, 128 giờ cho tám chu kỳ.')
p('Giờ công WBS chỉ phản ánh tải trực tiếp, không khẳng định tận dụng toàn bộ công suất đội. Phần sửa lỗi trong M và hỗ trợ bàn giao cần chia theo người trong lịch chi tiết. Chưa có lịch nghỉ hoặc cam kết phân bổ thực tế, nên đây là kiểm tra xung đột ở mức hoạt động chính.')
h('Hai phương án khi quỹ thời gian bị thiếu')
table(['Phương án','Lợi ích và điều kiện','Đánh đổi'],[['Crashing','Tăng hỗ trợ tại L để giảm từ 10 xuống 8 ngày; dự kiến tiết kiệm 2 ngày nếu việc kiểm thử chia được.','Giả định thêm 8 triệu từ dự phòng; phải xác nhận người hỗ trợ và năng suất trước cam kết.'],['Fast tracking','Chuẩn bị tài liệu đào tạo trong 2 ngày cuối M; phần chuyển đổi vẫn chờ UAT đạt.','Có thể rút 2 ngày nếu tài liệu ổn định; rủi ro sửa lại và hướng dẫn sai phiên bản.']],[3,7.5,6.9])
p('Ưu tiên giữ lịch cơ sở nếu lịch thực tế đủ; khi thiếu hai ngày, chọn crashing ở kiểm thử nếu có người và ngân sách được duyệt. Không chồng lấn kiểm thử thanh toán với chạy thật. Mọi thay đổi phải tính lại toàn bộ các đường găng.')
page('6 Sổ đăng ký rủi ro')
p('Thang xác suất 1–5: rất thấp đến rất cao. Thang tác động 1–5: nhỏ đến nghiêm trọng đối với lịch, chi phí hoặc dữ liệu. Điểm 15–25 là cao, 8–14 trung bình, 1–7 thấp. Đây là thang định tính đề xuất, cần nhóm thống nhất ngưỡng sử dụng.')
risks=[('R1','Thủ tục nhà cung cấp chậm → chưa có quyền chạy thật → lùi go live.','Bên ngoài',4,5,'Giảm','PM: đăng ký sớm, kiểm tra tiến độ hằng tuần.'),('R2','Lỗi webhook → ghi nhận tiền sai/lặp → thất thoát và khiếu nại.','Kỹ thuật',4,5,'Giảm','Backend: xác minh, chống lặp, đối soát và thử lỗi.'),('R3','Yêu cầu kế toán chưa rõ → thêm tích hợp muộn → tăng phạm vi.','Yêu cầu',4,4,'Tránh','BA: chốt giao diện; đưa thay đổi qua Sponsor.'),('R4','Thiếu quy tắc dữ liệu → nhập trùng/sai → sai hồ sơ và báo cáo.','Dữ liệu',4,4,'Giảm','BA: làm sạch, chạy thử, đối chiếu và rollback.'),('R5','Backend vắng mặt → đình trệ tích hợp → chậm đường găng.','Con người',3,5,'Giảm','PM: chia sẻ mã, tài liệu và người dự phòng.'),('R6','Tranh chấp giữ chỗ → vượt sĩ số → phải xử lý đăng ký lại.','Kỹ thuật',3,5,'Giảm','Web 1: khóa/kiểm tra giao dịch; thử đồng thời.'),('R7','Tải tuyển sinh vượt cấu hình → trang chậm → mất đăng ký.','Hạ tầng',3,4,'Giảm','Backend: kiểm thử tải, giám sát, nâng cấu hình.'),('R8','Chậm duyệt mẫu Zalo → không gửi nhắc lịch → học viên bỏ lỡ.','Bên ngoài',3,4,'Giảm','BA: gửi duyệt sớm, theo dõi lỗi, xác nhận kênh email.'),('R9','Gộp mã sát hạn → xung đột → lỗi hồi quy và trễ demo.','Con người',3,4,'Giảm','Web 2: tích hợp hằng ngày, review và kiểm thử tự động.'),('R10','Lịch thi/nghỉ trùng UAT → thiếu người duyệt → lùi nghiệm thu.','Con người',3,4,'Giảm','PM: chốt lịch, người thay thế và phiên UAT dự phòng.')]
table(['ID và nhóm','Nguyên nhân và hậu quả','XS × TĐ','Ứng phó và chủ trì'],[[r[0]+'\n'+r[2],r[1],f'{r[3]} × {r[4]} = {r[3]*r[4]}',r[5]+': '+r[6]] for r in risks],[2.3,7,2,6.1])
p('R9 và R10 là hai rủi ro bổ sung để nhóm thảo luận từ trải nghiệm thực tế. Nhóm cần xác nhận hoặc thay bằng tình huống đã gặp; không coi đây là bằng chứng nhóm đã tự đề xuất.')
page('6 Ma trận và kế hoạch dự phòng')
rows=[]
for prob in range(5,0,-1):rows.append([str(prob)]+[', '.join(r[0] for r in risks if r[3]==prob and r[4]==impact) or '—' for impact in range(1,6)])
table(['XS \\ TĐ','1','2','3','4','5'],rows,[2.4,3,3,3,3,3])
p('Xác suất tăng từ dưới lên; tác động tăng từ trái sang phải. R1 và R2 cùng đạt điểm cao nhất 20. PM xem xét cả hai hàng tuần, cập nhật chủ sở hữu và bằng chứng đóng hành động.')
h('Dự phòng chi tiết cho R1')
p('Kích hoạt: đến D29 chưa có sandbox ổn định hoặc đến D59 chưa có xác nhận cấp tài khoản chạy thật. PM ghi issue trong ngày, yêu cầu nhà cung cấp trả lời thời điểm xử lý và thông báo Sponsor.')
p('Trong một ngày làm việc, backend đánh giá khả năng tiếp tục kiểm thử bằng môi trường mô phỏng; BA xác nhận nghiệp vụ QR và quy trình đối soát. Môi trường mô phỏng chỉ phục vụ phát triển, không được dùng để ghi nhận tiền thật.')
p('Trong hai ngày tiếp theo, PM trình lựa chọn: chuyển sang cổng thay thế nếu có thể hoàn tất thủ tục và kiểm thử; hoặc đổi mốc go live. Chỉ dùng QR làm phương án vận hành tạm khi Sponsor chấp thuận thay đổi phạm vi bằng văn bản và kế toán chấp thuận đối soát thủ công; điều này không tự động đáp ứng yêu cầu cổng trực tuyến của FR03.')
p('Hạn mức đề xuất: tối đa 15 triệu từ khoản dự phòng 35 triệu, phải có dự toán và phê duyệt trước chi. Tester chạy lại các ca thanh toán, lặp thông báo, sai số tiền và hoàn tác; kế toán ký đối soát trước khi mở thu tiền.')
p('Đóng tình huống khi tài khoản thật hoạt động, giao dịch kiểm tra khớp, lỗi nghiêm trọng bằng 0 và Sponsor xác nhận mốc mới hoặc giữ mốc cũ. Nếu không đạt, giữ hệ thống ở chế độ chưa thu tiền và thông báo phương án tuyển sinh được khách hàng duyệt.')
h('Dự phòng cho R2 đồng hạng cao nhất')
p('Khi có giao dịch thu tiền sai hoặc bị ghi nhận lặp, khóa luồng xác nhận tự động bị lỗi; bảo toàn log và danh sách giao dịch. Backend sửa lỗi, tester chạy lại bộ kiểm thử chống lặp, kế toán đối chiếu từng giao dịch ảnh hưởng. Chỉ mở lại sau xác nhận của kế toán và PM; mọi hoàn tiền theo quy trình được khách hàng duyệt.')
page('7 Phản biện và phản tư')
p('Các câu trả lời dưới đây là phương án tham khảo do AI hỗ trợ. Nhóm cần tự trả lời, sửa theo quyết định thực tế và xác nhận lập luận trước khi nộp phần yêu cầu tự làm.')
qas=[('Vì sao cam kết bốn tháng khi lịch đã chiếm 79 ngày?','Không cam kết chỉ từ phép quy đổi 80 ngày. PM phải nhập ngày bắt đầu, lịch nghỉ và hạn tuyển sinh để kiểm tra. Nếu quỹ ngày nhỏ hơn 77, trình thay đổi nguồn lực hoặc phạm vi; một ngày còn lại chỉ là dự phòng nhỏ theo giả định.'),('350 triệu có đủ cho bảy người và hosting không?','Chỉ đủ khi mức phân bổ nhân sự và báo giá nằm trong 240 triệu dự kiến. Nhóm có 7 vai trò nhưng designer bán thời gian và các vai trò khác tham gia theo công việc. Cần báo giá nhân sự, dịch vụ và thuế trước duyệt; không được coi bảng phân bổ là chứng minh chi phí thực tế.'),('Vì sao không làm FR06 và FR08 ngay?','Đề bài xếp chúng là nên có. Kế hoạch cơ sở ưu tiên sáu chức năng bắt buộc; việc hoãn cần Sponsor chấp thuận. Nếu khách hàng bắt buộc đưa vào đợt đầu, phải thêm WBS, ước lượng và tính lại lịch trước cam kết.'),('Làm sao biết số tiền thu không bị sai?','Thiết kế xác minh webhook, kiểm tra số tiền và mã đơn, xử lý chống lặp và đối soát. UAT phải có kế toán; thử giao dịch lặp, đến muộn, sai dữ liệu và lỗi mạng. Không dùng chỉ tiêu 500 người dùng để thay cho kiểm thử chính xác tài chính.'),('Nếu một người chủ chốt nghỉ vào tuần cuối thì sao?','PM chỉ định người hỗ trợ từ sớm, lưu hướng dẫn vận hành và tổ chức bàn giao chéo. Kiểm tra lại công suất thực tế của người thay thế; nếu không đủ, báo Sponsor và thay đổi lịch thay vì giữ một cam kết thiếu cơ sở.')]
for i,(q,a) in enumerate(qas,1):h(f'Câu {i}  {q.rstrip("?")}');p(a)
h('Phản tư tham khảo')
p('AI hỗ trợ nhanh ở việc dựng khung Charter, phân rã sản phẩm và đưa ra danh sách rủi ro. Những điểm phải kiểm tra là giả định bốn tháng bằng 80 ngày làm việc, cách xử lý nhiều đường găng và xung đột nhân lực giữa I với J. Đây là các điểm kiểm tra của bản kế hoạch, không phải mô tả trải nghiệm chưa được nhóm thực hiện.')
p('Quyết định chấp nhận phạm vi, chi ngân sách dự phòng, xử lý dữ liệu học viên và cho phép chạy thật thuộc người có thẩm quyền. AI hỗ trợ phân tích nhưng không có đủ bối cảnh, quyền phê duyệt hoặc trách nhiệm với tổ chức để tự quyết định các việc này.')
page('8 Nhật ký và kiểm tra trước khi nộp')
p('Nhật ký dưới đây mô tả các phần được AI hỗ trợ trong bản báo cáo này; cột cuối dành cho nhóm ghi việc tự kiểm tra thực tế. Không trình bày các prompt gợi ý như lịch sử chat đã diễn ra trên Claude.')
table(['Phần','Nội dung AI hỗ trợ','Nhóm cần kiểm tra và ghi kết quả'],[['Thiết lập','Soạn Instructions và danh sách Knowledge.','Tạo Project; chèn ảnh thật và ngày thao tác.'],['Charter','Soạn phạm vi, SMART, ngân sách và câu hỏi.','Chốt giả định; ghi mục tiêu nhóm đã sửa.'],['WBS','Phân rã 3 cấp; giờ công; từ điển và sơ đồ.','Kiểm tra 100%; xác nhận 8/80; sửa theo năng lực.'],['Lịch','Tính PERT, tiến/lùi, Slack và Gantt.','Tính độc lập bằng Excel; ghi chênh lệch hoặc xác nhận trùng.'],['Rủi ro','Đề xuất 10 rủi ro, ma trận và dự phòng.','Bổ sung ít nhất 2 rủi ro từ trải nghiệm nhóm.'],['Phản biện','Đề xuất 5 câu hỏi và phương án trả lời.','Tự viết câu trả lời và phản tư theo hoạt động đã làm.']],[2.3,7,8.1])
h('Công thức để nhóm kiểm tra trong Excel')
p('Đặt các cột A đến M lần lượt: mã, tên, trước, O, M, P, TE, phương sai, ES, EF, LS, LF, Slack. Với dòng 2: G2=(D2+4*E2+F2)/6; H2=((F2-D2)/6)^2; J2=I2+G2; K2=L2-G2; M2=K2-I2. ES dùng MAX của EF các tiền nhiệm; LF dùng MIN của LS các hậu nhiệm; hoạt động cuối có LF bằng thời lượng dự án. Phải liên kết đúng dòng, không dùng MAX cho toàn bộ cột.')
h('Danh sách hoàn thiện hồ sơ')
p('□ Điền số nhóm, lớp, tên thành viên và người phụ trách.\n□ Chèn ảnh Instructions và Knowledge thật.\n□ Xác nhận ngày khởi động, năm tuyển sinh và lịch nghỉ.\n□ Đính kèm file Excel có công thức PERT và Gantt theo yêu cầu đề bài.\n□ Ghi kết quả tính lại, những thay đổi nhóm tự thực hiện và nhật ký prompt thật.\n□ Tự hoàn thiện phần phản biện, hai rủi ro từ kinh nghiệm và phê duyệt Charter.\n□ Đổi tên báo cáo thành QLDA_Nhom<số>_Lab.docx.')
h('Tài liệu căn cứ')
p('Lab_QLDA_CNTT_Claude_Projects.docx do người học cung cấp; đặc biệt Phụ lục A về yêu cầu EduReg, Phụ lục B về Charter và Phụ lục C về nhật ký. Ngân sách, số học viên, đội dự án và mức ưu tiên FR lấy từ đề bài; lịch, giờ công, chi phí chi tiết và biện pháp ứng phó là phương án ước lượng cần xác nhận.')
doc.save(out/'QLDA_Nhom_Lab_EduReg.docx')
print(json.dumps({'duration':T,'data':data,'pages_sections':13,'file':str(out/'QLDA_Nhom_Lab_EduReg.docx')},ensure_ascii=False))



