# KẾ HOẠCH LÀM BÀI GIỮA KỲ – DT043

**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ (huấn luyện theo từng thiết bị + đánh giá khả năng triển khai edge)

| Mục | Nội dung |
|---|---|
| Sinh viên | Hoàng Thanh Trà – MSSV 1150080120 – Lớp 11_ĐHCNPM_2 |
| Ngày lập kế hoạch | 11/10/2026 |
| Giả định thời hạn | 4 tuần (12/10 → 08/11/2026). Nếu hạn nộp khác, co/giãn theo tỷ lệ ở mục 11 |
| Dataset | N-BaIoT – UCI ML Repository, DOI 10.24432/C5RC8J, giấy phép CC BY 4.0 |
| Paper chính (đề giao) | Masud, Keshk, Moustafa, Turnbull, Susilo (2025). *Vulnerability defence using hybrid moving target defence in Internet of Things systems.* Computers & Security 153, 104380. DOI 10.1016/j.cose.2025.104380 (Open Access, CC BY) |
| Paper tham chiếu kỹ thuật | Meidan et al. (2018). *N-BaIoT—Network-Based Detection of IoT Botnet Attacks Using Deep Autoencoders.* IEEE Pervasive Computing. arXiv:1805.03409 |

---

## 0. Tóm tắt nhanh

1. Xây **bộ phát hiện bất thường autoencoder (AE) riêng cho từng thiết bị** trong 9 thiết bị của N-BaIoT, chỉ học trên lưu lượng benign, chuẩn hóa theo từng thiết bị.
2. **Baseline** = tái lập AE của Meidan 2018 (115 → 75%-50%-33%-25% → 115, ngưỡng `tr* = mean + std`, cửa sổ majority vote `ws*`), so với baseline "global" (một model cho mọi thiết bị) và Isolation Forest.
3. **Biến thể/cải tiến** = AE nhẹ (ít tham số hơn ≥4 lần) + **lượng tử hóa TFLite int8** + **hiệu chỉnh lại ngưỡng sau lượng tử hóa** cho từng thiết bị.
4. **Edge benchmark**: đo F1, kích thước model, bộ nhớ, latency p50/p95/p99, throughput và energy proxy trên cấu hình "edge giả lập" (1 luồng, ghim 1 lõi E-core) và Raspberry Pi nếu mượn được.
5. **Cầu nối với paper chính (MTD)**: tái lập có chọn lọc cách đánh giá MTD bằng mô hình đồ thị tấn công rút gọn, rồi bổ sung biến thể **"hybrid MTD kích hoạt bởi cảnh báo AE"**. Đây là phần đóng góp riêng nối hai mảng.
6. Tối thiểu **5 seed** cho mỗi cấu hình, lưu toàn bộ config/log/artifact, báo cáo mean ± std, khoảng tin cậy 95% và kiểm định Wilcoxon.

---

## 1. ⚠️ Phát hiện quan trọng: paper chính KHÔNG cùng chủ đề với tên đề tài

Theo abstract chính thức (lấy qua Crossref/OpenAlex ngày 11/10/2026), paper DOI 10.1016/j.cose.2025.104380:

- nghiên cứu **Moving Target Defence (MTD)**, tức là liên tục thay đổi bề mặt tấn công;
- đề xuất phương pháp *Vulnerability Defence* dùng **mô hình 3-layer Temporal Hierarchical Attack Representation Model (3-layer-THARM)**, một mô hình đồ thị/cây tấn công theo thời gian;
- đánh giá bằng các **security metric**: xác suất tấn công thành công, attack risk, attack cost, đường tấn công;
- kết luận: **kết hợp các kỹ thuật MTD khác nhóm (shuffle + diversity)** cho kết quả tốt hơn dùng riêng lẻ;
- **không** nhắc tới autoencoder, N-BaIoT, quantization hay edge benchmark.

**Hệ quả:** không thể "tái lập kết quả" của paper chính trên N-BaIoT bằng autoencoder. Vì vậy chia làm hai track:

| Track | Tỷ trọng | Nội dung | Vai trò với yêu cầu đề |
|---|---|---|---|
| **A – Lõi** | ~70% | Per-device AE trên N-BaIoT, chuẩn hóa, model nhẹ, quantization, edge benchmark. Baseline tái lập Meidan 2018 | Đáp ứng toàn bộ phần "Triển khai cốt lõi / Thực nghiệm / Đánh giá" |
| **B – Cầu nối** | ~30% | Tái lập **có chọn lọc** phần đánh giá MTD của paper chính (mô hình HARM rút gọn: shuffle / diversity / kết hợp), sau đó thêm biến thể **MTD lai (time-based + event-based) trong đó sự kiện là cảnh báo của AE** ở Track A | Đáp ứng "tái lập có chọn lọc bài báo Q1 + bổ sung ≥1 biến thể phù hợp" |

**Việc cần làm ngay trong tuần 1:** hỏi giảng viên một câu ngắn, ví dụ:
> "Thưa thầy/cô, đề DT043 (autoencoder nhẹ, N-BaIoT) gắn với paper 10.1016/j.cose.2025.104380 về Moving Target Defence/THARM, paper này không dùng autoencoder hay N-BaIoT. Em dự định tái lập có chọn lọc phần đánh giá MTD của paper và dùng AE làm bộ kích hoạt cho MTD lai, còn baseline AE tái lập theo Meidan 2018. Hướng này có phù hợp không ạ?"

- Nếu giảng viên đồng ý → làm đúng kế hoạch này.
- Nếu giảng viên cho đổi paper → Track B thu nhỏ còn phần thảo luận, dồn thời gian cho Track A (thêm ablation và benchmark Raspberry Pi).

