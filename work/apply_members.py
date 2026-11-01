from pathlib import Path
from docx import Document
from docx.shared import Cm
from PIL import Image,ImageDraw,ImageFont
base=Path(r'D:\QL dự án nhóm');work=base/'work';out=base/'output'
path=work/'build_schedule.mjs';s=path.read_text(encoding='utf-8')
s=s.replace("val(cp,'B5',40)","val(cp,'B5',45)").replace('Giả định 8 tuần × 5 ngày, chưa trừ ngày nghỉ.','9 tuần × 5 ngày theo cập nhật của nhóm; chưa trừ ngày nghỉ.')
s=s.replace("'A1:AU49'","'A1:AZ49'").replace('Array(40)','Array(45)').replace('day<=40','day<=45').replace('length:40','length:45').replace(':AT',':AY').replace('Nếu EF vượt 40','Nếu EF vượt 45')
s=s.replace("val(pe,'A30','Tiền nhiệm", "val(pe,'A32','Nhóm 11 có 5 thành viên, thời gian 9 tuần theo xác nhận của người học.');\nval(pe,'A30','Tiền nhiệm")
path.write_text(s,encoding='utf-8')
doc=Document(out/'QLDA_Nhom11_Lab.docx')
replacements={
 '6 thành viên':'5 thành viên','sáu thành viên':'năm thành viên','sáu Sprint':'năm Sprint',
 '8 tuần':'9 tuần','tám tuần':'chín tuần','tám Sprint':'chín Sprint','hết tuần 8':'hết tuần 9','cuối tuần 8':'cuối tuần 9',
 'quỹ 40 ngày':'quỹ 45 ngày','40 ngày làm việc':'45 ngày làm việc','giả định 40 ngày':'giả định 45 ngày','ngày 40':'ngày 45','0–40':'0–45',
 '2,98 ngày dự phòng':'7,98 ngày dự phòng','là 2,98 ngày':'là 7,98 ngày','12,98 ngày':'12,98 ngày','7,49 ngày':'12,49 ngày',
 '1.1.3–1.1.6':'1.1.3–1.1.7','4 bộ hồ sơ theo dõi, mỗi bộ 2 Sprint':'5 bộ hồ sơ theo dõi cho 9 Sprint',
 'gồm bốn gói, mỗi gói 8 giờ':'gồm năm gói, mỗi gói 8 giờ; bốn gói đầu theo dõi 2 Sprint/gói, gói cuối theo dõi Sprint 9',
 '496':'504','24.800.000':'25.200.000','29.325.000':'29.725.000',
 'TV6':'TV1 và TV5',
 'Gantt hiện thể hiện 40 ngày làm việc; nếu lịch vượt 40 ngày':'Gantt hiện thể hiện 45 ngày làm việc; nếu lịch vượt 45 ngày',
}
paras=list(doc.paragraphs)+[p for t in doc.tables for row in t.rows for cell in row.cells for p in cell.paragraphs]
for p in paras:
 txt=p.text
 for old,new in replacements.items():txt=txt.replace(old,new)
 if txt!=p.text:p.text=txt
for p in doc.paragraphs:
 if p.text.startswith('Thành viên:'):
  p.text='Thành viên\nNguyễn Đình Kiên\nNguyễn Trọng Khánh\nNguyễn Trướng Quốc Huy\nTrịnh Châu Hồng Phát\nHuỳnh Minh Nhựt'
 if p.text.startswith('Phân vai đề xuất cho'):
  p.text='Phân vai đề xuất cho năm thành viên'
 if p.text.startswith('Phân vai trên chưa gắn tên cá nhân'):
  p.text='Tên thành viên và thời gian 9 tuần theo thông tin người học xác nhận. Vai trò dưới đây là phương án phân công đề xuất, cần nhóm thống nhất theo năng lực và lịch tham gia.'
 if p.text.startswith('Quy mô') or p.text.startswith('Nhóm 11  •'):
  p.text='Nhóm 11  •  5 thành viên  •  Thời gian 9 tuần'
 if p.text.startswith('Với PERT đề xuất'):
  p.text=p.text.replace('40','45')
 if p.text.startswith('Báo cáo sản phẩm tuần 1–4 là căn cứ'):
  p.add_run(' Quy mô 5 thành viên và thời gian 9 tuần theo xác nhận mới của người học thay cho 6 thành viên và 8 tuần trong tài liệu nguồn.')
 if p.text.startswith('Gantt dùng lịch cơ sở.'):
  p.text='Gantt dùng lịch cơ sở. Thanh đậm là hoạt động găng; thanh nhạt có độ dự trữ. Trục ngang thể hiện 45 ngày làm việc kể từ khởi động, theo giả định 9 tuần × 5 ngày.'
 if p.text.startswith('M4  Trong Sprint cuối'):
  p.text=p.text.replace('Sprint cuối','Sprint 9')
