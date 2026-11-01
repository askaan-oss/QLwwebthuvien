from pathlib import Path
import re, unicodedata, json
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph
from PIL import Image
from PIL import ImageDraw, ImageFont
import math

ROOT=Path(r'D:\QL dự án nhóm'); W=ROOT/'work/report-final'; OUT=ROOT/'output/Bao_cao_cuoi_ky_Nhom11_hoan_thien.docx'
src=Document(W/'source.docx'); doc=Document()
sec=doc.sections[0]; sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.left_margin=Cm(3);sec.right_margin=Cm(2);sec.top_margin=Cm(2);sec.bottom_margin=Cm(2);sec.header_distance=Cm(.8);sec.footer_distance=Cm(.8)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 s=doc.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0);s.font.size=Pt(12.5)
 s.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Times New Roman')
n=doc.styles['Normal'].paragraph_format;n.space_after=Pt(5);n.line_spacing=1.15;n.widow_control=True
for st in doc.styles:
 for node in st.element.xpath('.//w:pBdr'):node.getparent().remove(node)
 if st.type==1:
  st.font.name='Times New Roman'
  for rf in st.element.xpath('.//w:rFonts'):
   for key in list(rf.attrib):
    if key.endswith('Theme'):del rf.attrib[key]
for k,size in [(1,15),(2,13.5),(3,12.5)]:
 s=doc.styles['Heading '+str(k)];s.font.size=Pt(size);s.font.bold=True;s.paragraph_format.space_before=Pt(12);s.paragraph_format.space_after=Pt(8);s.paragraph_format.keep_with_next=True
doc.styles['Heading 1'].paragraph_format.page_break_before=True
doc.styles['Caption'].font.size=Pt(11);doc.styles['Caption'].font.italic=True;doc.styles['Caption'].paragraph_format.space_after=Pt(8)
doc.styles['Title'].font.size=Pt(16);doc.styles['Title'].font.bold=True
for styname in ['TOC 1','TOC 2','TOC 3']:
 if styname not in doc.styles:
  doc.styles.add_style(styname,1)
 st=doc.styles[styname];st.font.name='Times New Roman';st.font.size=Pt(11)
 st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(2);st.paragraph_format.line_spacing=1
sec.different_first_page_header_footer=True
fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld)
doc.core_properties.title='Báo cáo cuối kỳ Website bán và thanh toán cho thư viện Libra'
doc.core_properties.author='Nhóm 11';doc.core_properties.subject='Quản lý dự án công nghệ thông tin'

def clean(t):
 t=unicodedata.normalize('NFC',t).strip().replace('\x0b','\n').replace('\x0c','')
 for a,b in [('Nguyễn Trướng Quốc Huy','Nguyễn Trương Quốc Huy'),('Chatbox','Chatbot'),('chatbox','chatbot'),('23dthc4','23DTHC4'),('[Anzio Vulcan 25]','Anzio Vulcan 25'),('mã hóa mật khẩu','băm mật khẩu'),('375000','375.000')]:t=t.replace(a,b)
 return t
def p(t='',style=None):
 z=doc.add_paragraph(clean(t),style);z.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY if not style else None;return z
def h(t,level=2):return p(t,'Heading '+str(level))
def cap(t):
 z=p(t,'Caption');z.alignment=WD_ALIGN_PARAGRAPH.CENTER;z.paragraph_format.keep_with_next=t.startswith('Bảng');return z
def pic(path,width=16,maxheight=19):
 im=Image.open(path);w,hg=im.size;width=min(width,maxheight*w/hg)
 if path.suffix.lower()!='.png':
  path=path.with_suffix('.converted.png');im.convert('RGB').save(path)
 z=p();z.alignment=WD_ALIGN_PARAGRAPH.CENTER;z.paragraph_format.keep_with_next=True;z.add_run().add_picture(str(path),width=Cm(width));return z
def tbl(rows,widths=None,size=10.5):
 rows=[[clean(str(c)) for c in r] for r in rows]; nc=len(rows[0]); widths=widths or ([16/nc]*nc)
 widths=[v*16/sum(widths) for v in widths]
 t=doc.add_table(rows=0,cols=nc);t.autofit=False
 for col,w in zip(t.columns,widths):col.width=Cm(w)
 for ri,row in enumerate(rows):
  cells=t.add_row().cells
  for ci,(c,txt) in enumerate(zip(cells,row)):
   c.width=Cm(widths[ci]);c.vertical_alignment=1
   tcpr=c._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
   for side,val in [('top',65),('bottom',65),('left',85),('right',85)]:
    e=OxmlElement('w:'+side);e.set(qn('w:w'),str(val));e.set(qn('w:type'),'dxa');m.append(e)
   tcpr.append(m)
   shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EDF2' if ri==0 else 'FFFFFF');tcpr.append(shade)
   z=c.paragraphs[0];z.text=txt;z.paragraph_format.space_after=Pt(0);z.paragraph_format.space_before=Pt(0);z.paragraph_format.line_spacing=1.05
   z.alignment=WD_ALIGN_PARAGRAPH.CENTER if (ri==0 or (ci==0 and len(txt)<8)) else WD_ALIGN_PARAGRAPH.LEFT
   z.paragraph_format.keep_with_next=ri==0
   for r in z.runs:r.font.size=Pt(size);r.bold=ri==0
  trpr=t.rows[-1]._tr.get_or_add_trPr();keep=OxmlElement('w:cantSplit');trpr.append(keep)
  if ri==0:
   e=OxmlElement('w:tblHeader');trpr.append(e)
 pr=t._tbl.tblPr;borders=OxmlElement('w:tblBorders')
 for edge in ['top','left','bottom','right','insideH','insideV']:
  e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
 pr.append(borders);p().paragraph_format.space_after=Pt(0)
 return t

# The cover retains the source institution, topic and verified group details.
for text,size,bold in [('BỘ GIÁO DỤC VÀ ĐÀO TẠO',13,False),('TRƯỜNG ĐẠI HỌC CÔNG NGHỆ TP HCM',14,True)]:
 z=p(text);z.alignment=1;z.runs[0].font.size=Pt(size);z.runs[0].bold=bold
