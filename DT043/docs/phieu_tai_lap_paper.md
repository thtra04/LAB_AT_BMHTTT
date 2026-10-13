# Phiếu tái lập bài báo

## A. Paper chính (đề giao)
**Masud M.T., Keshk M., Moustafa N., Turnbull B., Susilo W.** (2025). *Vulnerability defence using hybrid moving target defence in Internet of Things systems.* Computers & Security, 153, 104380. DOI 10.1016/j.cose.2025.104380. Open Access (CC BY), online 28/02/2025.

> Nguồn thông tin: metadata + abstract chính thức (Crossref, OpenAlex). Toàn văn trên ScienceDirect chặn truy cập tự động khi lập phiếu; các mục đánh dấu **[cần đối chiếu toàn văn]** phải được kiểm tra lại với PDF trước khi nộp.

| Mục | Nội dung |
|---|---|
| Bài toán | MTD liên tục thay đổi bề mặt tấn công; thiếu nghiên cứu về hiệu quả **kết hợp** nhiều kỹ thuật MTD xét đồng thời thời gian, chi phí, công sức; IoT không đồng nhất; MTD có thể **tiêu tốn quá mức tài nguyên** mạng/hệ thống |
| Phương pháp | *Vulnerability Defence* dựa trên **3-layer Temporal Hierarchical Attack Representation Model (3-layer-THARM)**: đánh giá an toàn của các trạng thái mạng gộp theo thời gian, xét metric an ninh ở mỗi trạng thái và khả năng tiếp cận của node/cạnh |
| Kỹ thuật MTD | nhóm **shuffle** và **diversity** (và tổ hợp) **[cần đối chiếu toàn văn: có redundancy không, tham số chu kỳ]** |
| Dữ liệu | topology/kịch bản IoT và lỗ hổng **[cần đối chiếu toàn văn: CVE, nguồn CVSS, có công bố code không]** |
| Metric | xác suất tấn công thành công, attack risk, attack cost; nhận diện đường tấn công |
| Kết quả chính | kết hợp kỹ thuật MTD khác nhóm (shuffle + diversity) → **xác suất tấn công thành công thấp hơn, rủi ro thấp hơn, chi phí tấn công cao hơn** so với dùng riêng |
| Không có | autoencoder, N-BaIoT, lượng tử hóa, đo edge → **khác chủ đề DT043** |

### Điểm hạn chế / cần tái lập (≥ 5)
| # | Hạn chế / điểm cần tái lập | Trạng thái | Cách DT043 xử lý |
|---|---|---|---|
| 1 | Đánh giá bằng mô hình đồ thị tấn công (mô phỏng), không phải triển khai thiết bị thật | Giả thuyết – theo abstract | Track B cũng chỉ mô phỏng; nêu rõ giới hạn |
| 2 | Xác suất khai thác gán tĩnh (CVSS), không phản ánh kẻ tấn công thích nghi | cần đối chiếu | Mô phỏng có "thích nghi sau 1 lần thất bại" cho diversity |
| 3 | Không mô hình hóa **bộ phát hiện kích hoạt MTD** và sai số của nó (FP → move vô ích, FN/độ trễ → lộ diện) | Giả thuyết – abstract không nhắc detector | **Đóng góp riêng**: MTD lai kích hoạt bởi cảnh báo AE thật (E10 phần 2) |
| 4 | Chi phí tài nguyên của MTD được nêu là vấn đề nhưng chưa đo trên thiết bị edge cụ thể | cần đối chiếu | Đo chi phí phía phát hiện (µs, KB, MB, µJ proxy) – E8 |
| 5 | Khả năng mở rộng khi số node/lỗ hổng tăng (bùng nổ đường tấn công) | cần đối chiếu | Ghi nhận; mô hình DT043 nhỏ (11 node, 9 đường) |
| 6 | Tính sẵn có của mã nguồn và cấu hình → khó tái lập số liệu chính xác | cần đối chiếu | Chỉ tái lập **xu hướng**, không so số tuyệt đối |
| 7 | Độ nhạy theo chu kỳ MTD | cần đối chiếu | Quét chu kỳ 5/10/20 bước |

## B. Paper tham chiếu kỹ thuật (baseline)
**Meidan Y. et al.** (2018). *N-BaIoT – Network-based Detection of IoT Botnet Attacks Using Deep Autoencoders.* IEEE Pervasive Computing. arXiv:1805.03409 (đã đọc toàn văn).

| Mục | Nội dung (theo paper) |
|---|---|
| Bài toán | Phát hiện thiết bị IoT bị nhiễm botnet ngay khi bắt đầu tấn công, từ lưu lượng mạng |
| Giả định | Lưu lượng ngay sau khi lắp đặt là sạch; mỗi thiết bị có hành vi riêng ổn định |
| Pipeline | 115 đặc trưng/gói → AE sâu **riêng từng thiết bị**, huấn luyện chỉ trên benign → MSE → ngưỡng `tr* = mean + std` (DSopt) → majority vote cửa sổ `ws*` nhỏ nhất cho FPR = 0 trên DSopt |
| Kiến trúc | encoder 75%, 50%, 33%, 25% đầu vào, decoder đối xứng (Keras) |
| Chia dữ liệu | benign mỗi thiết bị chia **theo thời gian** 3 phần bằng nhau: DStrn, DSopt, DStst-benign |
| Baseline | LOF, One-Class SVM, Isolation Forest (tối ưu tr, ws như AE) |
| Kết quả | TPR 100% mọi thiết bị; FPR 0.007 ± 0.01 (SVM 0.026 ± 0.029, IF 0.027 ± 0.041, LOF 0.086 ± 0.081); thời gian phát hiện 174 ± 212 ms; object 172 kB |
| Hạn chế | 1 lần chia, không nhiều seed; siêu tham số tối ưu riêng từng thiết bị (η, epochs 100–800); ws* chọn để FPR = 0 trên DSopt; không lượng tử hóa/đo edge; test mất cân bằng; 9 thiết bị, 2 botnet, lab |

## C. Khác biệt có chủ đích khi tái lập B0
| Điểm | Meidan 2018 | DT043 | Lý do |
|---|---|---|---|
| Trùng lặp | không đề cập | khử trùng lặp trong từng file | chống thổi phồng kết quả |
| Ranh giới split | không đề cập | purge gap 500 dòng | đặc trưng cửa sổ 1 phút làm dòng liền kề gần giống nhau |
| Tối ưu | η, epochs tối ưu từng thiết bị | Adam lr 1e-3, early stopping (patience 8) trên DSopt | thống nhất, tái lập được |
| Chuẩn hóa | không nêu rõ | z-score per-device fit trên DStrn | yêu cầu đề: per-device normalization |
| Số lần chạy | 1 | 5 seed | yêu cầu đề: ≥ 3 lần chạy |
| Thời gian phát hiện | ms (có timestamp gốc) | số mẫu (CSV không có timestamp) | không đổi được sang ms |
