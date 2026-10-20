# Phiếu tái lập bài báo

## A. Paper chính (đề giao)
**Masud M.T., Keshk M., Moustafa N., Turnbull B., Susilo W.** (2025). *Vulnerability defence using hybrid moving target defence in Internet of Things systems.* Computers & Security, 153, 104380. DOI 10.1016/j.cose.2025.104380. Open Access (CC BY), online 28/02/2025.

> Nguồn thông tin: **toàn văn PDF Open Access** (17 trang) lưu tại `docs/Vulnerability defence using hybrid moving target defence in Internet of.pdf`, đã đọc đầy đủ ngày 20/10/2026. Kết quả tái lập chi tiết: [tai_lap_paper_chinh.md](tai_lap_paper_chinh.md).

| Mục | Nội dung (theo toàn văn) |
|---|---|
| Bài toán | MTD liên tục thay đổi bề mặt tấn công; thiếu đánh giá hiệu quả **kết hợp** nhiều kỹ thuật MTD xét thời gian, chi phí, công sức; IoT không đồng nhất, tài nguyên hạn chế |
| Phương pháp | *Vulnerability Defence* dựa trên **3-layer THARM** = (N, U, S, L, C): U – đồ thị tấn công giữa VM, S – đồ thị tấn công giữa dịch vụ, L – cây tấn công (OR) lỗ hổng OS + dịch vụ của từng VM (Definition 1–4) |
| Kỹ thuật MTD | **Shuffle** (VM live migration, IP shuffling qua SDN – Algorithm 1), **Diversity** (đổi OS: Windows 11 → Linux, FreeBSD → Windows 11, Linux → FreeBSD), **Redundancy** (nhân bản VM); kích hoạt **time-based**, chu kỳ **10 phút**; shuffle và redundancy không chạy đồng thời, diversity chạy song song được |
| Dữ liệu / kịch bản | **Không có dataset** ("No data was used"). Mạng mô phỏng: 4 host, **8 VM** (Linux: V1, V4, V7, V8; Windows 11: V2, V5; FreeBSD: V3, V6), mỗi VM 2 dịch vụ (s1–s14); V8 là CSDL đích. **18 CVE hệ điều hành** (Bảng 1) + **14 CVE dịch vụ** (Bảng 2) kèm CVSS base score, impact, exploitability, attack cost; đồ thị VM theo Definition 2 |
| Metric | ASP, Attack Risk (AR), Attack Cost (AC), Return on Attack (RoC = R/AC), độ trung tâm (closeness, degree, betweenness – chọn VM cần MTD), IPV, PSV (Algorithm 2–3) |
| Kết quả chính | Ví dụ V5: shuffle R_s = 167.38, AC_s = 666.2, RoC_s = 1.01; diversity R_d = 163.73, AC_d = 624.73, RoC_d = 1.04; redundancy R_r = 260.84, AC_r = 878.3, RoC_r = 1.46; kết luận: **shuffle + diversity** tốt nhất (ASP thấp hơn, rủi ro thấp hơn, chi phí tấn công cao hơn); S+D+R giảm AR và RoC, tăng độ tin cậy |
| Mã nguồn | Không công bố mã nguồn |
| Không có | autoencoder, N-BaIoT, lượng tử hóa, đo edge, bộ phát hiện xâm nhập thật → **khác chủ đề DT043** |

### Điểm hạn chế / cần tái lập (≥ 5) – đã đối chiếu toàn văn
| # | Hạn chế / điểm cần tái lập | Trạng thái (toàn văn) | Cách DT043 xử lý |
|---|---|---|---|
| 1 | Chỉ mô phỏng bằng mô hình đồ thị, không triển khai thiết bị thật; tác giả tự nêu chưa đo QoS | **Xác nhận** (mục 5) | Track B cũng chỉ mô phỏng, nêu rõ giới hạn |
| 2 | Xác suất khai thác gán tĩnh theo CVSS, không mô hình kẻ tấn công thích nghi | **Xác nhận** (Bảng 1–2, mục 6 tự nêu "fixed vulnerability") | `harm.py` mô phỏng "thích nghi sau 1 lần thất bại" cho diversity |
| 3 | Không mô hình bộ phát hiện kích hoạt MTD và sai số của nó; paper chỉ xét time-based dù có nêu hybrid | **Xác nhận** (mục 2.1: "we considered time-based MTD") | **Đóng góp riêng**: MTD lai kích hoạt bởi cảnh báo AE thật (E10) |
| 4 | Chi phí tài nguyên của MTD được nêu nhưng không đo trên thiết bị | **Xác nhận** | Đo chi phí phía phát hiện (µs, KB, MB, µJ proxy) – E8 |
| 5 | Công thức in mâu thuẫn: Eq. 1 "1 − (Π + Π)" có thể âm, Eq. 2–3 ghi "∏" nhưng số trong bài là tổng; danh sách cạnh sau shuffle bị cắt bằng "…"; R_V2 = 16.28 và AC theo VM (37.5–46.4) không suy ra được từ Bảng 1–2 | **Phát hiện khi tái lập** (E11) | Diễn giải R = Σ E·I (khớp mọi giá trị R mức VM paper dùng ±0.01), ghi rõ chỗ không tái lập được |
| 6 | Không công bố mã nguồn, Bảng 4 (ASP/AC/AR từng VM) không nêu cách tính đủ để tái lập | **Xác nhận** | Tái lập từ bảng/hình; đối chiếu từng số trong `results/tables/tharm_*_vs_paper.csv` |
| 7 | Topology không nhất quán: Definition 2 thiếu cạnh V6 → V4 có trong Hình 3; kết luận "S+D tốt nhất" chỉ đúng với topology Hình 3 | **Phát hiện khi tái lập** (E11) | Chạy cả hai topology và báo cáo cả hai |

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