---

## 2. Phạm vi, câu hỏi nghiên cứu, giả thuyết, đối tượng đánh giá

### 2.1 Phạm vi
- **Trong phạm vi:** phát hiện bất thường không giám sát (chỉ học benign), từng thiết bị một; suy luận trên vector đặc trưng 115 chiều có sẵn trong N-BaIoT; lượng tử hóa sau huấn luyện (PTQ); đo tài nguyên khi suy luận; mô phỏng MTD hoàn toàn trên máy (in-silico).
- **Ngoài phạm vi:** bắt gói tin và trích đặc trưng thời gian thực; chạy Mirai/BASHLITE thật; phân loại đa lớp loại tấn công (chỉ phân tích lỗi theo loại); triển khai MTD trên mạng thật.

### 2.2 Đối tượng đánh giá
- 9 bộ phát hiện (mỗi thiết bị một bộ) × các cấu hình model/quantization.
- Pipeline suy luận trên cấu hình edge giả lập (và Raspberry Pi nếu có).
- Chính sách MTD mô phỏng (Track B).

### 2.3 Câu hỏi nghiên cứu (RQ), giả thuyết (H) và tiêu chí thành công
Tiêu chí phải được **chốt và commit vào `docs/tieu_chi_thanh_cong.md` TRƯỚC khi chạy trên tập test**. Commit timestamp là bằng chứng không chỉnh tiêu chí theo kết quả.

| RQ | Câu hỏi | Giả thuyết | Tiêu chí thành công (đề xuất, chốt trước khi chạy) |
|---|---|---|---|
| RQ1 | Tái lập baseline Meidan có đạt mức paper không? | H1: AE per-device đạt TPR ≈ 1 và FPR thấp ở mức cửa sổ | TPR trung bình ≥ 0.99, FPR trung bình ≤ 0.02 (paper: TPR 100%, FPR 0.007 ± 0.01) |
| RQ2 | Chuẩn hóa + model theo từng thiết bị có tốt hơn một model chung? | H2: per-device > global | macro-F1 cao hơn ở ≥ 7/9 thiết bị, Wilcoxon p < 0.05 |
| RQ3 | AE nhẹ giữ được hiệu năng? | H3: giảm ≥ 4× tham số mà macro-F1 giảm ≤ 0.01 | ΔmacroF1 ≤ 0.01 (tuyệt đối), tham số ≤ 25% baseline |
| RQ4 | Lượng tử hóa int8 có làm giảm chất lượng? Hiệu chỉnh lại ngưỡng có giúp không? | H4: full-int8 + hiệu chỉnh ngưỡng giảm F1 ≤ 0.005, kích thước ≈ 1/4 | ΔF1 ≤ 0.005; kích thước ≤ 30% bản fp32 |
| RQ5 | Có triển khai được trên edge không? | H5: đủ nhanh và nhẹ cho 1 lõi | p95 latency ≤ 1 ms/mẫu ở profile P1; model ≤ 50 KB; RSS tăng thêm ≤ 50 MB |
| RQ6 (Track B) | Chất lượng detector (FPR, độ trễ) ảnh hưởng thế nào tới hiệu quả và chi phí của MTD lai? | H6: hybrid MTD dùng AE giảm thời gian lộ diện so với time-based với cùng số lần "move"; FP làm tăng move vô ích tỷ lệ thuận với FPR | So sánh 3 chính sách trên cùng luồng dữ liệu; báo cáo đường cong trade-off |

---

## 3. Tài liệu nền và phiếu tái lập (Bước 1)

### 3.1 Phiếu tái lập paper chính → `docs/phieu_tai_lap_paper.md`
Tải PDF (Open Access) tại https://doi.org/10.1016/j.cose.2025.104380 rồi điền các mục:

| Mục | Cần trích | Ghi kèm |
|---|---|---|
| Bài toán | Vấn đề MTD trong IoT, khoảng trống (thiếu đánh giá MTD kết hợp; MTD tốn tài nguyên) | số trang/mục |
| Giả định | Mô hình kẻ tấn công, mức hiểu biết, cách gán xác suất khai thác (CVSS?), thời gian | |
| Pipeline | Cấu trúc 3 lớp của THARM; cách sinh trạng thái mạng theo thời gian; cách áp dụng shuffle/diversity/(redundancy?) | vẽ lại sơ đồ |
| Dữ liệu | Topology IoT dùng để thử, danh sách lỗ hổng/CVE, có công bố code/cấu hình không | |
| Metric | Định nghĩa chính xác: attack success probability, attack risk, attack cost, số đường tấn công… | ghi công thức |
| Kết quả mục tiêu | Các bảng/hình chính: giá trị metric theo từng kỹ thuật MTD và tổ hợp | chụp bảng → bảng ánh xạ |
| Hạn chế/điểm cần tái lập | ≥ 5 mục (xem 3.3) | |

### 3.2 Phiếu tóm tắt Meidan 2018 (đã đọc, dùng làm mục tiêu tái lập baseline)
| Thành phần | Theo paper |
|---|---|
| Đặc trưng | 115 = 23 đặc trưng × 5 cửa sổ thời gian (100 ms, 500 ms, 1.5 s, 10 s, 1 phút) |
| Model | AE sâu, mỗi thiết bị một model; encoder 75%, 50%, 33%, 25% kích thước đầu vào, decoder đối xứng; Keras |
| Chia dữ liệu | Benign của mỗi thiết bị chia **theo thời gian** thành 3 phần bằng nhau: DStrn (train), DSopt (tối ưu η, epochs, ngưỡng, cửa sổ), phần benign của DStst |
| Ngưỡng | `tr* = mean(MSE_DSopt) + std(MSE_DSopt)` |
| Cửa sổ | `ws*` = cửa sổ ngắn nhất sao cho majority vote cho FPR = 0% trên DSopt |
| Baseline so sánh | LOF, One-Class SVM, Isolation Forest (tối ưu tr, ws giống AE) |
| Kết quả | TPR 100% mọi thiết bị; FPR trung bình 0.007 ± 0.01 (SVM 0.026 ± 0.029, IF 0.027 ± 0.041, LOF 0.086 ± 0.081); thời gian phát hiện 174 ± 212 ms |
| Bảng 3 | Mỗi thiết bị có η, epochs (100–800), tr* (0.004–0.074), ws* (20–82), object size 172 kB |
| Ghi chú | Ennio Doorbell và Samsung SNH-1011-N chỉ có BASHLITE (không có Mirai) |

