# FE tích hợp bản BE RAR ngày 04/10/2026

Tài liệu này thay thế hợp đồng đề xuất cũ. FE dist/live.js đã khớp mã nguồn ban đầu của API; bản backend hiện tại nằm trong be.qlythuvien. Không thay thế backend đang chạy hoặc thay đổi database khi cập nhật FE.

## Chat
POST /api/ai/chat gửi {"message":"Văn học"}.
Data trả về: {"response":"...","relatedProducts":[{"productId":1}],"timestamp":"..."}.
FE đọc response, lấy ID từ relatedProducts và kiểm tra lại tối đa 4 sản phẩm bằng GET /api/Products/{id}. relatedProducts null được xem là không có gợi ý. Không gửi API key hoặc history vì BE hiện chưa hỗ trợ hội thoại nhiều lượt. Văn bản được escape trước khi hiển thị.

## Dashboard
GET /api/dashboard?fromDate=2026-10-01T00:00:00&toDate=2026-10-03T23:59:59.999&topProducts=5&lowStockThreshold=5
FE giữ from/to trên URL trang để lưu bộ lọc, ánh xạ thành fromDate/toDate khi gọi API.
Data: totalRevenue, totalOrders, totalCustomers, bestSellingProducts[], lowStockProducts[], dailyRevenue (nullable).
FE hiển thị totalCustomers với nhãn Tổng tài khoản hệ thống, vì BE đếm toàn bộ bảng Customers. dailyRevenue gồm date, revenue, orderCount; hiển thị Doanh thu ngày cuối kỳ. Chưa có biểu đồ tháng vì BE không trả chuỗi số liệu tháng.
Khoảng ngày gửi không kèm timezone để khớp truy vấn DateTime hiện tại của BE; BE vẫn cần thống nhất UTC/giờ Việt Nam. Sai lệch nghiệp vụ doanh thu, đơn hủy trong sách bán chạy và tồn khả dụng cần sửa ở BE, FE không tự tính lại.

## Thông báo
GET /api/notifications trả data là mảng, chưa phân trang. FE đếm các mục isRead=false để hiện badge.
PUT /api/notifications/{id}/read; PUT /api/notifications/mark-all-read, không có body.
Trường hiển thị: notificationId, title, message, type, isRead, createdAt. Ngày null để trống. type order/payment có liên kết tới danh sách đơn hàng theo vai trò; BE chưa có orderId nên không mở chi tiết đơn cụ thể.
FE tiếp tục cập nhật khi mở chuông, tải lại, sau đánh dấu đọc và mỗi 60 giây khi tab hiện. Phân quyền người nhận do BE kiểm tra.

## Kiểm thử
node --test tests/features.test.cjs tests/api.test.cjs tests/live-api.test.cjs
Các test mới dùng phản hồi mô phỏng đúng DTO BE; chưa xác nhận tích hợp chạy trực tiếp với bản BE mới. Cần chạy bản BE mới và đặt dist/config.js apiBaseUrl đúng địa chỉ của nó. useMock=false.

## Đọc thử (FE bổ sung)
Trang chi tiết gọi GET /api/Products/{id}/preview khi mở phần đọc thử. Envelope success/data như các API còn lại; data: {"excerpt":"Đoạn văn thuần đã được phép cung cấp miễn phí"}. Không gửi toàn bộ sách rồi cắt/che bằng CSS. FE hiển thị bằng textContent, không thực thi HTML. Khi API chưa có, hiển thị mô tả với nhãn Giới thiệu sách, không coi mô tả là trích đoạn.
Nút Mua sách thêm một cuốn nếu chưa có trong giỏ; nếu đã có giữ nguyên số lượng, chọn riêng sách đó và mở giỏ hàng. Không tạo đơn hay đánh dấu đã thanh toán tự động.
Nếu cần ebook: BE cần endpoint nội dung được bảo vệ bởi JWT và kiểm tra quyền sở hữu/đã thanh toán, xử lý hủy/hoàn tiền; COD mới đặt chưa đủ điều kiện mở khóa. Cần file ebook/đoạn trích được phép sử dụng từ chủ dự án. Chức năng ebook đầy đủ chưa triển khai.