# Replace the staffing table with five named assignments.
names=[('TV1  Nguyễn Đình Kiên','PM kiêm BA; lập kế hoạch và Backlog; chủ trì test case, nghiệm thu và phối hợp kiểm thử.'),('TV2  Nguyễn Trọng Khánh','Frontend kiêm UI/UX; Figma và giao diện khách hàng; kiểm tra chéo giao diện quản trị.'),('TV3  Nguyễn Trướng Quốc Huy','Frontend giỏ hàng và quản trị; phối hợp đơn hàng; kiểm tra chéo luồng khách hàng.'),('TV4  Trịnh Châu Hồng Phát','Backend dữ liệu, REST API, tài khoản và sách; hỗ trợ tích hợp và rà soát bảo mật.'),('TV5  Huỳnh Minh Nhựt','Backend đơn hàng và thanh toán; môi trường, triển khai và hướng dẫn vận hành.')]
for t in doc.tables:
 if t.cell(0,0).text=='Vị trí':
  while len(t.rows)>6:t._tbl.remove(t.rows[-1]._tr)
  for row,(name,role) in zip(t.rows[1:],names):row.cells[0].text=name;row.cells[1].text=role
  for row in t.rows:
   row.cells[0].width=Cm(5.3);row.cells[1].width=Cm(12.1)
  t.columns[0].width=Cm(5.3);t.columns[1].width=Cm(12.1)
 for row in t.rows:
  if row.cells[0].text=='1.1.3–1.1.7':row.cells[2].text='40'
  if len(row.cells)>2 and row.cells[0].text=='Triển khai và nghiệm thu':
   row.cells[0].text='Triển khai và demo cơ sở';row.cells[2].text='8'
# Keep source milestone 37.02 and add Sprint 9 reserve explicitly.
for t in doc.tables:
 if t.cell(0,0).text=='Mốc bàn giao':
  r=t.add_row();r.cells[0].text='Dự phòng, phản hồi và nghiệm thu cuối';r.cells[1].text='Đến 45,00';r.cells[2].text='9'
 if t.cell(0,0).text=='Yêu cầu người dùng':
  r=t.add_row();r.cells[0].text='Cập nhật 5 thành viên và học 9 tuần';r.cells[1].text='Điền danh sách tên, điều chỉnh WBS quản lý, dự toán và quỹ 45 ngày.';r.cells[2].text='Tên Trịnh Châu Hồng Phát được người học xác nhận; lớp chưa được cung cấp.'
# Update the WBS image directly from the original drawing generator with the new range.
src=(work/'build_library.py').read_text(encoding='utf-8-sig')
chunk=src[src.index('branches='):src.index("im=Image.new('RGB',(1500,1040)")]
chunk=chunk.replace('1.1.3–1.1.6','1.1.3–1.1.7')
exec(chunk)
shape=doc.inline_shapes[0];rel=doc.part.related_parts[shape._inline.graphic.graphicData.pic.blipFill.blip.embed];rel._blob=(work/'thu_vien_wbs.png').read_bytes()
# Recreate the report Gantt with 45 days, preserving source durations.
import json
tables=json.loads((work/'source_tables.json').read_text(encoding='utf-8'));dd={};acts=[]
for row in tables[5][1:]:
 a,n,pr,t=row;pre=[] if pr=='-' else pr.split(',');te=float(t.replace(',','.'));es=max([dd[x]['ef'] for x in pre] or [0]);dd[a]={'es':es,'ef':es+te};acts.append((a,n))
crit=set('ACDGIJKMNOPQ');font=r'C:\Windows\Fonts\arial.ttf';im=Image.new('RGB',(1600,1040),'white');dr=ImageDraw.Draw(im);f=ImageFont.truetype(font,23)
for tick in range(0,46,5):
 x=480+tick*24;dr.line((x,55,x,1000),fill='#dddddd');dr.text((x-10,15),str(tick),font=f,fill='black')
for i,(a,n) in enumerate(acts):
 y=68+i*53;dr.text((12,y),a+'  '+n,font=f,fill='black');dr.rectangle((480+dd[a]['es']*24,y,480+dd[a]['ef']*24,y+30),fill='#314d66' if a in crit else '#a1b3c2')
im.save(work/'thu_vien_gantt.png');shape=doc.inline_shapes[1];rel=doc.part.related_parts[shape._inline.graphic.graphicData.pic.blipFill.blip.embed];rel._blob=(work/'thu_vien_gantt.png').read_bytes()
doc.save(out/'QLDA_Nhom11_Lab.docx')
print('Updated five names, nine weeks, 504 hours and proposed budget 29,725,000 VND')