### 3.3 Hạn chế/điểm cần tái lập (≥ 5 – giả thuyết, phải XÁC NHẬN hoặc LOẠI BỎ khi đọc full text, ghi số trang)
**Paper chính (MTD/THARM):**
1. Đánh giá chủ yếu bằng mô hình/mô phỏng đồ thị tấn công, cần kiểm tra có testbed thiết bị thật không.
2. Xác suất khai thác có thể gán tĩnh từ CVSS, chưa phản ánh hành vi kẻ tấn công thích nghi.
3. Thời điểm kích hoạt MTD (theo chu kỳ hay theo sự kiện) và **sai số của bộ phát hiện kích hoạt** (FP/FN) có thể chưa được mô hình hóa. Track B nhắm vào khoảng trống này.
4. Paper nêu MTD có thể làm "quá tải tài nguyên", cần kiểm tra mức đo cụ thể (CPU/RAM/năng lượng trên thiết bị IoT).
5. Khả năng mở rộng khi số node/lỗ hổng tăng (bùng nổ số đường tấn công).
6. Tính sẵn có của mã nguồn và cấu hình topology/CVE, ảnh hưởng trực tiếp đến khả năng tái lập.
7. Độ nhạy của kết quả theo tham số chu kỳ shuffle/diversity.

**Meidan 2018 (đã xác nhận từ bài):**
1. Chỉ một lần chia dữ liệu, không báo cáo nhiều seed/CV, nên không có khoảng tin cậy.
2. Siêu tham số (η, epochs đến 800) tối ưu riêng từng thiết bị, khó tái lập chính xác.
3. `ws*` được chọn để FPR = 0% trên DSopt, nên FPR test phụ thuộc mạnh vào độ "dễ đoán" của lưu lượng.
4. Không có lượng tử hóa, không đo latency/bộ nhớ khi suy luận trên edge (chỉ có training time và object size).
5. Tập test mất cân bằng (attack nhiều hơn benign rất nhiều), nên TPR/F1 lớp attack dễ "đẹp".
6. 9 thiết bị, 2 botnet, môi trường lab, nên khả năng tổng quát hóa sang thiết bị/botnet mới chưa rõ.

---

## 4. Dữ liệu N-BaIoT (Bước 2) → `docs/data_card.md`

### 4.1 Thông tin đã xác minh
- Nguồn: https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot
- File zip trực tiếp: `https://archive.ics.uci.edu/static/public/442/detection+of+iot+botnet+attacks+n+baiot.zip` (~1.7 GB, đã kiểm tra trả HTTP 200)
- Ngày đóng góp 18/03/2018; DOI 10.24432/C5RC8J; **CC BY 4.0** (bắt buộc ghi nguồn: trích dẫn Meidan 2018 và UCI).
- 7,062,606 dòng; 9 thiết bị; 1 lớp benign + 10 tấn công (BASHLITE: combo, junk, scan, tcp, udp; Mirai: ack, scan, syn, udp, udpplain).
- Mỗi thiết bị: `benign_traffic.csv`, `gafgyt_attacks.rar`, `mirai_attacks.rar` (nếu có). Giải nén `.rar` bằng UnRAR đã có tại `D:\Program Files\UnRAR.exe`.
- UCI **không cung cấp checksum**, nên ta tự tạo manifest SHA-256.

### 4.2 Việc phải làm và ghi lại
| Việc | Script | Đầu ra (commit được) |
|---|---|---|
| Tải zip, ghi URL, ngày giờ tải, kích thước, SHA-256 | `scripts/01_download.py` | `data/DOWNLOAD_INFO.json` |
| Giải nén zip + rar, tạo manifest SHA-256 từng file | `scripts/01_download.py` | `data/MANIFEST.sha256` |
| Kiểm tra manifest khi chạy lại | `scripts/02_verify_manifest.py` | exit code ≠ 0 nếu sai |
| Kiểm tra schema: 115 cột, đúng tên, đúng thứ tự, kiểu số | `src/nbaiot/data.py` | `results/data_quality/schema.json` |
| Thống kê chất lượng: số dòng/thiết bị/lớp, NaN, ±inf, cột hằng, trùng lặp chính xác (trong file và giữa các file), min/max | `scripts/03_prepare.py` | `results/data_quality/*.csv` |
| Chuyển sang Parquet float32 theo thiết bị (giảm RAM: 7M × 115 × 4 B ≈ 3.2 GB) | `scripts/03_prepare.py` | `data/processed/<device>/*.parquet` (không commit) |

