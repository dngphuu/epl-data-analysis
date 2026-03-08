# Phương pháp Ước tính Giá trị Chuyển nhượng Cầu thủ

## Tổng quan
Tài liệu này trình bày chi tiết phương pháp được sử dụng để ước tính giá trị chuyển nhượng của các cầu thủ Ngoại hạng Anh mùa giải 2024-2025. Mục tiêu là xây dựng một mô hình dự đoán có thể ước lượng giá trị thị trường của cầu thủ dựa trên các thống kê hiệu suất trên sân.

## Thu thập Dữ liệu
- **Dữ liệu Hiệu suất**: Dữ liệu thống kê được tổng hợp từ nhiều nguồn bao gồm FBRef và cơ sở dữ liệu trận đấu địa phương.
- **Giá trị Chuyển nhượng**: Giá trị thị trường hiện tại được thu thập từ Transfermarkt cho các cầu thủ có thời gian thi đấu trên 900 phút.
- **Lọc dữ liệu**: Để đảm bảo mô hình được huấn luyện trên những cầu thủ đã khẳng định được bản thân với cỡ mẫu đáng kể, chỉ những cầu thủ thi đấu trên 900 phút trong mùa giải 2024-2025 mới được đưa vào tập huấn luyện.

## Lựa chọn Tính năng
Các tính năng được chọn cho mô hình bao gồm:
1. **Tuổi**: Một yếu tố cực kỳ quan trọng đối với giá trị thị trường, vì những cầu thủ trẻ có tiềm năng cao thường có mức phí chuyển nhượng lớn hơn.
2. **Thời gian thi đấu**: Tổng số phút và số lần ra sân.
3. **Hiệu suất cốt lõi**: Bàn thắng, Kiến tạo, Thẻ vàng/Thẻ đỏ.
4. **Các chỉ số nâng cao**:
   - **Bàn thắng kỳ vọng (xG)** và **Kiến tạo kỳ vọng (xAG)** để đo lường chất lượng hiệu suất thực tế.
   - **Hành động tạo cú sút (SCA)** và **Hành động tạo bàn thắng (GCA)**.
   - **Các hành động tịnh tiến**: Chuyền bóng tịnh tiến (PrgP), Dẫn bóng tịnh tiến (PrgC) và Nhận bóng tịnh tiến (PrgR).
5. **Hành động phòng ngự**: Tắc bóng, Chặn bóng và Đánh chặn.

## Lựa chọn Mô hình: Random Forest Regressor
Chúng tôi chọn **Random Forest Regressor** vì các lý do sau:
- **Tính phi tuyến tính**: Giá trị thị trường không phải lúc nào cũng tăng tuyến tính theo số liệu thống kê (ví dụ: một tiền đạo ghi 20 bàn có giá trị cao hơn nhiều so với gấp đôi giá trị của một người ghi 10 bàn).
- **Tương tác tính năng**: Mô hình nắm bắt hiệu quả các tương tác giữa các tính năng (ví dụ: giá trị của xG cao kết hợp với độ tuổi trẻ).
- **Tính ổn định**: Mô hình ít bị quá bản (overfitting) hơn so với một cây quyết định đơn lẻ và xử lý các giá trị ngoại lai (thường gặp trong phí chuyển nhượng) tương đối tốt.

## Hiệu suất Mô hình
- **RMSE**: Khoảng 18,6 triệu Euro.
- **R² Score**: 0.563, cho thấy mô hình giải thích được khoảng 56% sự biến thiên trong giá trị của cầu thủ.

## Các phát hiện chính (Tầm quan trọng của tính năng)
Các chỉ số hàng đầu báo hiệu giá trị của cầu thủ theo mô hình là:
1. **Tuổi** (Yếu tố quan trọng nhất)
2. **Tổng khối lượng sút bóng**
3. **Kiến tạo kỳ vọng (xAG)**
4. **Chuyền bóng tịnh tiến (PrgP)**
5. **Độ chính xác của cú sút (SoT)**

## Kết luận
Mặc dù các thống kê hiệu suất là những chỉ số dự báo mạnh mẽ, giá trị chuyển nhượng còn bị ảnh hưởng bởi các yếu tố không được nắm bắt hoàn toàn trong dữ liệu, chẳng hạn như thời hạn hợp đồng, giá trị thương mại và "sức hút ngôi sao". Tuy nhiên, mô hình này cung cấp một nền tảng vững chắc để ước tính giá trị dựa thuần túy trên các đóng góp chuyên môn.