pic(W/'rId8-image1.jpeg',4,3)
z=p('BÁO CÁO CUỐI KỲ','Title');z.alignment=1;z.runs[0].font.size=Pt(22);z.runs[0].bold=True;z.paragraph_format.space_before=Pt(20);z.paragraph_format.space_after=Pt(22)
z=p('WEBSITE BÁN VÀ THANH TOÁN\nCHO THƯ VIỆN LIBRA');z.alignment=1;z.runs[0].bold=True;z.runs[0].font.size=Pt(18);z.paragraph_format.space_after=Pt(28)
p('Giảng viên hướng dẫn: Nguyễn Hữu Trung').alignment=1
p('Nhóm 11  |  Anzio Vulcan 25  |  Lớp 23DTHC4').alignment=1
members=[[clean(c.text) for c in r.cells] for r in src.tables[1].rows]
tbl([['Họ và tên','MSSV']]+[[r[1],r[2]] for r in members[1:]],[10,6],12)
p('TP Hồ Chí Minh, năm 2026').alignment=1
z=h('MỤC LỤC',1);z.style='Title';z.paragraph_format.page_break_before=True
z=p();f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'TOC \\o "1-2" \\h \\z \\u');z._p.append(f)
z=h('DANH MỤC BẢNG VÀ HÌNH',1);z.style='Title';z.paragraph_format.page_break_before=True
z=p();f=OxmlElement('w:fldSimple');f.set(qn('w:instr'),'TOC \\h \\z \\t "Caption,1"');z._p.append(f)
h('TÓM TẮT BÁO CÁO',1)
p('Báo cáo trình bày quá trình quản lý dự án xây dựng website bán và thanh toán cho thư viện Libra của Nhóm 11. Nội dung gồm quản lý phạm vi, thời gian, chi phí, chất lượng, nhân sự, truyền thông, rủi ro và mua sắm; phần cuối mô tả sản phẩm, công nghệ, chức năng và giao diện thực tế.')
p('Libra hỗ trợ khách hàng tìm sách, đọc phần giới thiệu, quản lý giỏ hàng và đặt đơn thanh toán khi nhận hàng. Hệ thống có bốn vai trò Khách hàng, Nhân viên, Quản lý và Quản trị viên; bổ sung tư vấn sách, thống kê và thông báo trong website. Phiên bản trình bày sử dụng HTML, CSS, JavaScript, ASP.NET Core Web API .NET 8 và SQL Server.')
p('Ngân sách 143.000.000 đồng và bảng EVM được sử dụng trong bài toán quản lý dự án. Các chi phí minh họa được tách khỏi kết quả vận hành phần mềm; thanh toán trực tuyến qua cổng thanh toán chưa được bật trong phiên bản trình diễn.')

# Recalculate CPM from the exact predecessor table instead of retaining inconsistent diagrams.
names=['Khởi động','Phân tích yêu cầu','Thiết kế CSDL','Thiết kế UI','Thiết kế chatbot','Backend','Frontend','Chatbot và báo cáo','Kiểm thử tích hợp','Bàn giao']
dur=[6,11,5,3,2,16,13,5,8,5];pred=[[],[0],[1],[1],[1],[2],[3,5],[4,5],[6,7],[8]]
def cpm(ds,ps):
 es=[];ef=[]
 for i,d in enumerate(ds):es.append(max([ef[j] for j in ps[i]] or [0]));ef.append(es[-1]+d)
 lf=[max(ef)]*10;ls=[0]*10
 for i in range(9,-1,-1):
  nxt=[j for j in range(10) if i in ps[j]]
  lf[i]=min([ls[j] for j in nxt] or [max(ef)]);ls[i]=lf[i]-ds[i]
 return es,ef,ls,lf
