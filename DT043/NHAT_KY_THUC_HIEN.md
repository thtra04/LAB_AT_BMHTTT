# NHẬT KÝ THỰC HIỆN – DT043

File này ghi lại **các bước đã thực hiện theo thứ tự thời gian**, kèm lệnh đã chạy, kết quả và sự cố gặp phải. Kế hoạch tổng thể nằm ở [KE_HOACH.md](KE_HOACH.md).

---

## Bước 1 – Đọc tài liệu nền (11/10/2026)

- Xác minh paper chính DOI 10.1016/j.cose.2025.104380 qua Crossref/OpenAlex: Masud, Keshk, Moustafa, Turnbull, Susilo, *Computers & Security* 153 (2025), Open Access CC BY.
- Nội dung paper: Moving Target Defence (MTD) + mô hình 3-layer THARM, các metric attack success probability / risk / attack cost; kết luận kết hợp shuffle + diversity tốt hơn dùng riêng. **Không dùng autoencoder/N-BaIoT** → chia 2 track (xem KE_HOACH.md mục 1).
- Đọc Meidan et al. 2018 (arXiv:1805.03409), trích các thông số tái lập: kiến trúc 75/50/33/25%, chia benign theo thời gian 3 phần bằng nhau, `tr* = mean + std` trên DSopt, `ws*` nhỏ nhất cho FPR = 0 trên DSopt, kết quả TPR 100%, FPR 0.007 ± 0.01.
- Đầu ra: `KE_HOACH.md`.

## Bước 2 – Chuẩn bị môi trường (11/10/2026)

| Mục | Giá trị |
|---|---|
| Máy | Intel i7-13650HX (14 lõi / 20 luồng), RAM 23.7 GB, GPU RTX 4060 Laptop (không dùng – TF trên Windows chỉ chạy CPU), Windows 11 Home |
| Python | 3.11.9 trong `.venv` (không dùng 3.14 mặc định vì TensorFlow chưa hỗ trợ) |
| Thư viện chính | tensorflow 2.21.0, numpy 2.4.6, pandas 3.0.6, scikit-learn 1.9.1 (đầy đủ trong `requirements-lock.txt`) |

Lệnh:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Sự cố & cách xử lý:**
1. Ổ C: còn 237 MB → pip báo `No space left on device` khi giải nén gói TensorFlow vào thư mục tạm. Xử lý: đặt `TMP`, `TEMP`, `PIP_CACHE_DIR` sang ổ D: (`D:\BAITAP\_tmp`).
2. Mạng chập chờn (`IncompleteRead`, `SSLEOFError`) → chạy lại pip với `--retries 10 --timeout 60`.
3. Console Windows dùng cp1252 nên `print` tiếng Việt lỗi `UnicodeEncodeError` → chạy với `PYTHONIOENCODING=utf-8`.

## Bước 3 – Tải dữ liệu N-BaIoT (11/10/2026)

Lệnh: `python scripts/01_download.py` (tải zip → SHA-256 → giải nén zip → giải nén các `.rar` bằng UnRAR → manifest).

| Mục | Giá trị |
|---|---|
| URL | https://archive.ics.uci.edu/static/public/442/detection+of+iot+botnet+attacks+n+baiot.zip |
| Thời điểm tải (UTC) | 2026-10-11T04:41:52 |
| Kích thước zip | 1,772,922,927 byte |
| SHA-256 zip | `64929678b081d8e579a8d7c488cf11cc588403f282d5fb065b4156edbd55de9b` |
| Giấy phép | CC BY 4.0, DOI 10.24432/C5RC8J |
| Manifest | `data/MANIFEST.sha256` – 107 file (CSV, RAR, mô tả) |

Cấu trúc sau giải nén: `data/raw/<thiết bị>/benign_traffic.csv`, `gafgyt_attacks/{combo,junk,scan,tcp,udp}.csv`, `mirai_attacks/{ack,scan,syn,udp,udpplain}.csv` (Ennio_Doorbell và Samsung_SNH_1011_N_Webcam không có Mirai). Đầu ra: `data/DOWNLOAD_INFO.json`, `data/MANIFEST.sha256`.

## Bước 4 – Chuẩn bị dữ liệu & kiểm tra chất lượng (11/10/2026)

Lệnh: `python scripts/03_prepare.py` → kiểm tra schema từng file (115 cột đúng tên/thứ tự, kiểu số, không NaN/±inf), khử trùng lặp chính xác **trong từng file** (giữ dòng đầu, giữ thứ tự thời gian), lưu `data/processed/<thiết bị>/<segment>.parquet` (float32, 1.5 GB).