### 4.3 Chống rò rỉ train/test (bắt buộc, có test tự động)
1. **Chia theo thời gian** (giữ thứ tự dòng như Meidan): benign → DStrn 1/3 | DSopt 1/3 | DStst-benign 1/3. Thêm **khoảng đệm (purge gap)**, ví dụ bỏ 500 dòng ở mỗi ranh giới, vì đặc trưng cửa sổ 1 phút khiến các dòng liền kề gần như trùng nhau.
2. **Khử trùng lặp** chính xác trong từng file. Sau khi chia, xóa khỏi test mọi dòng có hash trùng với DStrn/DSopt. Ghi số dòng bị loại.
3. **Scaler fit chỉ trên DStrn của đúng thiết bị đó.** DSopt/test chỉ `transform`.
4. Ngưỡng `tr*`, cửa sổ `ws*`, early-stopping, chọn epochs **chỉ dùng DSopt (benign)**. Dữ liệu attack **không bao giờ** dùng khi huấn luyện hay chọn tham số.
5. Majority vote **không được trượt qua ranh giới giữa các file** (benign ↔ attack, attack ↔ attack).
6. Thí nghiệm đối chứng E6 cố tình chia ngẫu nhiên để **đo mức "đẹp giả" do rò rỉ**, đưa vào báo cáo như bằng chứng.

---

## 5. Môi trường tái lập (Bước 3)

### 5.1 Phần cứng (ghi vào báo cáo và `results/env_info.json`)
- CPU Intel Core i7-13650HX (14 lõi: 6P + 8E, 20 luồng), RAM 23.7 GB, Windows 11 Home, ổ D: còn ~700 GB.
- Chưa có Docker/WSL. Không bắt buộc. Nếu muốn đo dưới giới hạn CPU/RAM kiểu container thì cài thêm (tùy chọn).

### 5.2 Phần mềm
- **Python 3.11** trong venv riêng (KHÔNG dùng 3.14 mặc định vì TensorFlow chưa hỗ trợ). Máy đã có 3.11 (bản Microsoft Store). Nếu gặp lỗi đường dẫn thì cài bản 3.11 từ python.org.
- Thư viện: `tensorflow` (Keras + TFLite converter/interpreter), `numpy`, `pandas`, `pyarrow`, `scikit-learn`, `scipy`, `psutil`, `pyyaml`, `matplotlib`, `pytest`, `networkx` (Track B), `rarfile` (tùy chọn), `jupyter`.
- Khóa phiên bản: `requirements.txt` (phụ thuộc trực tiếp, có pin) + `requirements-lock.txt` (`pip freeze`) + `results/env_info.json` (sinh tự động: OS, CPU, RAM, phiên bản Python/TF/numpy, git commit).

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip freeze > requirements-lock.txt
```

### 5.3 Seed và tính tất định
- Danh sách seed cố định trong `configs/base.yaml`: `[42, 1337, 2024, 7, 123]`.
- Đặt `PYTHONHASHSEED`, `random.seed`, `np.random.seed`, `tf.keras.utils.set_random_seed`, `tf.config.experimental.enable_op_determinism()`; cố định số luồng TF (intra/inter-op).
- Mỗi lần chạy lưu: config đã resolve, seed, git commit hash, thời gian bắt đầu/kết thúc, log, model, metrics.

### 5.4 Cấu trúc thư mục
```
DT043/
├── KE_HOACH.md                  # file này
├── README.md                    # hướng dẫn chạy từ đầu (khung ở tuần 1, hoàn thiện tuần 4)
├── requirements.txt / requirements-lock.txt
├── configs/
│   ├── base.yaml                # đường dẫn, seed, split, purge gap, hyperparams mặc định
│   └── exp/E1_baseline.yaml … E9_mtd.yaml
├── docs/
│   ├── phieu_tai_lap_paper.md
│   ├── data_card.md
│   ├── threat_model.md
│   └── tieu_chi_thanh_cong.md   # commit TRƯỚC khi chạy test
├── data/                        # .gitignore toàn bộ, trừ 2 file dưới
│   ├── DOWNLOAD_INFO.json
│   └── MANIFEST.sha256
├── scripts/
│   ├── 00_env_info.py   01_download.py   02_verify_manifest.py   03_prepare.py
│   ├── 04_run_matrix.py 05_bench_edge.py 06_aggregate.py       07_mtd_sim.py
│   └── run_all.ps1              # chạy toàn bộ từ đầu
├── src/nbaiot/
│   ├── data.py  split.py  scaling.py  models.py  train.py  threshold.py
│   ├── quantize.py  metrics.py  bench.py  seed.py
│   └── mtd/harm.py  mtd/policy_sim.py
├── tests/                       # unit / integration / negative
├── notebooks/01_eda.ipynb
├── results/  raw/  tables/  figures/  data_quality/
├── artifacts/models/            # .keras, .tflite (vài chục KB, commit được)
└── report/                      # báo cáo .docx/.pdf, slide, link video
```
Thêm `DT043/data/raw/`, `DT043/data/interim/`, `DT043/data/processed/`, `DT043/.venv/` vào `.gitignore` gốc.

---

## 6. EDA và Threat model, trước khi huấn luyện (Bước 4)

### 6.1 EDA (`notebooks/01_eda.ipynb`)
- Số mẫu benign/attack theo thiết bị và loại tấn công → **mức mất cân bằng** (attack nhiều gấp nhiều lần benign).
- Phân phối 23 đặc trưng gốc theo 5 cửa sổ; cột hằng/gần hằng; tương quan giữa các cửa sổ.
- Tỷ lệ trùng lặp; tự tương quan theo thứ tự dòng (lý do bắt buộc chia theo thời gian).
- So sánh phân phối giữa các thiết bị (lý do cần per-device normalization).
- PCA/t-SNE trên mẫu nhỏ để minh họa benign và attack.

### 6.2 Threat model (`docs/threat_model.md`)
```
[Thiết bị IoT] ──LAN──> [Edge gateway: trích đặc trưng + AE per-device] ──> [Cloud/SOC: log, cảnh báo, điều phối MTD]
     ▲  trust boundary 1 (thiết bị không tin cậy)      ▲ trust boundary 2 (gateway ↔ cloud)
