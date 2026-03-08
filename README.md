# ⚽ EPL Data Analysis 24/25

## 📂 Project Structure & Workflow

Luồng hoạt động chính của project được chia thành 4 phần tương ứng với các script trong thư mục `src/`:

### 1. Thu thập và làm sạch dữ liệu (`src/data_collection.py`)
- **Đầu vào:** Ban đầu định cào data từ FBref nhưng bị chặn bot rát quá và code bị lỗi thiếu cột, nên tôi dùng file data lấy từ Kaggle (`epl_player_stats_24_25.csv`) và ghép thêm một số chỉ số phụ (xG, xAG, SCA, GCA...) từ các nguồn data phụ (`database.csv` & `fbref_PL_2024-25.csv`).
- **Xử lý:** Script này sẽ clean data, đổi các cột phần trăm sang số thập phân để tiện tính toán.
- **Đầu ra:** Xuất ra file chuẩn chỉnh cuối cùng tại `data/processed/merged_epl_24_25.csv` để dùng chung cho các bước phân tích sau.

### 2. Thống kê mô tả & Trực quan hóa (`src/analysis.py`)
- **Top & Bottom:** Extract ra Top 3 & Bottom 3 cầu thủ cho mỗi chỉ số (lọc bỏ NaN để tránh nhiễu) và lưu vào `top_3.txt`.
- **Chỉ số thống kê:** Tính toán Mean, Median, Standard Deviation cho toàn bộ giải đấu và tính riêng theo từng đội bóng $\rightarrow$ xuất ra `results2.csv`.
- **Trực quan hóa:** Vẽ các biểu đồ Histogram phân phối chỉ số và lưu đồ thị trong mục `reports/figures/`.
- **Đánh giá đội bóng:** Tự build một công thức tính điểm phong độ tổng hợp dựa trên z-score của các thông số tích cực (bàn thắng, tỷ lệ chuyền thành công...) trừ đi thông số tiêu cực (bàn thua) (lấy cảm hứng từ chỉ số KDA trong game =)). Kết quả chạy ra thuật toán đánh giá **Newcastle United** là đội có bộ chỉ số tốt nhất toàn giải.

### 3. Phân cụm (Clustering) cầu thủ (`src/ml_analysis.py`)
- Sử dụng thuật toán **K-Means** kết hợp với thư viện `StandardScaler` để chuẩn hóa các feature trước khi đưa vào phân cụm.
- **Chọn K bằng phương pháp Elbow:** Cho $k$ chạy từ 2 đến 10, thấy đường gấp khúc (elbow) rõ nét nhất ở $k=4$. Nghĩa là data có thể phân các cầu thủ thành 4 nhóm vai trò chính kiểu như: phòng ngự, cầm nhịp/chuyền bóng, kiến thiết, và tiền đạo chủ lực.
- **Giảm chiều dữ liệu bằng PCA:** Không gian đa chiều rất khó biểu diễn, nên tôi dùng thuật toán PCA kéo dữ liệu tóm gọn lại còn 2 chiều (2D). Nhờ thế mà chấm lên scatter plot sẽ thấy các phân vùng dữ liệu (clusters) tách nhau ra cực kì rõ ràng và mịn.

### 4. Dự đoán giá trị chuyển nhượng
- **Cào dữ liệu (Web Scraping):** Dùng `requests` và `BeautifulSoup` script để crawl auto lấy giá chuyển nhượng thực tế từ `transfermarkt.co.uk`. Crawl lách bằng cách duyệt qua từng nhóm đội rồi đi sâu vào detail vào từng cầu thủ để mở khóa giới hạn độ dài hiển thị trên trang.
- **Training Model:** Lọc điều kiện các cầu thủ đá $\ge$ 900 phút. Dùng mô hình **Random Forest Regressor** để chạy dự đoán biến trị giá `TransferValue_EUR`.
- **Feature Selection:** Tận dụng đặc tính của cây quyết định Random Forest (tự đánh giá tiêu chuẩn và loại bỏ feature rác) nên tôi feed thẳng toàn bộ biến vào cho model học luôn mà không cần chọn lọc hay tinh giảm thủ công.
- **Kết quả:** Quá trình huấn luyện chỉ ra 5 chỉ số có sức ảnh hưởng gánh giá nhất đến túi tiền chuyển nhượng của một cầu thủ Ngoại Hạng Anh:
  1. Số cú sút (Shots Attempted)
  2. Bàn thắng kỳ vọng (xG)
  3. Tổng số lần chạm bóng (Total Touches)
  4. Số hành động dẫn đến dứt điểm (SCA)
  5. Kỷ lục giữ sạch lưới (Clean Sheets)
- *Note:* Kết luận rút ra được từ model phân tích cũng khá tương đồng với thực tế bóng đá: Sút nhiều, chạm 1 tốt, năng nổ tự tạo cơ hội xG/SCA cao là tự động giá cầu thủ cao. 📈


