# DT043 – Phát hiện botnet IoT bằng autoencoder nhẹ

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| MSSV | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | An toàn Bảo mật Hệ thống thông tin – Bài giữa kỳ (mã đề DT043) |
| Dữ liệu | N-BaIoT – UCI, DOI 10.24432/C5RC8J, CC BY 4.0 |
| Paper chính | Masud et al. (2025), *Vulnerability defence using hybrid moving target defence in IoT systems*, Computers & Security 153, 104380 |
| Paper tham chiếu kỹ thuật | Meidan et al. (2018), *N-BaIoT*, IEEE Pervasive Computing (arXiv:1805.03409) |
| Báo cáo (27 trang) | [report/BaoCao_DT043_1150080120_HoangThanhTra.docx](report/BaoCao_DT043_1150080120_HoangThanhTra.docx) · [PDF](report/BaoCao_DT043_1150080120_HoangThanhTra.pdf) |
| Slide thuyết trình (17 slide, có ghi chú) | [report/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx](report/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx) · [PDF](report/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pdf) |
| Kế hoạch / nhật ký | [KE_HOACH.md](KE_HOACH.md) · [NHAT_KY_THUC_HIEN.md](NHAT_KY_THUC_HIEN.md) |

## 1. Kiến trúc 4 tầng

```
DT043/
├── ai/                    # AI – huấn luyện, đánh giá, lượng tử hóa, benchmark, mô phỏng MTD
│   ├── src/nbaiot/        #   thư viện: data, split, scaling, models, threshold, metrics, quantize, bench, pipeline, mtd/
│   ├── configs/           #   base.yaml + exp/*.yaml (mỗi thí nghiệm 1 file)
│   ├── scripts/           #   00…08: môi trường → dữ liệu → EDA → ma trận → benchmark → tổng hợp → MTD → xuất gói
│   └── tests/             #   unit / integration / negative (pytest)
├── backend/               # BE – FastAPI: nạp gói triển khai, API phát hiện/replay/cảnh báo/MTD
│   ├── app/               #   main.py, detector.py, mtd.py, schemas.py, settings.py
│   └── tests/
├── db/                    # DB – SQLite: schema.sql + repository.py
├── frontend/              # FE – dashboard HTML/CSS/JS thuần (không cần build)
├── data/                  # dữ liệu (raw/processed KHÔNG commit) + DOWNLOAD_INFO.json + MANIFEST.sha256
├── artifacts/             # models/ (theo thí nghiệm, seed 42) + deploy/ (gói AI → BE)
├── results/               # raw/ (mọi lần chạy), tables/, figures/, data_quality/, env_info.json
├── docs/                  # phiếu tái lập, data card, threat model, tiêu chí thành công
└── report/                # báo cáo .docx + script sinh báo cáo
```

Hợp đồng AI → BE: `artifacts/deploy/<thiết bị>/{model.tflite, scaler.json, meta.json}`; `meta.json` chứa ngưỡng `tr*`, cửa sổ `ws*`, danh sách cột đặc trưng và SHA-256 của model (backend từ chối nạp nếu lệch).

## 2. Chạy lại từ đầu (Windows, PowerShell, tại thư mục `DT043`)

Yêu cầu: Python **3.11**, ~6 GB đĩa trống (zip 1.7 GB + giải nén + parquet), UnRAR hoặc 7-Zip để giải nén file `.rar` của dataset.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt     # bản khóa đầy đủ: requirements-lock.txt
$env:PYTHONIOENCODING = "utf-8"
```

| Bước | Lệnh | Thời gian (máy tham chiếu) |
|---|---|---|
| 0. Ghi cấu hình máy | `.venv\Scripts\python ai/scripts/00_env_info.py` | vài giây |
| 1. Tải + giải nén + manifest | `.venv\Scripts\python ai/scripts/01_download.py` | ~5–15 phút |
| 2. Kiểm tra checksum | `.venv\Scripts\python ai/scripts/02_verify_manifest.py` | ~1 phút |
| 3. Kiểm tra chất lượng + Parquet | `.venv\Scripts\python ai/scripts/03_prepare.py` | ~5 phút |
| 3b. EDA | `.venv\Scripts\python ai/scripts/03b_eda.py` | ~1 phút |
| 4. Kiểm thử | `.venv\Scripts\python -m pytest ai/tests backend/tests -q` | ~1 phút |
| 5. Ma trận thí nghiệm | `.venv\Scripts\python ai/scripts/04_run_matrix.py E1_baseline E4_light E3_iforest E2_global E2_shared_pdnorm E4_tiny_L5 E4_tiny_L3 E4_tiny_L1 E4_tiny_L01 E4_tiny_L001 E6_leak E9_robust E9_poison_1 E9_poison_5 --workers 2` | ~4–5 giờ (CPU) |
| 6. Edge benchmark (máy rảnh) | `.venv\Scripts\python ai/scripts/05_bench_edge.py` | ~15 phút |
| 7. Mô phỏng MTD | `.venv\Scripts\python ai/scripts/07_mtd_sim.py` | ~2 phút |
| 8. Tổng hợp bảng/hình/kiểm định | `.venv\Scripts\python ai/scripts/06_aggregate.py` | ~1 phút |
| 8b. Phân tích hậu kiểm ngưỡng | `.venv\Scripts\python ai/scripts/09_posthoc_threshold.py` | ~1 phút |
| 9. Xuất gói triển khai AI → BE | `.venv\Scripts\python ai/scripts/08_export_deploy.py` | vài giây |
| 10. Sinh báo cáo Word | `.venv\Scripts\python report/build_report.py` rồi `report/finalize_word.ps1` (cập nhật mục lục, xuất PDF) | ~1 phút |
| 11. Sinh slide PowerPoint | `.venv\Scripts\python report/export_deck_data.py`, rồi trong `report/`: `npm install` (lần đầu) và `node build_deck.js` | ~1 phút |

Hoặc chạy toàn bộ: `powershell -ExecutionPolicy Bypass -File run_all.ps1`.

Mẹo: `04_run_matrix.py` bỏ qua các lần chạy đã có `metrics.json` → có thể dừng/chạy lại bất kỳ lúc nào. Thử nhanh 1 lần chạy: `... 04_run_matrix.py E1_baseline --devices Danmini_Doorbell --seeds 42 --workers 1`. Nếu máy ít RAM, giữ `--workers 2` hoặc 1.

## 3. Chạy demo (BE + FE + DB)

```powershell
.venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
```
Mở http://127.0.0.1:8000/ (dashboard) và http://127.0.0.1:8000/docs (Swagger). CSDL SQLite tự tạo tại `db/dt043.sqlite3`.

| API | Ý nghĩa |
|---|---|
| `GET /api/health` | số model đã nạp, lỗi gói (nếu có) |
| `GET /api/devices` | thiết bị + model đang hoạt động + số cảnh báo mở |
| `POST /api/detect` | `{device, features: [[115 số], …]}` → MSE, cờ, cảnh báo |
| `POST /api/replay/{device}?segment=mirai/syn&n=2000&offset=0` | phát lại dữ liệu công khai (benign chỉ lấy phần test) |
| `GET /api/alerts`, `POST /api/alerts/{id}/ack` | danh sách / xác nhận cảnh báo |
| `GET /api/mtd/actions`, `POST /api/mtd/tick` | nhật ký MTD; chạy chu kỳ time-based |
| `GET /api/experiments` | bảng tổng hợp kết quả thực nghiệm |

Mẹo demo/quay video: mở `http://127.0.0.1:8000/?replay=Danmini_Doorbell:mirai/syn` để dashboard tự phát lại khi tải trang.