```
- **Tài sản:** thiết bị IoT, gateway, model + ngưỡng, luồng cảnh báo.
- **Kẻ tấn công:** botnet Mirai/BASHLITE (dò quét, brute-force Telnet, chiếm thiết bị, DDoS).
- **Giả định:** gateway tin cậy; dữ liệu benign lúc huấn luyện sạch (như Meidan); model không bị lộ.
- **Tấn công lên chính bộ phát hiện (chỉ thử offline):** đầu độc dữ liệu train (poisoning), né tránh bằng cách làm giống benign (mimicry/evasion), làm trôi phân phối (drift).
- **Quyền riêng tư:** đặc trưng là thống kê tổng hợp, không có payload; N-BaIoT không chứa dữ liệu cá nhân trực tiếp. Không thu thập lưu lượng của người khác.
- **Đạo đức:** chỉ dùng dữ liệu công khai, máy cá nhân; không chạy mã độc thật, không quét/tấn công mục tiêu thật; MTD chỉ mô phỏng.

---

## 7. Triển khai (Bước 5)

### 7.1 Pipeline
`load → schema check → dedup → chronological split + purge → per-device scaler (fit DStrn) → train AE (early stop trên DSopt) → MSE trên DSopt → tr*, ws* → (convert TFLite / quantize → recalibrate tr*) → evaluate test → benchmark → lưu artifact`

### 7.2 Baseline (rõ ràng, cố định)
| Mã | Mô tả | Tham số ≈ |
|---|---|---|
| **B0** | AE kiểu Meidan: 115-86-58-38-29-38-58-86-115, per-device z-score, `tr* = mean + std`, `ws*` như paper, fp32 | ~36.9k (≈144 KB fp32) |
| **B1** | Cùng kiến trúc nhưng **một model + một scaler chung** cho 9 thiết bị (global) | ~36.9k |
| **B2** | Isolation Forest per-device (non-NN, cùng cách chọn tr/ws) | – |

### 7.3 Biến thể / cải tiến
| Mã | Mô tả | Tham số ≈ |
|---|---|---|
| **V1** | AE nhẹ 115-32-8-32-115 | ~8.1k (≈4.6× nhỏ hơn) |
| **V2** | AE siêu nhẹ dùng 23 đặc trưng của **một** cửa sổ thời gian: 23-12-4-12-23. Chạy **cả 5 cửa sổ** và báo cáo hết, không chọn cửa sổ đẹp nhất trên test | ~0.7k |
| **Q-fp16 / Q-dyn / Q-int8** | TFLite: float16, dynamic-range int8, full-integer int8 (representative dataset = mẫu từ DStrn) | – |
| **★ Cải tiến chính** | **V1 + full-int8 + hiệu chỉnh lại `tr*`/`ws*` trên DSopt bằng chính model đã lượng tử hóa** (lượng tử hóa làm lệch phân phối MSE, nếu giữ ngưỡng fp32 thì FPR/TPR sẽ trượt) | – |
| V-thr (ablation) | Quy tắc ngưỡng: mean+std (paper) / mean+3std / percentile 99.9 | – |

### 7.4 Edge benchmark (`scripts/05_bench_edge.py`)
| Profile | Mô tả |
|---|---|
| P0 | PC đầy đủ (tham chiếu, batch 1 và batch 256) |
| **P1 – edge giả lập** | `num_threads=1`, ghim process vào **1 lõi E-core** bằng `psutil.Process().cpu_affinity([...])`, batch = 1. Lõi E-core tiết kiệm điện gần với CPU edge hơn |
| P2 (tùy chọn) | Raspberry Pi 4/5 nếu mượn được: chạy **cùng script**, cùng file `.tflite` |

Đo cho mỗi model × kiểu lượng tử:
- **Bộ nhớ:** kích thước file model (KB); RSS trước và sau khi nạp model và khi chạy (psutil); peak RSS.
- **Latency:** warm-up 200 lần, đo 10,000 lần suy luận 1 mẫu, lấy p50/p95/p99 và throughput (mẫu/giây). Lặp 5 lần, báo cáo mean ± std.
- **Energy proxy** (ghi rõ là *proxy*, không phải đo điện thật):
  1. MACs/suy luận, tính giải tích = tổng (in × out) của các lớp Dense (B0 ≈ 36k, V1 ≈ 8k, V2 ≈ 0.6k);
  2. CPU-time/suy luận × công suất giả định của 1 lõi → mJ/suy luận (ghi giả định công suất và nguồn);
  3. (tùy chọn) đo công suất package bằng HWiNFO khi chạy vòng lặp, trừ nền idle.
- Chi phí huấn luyện: thời gian train/thiết bị, số epoch thực tế.

### 7.5 Kiểm thử (`tests/`, chạy bằng `pytest`)
| Loại | Test |
|---|---|
| Unit | schema 115 cột; dedup đúng; split theo thời gian có purge gap; **không có hash trùng giữa train/opt/test**; scaler chỉ fit trên DStrn (kiểm tra mean/std); công thức `tr*`; tìm `ws*`; majority vote không vượt ranh giới file; tính metric đúng trên ví dụ nhỏ biết trước đáp án |
| Integration | Pipeline end-to-end trên **bộ dữ liệu tổng hợp nhỏ** (vài nghìn dòng) chạy < 1 phút; Keras và TFLite fp32 cho MSE lệch < 1e-4; TFLite int8 chạy được và ra quyết định |
| Negative / lỗi | CSV hỏng, thiếu hoặc thừa cột, sai thứ tự cột, NaN/±inf, file rỗng, dtype sai → phải raise lỗi rõ ràng; manifest sai checksum → dừng; nạp model của thiết bị A cho thiết bị B → bị chặn |
| Tấn công được phép (offline) | **Evasion/mimicry:** dịch dần mẫu attack về tâm benign theo hệ số α rồi đo TPR theo α. **Poisoning:** trộn x% ∈ {0.1, 1, 5}% mẫu attack vào DStrn rồi đo suy giảm. **Nhiễu đầu vào:** Gaussian noise trên test benign rồi đo FPR |

---

## 8. Ma trận thí nghiệm có kiểm soát (Bước 6)

Nguyên tắc: **mọi cấu hình được định nghĩa sẵn trong `configs/exp/`**, chạy đủ 5 seed × 9 thiết bị, **lưu toàn bộ** kết quả thô, không xóa lần chạy xấu, không chọn seed đẹp. Tập test chỉ dùng để đánh giá cuối, không dùng để chọn tham số.

| ID | Mục đích | Cấu hình | Số lần chạy |
|---|---|---|---|
| E0 | Kiểm tra pipeline | B0 trên dữ liệu tổng hợp + 1 thiết bị | smoke |
| **E1** | Tái lập baseline (RQ1) | B0 | 9 × 5 |
| **E2** | Per-device vs global (RQ2) | B0 vs B1 (và per-device scaler + model chung, ablation) | 9 × 5 × 2–3 |
| E3 | Baseline non-NN | B2 Isolation Forest | 9 × 5 |
| **E4** | Model nhẹ (RQ3) | V1; V2 × 5 cửa sổ | 9 × 5 × 6 |
| **E5** | Lượng tử hóa (RQ4) | {B0, V1, V2-best-on-DSopt} × {fp32, fp16, dyn, int8} × {giữ ngưỡng, hiệu chỉnh lại} | dùng lại model E1/E4 |
| E6 | Bằng chứng rò rỉ | B0 chia ngẫu nhiên, không purge, scaler fit trên toàn bộ | 9 × 3 |
| E7 | Ablation ngưỡng và cửa sổ | 3 quy tắc ngưỡng × ws ∈ {1, ws*, 2ws*} | dùng lại model |
| **E8** | Edge benchmark (RQ5) | mọi model .tflite × P0/P1/(P2) | 5 lần lặp |
| E9 | Robustness | evasion α, poisoning x%, noise | 9 × 3 |
| E10 | Track B (RQ6) | xem mục 10 | 5 seed mô phỏng |

Ước tính chi phí: mỗi model nhỏ (≤ 58k dòng train), CPU ~1–3 phút/model, tổng ~400–500 model, khoảng **8–15 giờ CPU**. Chạy song song nhiều process theo thiết bị và chạy qua đêm.

Lưu kết quả: `results/raw/<exp>/<device>/seed=<s>/{config.yaml, metrics.json, scores.parquet, train_log.csv, timing.json}` + `results/raw/runs_index.csv` (mỗi dòng một lần chạy).

---

## 9. Đánh giá và phân tích (Bước 7)

### 9.1 Metric (không chỉ Accuracy)
- **Chính:** macro-F1 (benign + attack), F1 lớp attack, Precision, Recall/TPR, **FPR**, balanced accuracy, MCC, ROC-AUC, PR-AUC trên điểm MSE. Tính ở **cả mức mẫu và mức cửa sổ (sau majority vote)**.
- Do test rất mất cân bằng (attack ≫ benign), F1 lớp attack dễ cao ảo. Vì vậy báo cáo thêm **F1 trên test cân bằng** (bootstrap lấy số attack bằng số benign, 1000 lần).
- **Recall theo từng loại tấn công** (10 loại) và **độ trễ phát hiện** tính bằng số mẫu (N-BaIoT không có timestamp nên không đổi ra ms như Meidan; ghi rõ khác biệt này).
- **Tài nguyên:** tham số, KB, RSS, latency p50/p95/p99, throughput, MACs, mJ proxy, thời gian train.

### 9.2 Thống kê
- Mean ± std qua 5 seed, **KTC 95%** (phân phối t với n = 5; hoặc bootstrap).
- So sánh cặp (B0 vs B1, B0 vs V1, fp32 vs int8): **Wilcoxon signed-rank** trên 9 thiết bị (mỗi thiết bị lấy trung bình 5 seed), hiệu chỉnh **Holm** khi so nhiều cặp, kèm effect size.
- Chỉ dùng chữ "tốt hơn / vượt" khi kiểm định có ý nghĩa. Không tuyên bố vượt paper vì khác điều kiện thí nghiệm.

### 9.3 Phân tích bắt buộc
- **Phân tích lỗi:** FP rơi vào đoạn benign nào (vẽ MSE theo thứ tự dòng); FN rơi vào loại tấn công nào (dự đoán: các kiểu *scan* khó hơn flood); thiết bị khó (Meidan ghi nhận baby monitor có FPR cao nhất); so histogram MSE benign và attack.
- **Độ ổn định:** độ lệch giữa các seed; độ nhạy của F1/FPR theo ngưỡng (vẽ đường cong); biến động `ws*`.
- **Ablation:** per-device scaler, kích thước model, cửa sổ thời gian, quy tắc ngưỡng, hiệu chỉnh ngưỡng sau lượng tử hóa, purge gap.
- **Chi phí tính toán/triển khai:** bảng "chất lượng và chi phí" (macro-F1 so với KB, latency, mJ), vẽ biểu đồ Pareto.
- **Giới hạn:** dữ liệu lab 2018; không có pipeline trích đặc trưng thời gian thực; edge chỉ giả lập nếu không có Pi; energy là proxy; MTD là mô phỏng.

### 9.4 Bảng ánh xạ kết quả với paper (mẫu, điền khi có số)
**Với Meidan 2018:**
| Chỉ số | Meidan 2018 | B0 của em (mean ± std, 5 seed) | V1+int8 hiệu chỉnh | Khác biệt điều kiện |
|---|---|---|---|---|
| TPR (mức cửa sổ) | 100% mọi thiết bị | | | dedup, purge gap, nhiều seed |
| FPR trung bình | 0.007 ± 0.01 | | | |
| tr* từng thiết bị | 0.004–0.074 | | | scaler có thể khác |
| ws* từng thiết bị | 20–82 | | | |
| Kích thước model | 172 kB | | | Keras object vs .tflite |
| Thời gian phát hiện | 174 ± 212 ms | (số mẫu) | | không có timestamp |
| So với baseline | SVM/IF/LOF FPR 0.026/0.027/0.086 | IF: | | |

**Với paper chính (MTD):** cột = metric của paper (attack success probability, risk, attack cost) × {không MTD, shuffle, diversity, kết hợp}. Hàng = "Paper báo cáo" / "Mô phỏng rút gọn của em" / "Xu hướng có khớp không".

---

## 10. Track B – Tái lập có chọn lọc MTD và biến thể "MTD lai kích hoạt bởi AE"

**B-1. Tái lập rút gọn (theo định nghĩa trong paper, điền sau khi đọc full text):**
- Dựng mạng IoT nhỏ bằng `networkx`: 9 thiết bị loại như N-BaIoT + gateway + server + điểm vào của kẻ tấn công.
- Lớp lỗ hổng: gán lỗ hổng điển hình bị botnet IoT khai thác (ví dụ Telnet/mật khẩu mặc định, CVE công khai), xác suất lấy từ CVSS **theo cách paper làm**.
- Tính các metric của paper cho 4 trường hợp: không MTD / shuffle / diversity / shuffle + diversity.
- **Mục tiêu tái lập:** xu hướng "kết hợp tốt hơn đơn lẻ" (không kỳ vọng trùng số vì topology khác).

**B-2. Biến thể đóng góp riêng (nối với Track A):**
- Dùng **chuỗi quyết định thật** của AE (V1+int8) trên luồng test từng thiết bị (benign rồi đến các đoạn attack).
- So sánh 3 chính sách: (i) time-based (shuffle mỗi T bước), (ii) event-based (shuffle khi AE cảnh báo, có cooldown), (iii) **hybrid** (cả hai).
- Đo: **thời gian lộ diện** (từ lúc bắt đầu tấn công đến lần "move" đầu tiên), **số lần move/1000 bước** (chi phí), **số move vô ích do FP**, attack success probability tích lũy (từ mô hình B-1).
- Quét T và FPR (bằng cách đổi ngưỡng) để vẽ **đường trade-off an ninh và chi phí**. Đây là chỗ trả lời RQ6 và nối với hạn chế số 3–4 của paper chính.
- Toàn bộ là mô phỏng trên máy cá nhân.

---

## 11. Lịch thực hiện (4 tuần, bắt đầu 12/10/2026)

| Tuần | Ngày | Việc | Đầu ra / checkpoint |
|---|---|---|---|
| **1** | 12–13/10 | Đọc paper chính và điền phiếu tái lập; **hỏi giảng viên** về độ lệch paper | `docs/phieu_tai_lap_paper.md` |
| | 13–14/10 | Tạo venv 3.11, `requirements`, khung thư mục, `00_env_info.py`, `.gitignore` | `env_info.json`, lock file |
| | 14–16/10 | Viết `01_download`, `02_verify`, `03_prepare`; tải, giải nén, tạo manifest, data quality | `MANIFEST.sha256`, `data_card.md` |
| | 17–18/10 | EDA notebook, threat model, **chốt tiêu chí thành công và commit** | `01_eda.ipynb`, `threat_model.md`, `tieu_chi_thanh_cong.md` ✅ **Checkpoint 1** |
| **2** | 19–20/10 | `split/scaling/models/train/threshold` + unit test chống rò rỉ | `pytest` xanh |
| | 21–22/10 | E0 smoke → **E1 baseline** (5 seed × 9), so với Meidan | bảng E1 ✅ **Checkpoint 2: tái lập baseline** |
| | 23–25/10 | E2 (global), E3 (IF), E6 (rò rỉ); chạy đêm | raw results |
| **3** | 26–27/10 | E4 model nhẹ; `quantize.py` + test Keras↔TFLite | `.tflite` artifacts |
| | 28–29/10 | E5 lượng tử hóa + hiệu chỉnh ngưỡng; E7 ablation | bảng E5/E7 |
| | 30/10–01/11 | E8 edge benchmark (P0, P1, Pi nếu có); E9 robustness | ✅ **Checkpoint 3: đủ số liệu Track A** |
| **4** | 02–03/11 | Track B: B-1 HARM rút gọn, B-2 mô phỏng MTD lai | bảng/đồ thị E10 |
| | 03–04/11 | `06_aggregate`: bảng tổng, KTC 95%, Wilcoxon, hình; bảng ánh xạ paper | `results/tables`, `figures` |
| | 04–07/11 | Viết báo cáo 20–30 trang, slide, quay video demo 5–7 phút | `report/` |
| | 07–08/11 | **Chạy lại từ đầu bằng README trên thư mục sạch** (clone mới), dọn secret/file lớn, nộp | ✅ **Checkpoint 4: nộp** |

Bộ đệm: nếu trễ, cắt theo thứ tự E9 → V2 năm cửa sổ (chỉ giữ 1 cửa sổ chọn trên DSopt) → P2 Pi → B-1 rút gọn còn 1 kỹ thuật MTD. **Không cắt** E1, E2, E5, E8, test chống rò rỉ, 5 seed.

---

## 12. Sản phẩm nộp (Bước 8) – checklist

- [ ] Mã nguồn sạch (`src/`, `scripts/`), `pytest` pass, không có đường dẫn tuyệt đối cứng (đưa vào config)
- [ ] `requirements.txt` + `requirements-lock.txt` + `env_info.json`
- [ ] `README.md`: cài đặt → tải dữ liệu → kiểm checksum → chuẩn bị → chạy ma trận → benchmark → tổng hợp bảng/hình (một lệnh `scripts/run_all.ps1`)
- [ ] `data/DOWNLOAD_INFO.json`, `data/MANIFEST.sha256`, `docs/data_card.md` (nguồn, CC BY 4.0, ngày tải, schema, thống kê chất lượng)
- [ ] **Không** commit dữ liệu thô 1.7 GB, chỉ nộp dữ liệu dẫn xuất nhỏ hợp lệ (bảng thống kê, điểm MSE tóm tắt) kèm ghi nguồn
- [ ] `results/raw` (toàn bộ lần chạy), `results/tables`, `results/figures`, artifacts model
- [ ] Bảng ánh xạ kết quả với Meidan 2018 và với paper chính
- [ ] Báo cáo 20–30 trang có mục **"Đóng góp riêng"** và **"Giới hạn"**
- [ ] Slide và video ngắn (demo: chạy test, chạy benchmark P1, đọc bảng kết quả)
- [ ] Rà secret/dữ liệu cá nhân: không token, không đường dẫn chứa thông tin cá nhân không cần thiết, không file tạm Office (`~$*`)
- [ ] Cập nhật bảng "Danh sách bài" trong `README.md` gốc của repo

---

## 13. Dàn ý báo cáo (~26 trang)

| Chương | Nội dung | Trang |
|---|---|---|
| 1. Mở đầu | Bối cảnh botnet IoT, mục tiêu, RQ/H, đóng góp riêng, phạm vi | 2 |
| 2. Tài liệu nền | Phiếu tái lập paper chính (MTD/THARM) và ≥5 hạn chế; Meidan 2018; AE, quantization, edge AI; lý do chia 2 track | 4 |
| 3. Dữ liệu và threat model | Data card, EDA, mất cân bằng, rò rỉ và cách chặn, threat model, đạo đức | 4 |
| 4. Phương pháp | Pipeline, B0/B1/B2, V1/V2, lượng tử hóa và hiệu chỉnh ngưỡng, edge benchmark, mô phỏng MTD | 5 |
| 5. Thiết lập thực nghiệm | Phần cứng/phần mềm, seed, ma trận E0–E10, metric, thống kê | 2 |
| 6. Kết quả | RQ1→RQ6, bảng + hình, KTC 95%, kiểm định | 5 |
| 7. Phân tích | Lỗi, ổn định, ablation, robustness, chi phí, Pareto | 3 |
| 8. Thảo luận và kết luận | Giới hạn, mối đe dọa với tính hợp lệ, hướng phát triển | 1–2 |
| Phụ lục | Bảng ánh xạ paper, cấu hình, hướng dẫn tái lập, test | ngoài số trang |

---

## 14. Rủi ro và phương án dự phòng

| Rủi ro | Mức | Phương án |
|---|---|---|
| Paper chính lệch chủ đề | Cao | Hỏi giảng viên tuần 1; chiến lược 2 track (mục 1) |
| Không có Raspberry Pi | Trung bình | Profile P1 (1 luồng, 1 E-core); ghi rõ là giả lập; đọc thêm số liệu Pi công khai chỉ để thảo luận |
| TensorFlow lỗi trên Windows / Python 3.11 bản Store | Trung bình | Cài Python 3.11 python.org; phương án B: PyTorch → ONNX → ONNX Runtime quantization |
| Giải nén `.rar` lỗi | Thấp | UnRAR tại `D:\Program Files\UnRAR.exe`; hoặc 7-Zip |
| Kết quả không đạt mức Meidan (TPR 100%) | Trung bình | Báo cáo trung thực; phân tích nguyên nhân (dedup, purge gap, nhiều seed làm số "khó" hơn); đây là phát hiện hợp lệ |
| F1 cao ảo do mất cân bằng | Cao | macro-F1, FPR, F1 trên test cân bằng (mục 9.1) |
| Thiếu thời gian | Trung bình | Thứ tự cắt giảm ở mục 11; chạy thí nghiệm qua đêm |
| RAM khi đọc toàn bộ 7M dòng | Thấp | Xử lý từng thiết bị, Parquet float32 |

---

## 15. Việc làm ngay (hôm nay/ngày mai)

1. Tải PDF paper chính, đọc abstract + phần phương pháp/kết quả, gửi câu hỏi cho giảng viên (mục 1).
2. Tạo venv Python 3.11 và cài thư viện.
3. Bắt đầu tải N-BaIoT (1.7 GB) bằng script để ghi ngày giờ và SHA-256 ngay từ lần đầu.
4. Tạo khung thư mục và `.gitignore` cho `DT043/data/`.

---

### Nguồn đã xác minh khi lập kế hoạch (11/10/2026)
- Metadata và abstract paper chính: Crossref `api.crossref.org/works/10.1016/j.cose.2025.104380`, OpenAlex `api.openalex.org/works/doi:10.1016/j.cose.2025.104380`
- Trang dataset UCI: https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot
- Meidan et al. 2018 (arXiv): https://arxiv.org/abs/1805.03409
