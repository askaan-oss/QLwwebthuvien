from docx import Document
p='output/Bao_cao_cuoi_ky_Nhom11_hoan_thien.docx'
d=Document(p)
for i,x in enumerate(d.paragraphs):
 if any(k in x.text for k in ['74','48 ngày*','cập nhật','132.000.000 VNĐ là','Baseline','phê duyệt trước']):print(i,x.text)
