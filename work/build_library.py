from pathlib import Path
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
base=Path(r'D:\QL dự án nhóm'); work=base/'work'; out=base/'output'
source=Document(r'C:\Users\Dell\Downloads\bao_cao_tuan_1_4.docx')
acts=[]
for r in source.tables[5].rows[1:]:
 a,n,pred,t=[c.text for c in r.cells]; acts.append((a,n,[] if pred=='-' else pred.split(','),Decimal(t.replace(',','.'))))
def cpm(opt=False):
 d={}
 for a,n,pre,t in acts:
  if opt and a in ['G','J','N']:t=Decimal(3)
  if opt and a=='O':t=Decimal(2)
  es=max([d[k]['ef'] for k in pre] or [Decimal(0)]);d[a]={'es':es,'ef':es+t,'t':t}
 T=max(v['ef'] for v in d.values())
 for a,n,pre,t in reversed(acts):
  lf=min([d[k]['ls'] for k,nn,pp,tt in acts if a in pp] or [T]); d[a].update(lf=lf,ls=lf-d[a]['t']);d[a]['sl']=d[a]['ls']-d[a]['es']
 return d,T
d,T=cpm(); opt,OT=cpm(True)
fmt=lambda x:f'{x:.2f}'.replace('.',',')
# Reuse only layout helpers; no content from the earlier project.
s=(work/'build_doc.py').read_text(encoding='utf-8-sig')
exec(s[s.index('doc=Document();'):s.index("p('BÁO CÁO THỰC HÀNH'")])
# True tree with full WBS branch IDs.
branches=[('1.1 Hồ sơ quản lý dự án',['1.1.1 Charter và phân công','1.1.2 Backlog và kế hoạch Sprint','1.1.3–1.1.6 Hồ sơ theo dõi']),('1.2 Bộ yêu cầu',['1.2.1 SRS và phạm vi','1.2.2 User Story và nghiệm thu']),('1.3 Bộ thiết kế',['1.3.1 UI Flow và wireframe','1.3.2 ERD và dữ liệu','1.3.3 Đặc tả REST API']),('1.4 Phần mềm MVP',['1.4.1 Môi trường phát triển','1.4.2 Tài khoản và phân quyền','1.4.3 Danh mục và tìm sách','1.4.4 Giao diện khách hàng','1.4.5 Giỏ hàng','1.4.6 Đơn hàng','1.4.7 Thanh toán','1.4.8 Giao diện quản trị']),('1.5 Bản tích hợp đạt kiểm thử',['1.5.1 Bản tích hợp','1.5.2 Kết quả kiểm thử','1.5.3 Bản sửa lỗi']),('1.6 Bản triển khai',['1.6.1 Cấu hình và bản phát hành','1.6.2 Hướng dẫn vận hành']),('1.7 Hồ sơ nghiệm thu',['1.7.1 Kịch bản và buổi demo','1.7.2 Biên bản bàn giao'])]
font=r'C:\Windows\Fonts\arial.ttf'; im=Image.new('RGB',(1560,1510),'white');dr=ImageDraw.Draw(im); f=ImageFont.truetype(font,24); fb=ImageFont.truetype(font,26)
dr.text((30,15),'1.0  WEBSITE BÁN HÀNG VÀ THANH TOÁN CHO THƯ VIỆN',font=fb,fill='black')
dr.line((45,55,45,1440),fill='#566778',width=3)
y=76
for title,children in branches:
 dr.line((45,y+15,90,y+15),fill='#566778',width=3);dr.text((100,y),title,font=fb,fill='black');y+=39
 for child in children:
  dr.line((117,y-7,117,y+16),fill='#9ba9b4',width=2);dr.line((117,y+16,145,y+16),fill='#9ba9b4',width=2);dr.text((157,y),child,font=f,fill='black');y+=34
 y+=18
im=im.crop((0,0,960,y+10));im.save(work/'thu_vien_wbs.png')
im=Image.new('RGB',(1500,1040),'white');dr=ImageDraw.Draw(im);f=ImageFont.truetype(font,23)
for v in range(0,41,5):
 x=470+v*24;dr.line((x,55,x,1000),fill='#dddddd');dr.text((x-10,15),str(v),font=f,fill='black')
for i,(a,n,pre,t) in enumerate(acts):
 y=68+i*53;dr.text((12,y),a+'  '+n,font=f,fill='black'); dr.rectangle((470+float(d[a]['es'])*24,y,470+float(d[a]['ef'])*24,y+30),fill='#314d66' if d[a]['sl']==0 else '#a1b3c2')
