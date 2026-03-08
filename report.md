# Bài tập 1 - Phân tích Dữ liệu Cầu thủ Ngoại hạng Anh 2024/2025

## I. Thu thập dữ liệu
Yêu cầu ban đầu của đề bài là lấy các thông số chi tiết (như bàn thắng kỳ vọng, kỹ năng chuyền, kiểm soát bóng, v.v.) của tất cả cầu thủ đá trên 90 phút ở Ngoại hạng Anh mùa 2024-2025. 
Vì FBref chặn bot tương đối gắt và thiếu nhiều cột dữ liệuliệu, nên em chuyển sang dùng file dữ liệu được share public trên Kaggle (`epl_player_stats_24_25.csv`). Tuy nhiên, dataset vẫn chưa thiếu một vài chỉ số nên em đã phải ghép thêm các chỉ số phụ như xG, xAG, SCA, GCA từ dữ liệu của các user kháckhác (`database.csv` & `fbref_PL_2024-25.csv`).

Em dùng một script Python (`src/data_collection.py`) để clean data, đổi các cột phần trăm sang số thập phân rồi gộp hết lại thành một file dữ liệu hoàn chỉnh (`data/processed/merged_epl_24_25.csv`) cho dễ phân tích ở các bước sau.

## II. Thống kê mô tả & Vẽ biểu đồ
Phần này em viết một file Python riêng (`src/analysis.py`) để chạy phân tích trên tập data vừa gộp.
1. **Top 3 & Bottom 3**: Tìm ra 3 người đứng đầu và 3 người chót bảng cho mỗi chỉ số, sau đó lưu phần thống kê này vào file `top_3.txt`. Ở bước này, em bỏ đi các giá trị NaN để loại bớt rác, tránh trường hợp tính các cầu thủ thiếu dữ liệu vào nhóm bottom 3.
2. **Mean, Median & Standard Deviation**: Tính trung vị chung, giá trị trung bình và độ lệch chuẩn cho cả mặt bằng giải đấu cũng như chia theo từng đội. Kết quả được lưu thành file `results2.csv`.
3. **Biểu đồ Histogram**: Các đồ thị này được lưu trong mục `reports/figures/`.
4. **Đội bóng có phong độ tốt nhất**: Để xem trên thống kê thì đội nào thi đấu tốt nhất một cách khách quan, em tính ra một điểm số tổng hợp bằng cách cộng dồn z-score của các thông số tích cực (như số bàn thắng, tỷ lệ chuyền thành công) và trừ đi các thông số cản trở (như số bàn thua). Sau khi tính toán, thuật toán cho ra **Newcastle United** là đội có bộ chỉ số thống kê ấn tượng nhất trong cả giải. Em lấy cảm hứng từ KDA trong game =)). 

## III. Phân cụm bằng K-Means & PCA
Toàn bộ phần đánh giá này được em xử lý trong file `src/ml_analysis.py`:
- Đầu tiên, em áp dụng mô hình **K-Means** đi kèm bộ thư viện Standard Scaling để chuẩn hóa dữ liệu.
- **Chọn K**: Dùng phương pháp Elbow (để $k$ chạy từ 2 đến 10), đường đồ thị gập rõ nhất ngay ở mức **$k=4$**. Tức là, các cầu thủ có thể được phân loại gọn lại thành 4 nhóm vai trò (kiểu như: phòng thủ, cầm nhịp/chuyền bóng, kiến thiết, và tiền đạo chủ lực).
- **PCA**: Nhìn không gian dữ liệu gốc thì hơi rối nên em kéo nó xuống còn 2 chiều (2D) bằng thuật toán PCA. Chấm lên scatter plot thì thấy các phân vùng dữ liệu tách nhau ra khá mịn và rõ ràng.

## IV. Dự đoán giá trị chuyển nhượng
- **Cào dữ liệu (Web Scraping)**: Em kết hợp thư viện `requests` và `BeautifulSoup` để auto "cào" giá chuyển nhượng từ trang `transfermarkt.co.uk`. Thay vì ăn sẵn bảng 100 kết quả đầu tiên trang cung cấp, em code lách bằng cách cho duyệt qua từng nhóm đội rồi lấy số liệu sâu đến từng cầu thủ.
- **Dựng mô hình**: Tiến hành lọc các cầu thủ ra sân ít nhất 900 phút cho cứng form, sau đó gọi mô hình **Random Forest Regressor** để chạy dự đoán biến `TransferValue_EUR` (giá trị chuyển nhượng).
- **Đánh giá đặc trưng (Feature Selection)**: Thay vì tự tay chọn thủ công, em đưa thẳng tất cả biến vào cho mô hình đào tạo luôn. Bản thân cấu trúc cây quyết định trong Random Forest vốn đã tích hợp lọc mấy biến tạp và phạt các biến rác nên cứ chèn tất cả thôi.
- **Kết quả**: Demo mô hình xong thu lại được 5 chỉ số quan trọng nhất quyết định mức giá của một cầu thủ chính là:
  1. Số cú sút (Shots Attempted)
  2. Bàn thắng kỳ vọng (xG)
  3. Tổng số lần chạm bóng (Total Touches)
  4. Số lần tạo cơ hội dứt điểm (SCA)
  5. Giữ sạch lưới (Clean Sheets)
Cơ bản mô hình tính toán rất sát với thực tế: thời nay cứ cầu thủ nào sút khỏe, cầm bóng chắc, năng nổ mở ra cơ hội (xG cao, SCA cao) là tự động giá trị chuyển nhượng sẽ rất cao.