## 4. Kết quả chính (468 kết quả theo thiết bị × seed, mức cửa sổ)

| Cấu hình | Tham số | macro-F1 (±KTC95) | TPR | FPR |
|---|---|---|---|---|
| B0 – AE Meidan per-device | 36,876 | 0.706 ± 0.066 | 0.822 | 0.0025 |
| B1 – model + scaler + ngưỡng chung | 36,876 | 0.684 ± 0.358 | 0.809 | 0.0000 |
| B1 – model chung + chuẩn hóa/ngưỡng riêng | 36,876 | 0.775 ± 0.039 | 0.863 | 0.0022 |
| B2 – Isolation Forest | – | 0.886 ± 0.014 | 0.928 | 0.0025 |
| V1 – AE nhẹ | 8,059 | 0.689 ± 0.056 | 0.812 | 0.0027 |
| V1 int8 + hiệu chỉnh ngưỡng | 8,059 (15.3 KB) | 0.717 | 0.829 | 0.0016 |

- 8/10 loại tấn công có recall ≈ 1.0; toàn bộ suy giảm đến từ **BASHLITE tcp/udp** (flood giả mạo nguồn trông như "luồng mới" benign) → **không tái lập được TPR 100%** của Meidan; FPR thấp hơn paper.
- Edge (V1 int8, 1 luồng ghim 1 E-core): **p95 = 10.8 µs/mẫu, ~103.000 mẫu/s, RAM +4.6 MB** → đạt tiêu chí RQ5. Chạy 20 luồng với batch 1 chậm hơn ~50 lần.
- Tiêu chí chốt trước: RQ5 **đạt**; RQ1–RQ4 **không đạt** (giải thích đầy đủ trong báo cáo, không chỉnh tiêu chí).
- MTD (HARM rút gọn, chu kỳ 20 bước): ASP không MTD 0.498 → shuffle 0.409, diversity 0.437, **kết hợp 0.327** (khớp xu hướng paper chính). MTD lai kích hoạt bởi AE có thời gian lộ diện thấp hơn time-based ở cùng chi phí.

Chi tiết: `results/tables/` (CSV), `results/figures/` (PNG), Chương 6–8 của báo cáo, và [NHAT_KY_THUC_HIEN.md](NHAT_KY_THUC_HIEN.md).

## 5. Phần sinh viên tự làm trước khi nộp

- [ ] Quay **video demo ngắn** (dashboard + slide): công cụ không quay video thay được.
- [ ] Đối chiếu toàn văn PDF paper chính với các mục đánh dấu "cần đối chiếu toàn văn" trong [docs/phieu_tai_lap_paper.md](docs/phieu_tai_lap_paper.md).
- [ ] Commit và push thư mục `DT043/` lên GitHub.

## 6. An toàn và đạo đức

Chỉ dùng dữ liệu công khai N-BaIoT trên máy cá nhân. Không chạy mã độc, không quét/tấn công hệ thống thật. Các "tấn công" trong E9 là biến đổi dữ liệu offline; MTD chỉ được mô phỏng và ghi vào CSDL. Không commit dữ liệu thô (đã có trong `.gitignore`); người dùng tự tải lại từ UCI và kiểm tra bằng manifest.
