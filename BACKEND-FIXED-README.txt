BẢN SỬA NGÀY 10/10/2026

Backend đã sửa nằm tại be.qlythuvien.
- Bỏ hỗ trợ JWT qua URL; sử dụng Authorization: Bearer.
- Mục lục dùng textContent, không diễn giải tiêu đề chương thành HTML.
- AI chỉ tin proxy được khai báo trong Ai:TrustedProxies.
Frontend dist/app.js dùng /Products/{id}/preview và /Products/{id}/read để mở hộp đọc sách, phân biệt toàn văn với tóm tắt.

Chạy: dừng backend cũ đang chiếm cổng 5160, chạy start-backend.ps1; frontend vẫn dùng cổng 4173. Hoặc mở project be.qlythuvien trong Visual Studio và cấu hình cổng tương ứng.
Script start-backend.ps1 đã trỏ tới bản BE mới. Bản sửa chưa được khởi động trên database thật.
Build BE: 0 lỗi, 0 cảnh báo. Kiểm tra cú pháp FE và 31 kiểm thử hiện có đạt. Luồng đọc mới cần kiểm thử với dữ liệu mua sách thật.
Lưu ý: backend tự cập nhật schema khi khởi động như mã nguồn được cung cấp. Nội dung sách đầy đủ cần nhập qua PUT /api/Products/{id}/content; không tự có toàn văn.