im.save(work/'thu_vien_gantt.png')
p('BÁO CÁO THỰC HÀNH','Title');p('Lập kế hoạch dự án website bán hàng và thanh toán cho thư viện','Title')
p('Học phần Quản lý dự án công nghệ thông tin');p('Nhóm 11  •  Quy mô 6 thành viên  •  Thời gian 8 tuần')
p('Lớp: ............................................................')
p('Thành viên: ..............................................................................\n.................................................................................................')
h('Tóm tắt dự án')
p('Nhóm 11 xây dựng website hỗ trợ khách hàng xem và tìm sách, quản lý giỏ hàng, đặt hàng, thanh toán và xem lịch sử đơn hàng. Admin quản lý sách, danh mục, khách hàng, đơn hàng, thanh toán và thống kê cơ bản. Dự án áp dụng Agile Scrum với một Sprint mỗi tuần, sử dụng ReactJS, NodeJS và Figma.')
p(f'Từ 17 hoạt động trong kế hoạch, thời gian tính lại theo CPM là {fmt(T)} ngày làm việc. Phương án tối ưu giảm còn {fmt(OT)} ngày nếu việc chia việc và tăng phối hợp thực hiện được. Tổng EMV minh họa là 2.825.000 đồng; đây không phải tổng ngân sách dự án.')
h('Cơ sở kế hoạch')
p('Báo cáo sản phẩm tuần 1–4 là căn cứ về đề tài, phạm vi MVP, công nghệ, quy mô nhóm và các số liệu lịch. Những tiêu chí nghiệm thu, giờ công WBS và phân vai chi tiết được ghi là đề xuất để nhóm xác nhận. Kết quả Actual trong báo cáo tuần là số liệu mẫu, chưa chứng minh tiến độ Jira thực tế.')
h('Nội dung')
p('1  Thiết lập Project và tổ chức công việc\n2  Project Charter và yêu cầu\n3  WBS và từ điển gói công việc\n4  Lịch dự án và đường găng\n5  Gantt và phương án tối ưu\n6  Rủi ro và EMV\n7  Theo dõi tuần 1 đến tuần 4\n8  Phản biện và nhật ký AI')
page('1 Thiết lập Project và tổ chức công việc')
h('Thông tin Project')
p('Tên Project hiện dùng: QLDA_Nhom11_EduReg. Nội dung dự án trong báo cáo là website bán hàng và thanh toán cho thư viện. Tên đề xuất để đồng nhất nội dung: QLDA_Nhom11_ThuVien. Việc đổi tên Project thực tế do nhóm thực hiện khi thống nhất.')
h('Instructions đề xuất')
p('Bạn là trợ lý lập kế hoạch dự án cho Nhóm 11, gồm 6 thành viên, thực hiện website bán hàng và thanh toán cho thư viện trong 8 tuần. Dùng báo cáo tuần 1–4 làm dữ liệu gốc. Giữ nhất quán phạm vi tài khoản, sách, tìm kiếm, giỏ hàng, đơn hàng, thanh toán và quản trị. Mọi ước lượng bổ sung phải ghi giả định. Không coi Actual mẫu là tiến độ thật; không coi EMV là ngân sách được duyệt. Kiểm tra số học, phụ thuộc và nguồn lực. Những thông tin chưa có như cổng thanh toán, hệ quản trị cơ sở dữ liệu, ngân sách và ngày khởi động phải được nêu để xác nhận.')
h('Knowledge và minh chứng')
table(['Tài liệu','Cách sử dụng'],[['bao_cao_tuan_1_4.docx','Nguồn dữ liệu dự án và số liệu lịch ban đầu.'],['Charter và WBS đã xác nhận','Dùng làm đường cơ sở phạm vi và bàn giao.'],['Lịch có công thức và Risk Register','Đối chiếu phụ thuộc, tiến độ và ứng phó.'],['Ảnh Instructions và Knowledge','Nhóm chèn ảnh thật sau khi tạo hoặc cập nhật Project.']],[6,11.4])
p('Vị trí chèn ảnh Instructions: ................................................................\n\nVị trí chèn ảnh Knowledge: ................................................................')
h('Phân vai đề xuất cho sáu thành viên')
table(['Vị trí','Trách nhiệm'],[['TV1','PM kiêm BA: yêu cầu, Backlog, Sprint và điều phối nghiệm thu.'],['TV2','Frontend kiêm UI/UX: Figma, luồng và giao diện khách hàng.'],['TV3','Frontend: giỏ hàng, đơn hàng và giao diện quản trị.'],['TV4','Backend: dữ liệu, REST API, tài khoản và sách.'],['TV5','Backend: đơn hàng, thanh toán và hỗ trợ triển khai.'],['TV6','Tester kiêm hỗ trợ triển khai: kiểm thử, hồi quy và phát hành.']],[2,15.4])
p('Phân vai trên chưa gắn tên cá nhân và chưa thay thế lịch phân bổ nguồn lực thực tế. PM cần ghi rõ mức sẵn sàng của từng người trước khi chốt lịch.')
page('2 Project Charter')
table(['Nội dung','Thông tin'],[['Tên dự án','Website bán hàng và thanh toán cho thư viện'],['Đơn vị thực hiện','Nhóm 11, gồm 6 thành viên'],['Thời gian và cách làm','8 tuần; Agile Scrum; 1 Sprint/tuần'],['Công nghệ','ReactJS Frontend → REST API → NodeJS Backend → Database; Figma cho thiết kế'],['Người hướng dẫn và đánh giá','Giảng viên; chưa có tên và người phê duyệt nghiệp vụ cụ thể'],['Ngân sách','Chưa được xác định trong dữ liệu dự án; cần dự toán và phê duyệt riêng']],[5,12.4])
h('Mục đích và sản phẩm bàn giao')
p('Xây dựng luồng mua sách trên website từ tra cứu đến thanh toán, đồng thời cung cấp công cụ quản trị tập trung. Sản phẩm gồm bộ yêu cầu, thiết kế giao diện và dữ liệu, mã nguồn frontend/backend, bản triển khai, kết quả kiểm thử, hướng dẫn và hồ sơ nghiệm thu.')
h('Mục tiêu SMART đề xuất')
p('M1  Đến hết tuần 8, có bản triển khai cho phép thực hiện trọn luồng đăng ký hoặc đăng nhập → tìm sách → thêm giỏ → đặt hàng → thanh toán → xem lịch sử đơn hàng, theo bộ ca nghiệm thu đã thống nhất.')
p('M2  Trước buổi nghiệm thu cuối tuần 8, kiểm thử đạt 100% ca nghiệp vụ trọng yếu đã duyệt; không còn lỗi chặn mua hàng, sai số tiền hoặc truy cập trái phép chức năng Admin. Các lỗi còn lại có danh sách và quyết định xử lý.')
p('M3  Trước kết thúc tuần 3, chốt UI Flow, wireframe, ERD và đặc tả API cho phạm vi MVP; các thay đổi sau mốc này phải cập nhật Backlog và đánh giá tác động lịch.')
p('M4  Trong Sprint cuối, hoàn thành kiểm tra trên Chrome, Edge và Firefox với phiên bản nhóm ghi nhận; mọi lỗi chặn luồng chính phải được sửa hoặc có quyết định nghiệm thu rõ ràng. Đây là cách cụ thể hóa yêu cầu trình duyệt phổ biến trong tài liệu nguồn.')
h('Giả định và ràng buộc')
p('Kế hoạch minh họa dùng 5 ngày làm việc/tuần, tương đương quỹ 40 ngày cho 8 tuần nếu không có ngày nghỉ. Chưa có ngày khởi động, cam kết giờ của thành viên hoặc lịch thi. Chưa xác định cổng thanh toán, môi trường sandbox/chạy thật, cơ sở dữ liệu và hosting. Không lấy ngân sách hay chỉ tiêu tải của dự án khác áp vào dự án này.')
p('Phê duyệt: PM ........................  Người đánh giá ........................  Ngày ................')
page('2 Phạm vi và yêu cầu')
h('Phạm vi MVP')
for text in ['Tài khoản: đăng ký, đăng nhập, thông tin cá nhân và phân quyền Customer/Admin.','Sách: danh sách, chi tiết, tìm kiếm và lọc; Admin quản lý sách và danh mục.','Mua hàng: giỏ hàng, tạo đơn hàng, thanh toán và lịch sử đơn hàng.','Quản trị: khách hàng, đơn hàng, giao dịch thanh toán và thống kê cơ bản.','Chất lượng: bảo vệ thông tin xác thực, cấu trúc dễ bảo trì và hoạt động ổn định trên trình duyệt phổ biến.']:p(text)
h('Giới hạn phạm vi đề xuất')
p('Chưa đưa vào MVP các chức năng mượn/trả sách, quản lý phạt, ứng dụng di động riêng, hệ thống vận chuyển và tích hợp kế toán. Các nội dung này không được nêu trong phạm vi nguồn; việc loại trừ phải được nhóm và người đánh giá xác nhận. Invoice trong ERD là thực thể hóa đơn của hệ thống, chưa đồng nghĩa với tích hợp hóa đơn điện tử.')
table(['Story','Nội dung theo báo cáo','Tiêu chí chấp nhận đề xuất'],[['US01–02','Đăng ký và đăng nhập','Thông tin hợp lệ tạo/đăng nhập tài khoản; sai thông tin bị từ chối; Customer không gọi được API Admin.'],['US03','Tìm kiếm sách','Tìm theo từ khóa và bộ lọc đã thống nhất; hiển thị trạng thái không có kết quả.'],['US04','Thêm sách vào giỏ','Cập nhật số lượng và tổng tiền; chặn số lượng không hợp lệ.'],['US05','Đặt hàng','Đơn có mã, chi tiết và số tiền; kiểm tra lại giá và số lượng ở backend.'],['US06','Thanh toán','Chỉ ghi nhận thành công từ nguồn xác thực; xử lý thất bại và thông báo lặp.'],['US07–08','Admin quản lý sách và đơn','Chỉ Admin được cập nhật; thay đổi trạng thái đơn tuân theo quy tắc đã duyệt.']],[2.2,5.2,10])
h('Ba câu hỏi phải làm rõ')
p('1. Thanh toán dùng cổng nào, sandbox hay thu tiền thật, chính sách hủy và hoàn tiền ra sao? Câu trả lời quyết định luồng giao dịch và tiêu chí nghiệm thu.')
p('2. Bán sách vật lý hay sách điện tử; có quản lý tồn kho, địa chỉ nhận hàng và giao hàng không? ERD có Customer Address nhưng phạm vi giao hàng chưa rõ.')
p('3. Ngày bắt đầu, lịch rảnh của sáu thành viên và trần chi phí là gì? Thiếu các thông tin này thì chưa thể cam kết lịch theo ngày thực tế hoặc dự toán tổng.')
page('3 Sơ đồ WBS')
p('Giữ bảy nhánh WBS của báo cáo tuần và phân rã thành các gói sản phẩm cấp ba. Mỗi gói có người phụ trách và bằng chứng nghiệm thu; công việc quản lý bao phủ suốt tám Sprint.')
doc.add_picture(str(work/'thu_vien_wbs.png'),height=Cm(20.8))
page('3 Bảng gói công việc WBS')
packages=[('1.1.1','Charter và phân công',8,'TV1'),('1.1.2','Backlog và kế hoạch Sprint',16,'TV1'),('1.1.3–1.1.6','4 bộ hồ sơ theo dõi, mỗi bộ 2 Sprint',32,'TV1'),('1.2.1','SRS và phạm vi',16,'TV1'),('1.2.2','User Story và tiêu chí chấp nhận',8,'TV1'),('1.3.1','UI Flow và wireframe',24,'TV2'),('1.3.2','ERD và thiết kế dữ liệu',24,'TV4'),('1.3.3','Đặc tả REST API',24,'TV4'),('1.4.1','Môi trường phát triển',16,'TV6'),('1.4.2','Tài khoản và phân quyền',24,'TV4'),('1.4.3','Danh mục và tìm sách',32,'TV4'),('1.4.4','Giao diện khách hàng',48,'TV2'),('1.4.5','Giỏ hàng',24,'TV3'),('1.4.6','Đơn hàng',32,'TV5'),('1.4.7','Thanh toán',24,'TV5'),('1.4.8','Giao diện quản trị',32,'TV3'),('1.5.1','Bản tích hợp',24,'TV4 và TV5'),('1.5.2','Kết quả kiểm thử',32,'TV6'),('1.5.3','Bản sửa lỗi',24,'Nhóm dev'),('1.6.1','Cấu hình và bản phát hành',8,'TV6'),('1.6.2','Hướng dẫn vận hành',8,'TV6'),('1.7.1','Kịch bản và buổi demo',8,'TV1'),('1.7.2','Biên bản bàn giao',8,'TV1')]
table(['Mã','Sản phẩm bàn giao','Giờ','Phụ trách'],packages,[2.6,9.7,1.4,3.7])
p(f'Tổng giờ công đề xuất: {sum(r[2] for r in packages)} giờ. Dòng 1.1.3–1.1.6 gồm bốn gói, mỗi gói 8 giờ; các gói còn lại từ 8 đến 48 giờ, đáp ứng quy tắc 8/80. Đây là ước lượng bổ sung, không phải số giờ đã ghi nhận trong báo cáo tuần. Giờ công không đồng nhất với thời lượng TE theo ngày của một hoạt động.')
h('Kiểm tra phạm vi')
p('WBS bao phủ quản lý, yêu cầu, thiết kế, phát triển, tích hợp/kiểm thử, triển khai và nghiệm thu. Thống kê cơ bản thuộc 1.4.8; lịch sử đơn hàng thuộc 1.4.6 và 1.4.4. Giới hạn nội dung từng gói cần chốt để không tính trùng frontend chung với giao diện từng chức năng.')
page('3 Từ điển WBS')
for title,content in [('1 4 6 Đơn hàng','Đầu vào: giỏ hàng hợp lệ, dữ liệu sản phẩm và quy tắc trạng thái đơn. Sản phẩm: API đơn hàng, dữ liệu chi tiết và lịch sử đơn. Chủ trì TV5, phối hợp TV3; 32 giờ đề xuất. Phụ thuộc I trong lịch hoạt động. Nghiệm thu: backend tự tính lại giá và tổng tiền; không tạo đơn trùng khi gửi lặp; khách hàng chỉ xem đơn của mình. Phạm vi tồn kho, vận chuyển và hủy đơn phải được chốt trước triển khai.'),('1 4 7 Thanh toán','Đầu vào: đơn hàng và môi trường thanh toán được thống nhất. Sản phẩm: luồng thanh toán, giao dịch và cập nhật trạng thái đơn. Chủ trì TV5; 24 giờ đề xuất. Phụ thuộc J. Nghiệm thu: thử thành công, thất bại, hủy và gửi lặp; xác minh giao dịch ở backend; không đánh dấu đã trả tiền chỉ từ phản hồi trên trình duyệt. Chưa bao gồm tích hợp nhiều cổng hoặc tự động hoàn tiền nếu chưa được duyệt.'),('1 5 2 Kết quả kiểm thử','Đầu vào: bản tích hợp M và bộ tiêu chí chấp nhận. Sản phẩm: test case, kết quả chạy, danh sách lỗi và bằng chứng kiểm tra phân quyền. Chủ trì TV6; 32 giờ đề xuất. Nghiệm thu: có kết quả cho toàn bộ ca trọng yếu; lỗi ghi đầy đủ bước tái hiện, mức độ và chủ sở hữu. Sửa lỗi thuộc 1.5.3; kiểm tra lại lỗi đã sửa phải được tính trong gói đó, tránh bỏ sót hồi quy.')]:h(title);p(content)
h('Liên kết WBS với lịch')
table(['WBS','Hoạt động'],[['1.2','A Phân tích yêu cầu'],['1.3.1 / 1.3.2 / 1.3.3','B UI/UX / C Database / D API'],['1.4.1–1.4.8','E Môi trường; F Authentication; G Sách; H Frontend; I Cart; J Order; K Payment; L Admin'],['1.5.1–1.5.3','M Tích hợp; N Testing; O Fix Bug'],['1.6 / 1.7','P Deploy / Q Demo và nghiệm thu'],['1.1','Hoạt động quản trị xuyên suốt tám tuần; theo dõi riêng, không cộng nối tiếp vào CPM']],[5,12.4])
page('4 Lịch dự án và đường găng')
p('Bảng nguồn có TE nhưng không có ba ước lượng O, M, P. Vì vậy phép kiểm tra dưới đây là CPM trên TE đã cung cấp; chưa thể xác nhận công thức PERT ba điểm hoặc tính độ lệch chuẩn dự án. Không suy ngược một bộ O, M, P rồi coi đó là dữ liệu gốc.')
table(['Mã','Hoạt động','Trước','TE','ES','EF','LS','LF','Dư'],[[a,n,','.join(pre) or '—',fmt(t)]+[fmt(d[a][k]) for k in ['es','ef','ls','lf','sl']] for a,n,pre,t in acts],[0.9,4.3,1.6,1.65,1.8,1.8,1.8,1.8,1.75])
p('Đơn vị: ngày làm việc; ES bắt đầu tại 0. ES = max(EF của các tiền nhiệm); EF = ES + TE; LF = min(LS của các hậu nhiệm); LS = LF − TE; độ dự trữ = LS − ES.')
p('Đường găng: A → C → D → G → I → J → K → M → N → O → P → Q.')
p(f'Tổng thời gian: {fmt(T)} ngày, trùng kết quả khoảng 37,02 ngày trong báo cáo tuần. Với giả định 40 ngày làm việc, dự trữ tới hạn chót là {fmt(Decimal(40)-T)} ngày; chưa bao gồm ngày nghỉ hoặc giới hạn phân bổ nguồn lực.')
h('Ví dụ kiểm tra phụ thuộc')
p(f'G kết thúc tại {fmt(d["G"]["ef"])}; I phải chờ F và G nên bắt đầu tại {fmt(d["I"]["es"])}. M chờ H, K và L; K kết thúc muộn nhất tại {fmt(d["K"]["ef"])} nên quyết định thời điểm tích hợp. Điều này giải thích vì sao nhánh thanh toán nằm trên đường găng.')
page('5 Gantt và phương án tối ưu')
p('Gantt dùng lịch cơ sở. Thanh đậm là hoạt động găng; thanh nhạt là hoạt động có độ dự trữ. Mốc 0–40 thể hiện ngày làm việc kể từ khi khởi động.')
doc.add_picture(str(work/'thu_vien_gantt.png'),width=Cm(17.4))
table(['Hoạt động','Trước','Sau','Biện pháp theo nguồn'],[[c.text for c in r.cells] for r in source.tables[6].rows[1:]],[5,2,2,8.4])
p(f'Tính lại toàn bộ mạng sau điều chỉnh cho kết quả {fmt(OT)} ngày, giảm {fmt(T-OT)} ngày, khớp số 32,51 ngày của báo cáo. Đường găng vẫn giữ nguyên. Quỹ dự phòng tới ngày 40 tăng lên {fmt(Decimal(40)-OT)} ngày theo giả định lịch làm việc.')
h('Điều kiện chấp nhận phương án')
p('Chia việc ở G, N và O chỉ rút ngắn được lịch khi có người hỗ trợ phù hợp và chi phí phối hợp không triệt tiêu lợi ích. H và L vẫn có thể trùng nguồn lực với I hoặc công việc backend. Lịch CPM trên chưa san bằng nguồn lực; PM phải đối chiếu phân vai và giờ rảnh từng người trước khi dùng làm lịch cam kết.')
p('Các biện pháp nguồn chủ yếu giảm thời lượng nhờ chia việc và tái sử dụng, không tự chứng minh là fast tracking. Crashing cần bổ sung năng lực và tính chi phí; fast tracking cần thay đổi quan hệ phụ thuộc để chồng lấn các phần đủ điều kiện. Chưa có chi phí tăng tốc nên không kết luận phương án tối ưu về tiền.')
page('6 Rủi ro và chi phí kỳ vọng')
table(['Rủi ro','Xác suất','Tác động tiền','EMV'],[[c.text for c in r.cells] for r in source.tables[7].rows[1:]],[6.3,2.7,4.2,4.2])
p('EMV = xác suất × thiệt hại tiền giả định. Tổng = 600.000 + 525.000 + 625.000 + 400.000 + 450.000 + 225.000 = 2.825.000 đồng. Con số này trùng báo cáo nguồn, là minh họa tổn thất kỳ vọng; không phải chi phí thực tế, ngân sách dự án hay mức dự phòng đủ chắc chắn.')
h('Sổ rủi ro mở rộng đề xuất')
risks=[('R1','Backend chậm do thiếu năng lực → API trễ → frontend và tích hợp chờ.',3,4,'TV4: chia nhỏ API, chốt hợp đồng sớm.'),('R2','Lệch cấu trúc API → lỗi tích hợp → phải sửa và chạy lại test.',3,4,'TV4: kiểm thử hợp đồng và tích hợp thường xuyên.'),('R3','Xử lý giao dịch sai → sai trạng thái thu tiền → sai đơn hàng.',2,5,'TV5: xác minh, chống lặp, thử tình huống lỗi.'),('R4','Phạm vi chưa chốt → thêm chức năng → lùi nghiệm thu.',2,4,'TV1: duyệt thay đổi và ưu tiên Backlog.'),('R5','Thành viên chậm bàn giao → công việc phụ thuộc chờ → trễ Sprint.',3,3,'TV1: kiểm tra cam kết và hỗ trợ sớm.'),('R6','Sai cấu hình phát hành → website lỗi → không demo được.',2,4,'TV6: checklist, staging và rollback.'),('R7','Phân quyền thiếu ở API → Customer gọi chức năng Admin → sửa dữ liệu trái phép.',2,5,'TV4: kiểm tra quyền ở server và test phủ định.'),('R8','Lịch thi hoặc bận chung → thiếu người kiểm thử → lỗi tồn cuối kỳ.',3,3,'TV1: chốt lịch rảnh và người thay thế.')]
table(['ID','Nguyên nhân và hậu quả','XS × TĐ','Chủ trì và ứng phó'],[[r[0],r[1],f'{r[2]} × {r[3]} = {r[2]*r[3]}',r[4]] for r in sorted(risks,key=lambda r:r[2]*r[3],reverse=True)],[0.9,8,2.1,6.4])
p('R1–R6 bám nhóm rủi ro nguồn; tác động định tính và biện pháp là đề xuất. R7–R8 là gợi ý bổ sung của AI, cần nhóm tự xác nhận hoặc thay bằng rủi ro từ kinh nghiệm thực tế. Chiến lược hiện tại là giảm thiểu cho cả tám rủi ro.')
page('6 Ma trận và kế hoạch dự phòng')
p('Quy ước xác suất đề xuất: mức 1 ≤10%; mức 2 >10–25%; mức 3 >25–50%; mức 4 >50–75%; mức 5 >75%. Với R7–R8 chưa có xác suất phần trăm, mức XS là đánh giá sơ bộ. Tác động 1–5 tăng từ nhỏ đến nghiêm trọng đối với dữ liệu, chức năng hoặc hạn nộp; không quy đổi trực tiếp từ tiền EMV.')
table(['XS \\ TĐ','1','2','3','4','5'],[[str(prob)]+[', '.join(r[0] for r in risks if r[2]==prob and r[3]==impact) or '—' for impact in range(1,6)] for prob in range(5,0,-1)],[2.4,3,3,3,3,3])
p('Điểm 15–25: cao; 8–14: trung bình; 1–7: thấp. R1 và R2 cùng cao nhất trong danh sách với 12 điểm. R3 và R7 dù 10 điểm vẫn cần kiểm soát nghiêm vì tác động đến tiền hoặc quyền truy cập.')
h('Kế hoạch dự phòng cho R1')
p('Dấu hiệu kích hoạt: API trên đường găng trễ một ngày so với lịch đã duyệt, hoặc không có bản có thể kiểm thử trong hai lần cập nhật liên tiếp. TV1 xác nhận tình hình trong ngày và ghi issue trên Jira.')
p('TV4 liệt kê phần API còn thiếu, ưu tiên phần phục vụ sách, giỏ hàng và đơn hàng. TV5 hỗ trợ một phần độc lập nếu không làm trễ thanh toán; frontend dùng mock theo hợp đồng đã chốt để tiếp tục công việc, nhưng mock không được coi là tích hợp hoàn tất.')
p('Trong ngày làm việc kế tiếp, TV1 tính lại lịch và kiểm tra người hỗ trợ có thực sự rảnh. Nếu không thể phục hồi bằng phân công lại, trao đổi với giảng viên về giảm phần ngoài MVP hoặc điều chỉnh kế hoạch. Không tự loại chức năng thanh toán của đề tài.')
p('TV6 kiểm tra API và chạy lại các ca tích hợp sau bàn giao. Đóng rủi ro thành issue đã xử lý khi các ca trọng yếu đạt và lịch cập nhật được xác nhận. Tác động 2 triệu đồng của R1 là giả định EMV, không phải hạn mức chi đã được phê duyệt.')
h('Xử lý R2 đồng hạng')
p('Khi tích hợp không đạt, khóa phiên bản hợp đồng API dùng cho bản demo, ghi rõ sai khác frontend/backend, chia người sửa từng phía và chạy lại kiểm thử hợp đồng. Chỉ tích hợp vào bản phát hành sau khi kiểm tra luồng mua hàng hoàn chỉnh; không sửa tên trường hoặc trạng thái âm thầm.')
page('7 Theo dõi tuần 1 đến tuần 4')
table(['Tuần','Trọng tâm','Sản phẩm được mô tả trong báo cáo'],[['1','Khởi động','Charter, stakeholder, MVP và Product Backlog ban đầu.'],['2','Phân tích và kế hoạch','Yêu cầu chức năng/phi chức năng, User Story, WBS; danh sách SRS, phạm vi, Risk Register v1, Effort/Cost, UI Flow và ERD v1.'],['3','Thiết kế và môi trường','ReactJS → REST API → NodeJS → Database; ERD, API Design, UI/UX; khởi tạo Git và môi trường.'],['4','Phát triển và kiểm soát','Activity List, đường găng, phương án tối ưu, EMV và bảng theo dõi mẫu.']],[1.3,4.1,12])
h('Bảng theo dõi mẫu từ tài liệu nguồn')
table(['Công việc','Plan','Actual mẫu','Trạng thái mẫu'],[[c.text for c in r.cells] for r in source.tables[8].rows[1:]],[7,2,2.8,5.6])
p('Không sử dụng bảng này để tuyên bố nhóm đã hoàn thành chức năng. Khi cập nhật, ghi ngày chốt số liệu, mã Jira, người phụ trách và bằng chứng đạt tiêu chí Done. Plan và Actual cần dùng cùng đơn vị đo, tránh so phần trăm số task với phần trăm giờ công.')
h('Điểm cần đối chiếu giữa lịch và báo cáo tuần')
p('Báo cáo tuần mô tả thiết kế ở tuần 3 và bắt đầu phát triển ở tuần 4; lịch CPM bắt đầu từ phân tích và cho một số hoạt động phát triển sớm hơn. Đây là hai cách trình bày cần thống nhất bằng ngày thực tế, không coi ngay các mục tuần là mốc baseline. Chỉ khi có ngày và trạng thái Jira mới kết luận chậm hoặc vượt tiến độ.')
p('Trong Jira, Epic → Story → Task/Sub-task thể hiện phân cấp công việc. To Do, In Progress, Review/Test và Done là trạng thái xử lý; không gộp hai khái niệm này thành một chuỗi trạng thái duy nhất.')
page('8 Phản biện và phản tư')
p('Các đáp án là phương án tham khảo để nhóm tự hoàn thiện bằng quyết định và bằng chứng của mình.')
qa=[('Lịch 37,02 ngày có chắc đáp ứng tám tuần không','Chỉ đáp ứng khi tám tuần có ít nhất 37,02 ngày làm việc phù hợp và nguồn lực không xung đột. Với giả định 40 ngày, còn 2,98 ngày dự phòng; phải trừ ngày nghỉ và xác nhận thời gian tham gia của từng thành viên.'),('Vì sao gọi là PERT khi chưa có O M P','Báo cáo chỉ cung cấp TE. Có thể kiểm tra CPM từ TE nhưng chưa kiểm tra được cách ước lượng PERT. Cần bổ sung ba điểm từ người thực hiện trước khi tính phương sai hoặc xác suất hoàn thành.'),('32,51 ngày có phải cam kết mới không','Đó là kịch bản tối ưu của các hoạt động G, J, N, O. Phép tính mạng khớp nhưng chưa chứng minh có đủ người, kỹ năng và thời gian hỗ trợ. Chỉ duyệt thành baseline sau khi san bằng nguồn lực và thống nhất khối lượng.'),('2.825.000 đồng có phải ngân sách dự án không','Không. Đó là tổng tổn thất kỳ vọng của sáu rủi ro giả định. Ngân sách còn cần công sức nhân sự, hosting, dịch vụ thanh toán và các chi phí khác theo đơn giá được thống nhất.'),('Có thể dùng Actual mẫu để kết luận tuần 4 hoàn thành phần lớn công việc không','Không. Cần số liệu Jira và bằng chứng kiểm thử tại một ngày chốt cụ thể. Chỉ đếm công việc đạt tiêu chí Done; giao diện hiển thị chưa đồng nghĩa với luồng đã tích hợp và nghiệm thu.')]
for i,(q,a) in enumerate(qa,1):h(f'Câu {i}  {q}');p(a)
h('Phản tư tham khảo')
p('AI giúp hệ thống hóa nội dung tuần 1–4, mở rộng WBS và tính lại lịch. Các điểm phải kiểm tra là thiếu O/M/P, giới hạn nguồn lực, ý nghĩa của số liệu Actual mẫu và EMV. Việc xác nhận tiến độ, chấp nhận phạm vi, phê duyệt chi phí và quyết định thu tiền thật cần do nhóm và người có thẩm quyền thực hiện.')
h('Hai ví dụ cải thiện mục tiêu')
p('“Giao diện dễ sử dụng” được cụ thể hóa thành luồng mua hàng và các ca nghiệm thu M1–M2. “Chạy ổn định trên trình duyệt phổ biến” được cụ thể hóa thành danh sách trình duyệt, thời điểm kiểm tra và yêu cầu xử lý lỗi ở M4. Các tiêu chí bổ sung cần được thống nhất trước khi dùng để đánh giá.')
page('8 Nhật ký AI và hoàn thiện hồ sơ')
table(['Phần','AI đã hỗ trợ trong bản này','Nhóm cần bổ sung'],[['Dữ liệu','Đọc báo cáo tuần 1–4 và chuyển nội dung sang dự án thư viện.','Xác nhận đề tài, tên Project và thành viên.'],['Charter','Soạn mục tiêu và phạm vi theo dữ liệu nguồn.','Ngân sách, ngày khởi động, người duyệt và quyết định phạm vi.'],['WBS','Mở rộng bảy nhánh thành gói cấp ba, ước lượng giờ và từ điển.','Kiểm tra khối lượng với người thực hiện.'],['Lịch','Tính ES, EF, LS, LF và Slack từ TE; kiểm tra hai kịch bản.','Bổ sung O/M/P; tính lại bằng Excel; san bằng nguồn lực.'],['Rủi ro','Kiểm tra EMV; mở rộng register và dự phòng.','Hai rủi ro nhóm tự bổ sung và bằng chứng theo dõi.'],['Phản biện','Soạn câu hỏi và lập luận tham khảo.','Tự viết câu trả lời và phản tư dựa trên hoạt động thật.']],[2.4,8,7])
h('Kết quả kiểm tra số liệu')
p(f'CPM cơ sở: {fmt(T)} ngày, khớp nguồn. CPM tối ưu: {fmt(OT)} ngày, khớp nguồn. Mức rút ngắn: {fmt(T-OT)} ngày. EMV: 2.825.000 đồng, khớp nguồn. Chưa có O/M/P để kiểm tra TE và chưa có dữ liệu Jira để xác nhận Actual.')
h('Công thức khi hoàn thiện file Excel')
p('TE = (O + 4M + P) / 6; phương sai = ((P − O) / 6)². Đối với CPM: ES lấy MAX của EF các tiền nhiệm; EF = ES + TE; LF lấy MIN của LS các hậu nhiệm; LS = LF − TE; Slack = LS − ES. Dùng dữ liệu đủ độ chính xác trong tính toán, chỉ làm tròn ở phần hiển thị.')
h('Danh sách cần hoàn thiện trước khi nộp')
p('□ Điền lớp và tên sáu thành viên.\n□ Thống nhất tên Project theo đề tài thư viện; chèn ảnh thật Instructions và Knowledge.\n□ Bổ sung O/M/P và file Excel có công thức, Gantt theo yêu cầu lab.\n□ Ghi ngày khởi động, lịch nghỉ và phân bổ nguồn lực.\n□ Thay Actual mẫu bằng kết quả Jira thật.\n□ Tự hoàn thiện phản biện, phản tư và nhật ký prompt đã dùng.')
h('Tài liệu căn cứ')
p('bao_cao_tuan_1_4.docx: dữ liệu dự án website bán hàng và thanh toán cho thư viện. Lab_QLDA_CNTT_Claude_Projects.docx: khung sản phẩm bài thực hành gồm Charter, WBS, lịch, rủi ro, phản biện và nhật ký AI. Các thông số của tình huống EduReg không được dùng làm ràng buộc cho dự án thư viện.')
dest=out/'QLDA_Nhom11_Lab.docx';doc.save(dest)
check=Document(dest);alltext='\n'.join(p.text for p in check.paragraphs)+'\n'+'\n'.join(c.text for t in check.tables for r in t.rows for c in r.cells)
assert '350 triệu' not in alltext and '500 người' not in alltext
assert T==Decimal('37.02') and OT==Decimal('32.51')
assert sum(Decimal(r.cells[1].text.rstrip('%'))/100*Decimal(r.cells[2].text.replace('.','').replace('đ','')) for r in source.tables[7].rows[1:])==Decimal(2825000)
print({'file':str(dest),'base_days':str(T),'optimized_days':str(OT),'effort_hours':sum(r[2] for r in packages),'tables':len(check.tables),'images':len(check.inline_shapes)})


