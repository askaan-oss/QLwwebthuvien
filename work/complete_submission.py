from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import json
base=Path(r'D:\QL dự án nhóm');work=base/'work';out=base/'output'
s=(work/'build_doc.py').read_text(encoding='utf-8-sig')
exec(s[s.index('doc=Document();'):s.index("p('BÁO CÁO THỰC HÀNH'")])
doc=Document(out/'QLDA_Nhom11_Lab.docx')
repl={
'Bảng nguồn có TE nhưng không có ba ước lượng O, M, P. Vì vậy phép kiểm tra dưới đây là CPM trên TE đã cung cấp; chưa thể xác nhận công thức PERT ba điểm hoặc tính độ lệch chuẩn dự án. Không suy ngược một bộ O, M, P rồi coi đó là dữ liệu gốc.':'Bảng nguồn có TE nhưng không có ba ước lượng O, M, P. Bảng dưới đây kiểm tra CPM theo TE nguồn. Bộ O–M–P đề xuất và công thức PERT được bổ sung tại Phần 9 và file QLDA_Nhom11_LichDuAn.xlsx; đó là ước lượng AI hỗ trợ, chưa phải số liệu đã được nhóm xác nhận.',
'CPM cơ sở: 37,02 ngày, khớp nguồn. CPM tối ưu: 32,51 ngày, khớp nguồn. Mức rút ngắn: 4,51 ngày. EMV: 2.825.000 đồng, khớp nguồn. Chưa có O/M/P để kiểm tra TE và chưa có dữ liệu Jira để xác nhận Actual.':'CPM theo TE nguồn: 37,02 ngày; tối ưu: 32,51 ngày; rút ngắn: 4,51 ngày. EMV: 2.825.000 đồng. Các kết quả khớp nguồn. File Excel đã bổ sung bộ O–M–P đề xuất cùng phép tính PERT để nhóm kiểm tra; Actual vẫn cần xác nhận bằng Jira.',
'□ Bổ sung O/M/P và file Excel có công thức, Gantt theo yêu cầu lab.':'□ Rà soát bộ O–M–P đề xuất và đính kèm file QLDA_Nhom11_LichDuAn.xlsx đã tạo.',
'Bổ sung O/M/P; tính lại bằng Excel; san bằng nguồn lực.':'Rà soát O/M/P đề xuất và công thức Excel đã tạo; san bằng nguồn lực.',
'8  Phản biện và nhật ký AI':'8  Phản biện và nhật ký AI\n9  PERT ba điểm và đối chiếu bộ nộp'
}
paras=list(doc.paragraphs)+[p for t in doc.tables for r in t.rows for c in r.cells for p in c.paragraphs]
for para in paras:
 for old,new in repl.items():
  if old in para.text:
   para.text=para.text.replace(old,new)
