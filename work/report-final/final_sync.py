from docx import Document
p='output/Bao_cao_cuoi_ky_Nhom11_hoan_thien.docx'
d=Document(p)
for x in d.paragraphs:
 if 'thông tin hoạt động gốc (Baseline)' in x.text:x.text=x.text.replace('thông tin hoạt động gốc (Baseline)','ngân sách theo lịch cơ sở 48 ngày')
 if 'Thông tin hoạt động gốc (Baseline)' in x.text:x.text=x.text.replace('Thông tin hoạt động gốc (Baseline)','Ngân sách theo lịch cơ sở 48 ngày')
 if 'Đây là phương án kế hoạch, không phải xác nhận' in x.text:x.text='Báo cáo chọn phương án 48 ngày làm lịch cơ sở thống nhất cho WBS, mốc bàn giao và phân bổ chi phí. Đây là lịch kế hoạch điều chỉnh, không phải xác nhận đã rút ngắn tiến độ thực tế. Khi triển khai, PM cần kiểm soát nguồn lực, hợp đồng API và chất lượng kiểm thử; nếu API thay đổi nhiều, công việc song song có thể phải làm lại.'
d.save(p)
