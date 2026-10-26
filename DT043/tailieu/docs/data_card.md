# Data card – N-BaIoT (bản dùng trong DT043)

| Mục | Giá trị |
|---|---|
| Tên | detection_of_IoT_botnet_attacks_N_BaIoT |
| Nguồn | UCI Machine Learning Repository – https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot |
| DOI | 10.24432/C5RC8J |
| Tác giả | Y. Meidan, M. Bohadana, Y. Mathov, Y. Mirsky, D. Breitenbacher, A. Shabtai, Y. Elovici |
| Ngày đóng góp | 18/03/2018 (file mô tả ghi: "databases may change over time without name change") |
| Giấy phép | **CC BY 4.0** – được dùng, chia sẻ, chỉnh sửa với điều kiện ghi nguồn |
| Trích dẫn bắt buộc | Meidan et al., "N-BaIoT: Network-based Detection of IoT Botnet Attacks Using Deep Autoencoders", IEEE Pervasive Computing 17(3), 2018; bộ trích đặc trưng: Mirsky et al., "Kitsune", NDSS 2018 |
| Phiên bản tải | File zip UCI, tải lúc 2026-10-11T04:41:52Z, 1,772,922,927 byte |
| SHA-256 zip | `64929678b081d8e579a8d7c488cf11cc588403f282d5fb065b4156edbd55de9b` |
| Manifest | `data/MANIFEST.sha256` (107 file); kiểm tra lại bằng `python scripts/02_verify_manifest.py` |

## Nội dung
- 9 thiết bị IoT thương mại (chuông cửa, camera, baby monitor, thermostat, webcam) trong mạng lab.
- Mỗi dòng = "ảnh chụp hành vi" khi một gói tin đến: **115 đặc trưng** = 23 thống kê × 5 cửa sổ thời gian suy giảm (L5 ≈ 100 ms, L3 ≈ 500 ms, L1 ≈ 1.5 s, L0.1 ≈ 10 s, L0.01 ≈ 1 phút).
  - Nhóm luồng: `MI_dir` (MAC-IP nguồn), `H` (IP nguồn), `HH` (kênh IP→IP), `HH_jit` (jitter của kênh), `HpHp` (socket IP:port→IP:port).
  - Thống kê: weight, mean, variance/std, magnitude, radius, covariance, pcc.
- Nhãn theo file: `benign_traffic.csv`; BASHLITE (`gafgyt_attacks`: combo, junk, scan, tcp, udp); Mirai (`mirai_attacks`: ack, scan, syn, udp, udpplain). Ennio_Doorbell và Samsung_SNH_1011_N_Webcam **không có Mirai**.
- Không có cột thời gian, không có IP/MAC thô, không có payload → **không có dữ liệu cá nhân trực tiếp**.

## Chất lượng (sinh bởi `scripts/03_prepare.py`, xem `results/data_quality/`)
| Kiểm tra | Kết quả |
|---|---|
| Schema (115 cột, đúng tên/thứ tự, kiểu số) | 100% file đạt |
| NaN / ±inf | 0 |
| Cột hằng trong từng file | 0 |
| Trùng lặp chính xác | 157,779 dòng (2.2%) – benign 42,432 (Danmini 18.5%), gafgyt/tcp 64,560, gafgyt/udp 50,787 |
| Sau khử trùng | 6,904,827 dòng |
| Mất cân bằng attack : benign | 5.5× – 61.8× tùy thiết bị |
| Giá trị cực lớn | tới 5.88e17 (variance/covariance) → MSE tính bằng float64 |

## Cách dùng trong dự án (chống rò rỉ)
1. Khử trùng lặp chính xác trong từng file, giữ thứ tự dòng.
2. Benign mỗi thiết bị chia **theo thứ tự thời gian** 1/3 DStrn – 1/3 DSopt – 1/3 test, bỏ **500 dòng đệm** ở mỗi ranh giới.
3. Loại khỏi test mọi dòng trùng hash với DStrn/DSopt (đã kiểm tra: 0 dòng trùng sau bước 1).
4. Scaler z-score fit **chỉ trên DStrn** của đúng thiết bị.
5. Ngưỡng, cửa sổ, early stopping chỉ dùng DSopt (benign). Dữ liệu tấn công chỉ xuất hiện ở test.
6. Majority vote không vượt ranh giới giữa các file.

## Dữ liệu dẫn xuất được nộp
Chỉ nộp thống kê tổng hợp (`results/data_quality/*.csv`), điểm/metric của mô hình và model (vài chục KB). **Không** nộp lại dữ liệu thô 1.7 GB. Người dùng tải lại bằng `scripts/01_download.py` và kiểm tra bằng manifest.