base=cpm(dur,pred);optDur=dur.copy();optDur[8]=5;optDur[5]=11;optPred=[x.copy() for x in pred];optPred[6]=[2,3];opt=cpm(optDur,optPred)
assert max(base[1])==64 and max(opt[1])==48
def network(path,ds,ps,vals):
 pos={0:(120,260),1:(390,260),2:(660,260),3:(660,450),4:(660,70),5:(930,260),6:(1200,450),7:(1200,70),8:(1470,260),9:(1740,260)}
 im=Image.new('RGB',(1880,530),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
 for j,pre in enumerate(ps):
  for i in pre:
   x,y=pos[i];xx,yy=pos[j];start=(x+105,y);end=(xx-105,yy);dr.line([start,end],fill='#77808A',width=3)
   ang=math.atan2(end[1]-start[1],end[0]-start[0]);dr.polygon([end,(end[0]-14*math.cos(ang-.4),end[1]-14*math.sin(ang-.4)),(end[0]-14*math.cos(ang+.4),end[1]-14*math.sin(ang+.4))],fill='#77808A')
 for i,(x,y) in pos.items():
  critical=vals[2][i]==vals[0][i];dr.rounded_rectangle((x-105,y-50,x+105,y+50),12,fill='#FFF0DA' if critical else '#F0F3F6',outline='#B66B13' if critical else '#8693A0',width=2)
  dr.text((x,y-24),f'N{i+1} | {ds[i]} ngày',font=font,fill='black',anchor='mm');dr.text((x,y+20),f'ES {vals[0][i]}  EF {vals[1][i]}',font=font,fill='black',anchor='mm')
 im.save(path)
network(W/'cpm-base.png',dur,pred,base);network(W/'cpm-opt.png',optDur,optPred,opt)
im=Image.new('RGB',(1800,1000),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
for day in range(0,65,4):
 x=450+day*20;dr.line((x,70,x,875),fill='#DDDDDD',width=2);dr.text((x,905),str(day),font=font,fill='black',anchor='mm')
for i in range(10):
 y=100+i*76;dr.text((20,y+15),f'N{i+1} {names[i]}',font=font,fill='black');dr.rectangle((450+base[0][i]*20,y,450+base[1][i]*20,y+24),fill='#919CB0');dr.rectangle((450+opt[0][i]*20,y+29,450+opt[1][i]*20,y+53),fill='#EBA74E')
dr.text((450,15),'Xám: mạng gốc 64 ngày     Cam: phương án 48 ngày',font=font,fill='black');dr.text((700,950),'Ngày làm việc tính từ thời điểm bắt đầu',font=font,fill='black');im.save(W/'gantt-corrected.png')

def chapter3():
 h('CHƯƠNG 3 QUẢN LÝ THỜI GIAN DỰ ÁN',1)
 h('3.1 Cơ sở lập lịch')
 p('Mốc mục tiêu của dự án là từ 07/09/2026 đến 31/10/2026. Với lịch làm việc từ thứ Hai đến thứ Bảy và nghỉ Chủ nhật, khoảng thời gian này có 48 ngày làm việc. WBS ở Chương 2, mạng CPM điều chỉnh và bảng chi phí ở Chương 4 dùng chung lịch cơ sở 48 ngày. Mạng 64 ngày chỉ được giữ để so sánh phương án trước điều chỉnh.')
 p('Các thời lượng N1–N10 là ước lượng một giá trị. Vì chưa có bộ ba ước lượng lạc quan, khả dĩ và bi quan, báo cáo sử dụng phương pháp đường găng CPM trên sơ đồ mạng công việc; không tính phương sai hay xác suất hoàn thành theo PERT.')
 h('3.2 Mạng công việc ban đầu')
 tbl([['Mã','Gói công việc','Tiền nhiệm','Ngày']]+[[f'N{i+1}',names[i],', '.join(f'N{j+1}' for j in pred[i]) or 'Không',str(dur[i])] for i in range(10)],[1.2,8,4.8,2])
 pic(W/'cpm-base.png');cap('Hình 3.1 Mạng công việc ban đầu và thời điểm bắt đầu kết thúc sớm')
 p('Theo quan hệ N7 phải đợi cả N4 và N6, thời gian hoàn thành của mạng gốc là 64 ngày, vượt mục tiêu 48 ngày. Đường găng là N1 → N2 → N3 → N6 → N7 → N9 → N10. Tổng 74 ngày là tổng thời lượng của mọi hoạt động, không phải độ dài đường găng.')
 tbl([['Đường','Chuỗi công việc','Tổng ngày']]+[[str(i+1),s,str(v)] for i,(s,v) in enumerate([('N1 → N2 → N3 → N6 → N7 → N9 → N10',64),('N1 → N2 → N3 → N6 → N8 → N9 → N10',56),('N1 → N2 → N4 → N7 → N9 → N10',46),('N1 → N2 → N5 → N8 → N9 → N10',37)])],[1.3,12.7,2])
 h('3.3 Tính tiến và tính lùi')
 p('Tính tiến: ES của hoạt động bằng EF lớn nhất của các tiền nhiệm; EF = ES + thời lượng. Tính lùi: LF bằng LS nhỏ nhất của các công việc kế tiếp; LS = LF − thời lượng. Độ dự trữ toàn phần TF = LS − ES; hoạt động có TF bằng 0 thuộc đường găng. Mốc đầu tiên được quy ước bằng ngày 0.')
 tbl([['Mã','Ngày','ES','EF','LS','LF','TF']]+[[f'N{i+1}',dur[i],base[0][i],base[1][i],base[2][i],base[3][i],base[2][i]-base[0][i]] for i in range(10)],[2,2,2.4,2.4,2.4,2.4,2.4])
 h('3.4 Phương án đáp ứng mục tiêu 48 ngày')
 p('Phương án đề xuất gồm ba điều chỉnh: cho N7 phát triển giao diện sau N3 và N4 bằng hợp đồng API đã thống nhất, dữ liệu mô phỏng và các đầu API bàn giao từng phần; rút N6 từ 16 xuống 11 ngày nhờ tái sử dụng các mô-đun đã có và chốt hợp đồng API sớm; đồng thời rút N9 từ 8 xuống 5 ngày nhờ thực hiện kiểm thử từng chức năng trong giai đoạn phát triển. N9 vẫn chờ cả N7 và N8 để kiểm thử tích hợp cuối cùng.')
 p('Đây là phương án kế hoạch, không phải xác nhận đã rút ngắn tiến độ thực tế. PM cần kiểm tra năng lực nhân sự, phạm vi kiểm thử và phê duyệt thay đổi trước khi áp dụng. N7 không còn đợi hoàn tất toàn bộ N6; nếu API thay đổi nhiều, lợi ích chạy song song có thể bị mất do phải làm lại.')
 tbl([['Chỉ tiêu','Mạng gốc','Phương án đề xuất'],['Tiền nhiệm N7','N4 và N6','N3 và N4'],['Thời lượng N6','16 ngày','11 ngày'],['Thời lượng N9','8 ngày','5 ngày'],['Tổng thời lượng hoạt động','74 ngày','66 ngày'],['Thời gian hoàn thành','64 ngày','48 ngày'],['Đường găng','N1 N2 N3 N6 N7 N9 N10','N1 N2 N3 N6 N8 N9 N10']],[5.5,5.25,5.25])
 pic(W/'cpm-opt.png');cap('Hình 3.2 Mạng công việc theo phương án 48 ngày')
 tbl([['Mã','Ngày','ES','EF','LS','LF','TF']]+[[f'N{i+1}',optDur[i],opt[0][i],opt[1][i],opt[2][i],opt[3][i],opt[2][i]-opt[0][i]] for i in range(10)],[2,2,2.4,2.4,2.4,2.4,2.4])
 p('Theo mô hình đã điều chỉnh, thời gian hoàn thành giảm 16 ngày làm việc, từ 64 xuống 48 ngày. Đường găng chuyển qua N8; do đó cần theo dõi sát việc hoàn tất Backend, tích hợp chatbot và báo cáo trước kiểm thử cuối cùng. Lịch WBS chi tiết đã được quy đổi theo cùng ES và EF của phương án 48 ngày; ngày kết thúc được tính bao gồm ngày làm việc cuối cùng của gói.')

replacements={
 256:'Bảng 4.2 sử dụng một kịch bản minh họa tại mốc bàn giao dự kiến 31/10/2026: toàn bộ N1–N10 hoàn thành 100%. Các khoản AC trong bảng là số liệu minh họa phục vụ tính EVM, không phải xác nhận số tiền thực chi hay biên bản nghiệm thu.',
 255:'4.2 Kịch bản chi phí tại mốc bàn giao dự kiến',257:'Bảng 4.2 Chi phí minh họa tại mốc 31/10/2026',
 271:'EV (BCWP) = Ngân sách công việc × Tỷ lệ hoàn thành thực tế',272:'CPI = EV / AC;     CV = EV − AC',273:'SPI = EV / PV;     SV = EV − PV',
 274:'Bảng 4.3 Các chỉ số EVM theo kịch bản minh họa',
 282:'4.4 Sơ đồ Gantt đối chiếu hai phương án',
 283:'Sơ đồ Gantt dưới đây dùng các giá trị ES và thời lượng đã tính tại Chương 3. Màu xám thể hiện mạng gốc 64 ngày; màu cam thể hiện phương án 48 ngày. Các thanh là lịch kế hoạch, không phải dữ liệu thực tế đã đo.',
 292:'Hình 4.1 So sánh lịch công việc gốc và phương án 48 ngày',
 294:'4.5 Kết luận chương',
 296:'Theo kịch bản minh họa, EV = PV = 132.000.000 đồng và AC = 127.100.000 đồng. Các chỉ số được diễn giải như sau:',
 297:'CPI ≈ 1,04 và CV = 4.900.000 đồng: chi phí của kịch bản thấp hơn ngân sách tương ứng. Đây chưa phải bằng chứng nhóm đã tiết kiệm chi phí thực tế.',
 298:'SPI = 1,00 và SV = 0: khối lượng hoàn thành bằng kế hoạch tại mốc chốt của kịch bản. SPI bằng 1 ở cuối dự án không tự chứng minh dự án đã bàn giao đúng ngày.',
 299:'Để nghiệm thu về tiến độ và chi phí, cần đối chiếu ngày hoàn tất thực tế, chứng từ chi phí, phạm vi được chấp nhận và lịch cơ sở đã phê duyệt.',
 301:'Ngân sách 143.000.000 đồng gồm 132.000.000 đồng phân bổ cho công việc và 11.000.000 đồng dự phòng. Sau điều chỉnh tiến độ, nhóm phải rà soát lại phân bổ nguồn lực và chi phí; không mặc định rút ngắn thời gian sẽ làm giảm tổng chi phí.',
 366:'Bảng 6.3 là biểu mẫu chấm điểm theo trọng số. Các ô để trống chờ nhóm thống nhất điểm dựa trên kết quả công việc; không tự suy diễn điểm cá nhân từ phân công.',
 403:'7.6 Đề xuất trợ lý AI hỗ trợ truyền thông trên Zalo',
 405:'Đây là đề xuất trong kế hoạch truyền thông, chưa phải chức năng đã tích hợp trong website Libra. Trợ lý chỉ soạn thông báo từ WBS; việc gửi tự động cần kênh kết nối phù hợp và quyền do người quản lý cấp.',
 467:'7.7 Kết luận chương',
}
skip=set(range(284,291))|{293,300}
widthmap={1:[1.2,7,4.3,3.5],2:[5.5,10.5],3:[5,2.3,1.3,3.2,4.2],4:[8.2,1.8,3,3],5:[1.3,5.6,1.2,2.7,2.6,2.6],6:[8,8],7:[1.2,14.8],8:[1.2,3,11.8],9:[1.2,8.6,2.2,4],10:[6,10],11:[6,10],12:[1,3.2,4,7.8],13:[8,8],14:[1.5,7.1,2.2,2.6,2.6],22:[1.5,8,4.5,2],25:[5,2.2,1.6,3.2,4],26:[7,3,6],27:[1,2.5,2.5,2.5,1.3,2.2,1.3,2.7],28:[1,4,11],29:[1,4.5,7.5,3],30:[2.5,8,5.5],31:[1,4.2,3.3,7.5],32:[1,4,9,2],33:[1.5,3.5,11],34:[7,9],35:[5,2.2,1.7,1.9,1.9,1.9,1.4],36:[4,4,8],37:[4.5,5,6.5],38:[5,3.3,3.2,4.5],39:[6,10],40:[1.3,4.4,5.3,5],41:[2,6,8],42:[1,6.5,2,2,1.5,3],43:[1.3,5,9.7],44:[1,4,7,4],45:[4,12],46:[4.7,3.4,3,4.9]}
for i in range(15,22):widthmap[i]=[1.3,6.4,1.8,1.8,1.8,2.9]

from datetime import date, timedelta
calendar=[]
day=date(2026,9,7)
while len(calendar)<48:
 if day.weekday()!=6:calendar.append(day)
 day+=timedelta(days=1)
assert calendar[-1]==date(2026,10,31)
def dt(n):return calendar[n].strftime('%d/%m/%Y')
def pre(i):return ', '.join(f'N{j+1}' for j in optPred[i]) or 'Không'
# One schedule controls WBS, milestones, dependencies and cost durations.
roles=['PM','BA','BE','FE','BA','BE','FE','BE/BA','QA/Dev','PM/QA/Dev']
groups=[[0],[1],[2,3,4],[5],[6],[7,8],[9]]
custom={}
custom[8]=[['Mốc','Ngày hoàn thành','Nội dung']]+[[f'M{i+1}',dt(opt[1][n]-1),names[n]] for i,n in enumerate([0,1,2,5,6,7,8,9])]
custom[10]=[['Công việc','Phụ thuộc']]+[[f'N{i+1} – {names[i]}',pre(i)] for i in range(10)]
custom[14]=[['Mã WBS','Nhóm công việc','Thời lượng','Bắt đầu','Kết thúc']]
labels=['Khởi động và lập kế hoạch','Phân tích yêu cầu','Thiết kế hệ thống','Phát triển Backend','Phát triển Frontend','Tích hợp AI, báo cáo và kiểm thử','Triển khai và bàn giao']
for g,ns in enumerate(groups):
 a=min(opt[0][i] for i in ns);b=max(opt[1][i] for i in ns)
 custom[14].append([f'{g+1}.0',labels[g],f'{b-a} ngày',dt(a),dt(b-1)])
# Subtasks partition each node sequentially; design streams use different owners.
parts=[[(2,'Khởi động và thống nhất phạm vi'),(2,'Lập và chốt Project Charter'),(2,'Lập kế hoạch và phân công')],[(3,'Khảo sát và thu thập yêu cầu'),(3,'Phân tích nghiệp vụ và Use Case'),(2,'Phân tích yêu cầu AI'),(3,'Hoàn thiện và chốt SRS')],[(2,'Thiết kế kiến trúc và dữ liệu'),(3,'Thiết kế CSDL và hợp đồng API')],[(3,'Thiết kế giao diện khách hàng và quản trị')],[(2,'Thiết kế luồng chatbot và báo cáo')],[(2,'Khởi tạo API, CSDL và xác thực'),(2,'API sách, danh mục và tìm kiếm'),(2,'Giỏ hàng, địa chỉ và yêu thích'),(3,'Đơn hàng COD, tồn kho và phân quyền'),(2,'Thông báo, kiểm thử mô-đun và hoàn thiện API')],[(2,'Khung giao diện và đăng nhập'),(3,'Danh mục, tìm kiếm, chi tiết và đọc thử'),(3,'Giỏ hàng, địa chỉ và đặt hàng COD'),(3,'Đơn hàng và trang theo vai trò'),(2,'Hoàn thiện giao diện và kiểm thử mô-đun')],[(3,'Tích hợp chatbot với dữ liệu sách'),(2,'Tích hợp dashboard, thông báo và báo cáo')],[(2,'Kiểm thử tích hợp và luồng COD'),(2,'Kiểm thử phân quyền, sửa lỗi và hồi quy'),(1,'Kiểm tra sẵn sàng nghiệm thu')],[(2,'Chuẩn bị triển khai và tài liệu'),(2,'Triển khai, hướng dẫn sử dụng'),(1,'Nghiệm thu và bàn giao')]]
for g,ns in enumerate(groups):
 rows=[['Mã WBS','Công việc / CPM','Thời lượng','Bắt đầu','Kết thúc','Phụ trách']];k=0
 for i in ns:
  start=opt[0][i]
  assert sum(x[0] for x in parts[i])==optDur[i]
  for duration,title in parts[i]:
   k+=1;rows.append([f'{g+1}.{k}',f'N{i+1}: {title}',f'{duration} ngày',dt(start),dt(start+duration-1),roles[i]]);start+=duration
 custom[15+g]=rows
replacements[301]='Ngân sách công việc giữ ở mức 132.000.000 đồng theo gói, không giảm tự động theo thời lượng. Trong kịch bản quyết toán: chi phí thực hiện 127.100.000 đồng; chênh lệch 4.900.000 đồng được dành làm thưởng cho nhân sự sau nghiệm thu. Tổng chi phí gồm thưởng là 132.000.000 đồng, còn 11.000.000 đồng dự phòng chưa sử dụng. Không cộng khoản thưởng thêm một lần vào ngân sách 143.000.000 đồng. Việc chia thưởng theo cá nhân chờ nhóm thống nhất; báo cáo chưa ghi nhận đã chi thưởng thực tế.'
replacements[297]='Trước thưởng: CPI ≈ 1,04 và CV = 4.900.000 đồng. Khoản chênh lệch này được phân bổ làm thưởng nhân sự sau nghiệm thu. Sau tính đủ thưởng, tổng chi phí là 132.000.000 đồng, CPI = 1,00 và CV = 0. Bảng EVM trình bày trạng thái trước thưởng; đây là kịch bản minh họa.'

pi=-1;ti=-1;chapter=0
for el in src.element.body:
 if el.tag==qn('w:p'):
  pi+=1;sp=Paragraph(el,src);text=clean(sp.text)
  if pi<33:continue
  if pi==226:chapter3()
  if 226<=pi<249:continue
  if pi>=532:break
  if pi in skip:continue
  text=replacements.get(pi,text)
  if text.startswith('Người viết (Prepared by):'):text='Người lập: Nhóm 11; đại diện nhóm: Nguyễn Trương Quốc Huy.'
  if text.startswith('Bảng 1.2.'):text=text.replace('Bảng 1.2.','Bảng 1.1.',1)
  if pi==291:pic(W/'gantt-corrected.png');continue
  ids=[x.get(qn('r:id')) for x in sp._p.xpath('.//*[local-name()="imagedata"]')]
  if ids:
   for rid in ids:
    r=src.part.rels[rid];pic(W/(rid+'-'+Path(r.target_ref).name),16,15)
   if pi==73:cap('Hình 2.1 Quy trình xem xét yêu cầu thay đổi')
  if not text:continue
  if text.startswith('Ghi chú: Thời lượng 74'):
   text='Ghi chú: Tổng 66 ngày là tổng thời lượng các hoạt động chạy nối tiếp hoặc song song; lịch dự án dài 48 ngày làm việc. Ngân sách 132.000.000 đồng phân bổ theo gói và bao gồm nguồn lực quản lý xuyên suốt; chi phí bình quân/ngày chỉ là tỷ số ngân sách gói trên thời lượng, được làm tròn đến đồng.'
  if re.match(r'^[1-7]\.0[. ]',text):
   n=int(text[0]);text=f'{n}.0. {labels[n-1]}'
  if text.startswith('CHƯƠNG'):
   chapter=int(re.search(r'\d+',text).group());h(text.replace('.','',1),1)
  elif re.match(r'^'+str(chapter)+r'\.[1-9]\d*(?:\.\d+)?[. ]',text):
   depth=3 if re.match(r'^\d+\.\d+\.\d+',text) else 2
   h(re.sub(r'^(\d+(?:\.\d+)+)\.?\s*',r'\1 ',text),depth)
  elif re.match(r'^(Bảng|Hình) \d',text) and len(text)<110:cap(text)
  else:p(text)
  if pi==48:p('Các biểu phí, điều khoản hợp đồng và mốc phê duyệt trong chương này phục vụ tình huống quản lý dự án của học phần. Việc ký kết, thanh toán và nghiệm thu thực tế được xác lập bằng hồ sơ riêng.')
  if pi==53:p('Đơn giá và chi phí dưới đây là dự toán của bài toán; chưa phản ánh khoản thanh toán thực tế.')
 elif el.tag==qn('w:tbl'):
  ti+=1
  if ti==0 or 22<=ti<=24:continue
  if ti>=47:break
  st=Table(el,src);rows=[[clean(c.text) for c in r.cells] for r in st.rows]
  if ti==12:rows=[r[:4] for r in rows]
  if ti in [6,13]:
   for row in rows:
    for k,v in enumerate(row):
     if '<Chữ Ký>' in v:row[k]='Ký và ghi rõ họ tên'
     if v.startswith('Ngày ký:'):row[k]='Ngày dự kiến xác nhận: '+v.split(':',1)[1].strip()
  if ti==25:
   rows[0]=['Hoạt động','Tiền nhiệm','Ngày','Bình quân/ngày','Ngân sách đồng']
   for i in range(10):
    rows[i+1][1]=pre(i);rows[i+1][2]=str(optDur[i]);budget=int(rows[i+1][4].replace('.',''));rows[i+1][3]=f'{round(budget/optDur[i]):,}'.replace(',','.')
   rows[-1][2]='66'
  if ti in custom:rows=custom[ti]
  if ti in [6,13]:
   for row in rows:
    for k,v in enumerate(row):
     if v.startswith('Ngày dự kiến xác nhận:'):row[k]='Ngày dự kiến xác nhận: 07/09/2026'
  if ti==26:rows[0]=['Hoạt động','Hoàn thành giả định','Chi phí minh họa đồng']
  if ti==27:
   rows[0]=['Mã','AC','EV','PV','CPI','CV','SPI','SV']
   for row in rows[1:]:
    for k in [1,2,3,5,7]:row[k]=f'{int(row[k].replace(".",""))/1000000:.1f}'.replace('.',',')
   rows[-1][0]='Tổng';p('Đơn vị AC, EV, PV, CV và SV: triệu đồng; CPI và SPI là tỷ số.');widthmap[27]=[1.4,2.4,2.4,2.4,1.7,2,1.7,2]
  if ti==28:rows[5][2]='Quản lý thêm sách, sửa giá và tồn kho; Quản trị viên quản lý tài khoản và phân quyền.'
  if ti==29:rows[3][2]='Kiểm tra thêm sách, sửa giá và tồn kho trên giao diện; kiểm tra cập nhật đầy đủ và ngừng kinh doanh qua API.'
  if ti==35:
   rows[0]=['Thành viên','Công việc\n30%','Tiến độ\n25%','Chất lượng\n20%','Trách nhiệm\n15%','Phối hợp\n10%','Tổng']
   rows=[rows[0]]+[[r[0]]+['']*6 for r in rows[1:]]
  if ti in range(15,22):widthmap[ti]=[1.2,6.2,1.5,2.3,2.3,2.5]
  tbl(rows,widthmap.get(ti),10 if len(rows[0])>=5 else 11)
  if ti==14:p('Các ngày được tính theo lịch thứ Hai đến thứ Bảy, nghỉ Chủ nhật. N1 là gói khởi động; PM vẫn theo dõi, quản lý thay đổi và chi phí xuyên suốt 48 ngày trong định mức nhân sự Chương 1. N3, N4 và N5 được giao cho BE, FE và BA để triển khai song song. Đây là lịch kế hoạch điều chỉnh, không phải nhật ký hoàn tất thực tế.')
  if ti==25:p('Ngân sách gói được giữ nguyên khi rút lịch; chi phí bình quân/ngày được tính lại theo thời lượng điều chỉnh. Bảng nhân sự và dịch vụ ở Chương 1 là cách phân loại cùng tổng ngân sách, không phải khoản cộng thêm.')

# Product chapter is rewritten against the actual frontend and backend.
h('CHƯƠNG 10 TRÌNH BÀY SẢN PHẨM LIBRA',1)
h('10.1 Tổng quan sản phẩm')
p('Libra là website bán sách trực tuyến hỗ trợ khách hàng tìm kiếm và chọn sách, đọc phần giới thiệu, lưu sách yêu thích, quản lý giỏ hàng, địa chỉ giao hàng và đơn hàng. Luồng giao dịch chính của phiên bản trình diễn là đặt hàng và thanh toán khi nhận hàng (COD). Tạo đơn COD là ghi nhận yêu cầu mua hàng, chưa đồng nghĩa với việc đã thu tiền.')
p('Hệ thống tách giao diện và máy chủ nghiệp vụ, dùng SQL Server để lưu dữ liệu. Danh mục trình diễn có 70 sản phẩm. Phân quyền được áp dụng cho bốn vai trò: Customer, Staff, Manager và Admin. Các hình ở mục 10.6 được chụp trực tiếp từ phiên bản chạy trên máy tính ngày 30/10/2026.')
h('10.2 Công nghệ sử dụng')
tbl([['Thành phần','Công nghệ','Vai trò'],['Giao diện','HTML5, CSS3, JavaScript thuần','Xây dựng trang và xử lý thao tác; không sử dụng React hoặc Vue.'],['Bố cục','Grid, Flexbox, media queries','Điều chỉnh giao diện theo kích thước màn hình.'],['Máy chủ giao diện','Node.js','Phục vụ các tệp giao diện trong môi trường cục bộ.'],['Backend','C#, ASP.NET Core Web API .NET 8','Cung cấp REST API và kiểm soát nghiệp vụ.'],['Truy xuất dữ liệu','Entity Framework Core 8','Ánh xạ mô hình và làm việc với SQL Server.'],['Cơ sở dữ liệu','Microsoft SQL Server','Lưu tài khoản, sách, giỏ hàng, đơn hàng và thông báo.'],['Giao tiếp','Fetch API, REST, JSON','Trao đổi dữ liệu giữa giao diện và backend.'],['Xác thực','JWT Bearer, BCrypt','Xác thực phiên, kiểm tra quyền và băm mật khẩu.'],['Tư vấn sách','Dịch vụ Gemini và bộ gợi ý cục bộ','Tư vấn dựa trên danh mục; dùng phương án cục bộ khi dịch vụ AI không sẵn sàng.'],['Công cụ','Visual Studio, Swagger, bộ kiểm thử Node.js','Phát triển backend, tra cứu API và kiểm thử tự động.']],[3,5.3,7.7],10.5)
h('10.3 Chức năng và phân quyền')
h('10.3.1 Chức năng dành cho khách hàng',3)
tbl([['Nhóm chức năng','Nội dung'],['Tài khoản','Đăng ký, đăng nhập, đăng xuất; điều hướng theo vai trò và xử lý phiên hết hạn.'],['Khám phá sách','Trang chủ, danh sách, tìm tên sách hoặc tác giả, lọc danh mục và giá tối đa, phân trang, chi tiết và sách liên quan.'],['Đọc thử','Mở nội dung giới thiệu hoặc đoạn xem trước. Backend kiểm tra quyền trước khi cung cấp nội dung được mở khóa.'],['Yêu thích','Lưu hoặc bỏ sách trong danh sách yêu thích theo tài khoản.'],['Giỏ hàng','Thêm sách, tăng giảm số lượng, xóa, chọn từng sách hoặc chọn tất cả; chỉ thanh toán các sách đã chọn.'],['Địa chỉ','Thêm, sửa, xóa địa chỉ và chọn địa chỉ mặc định.'],['Ưu đãi và COD','Áp dụng mã phù hợp, tính phí giao hàng, xem tổng tiền và xác nhận đơn COD.'],['Đơn hàng','Xem lịch sử, chi tiết và trạng thái; hủy khi trạng thái cho phép.'],['Tư vấn sách','Gửi câu hỏi về nhu cầu đọc; xem gợi ý và mở chi tiết sản phẩm liên quan.'],['Thông báo','Xem thông báo theo tài khoản, số chưa đọc; đánh dấu từng thông báo hoặc đọc tất cả.']],[3.4,12.6],11)
h('10.3.2 Chức năng dành cho nhân sự vận hành',3)
tbl([['Vai trò','Chức năng chính','Trang'],['Nhân viên Staff','Xem và lọc đơn hàng; cập nhật trạng thái theo quyền; xem tồn kho.','Nhân viên'],['Quản lý Manager','Xử lý đơn; thêm sách; cập nhật giá và tồn kho; xem thống kê.','Quản lý và Thống kê'],['Quản trị viên Admin','Quản lý tài khoản, trạng thái hoạt động và vai trò; truy cập các chức năng quản lý.','Quản trị, Quản lý và Thống kê']],[3,9.5,3.5],11)
p('Giao diện ẩn chức năng không thuộc quyền của người dùng; backend vẫn phải kiểm tra quyền của từng yêu cầu. Customer và Staff không được truy cập dashboard; danh sách và phân quyền tài khoản thuộc Admin. Một số chức năng có API nhưng chưa có biểu mẫu riêng trên giao diện, như sửa đầy đủ thông tin sách, ngừng kinh doanh sách và quản lý nội dung điện tử.')
h('10.3.3 Thống kê và thông báo',3)
p('Dashboard dành cho Manager và Admin, gồm các chỉ số doanh thu, số đơn hàng, khách hàng, sách bán chạy và sách tồn kho thấp; có bộ lọc khoảng thời gian. Thông báo được tải từ backend theo tài khoản, cập nhật định kỳ và hỗ trợ đánh dấu đã đọc. Đây là thông báo trong website, chưa triển khai thông báo đẩy, email hay SMS.')
h('10.4 Quy trình xử lý nghiệp vụ')
for s in ['1. Khách hàng tìm sách, xem chi tiết hoặc nội dung đọc thử và thêm sách vào giỏ.','2. Trong giỏ hàng, khách chọn các sản phẩm cần mua, sửa số lượng và nhập mã ưu đãi nếu có.','3. Backend tính lại giá, mức giảm và phí vận chuyển. Khách kiểm tra địa chỉ giao hàng, chọn COD và xác nhận.','4. Hệ thống lưu đơn hàng; nhân viên tiếp nhận và chuyển trạng thái theo quy trình xử lý.','5. Khách theo dõi đơn hàng và thông báo. Đơn COD đủ điều kiện hoàn tất mới được dùng để xác định quyền đọc nội dung đã mua.']:
 p(s)
p('Với tư vấn sách, backend tìm các sản phẩm đang cung cấp theo chủ đề, tên sách hoặc tác giả rồi tạo câu trả lời. Dữ liệu gợi ý lấy từ danh mục của Libra. Khi không gọi được dịch vụ AI, bộ gợi ý cục bộ trả lời theo dữ liệu đã lọc; hệ thống không mặc định có thông tin đầy đủ về mọi sách trên thị trường.')
h('10.5 Kiến trúc và dữ liệu')
p('Luồng chính: Trình duyệt → REST API → lớp xử lý nghiệp vụ → Entity Framework Core → SQL Server. Backend xác thực JWT, phân quyền, kiểm tra dữ liệu và xử lý đơn hàng. API key của dịch vụ AI nằm ở backend, không đưa vào mã JavaScript phía khách hàng.')
tbl([['Nhóm dữ liệu','Mục đích'],['Tài khoản và địa chỉ','Xác định người dùng, vai trò, trạng thái và thông tin giao hàng.'],['Sách và nội dung','Lưu thông tin sản phẩm, giá, ảnh bìa, tồn kho; cung cấp phần xem trước và nội dung theo quyền.'],['Giỏ hàng và yêu thích','Lưu lựa chọn mua và danh sách quan tâm theo tài khoản.'],['Đơn hàng và chi tiết','Ghi nhận sách, số lượng, đơn giá, phí giao hàng, giảm giá và trạng thái.'],['Thông báo','Lưu nội dung, người nhận, trạng thái đọc và thời điểm tạo.']],[4.5,11.5],11)
h('10.6 Giao diện sản phẩm')
p('Các màn hình sau minh họa giao diện và dữ liệu của phiên bản trình diễn. Ảnh chụp không thay thế biên bản kiểm thử hoặc xác nhận đã hoàn thành giao dịch thực tế.')
figures=[
 ('home','Trang chủ','Trang chủ sử dụng tông xanh đậm và cam, trình bày lời giới thiệu, lối vào danh mục và các nhóm sách. Thanh tìm kiếm và điều hướng giúp người dùng chuyển nhanh đến khu vực cần sử dụng.'),
 ('catalog','Danh sách sách','Danh sách hiển thị bìa, tác giả, giá và các thao tác mua sách. Bộ lọc hỗ trợ danh mục và mức giá tối đa; phân trang giúp giảm số lượng sản phẩm hiển thị mỗi lần.'),
 ('detail','Chi tiết sách','Màn hình chi tiết trình bày thông tin sản phẩm và nút thêm vào giỏ hàng. Người dùng có thể chuyển xuống phần đọc thử trước khi quyết định mua.'),
 ('preview','Nội dung đọc thử','Phần đọc thử lấy dữ liệu từ backend. Nội dung giới thiệu được gắn nhãn để phân biệt với trích đoạn nguyên tác; chỉ những nội dung thực sự đã nạp mới có thể cung cấp cho người mua.'),
 ('login','Đăng nhập','Người dùng đăng nhập bằng email và mật khẩu. Hệ thống xác định vai trò từ tài khoản; khách hàng không được tự chọn hoặc tự cấp quyền quản trị khi đăng ký.'),
 ('cart','Giỏ hàng','Khách hàng chọn từng sách hoặc toàn bộ giỏ, điều chỉnh số lượng, xóa sách và áp dụng mã ưu đãi. Tổng tiền phản ánh các sản phẩm được chọn; sách chưa chọn được giữ lại trong giỏ.'),
 ('checkout','Đặt hàng COD','Màn hình đặt hàng yêu cầu thông tin nhận hàng, phương thức COD và xác nhận kiểm tra dữ liệu. Tổng tiền được đối chiếu với backend trước khi tạo đơn; ảnh chỉ minh họa bước nhập thông tin.'),
 ('manager','Trang quản lý','Khu vực quản lý cung cấp thao tác thêm sách và chỉnh sửa giá, số lượng tồn kho. Dữ liệu được gửi tới backend và phải vượt qua kiểm tra quyền Manager hoặc Admin.'),
 ('admin','Trang quản trị tài khoản','Quản trị viên xem danh sách tài khoản, thay đổi vai trò và trạng thái hoạt động theo quyền. Chức năng này không được cấp cho tài khoản Khách hàng, Nhân viên hoặc Quản lý.'),
 ('dashboard','Dashboard thống kê','Dashboard tổng hợp các chỉ số theo khoảng thời gian được chọn. Dữ liệu doanh thu cần đọc cùng điều kiện trạng thái đơn hàng; đơn vừa tạo không đồng nghĩa đã thu được tiền.'),
 ('ai','Tư vấn sách','Cửa sổ tư vấn cho phép nhập nhu cầu đọc và mở các sách được gợi ý. Trong môi trường trình diễn, câu trả lời có thể do bộ gợi ý cục bộ cung cấp khi dịch vụ AI bên ngoài không sẵn sàng.'),
 ('notifications','Thông báo trong website','Bảng thông báo cung cấp trạng thái chưa đọc, nút tải lại và đọc tất cả. Khi tài khoản chưa phát sinh sự kiện, giao diện hiển thị trạng thái chưa có thông báo.')]
for i,(file,title,desc) in enumerate(figures,1):
 z=h(f'10.6.{i} {title}',3)
 z.paragraph_format.page_break_before=True
 p(desc)
 pic(W/(file+'.png'),16,18)
 cap(f'Hình 10.{i} {title} trên website Libra')
h('10.7 Kết quả và phạm vi kiểm chứng')
p('Phiên bản hiện có đã xây dựng giao diện khách hàng, các trang theo vai trò và các API nghiệp vụ chính. Luồng truy cập danh mục, đăng nhập, phân quyền, giỏ hàng, địa chỉ, đơn hàng, nội dung đọc, thống kê và thông báo đã có triển khai. Kết quả kiểm thử API trước đó được lưu cùng dự án; việc chụp giao diện trong báo cáo chỉ xác nhận các màn hình đã tải được tại thời điểm ghi nhận.')
p('Phần thông báo đã được kiểm tra sau khi bổ sung bảng dữ liệu: bốn vai trò lấy danh sách thành công; khách hàng đánh dấu thông báo của mình đã đọc; tài khoản khác không được đánh dấu thông báo đó. Khi bàn giao, tester cần thực hiện lại trên đúng cơ sở dữ liệu và phiên bản mã nguồn nộp bài.')
tbl([['Nội dung','Phạm vi hiện tại'],['Thanh toán','Đặt hàng COD; thanh toán online đang tắt, chưa xác nhận tích hợp thu tiền thật.'],['AI','Có kết nối dịch vụ và phương án dự phòng cục bộ; chưa duy trì ngữ cảnh hội thoại nhiều lượt ở backend.'],['Đọc nội dung','Có xem trước và kiểm tra quyền đọc; không mặc định mọi sản phẩm có đầy đủ nội dung bản quyền.'],['Quản lý sách','Giao diện thêm sách, sửa giá và tồn; chỉnh sửa toàn bộ và ngừng kinh doanh có API riêng.'],['Thông báo','Trong website, theo tài khoản; chưa có email, SMS và push notification.'],['Kiểm thử','Cần kiểm thử lại luồng đặt hàng, tồn kho, hủy đơn và phân quyền trên bản bàn giao; ảnh chụp không chứng minh mọi ca kiểm thử đều đạt.']],[3.5,12.5],11)
h('10.8 Hướng phát triển và kết luận')
p('Các hướng phát triển tiếp theo gồm tích hợp cổng thanh toán thật và xác minh callback; bổ sung biểu mẫu sửa đầy đủ thông tin sách; nâng chất lượng dữ liệu tư vấn và hội thoại; hoàn thiện nội dung điện tử có quyền sử dụng; bổ sung biểu đồ thống kê theo thời gian, khôi phục mật khẩu và các kênh thông báo ngoài website.')
p('Dự án đã hình thành hệ thống bán sách theo mô hình tách giao diện và backend, có các luồng mua hàng COD và phân quyền phục vụ vận hành. Quá trình thực hiện giúp nhóm liên kết việc phân tích yêu cầu, lập lịch, kiểm soát chi phí và quản lý chất lượng với một sản phẩm có thể trình diễn. Việc nghiệm thu cuối cùng cần dựa trên mã nguồn bàn giao, dữ liệu kiểm thử và các tiêu chí chấp nhận đã thống nhất.')
h('TÀI LIỆU THAM KHẢO VÀ HỒ SƠ DỰ ÁN',1)
p('1. Nhóm 11. Mã nguồn website Libra, thư mục giao diện dist và backend be.qlythuvien, phiên bản dùng lập báo cáo tháng 10/2026.')
p('2. Nhóm 11. Hồ sơ yêu cầu, WBS, kế hoạch tiến độ, dự toán và kế hoạch kiểm thử trong báo cáo cuối kỳ.')
p('3. Nhóm 11. Kết quả kiểm tra API và kiểm tra thông báo lưu trong bộ hồ sơ kiểm thử của dự án.')
p('4. Microsoft Learn. Tài liệu ASP.NET Core, Entity Framework Core và SQL Server; dùng làm tài liệu tra cứu kỹ thuật khi tiếp tục phát triển hệ thống.')
doc.save(OUT)
print(OUT)