Kết quả chính (`results/data_quality/file_stats.csv`, `device_summary.csv`):

| Mục | Giá trị |
|---|---|
| Tổng dòng gốc → sau khử trùng | 7,062,606 → 6,904,827 (bỏ 157,779 dòng) |
| NaN / ±inf / cột hằng | 0 / 0 / 0 |
| Trùng lặp benign | 42,432 dòng; cao nhất **Danmini_Doorbell 18.5%**, Provision_PT_737E 11.2%, Ennio 9.4% |
| Trùng lặp attack | chỉ ở `gafgyt/tcp` (64,560) và `gafgyt/udp` (50,787); Mirai không có |
| Tỷ lệ attack : benign (sau khử trùng) | 5.5× (Philips) → 61.8× (Ecobee) → **mất cân bằng nặng**, không dùng Accuracy làm metric chính |
| Giá trị lớn nhất | 5.88e17 (các cột variance/covariance) → tính MSE bằng float64 để tránh tràn số |

## Bước 5 – Cài đặt pipeline & kiểm thử (11/10/2026)

Mã nguồn `src/nbaiot/`:

| Module | Vai trò |
|---|---|
| `data.py` | schema 115 cột, đọc/kiểm tra CSV, nạp parquet, hash dòng |
| `split.py` | chia theo thời gian 1/3–1/3–1/3 + purge gap 500 dòng; chia ngẫu nhiên (chỉ E6); loại dòng test trùng hash với train/opt |
| `scaling.py` | z-score fit **chỉ trên DStrn**, gắn tên thiết bị (chặn dùng nhầm scaler) |
| `models.py` | AE Meidan 115-86-58-38-29-…-115 (36,876 tham số), V1 115-32-8-32-115 (8,059), V2 23-12-4-12-23 |
| `threshold.py` | `tr* = mean + std` (và mean+3std, p99, p99.9), majority vote trượt, tìm `ws*` (FPR = 0 trên DSopt), độ trễ phát hiện |
| `metrics.py` | TPR, FPR, precision, F1 (attack/benign/macro), balanced acc, MCC, F1 cân bằng, ROC-AUC, PR-AUC, recall theo loại tấn công |
| `quantize.py` | Keras → SavedModel → TFLite fp32/fp16/dynamic-int8/full-int8, chạy TFLite theo lô |
| `pipeline.py` | 1 lần chạy hoàn chỉnh + lưu config/metrics/log/model; baseline model dùng chung (B1) |

Lưu ý kỹ thuật: chuyển TFLite int8 trực tiếp từ concrete function bị lỗi `READ_VARIABLE` trên TF 2.21 → xuất SavedModel trước rồi mới chuyển.

Kiểm thử: `python -m pytest tests -q` → **30 passed** (unit: schema, chia/purge, không trùng hash giữa các tập, scaler chỉ thấy train, ngưỡng, vote không vượt ranh giới segment, metric; integration: end-to-end trên dữ liệu tổng hợp + Keras↔TFLite + cùng seed cùng kết quả + Isolation Forest; negative: file rỗng, thiếu/thừa/sai thứ tự cột, NaN/±inf, chuỗi không phải số, dòng bị cắt, cửa sổ sai, manifest bị sửa, TFLite sai số chiều, int8 thiếu representative data).

## Bước 6 – Chốt tiêu chí & chạy ma trận thí nghiệm (11/10/2026)

- Smoke test E1 (Danmini, seed 42): TPR 1.000, FPR 0.0076 (Meidan: 0.007), ws* = 70, train 27 s, tổng 58 s. Int8 giữ ngưỡng fp32: FPR 0.0106; **int8 + hiệu chỉnh ngưỡng: FPR 0.0019, ws* = 14**.
- Chốt `docs/tieu_chi_thanh_cong.md` lúc 11:5x ngày 11/10/2026, SHA-256 `3ac9bfdb2cd84059df1263bf0f6be731475cfbd3ef88673dfe0a43909c2a7b53`.
- Ma trận: 14 cấu hình, 477 lần chạy (`scripts/04_run_matrix.py`, có resume, log từng lần chạy vào `results/raw/runs_index.csv`).

**Sự cố:** lần đầu chạy 6 worker song song → `MemoryError` (ổ C: đầy nên pagefile không mở rộng, commit còn trống ~5 GB). Xử lý: giảm còn 2 worker, mỗi worker chỉ chạy 1 task rồi thoát (`max_tasks_per_child=1`), baseline model chung (E2) chỉ giữ train/opt trong RAM và nạp lại test từng thiết bị khi đánh giá.