page('9 PERT ba điểm bổ sung')
p('Bộ ba điểm sau là ước lượng đề xuất để hoàn thiện phương pháp PERT. Nhóm cần điều chỉnh theo kinh nghiệm và thời gian thực tế của người làm. Bộ ba không được trình bày như dữ liệu có sẵn trong báo cáo tuần 1–4; TE nguồn được giữ riêng trong Excel.')
rows=json.loads((work/'pert_proposals.json').read_text(encoding='utf-8'))
fmt=lambda v:f'{v:.2f}'.replace('.',',')
table(['Mã','Hoạt động','O','M','P','TE','Phương sai'],[[r['id'],r['name'],fmt(r['o']),fmt(r['m']),fmt(r['p']),fmt(r['te']),fmt(r['variance'])] for r in rows],[0.9,5.8,1.5,1.5,1.5,2,4.2])
p('Công thức: TE = (O + 4M + P) / 6; phương sai = ((P − O) / 6)². Đơn vị O, M, P, TE là ngày làm việc; đơn vị phương sai là ngày². Ví dụ D: (2 + 4 × 3 + 5) / 6 = 19/6 = 3,166666… ngày; nguồn hiển thị 3,17 ngày.')
h('Đường găng và độ lệch chuẩn')
p('Với bộ đề xuất ban đầu, đường găng vẫn là A → C → D → G → I → J → K → M → N → O → P → Q. Tổng TE chưa làm tròn bằng 37,00 ngày. Tổng phương sai trên đường này bằng 2,027777… ngày²; độ lệch chuẩn bằng căn bậc hai của tổng phương sai, khoảng 1,424 ngày. Kết quả giả định các thời lượng độc lập và đường găng không đổi; không coi đây là bảo đảm hoàn thành đúng hạn.')
page('9 Đối chiếu Excel với báo cáo')
table(['Cách tính','Cơ sở','Tối ưu','Ý nghĩa'],[['Dùng TE đã làm tròn của nguồn','37,02','32,51','Khớp hai kết quả trong báo cáo tuần 1–4.'],['Dùng O–M–P đề xuất, không làm tròn trung gian','37,00','32,50','Giữ đủ độ chính xác của TE trong phép tính.'],['Chênh lệch so với nguồn','−0,02','−0,01','Chênh lệch do làm tròn TE với bộ đề xuất này.']],[6.6,2.1,2.1,6.6])
h('Sử dụng file Excel')
p('File QLDA_Nhom11_LichDuAn.xlsx có bốn trang tính. CPM chứa hai bảng lịch cơ sở và tối ưu với công thức ES, EF, LS, LF, Slack. Gantt liên kết với lịch và tự đổi khi thời lượng đổi. PERT lưu riêng TE nguồn, O–M–P đề xuất, phương sai và thời lượng tối ưu. EMV tính tổn thất kỳ vọng từ xác suất và tác động tiền trong nguồn.')
p('Ở CPM, ô B4 = 1 dùng TE nguồn; B4 = 2 dùng PERT đề xuất. Ô B5 là quỹ ngày làm việc giả định. Các ô vàng trong PERT là phần cần nhóm rà soát. Khi để thiếu O, M hoặc P trong chế độ PERT, tổng lịch sẽ báo thiếu dữ liệu thay vì tự coi là 0.')
p('Các quan hệ phụ thuộc theo báo cáo nguồn được giữ cố định trong công thức. Nếu nhóm đổi tiền nhiệm, phải cập nhật cả ES và LF, không chỉ sửa ô mô tả. Gantt hiện thể hiện 40 ngày làm việc; nếu lịch vượt 40 ngày, cần mở rộng lưới.')
h('Kết quả kiểm tra của bản tính')
p('Đã đối chiếu lịch nguồn, lịch PERT đề xuất và tổng EMV với phép tính độc lập. Đã thử thay đổi một ước lượng để kiểm tra tổng lịch cập nhật và thử xóa O để kiểm tra cảnh báo thiếu dữ liệu. Công thức được tính lại trong công cụ tạo bảng tính; nhóm cần mở bằng Excel để rà soát trước khi nộp và ghi việc kiểm tra thực tế vào nhật ký.')
h('Nội dung bổ sung vào nhật ký AI')
table(['Yêu cầu trong cuộc trao đổi','AI hỗ trợ','Phần nhóm cần xác nhận'],[['Rà đủ yêu cầu nộp bài','Bổ sung Excel PERT/CPM/Gantt/EMV, bộ O–M–P đề xuất và bảng đối chiếu kết quả.','Kiểm tra ước lượng, ghi prompt và kết quả rà soát; xác nhận hoạt động tự làm.']],[5.6,6,5.8])
page('9 Bảng đối chiếu yêu cầu nộp')
p('Đề yêu cầu một báo cáo Word hoặc PDF tổng hợp và một file Excel lịch dự án. Các mục nội dung dưới đây được gộp trong bộ hai file, không cần mỗi mục thành một file nộp riêng.')
table(['Yêu cầu theo đề','Đã có trong bộ tài liệu','Cần nhóm bổ sung'],[
['Ảnh Instructions và Knowledge','Phần 1 có nội dung thiết lập và vị trí chèn ảnh.','Ảnh chụp thật sau khi thiết lập Project.'],
['Project Charter bản cuối','Phần 2: mục đích, phạm vi, mục tiêu, giả định, bên liên quan và tiêu chí.','Ngày, ngân sách, tên người phụ trách và xác nhận quyết định.'],
['WBS sơ đồ cây, bảng và từ điển','Phần 3: bảy nhánh, gói cấp ba, giờ công và từ điển ba gói.','Rà soát giờ công và trách nhiệm thực tế.'],
['PERT, đường găng, Gantt và Excel','Phần 4–5, phần 9 và QLDA_Nhom11_LichDuAn.xlsx.','Xác nhận O–M–P đề xuất và ghi kết quả nhóm tính lại.'],
['Risk Register và ma trận','Phần 6: tám rủi ro, ma trận 5×5, kế hoạch dự phòng và EMV.','Hai rủi ro từ kinh nghiệm của nhóm; xác nhận người theo dõi.'],
['Năm câu hỏi phản biện và phản tư','Phần 8 có câu hỏi và phương án trả lời tham khảo.','Nhóm tự hoàn thiện câu trả lời và phản tư.'],
['Nhật ký sử dụng AI','Phần 8 và 9 mô tả các phần AI đã hỗ trợ.','Prompt thật, ngày thực hiện, người kiểm tra và thay đổi của nhóm.']
],[4.6,7,5.8])
h('Hai file trong bộ nộp')
p('1. QLDA_Nhom11_Lab.docx — báo cáo tổng hợp.\n2. QLDA_Nhom11_LichDuAn.xlsx — lịch có công thức, Gantt, dữ liệu PERT và EMV.')
h('Minh chứng cần lấy từ nhóm')
p('Ảnh Project, nhật ký thao tác và xác nhận tự kiểm tra là bằng chứng quá trình làm việc. Chỉ chèn ảnh và số liệu thực tế. Các giá trị Actual mẫu trong nguồn cần được thay bằng dữ liệu Jira nếu dùng để báo cáo tiến độ thật.')
doc.save(out/'QLDA_Nhom11_Lab.docx')
print('Updated report with PERT appendix and submission checklist')
