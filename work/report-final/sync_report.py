from pathlib import Path
p=Path('work/report-final/build_report.py')
s=p.read_text(encoding='utf-8')
s=s.replace("Lịch WBS ở Chương 2 thể hiện mục tiêu phân công theo lịch; mạng công việc dưới đây dùng để kiểm tra tính khả thi của quan hệ phụ thuộc.","WBS ở Chương 2, mạng CPM điều chỉnh và bảng chi phí ở Chương 4 dùng chung lịch cơ sở 48 ngày. Mạng 64 ngày chỉ được giữ để so sánh phương án trước điều chỉnh.")
s=s.replace('Lịch WBS chi tiết cần được cập nhật cùng phiên bản khi phương án này được duyệt.','Lịch WBS chi tiết đã được quy đổi theo cùng ES và EF của phương án 48 ngày; ngày kết thúc được tính bao gồm ngày làm việc cuối cùng của gói.')
insert='''
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
'''
s=s.replace('pi=-1;ti=-1;chapter=0',insert+'\npi=-1;ti=-1;chapter=0')
s=s.replace("  if not text:continue\n  if text.startswith('CHƯƠNG'):","""  if not text:continue
  if text.startswith('Ghi chú: Thời lượng 74'):
   text='Ghi chú: Tổng 66 ngày là tổng thời lượng các hoạt động chạy nối tiếp hoặc song song; lịch dự án dài 48 ngày làm việc. Ngân sách 132.000.000 đồng phân bổ theo gói và bao gồm nguồn lực quản lý xuyên suốt; chi phí bình quân/ngày chỉ là tỷ số ngân sách gói trên thời lượng, được làm tròn đến đồng.'
  if re.match(r'^[1-7]\\.0[. ]',text):
   n=int(text[0]);text=f'{n}.0. {labels[n-1]}'
  if text.startswith('CHƯƠNG'):""")
s=s.replace("  if ti==25:rows[0]=['Hoạt động','Tiền nhiệm','Ngày','Chi phí/ngày','Ngân sách đồng']", """  if ti==25:
   rows[0]=['Hoạt động','Tiền nhiệm','Ngày','Bình quân/ngày','Ngân sách đồng']
   for i in range(10):
    rows[i+1][1]=pre(i);rows[i+1][2]=str(optDur[i]);budget=int(rows[i+1][4].replace('.',''));rows[i+1][3]=f'{round(budget/optDur[i]):,}'.replace(',','.')
   rows[-1][2]='66'
  if ti in custom:rows=custom[ti]
  if ti in [6,13]:
   for row in rows:
    for k,v in enumerate(row):
     if v.startswith('Ngày dự kiến xác nhận:'):row[k]='Ngày dự kiến xác nhận: 07/09/2026'""")
s=s.replace("  tbl(rows,widthmap.get(ti),10 if len(rows[0])>=5 else 11)","""  if ti in range(15,22):widthmap[ti]=[1.2,6.2,1.5,2.3,2.3,2.5]
  tbl(rows,widthmap.get(ti),10 if len(rows[0])>=5 else 11)
  if ti==14:p('Các ngày được tính theo lịch thứ Hai đến thứ Bảy, nghỉ Chủ nhật. N1 là gói khởi động; PM vẫn theo dõi, quản lý thay đổi và chi phí xuyên suốt 48 ngày trong định mức nhân sự Chương 1. N3, N4 và N5 được giao cho BE, FE và BA để triển khai song song. Đây là lịch kế hoạch điều chỉnh, không phải nhật ký hoàn tất thực tế.')
  if ti==25:p('Ngân sách gói được giữ nguyên khi rút lịch; chi phí bình quân/ngày được tính lại theo thời lượng điều chỉnh. Bảng nhân sự và dịch vụ ở Chương 1 là cách phân loại cùng tổng ngân sách, không phải khoản cộng thêm.')""")
s=s.replace("p('Theo mô hình đã điều chỉnh,", "p('Theo mô hình đã điều chỉnh,")
p.write_text(s,encoding='utf-8')
print('patched builder')