**Phát hiện khi chạy (11/10/2026):** B0 trên Ennio_Doorbell chỉ đạt TPR 0.366 và Ecobee (seed 42) TPR 0.769 – recall của `gafgyt/tcp` và `gafgyt/udp` = 0. Kiểm tra dữ liệu thô: trong flood tcp/udp của BASHLITE, địa chỉ nguồn bị giả mạo liên tục nên **mỗi gói trông như gói đầu tiên của một luồng mới** (`weight = 1`, `variance = 0`, `mean = 60` byte) → vector đặc trưng gần như giống hệt nhau (MSE ≈ 0.17 cho mọi mẫu) và nằm gần vùng benign. Đồng thời phân phối MSE trên DSopt có đuôi rất dài (max 1182) làm `std` lớn → `tr* = mean + std` = 22.5 ≫ 0.17. Đây là đặc tính dữ liệu + quy tắc ngưỡng, không phải lỗi code → giữ nguyên, đưa vào phân tích lỗi. Cùng thiết bị Ecobee nhưng seed 1337 đạt TPR 1.0 → **độ bất ổn định theo seed** là một kết quả cần báo cáo.

**Tối ưu thời gian chạy:** tốc độ thực tế ~70 s/lần chạy với 2 worker (ước tính 9 giờ). Đã: (1) giảm V2 (5 cửa sổ) xuống 3 seed – vẫn đạt mức tối thiểu của đề; (2) tăng lên 3 worker; (3) bọc runner trong vòng lặp tự chạy lại (resume) nếu bị `MemoryError`. Còn 387 lần chạy.

## Bước 7 – Tách kiến trúc FE / BE / AI / DB (11/10/2026)

Theo yêu cầu, hệ thống được tách thành 4 tầng, giao tiếp qua **hợp đồng rõ ràng**:

```
AI  (huấn luyện, đánh giá, lượng tử hóa, benchmark)
 │   xuất "gói triển khai" artifacts/deploy/<thiết bị>/{model.tflite, scaler.json, meta.json}
 ▼
BE  (FastAPI) ── nạp gói (kiểm SHA-256) ── API: /api/detect, /api/replay, /api/alerts, /api/mtd, /api/experiments
 │                                                        ▲
 ▼                                                        │ REST/JSON
DB  (SQLite: devices, models, detection_batches,      FE (HTML/CSS/JS thuần, dashboard)
     alerts, mtd_actions, experiment_results)
```

| Tầng | Thư mục | Nội dung |
|---|---|---|
| AI | `src/nbaiot/`, `scripts/`, `configs/`, `tests/` (sẽ gom vào `ai/` sau khi ma trận chạy xong) | pipeline ML, `08_export_deploy.py` xuất gói triển khai |
| DB | `db/schema.sql`, `db/repository.py` | 6 bảng, khóa ngoại, CHECK ràng buộc trạng thái; không lưu dữ liệu thô |
| BE | `backend/app/` | `detector.py` (nạp gói, kiểm checksum, suy luận TFLite 1 luồng như edge), `mtd.py` (MTD lai: event khi có cảnh báo → shuffle + diversity; time-based theo chu kỳ), `schemas.py` (Pydantic kiểm tra đầu vào), `main.py` (API) |
| FE | `frontend/` | bảng thiết bị/model, phát lại dữ liệu test + biểu đồ MSE vs ngưỡng, cảnh báo (xác nhận), nhật ký MTD, bảng kết quả thực nghiệm |

Kiểm thử BE + DB: `python -m pytest backend/tests -q` → **12 passed** (health, replay benign không cảnh báo, replay tấn công sinh cảnh báo + 2 hành động MTD, xác nhận cảnh báo 2 lần bị từ chối, detect; negative: thiết bị không tồn tại 404, sai số chiều 422, dòng lệch độ dài 422, segment `../../etc` và tên thiết bị bất thường 422, lô quá lớn 422, **gói model bị sửa 1 byte → bị từ chối**; repository).

## Bước 8 – Track B: mô phỏng MTD (11/10/2026)

`python scripts/07_mtd_sim.py` (phần 1 – HARM rút gọn: internet → gateway → 9 thiết bị → cloud; lỗ hổng là giả định minh họa; Monte Carlo 2000 lần × 5 seed; kẻ tấn công có ngân sách 20 bước):

| Chu kỳ MTD | Không MTD | Shuffle | Diversity | Kết hợp |
|---|---|---|---|---|
| 20 bước | 0.498 | 0.409 | 0.437 | **0.327** |
| 10 bước | 0.498 | 0.000 | 0.358 | 0.000 |
| 5 bước | 0.498 | 0.000 | 0.203 | 0.000 |

→ Tái lập được **xu hướng** của paper chính: kết hợp shuffle + diversity cho xác suất tấn công thành công thấp nhất. Ở chu kỳ ngắn shuffle riêng đã chặn hoàn toàn nhưng chi phí (số lần move) tăng tương ứng – hạn chế của mô hình rút gọn. (Lần chạy đầu với ngân sách 200 bước cho ASP ≈ 1 ở mọi chiến lược → không phân biệt được; đã đổi sang 20 bước và ghi lại ở đây.)

Phần 2 – MTD lai kích hoạt bởi cảnh báo V1 (seed 42, luồng test thật): ở cùng chi phí, hybrid có thời gian lộ diện thấp hơn time-based (T = 2000: 263 mẫu với 8.9 move/10k; time-based cần T = 500, 20 move/10k để đạt 251 mẫu). Event-only lộ diện trung bình 11,835 mẫu vì các đợt tcp/udp bị AE bỏ sót không bao giờ kích hoạt move → thành phần time-based là lưới an toàn.

> **Ghi chú đường dẫn:** từ Bước 10, mã AI được gom vào `ai/` – các lệnh `scripts/…`, `src/…`, `configs/…`, `tests/…` ở các bước trên tương ứng với `ai/scripts/…`, `ai/src/…`, `ai/configs/…`, `ai/tests/…`.

## Bước 9 – Hoàn tất ma trận thí nghiệm (11/10/2026)

- `ProcessPoolExecutor` + `max_tasks_per_child` trên Windows/Python 3.11 liên tục gây `OSError: handle is closed` → `BrokenProcessPool`. **Sửa tận gốc:** runner chạy **mỗi lần chạy là một subprocess riêng** (`04_run_matrix.py --one EXP DEVICE SEED`), điều phối bằng thread pool 2 luồng; crash/OOM của một lần chạy chỉ ghi lỗi, không làm sập ma trận.
- Hàm robustness (E9) sao chép toàn bộ dữ liệu tấn công cho mỗi mức α → sửa để xử lý từng segment (cùng kết quả số học, ít RAM hơn).
- 9 lần chạy lỗi do hết RAM (E6 Philips seed 2024; 8 lần E9_robust) được **chạy lại riêng với 1 worker** → thành công. Kết quả cuối: **468 kết quả, không thiếu lần chạy nào** (`results/raw/runs_index.csv` giữ cả các dòng lỗi lịch sử).

## Bước 10 – Edge benchmark, gom tầng AI, kiểm thử lại (11/10/2026)

- `ai/scripts/05_bench_edge.py` chạy khi máy rảnh (mỗi cấu hình 1 process riêng, warm-up 200, 10.000 lần × 5 lượt). V1 int8 – profile P1 (1 luồng, ghim CPU 19 = E-core): **p50 9.0 µs, p95 10.8 µs, 102.899 mẫu/s, RAM +4.6 MB, 15.3 KB, ≈ 40.5 µJ/mẫu (proxy)**. Batch 1 với 20 luồng: p50 473 µs (chậm hơn ~50×).
- Gom `src/ scripts/ configs/ tests/` vào **`ai/`**, sửa đường dẫn (`ROOT`, `CONFIG_DIR`, `sys.path`). `pytest ai/tests backend/tests` → **42 passed** trên cấu trúc mới; manifest dữ liệu vẫn khớp SHA-256.

## Bước 11 – Tổng hợp, kiểm định, đối chiếu tiêu chí (11/10/2026)

`ai/scripts/07_mtd_sim.py`, `09_posthoc_threshold.py`, `06_aggregate.py` → `results/tables/*.csv`, `results/figures/*.png`.

| Cấu hình | macro-F1 (±KTC95) | TPR | FPR | F1 cân bằng |
|---|---|---|---|---|
| B0 AE Meidan | 0.706 ± 0.066 | 0.822 | 0.0025 | 0.884 |
| B1 global | 0.684 ± 0.358 | 0.809 | 0.0000 | 0.878 |
| B1 chung + pdnorm | 0.775 ± 0.039 | 0.863 | 0.0022 | 0.910 |
| B2 Isolation Forest | 0.886 ± 0.014 | 0.928 | 0.0025 | 0.955 |
| V1 AE nhẹ | 0.689 ± 0.056 | 0.812 | 0.0027 | 0.878 |
| V2 cửa sổ L0.01 (3 seed) | 0.841 ± 0.052 | 0.916 | 0.0036 | 0.947 |
| E6 rò rỉ (đối chứng) | 0.679 ± 0.236 | 0.804 | 0.0006 | 0.873 |
| V1 poison 1% / 5% | 0.470 / 0.437 | 0.675 / 0.616 | 0.0023 / 0.0024 | – |

Tiêu chí chốt trước (`results/tables/criteria_check.csv`): **RQ5 đạt** (p95 10.8 µs, 15.3 KB, ΔRSS 4.6 MB); **RQ1–RQ4 không đạt** – RQ1 TPR 0.822 < 0.99; RQ2 B0 thắng 4/9, p = 0.285; RQ3 Δmacro-F1 = 0.017 > 0.01; RQ4 kích thước int8 = 45.5% bản fp32 (khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ). Không chỉnh tiêu chí.

Phát hiện chính: (1) suy giảm hoàn toàn do gafgyt tcp/udp (recall 0.42–0.47 so với ≈ 1.0 ở 8 loại còn lại); (2) model chung + chuẩn hóa riêng tốt hơn B0 → phần "per-device" quan trọng là chuẩn hóa/ngưỡng (chưa có ý nghĩa thống kê); (3) rò rỉ làm FPR "đẹp giả" (0.0006 so với 0.0025); (4) 7 cặp (model, thiết bị) có TPR dao động > 0.05 chỉ do đổi seed; (5) hậu kiểm (không thuộc tiêu chí): ngưỡng p75 DSopt bắt 100% tcp/udp nhưng cần ws ≈ 1400 mẫu và FPR test 0.02.

## Bước 12 – Demo 4 tầng FE/BE/DB/AI (11/10/2026)

- `ai/scripts/08_export_deploy.py` xuất 9 gói `artifacts/deploy/<thiết bị>/` (V1 int8, ngưỡng hiệu chỉnh, 15,688 byte/model).
- Chạy `uvicorn backend.app.main:app` → `/api/health`: 9 model, 0 lỗi gói. Kiểm tra trên trình duyệt: phát lại 2.000 mẫu `mirai/syn` (Danmini) → 1989/1989 cửa sổ cảnh báo, cảnh báo mức high + 2 hành động MTD (shuffle IP, đổi firmware) ghi vào SQLite; benign (Ennio) → không cảnh báo; `gafgyt/tcp` (Ennio) → không cảnh báo (đúng lỗi bỏ sót đã phân tích).
- Sửa FE: định dạng số nguyên; thêm `?replay=<thiết bị>:<segment>` để tự phát lại khi mở trang (tiện demo/quay video). Rút gọn `/api/experiments` còn các cột chính. Ảnh chụp: `results/figures/demo_dashboard.png` (Edge headless).

## Bước 13 – Báo cáo Word và slide PowerPoint (11/10/2026)

- **Word:** `report/build_report.py` (python-docx, Times New Roman 13, A4) → `report/finalize_word.ps1` (Microsoft Word cập nhật mục lục, xuất PDF). **27 trang, 26 bảng, 12 hình**; mọi số liệu đọc tự động từ `results/tables`. Đã render từng trang kiểm tra; sửa: danh sách đánh số không bắt đầu lại từ 1, sơ đồ ASCII bị xuống dòng, ký tự `*` thừa, legend che dữ liệu trong hình lượng tử hóa, nhãn trục bị cắt.
- **PowerPoint:** `report/export_deck_data.py` → `report/deck_data.json` → `report/build_deck.js` (pptxgenjs, theme riêng, layout có placeholder, chart gốc PowerPoint, ghi chú thuyết trình từng slide) → `report/export_pptx_pdf.ps1`. **17 slide**, `validate.py`: All validations PASSED. Đã render kiểm tra; sửa: nhãn "500 dòng đệm" chồng chữ, slide kết luận dồn nội dung, thẻ quá cao; thêm slide demo.

## Việc sinh viên tự làm trước khi nộp
- Quay video demo ngắn (dashboard + slide).
- Đối chiếu toàn văn paper chính cho các mục "cần đối chiếu" trong `docs/phieu_tai_lap_paper.md`.
- Commit/push `DT043/` (dữ liệu thô, `.venv`, `node_modules`, `results/scores` đã nằm trong `.gitignore`).
