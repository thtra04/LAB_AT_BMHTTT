"""Sinh file Word giải thích chi tiết notebook DT043_walkthrough.ipynb (từng mục, từng ô, output và cách trình bày).

Chạy tại DT043/src:  .venv\\Scripts\\python report/build_giaithich_notebook.py
Đầu ra: ../tailieu/thuyet_trinh/GiaiThich_Notebook_DT043_1150080120_HoangThanhTra.docx
Số ô đếm từ 1 theo thứ tự trên xuống; hình phân bố MSE lấy trực tiếp từ output của notebook (ô 18).
"""
import base64
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from docx_helpers import Report  # noqa: E402

NB = ROOT / "DT043_walkthrough.ipynb"
OUT = ROOT.parent / "tailieu" / "thuyet_trinh" / "GiaiThich_Notebook_DT043_1150080120_HoangThanhTra.docx"


def cell_image(nb, cell_no):
    """Lưu hình PNG đầu tiên trong output của ô `cell_no` (đếm từ 1) ra file tạm."""
    for o in nb["cells"][cell_no - 1].get("outputs", []):
        png = o.get("data", {}).get("image/png")
        if png:
            p = Path(tempfile.mkdtemp()) / f"cell{cell_no}.png"
            p.write_bytes(base64.b64decode(png))
            return p
    return None


def tab(R, rows, cols, widths, caption=None, font=10):
    R.table(pd.DataFrame(rows, columns=cols), caption, font=font, col_widths_cm=widths)


def cells(R, rows):
    """Bảng 'Ô – Loại – Làm gì – Kết quả chính'."""
    tab(R, rows, ["Ô", "Loại", "Làm gì", "Kết quả chính"], [1.0, 1.6, 6.9, 6.5], font=9.5)


def say(R, text):
    R.para(f"**Khi trình bày / thầy hỏi:** {text}")


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    n_cells = len(nb["cells"])
    n_err = sum(1 for c in nb["cells"] if c["cell_type"] == "code"
                and any(o.get("output_type") == "error" for o in c.get("outputs", [])))
    R = Report()
    R.para("GIẢI THÍCH CHI TIẾT NOTEBOOK DT043_walkthrough.ipynb", bold=True, size=16, align="center")
    R.para("Phát hiện botnet IoT bằng autoencoder nhẹ – notebook trình bày", italic=True, align="center")
    R.para("Người trình bày: **Hoàng Thanh Trà** – MSSV 1150080120 – Lớp 11CNPM2", align="center")

    R.h1("1. Tổng quan")
    R.para(f"Notebook src/DT043_walkthrough.ipynb có **{n_cells} ô**, chia **11 mục**, đi lại toàn bộ đề tài **bằng chính mã nguồn "
           f"trong ai/src/nbaiot** (không viết lại thuật toán). Bản hiện tại đã chạy hết, **{n_err} ô lỗi**, đủ output. Số ô trong "
           "tài liệu này đếm từ 1 theo thứ tự từ trên xuống.")
    tab(R, [["1", "Môi trường và dataset", "Chạy thật", "Đúng bộ N-BaIoT, 107 file khớp SHA-256"],
            ["2", "Chất lượng dữ liệu, EDA", "Đọc kết quả", "7.062.606 dòng, 157.779 dòng trùng, tỷ lệ 12,4 : 1"],
            ["3", "Chia dữ liệu chống rò rỉ", "Chạy thật", "1/3 – 1/3 – 1/3 theo thời gian, đệm 500 dòng"],
            ["4", "Huấn luyện V1, chọn ngưỡng", "Chạy thật", "Ennio: tcp/udp recall ≈ 0 – lỗi chính"],
            ["5", "Lượng tử hóa int8", "Chạy thật", "15,3 KB; khớp lần chạy chính thức"],
            ["6", "Edge benchmark", "Chạy thật + đọc", "Chính thức: p95 10,8 µs"],
            ["7", "Kết quả 468 lần chạy", "Đọc kết quả", "B0 macro-F1 0,706, TPR 0,822, FPR 0,0025"],
            ["8", "MTD (HARM rút gọn)", "Đọc kết quả", "Kết hợp S + D có ASP thấp nhất"],
            ["9", "Tái lập hai bài báo", "Chạy thật", "Bảng % khớp 10 mức, vẽ lại Hình 6, 7, Meidan Hình 2"],
            ["10", "Demo API backend", "Chạy thật", "Mirai → 1989/1989 cửa sổ, 2 hành động MTD"],
            ["11", "Kết luận", "Văn bản", "3 ý chính"]],
        ["Mục", "Nội dung", "Kiểu ô", "Kết quả nổi bật"], [1.2, 5.0, 3.0, 6.8], "Cấu trúc notebook")
    R.para("**Chạy thật** = tính lại ngay trong notebook (tổng ≈ 1–3 phút). **Đọc kết quả** = đọc bảng/hình của ma trận 468 lần "
           "chạy đã lưu trong results/ (chạy lại toàn bộ mất 4–5 giờ bằng ai/scripts/04_run_matrix.py).")
    R.para("**Cách chạy:** mở bằng VS Code hoặc Jupyter, chọn kernel src/.venv (Python 3.11), chạy từ trên xuống; hoặc sinh lại và "
           "chạy toàn bộ:", justify=False)
    R.code("cd src\n.venv\\Scripts\\python report/build_notebook.py DT043_walkthrough.ipynb --execute")

    # ------------------------------------------------------------------ 0
    R.h1("2. Ô 1–2: Mở đầu và cài đặt")
    cells(R, [["1", "Markdown", "Tiêu đề, tên – MSSV, danh sách 11 mục, cách chạy", "–"],
              ["2", "Code", "Tìm thư mục dự án ROOT, thêm ai/src vào sys.path để import thư viện nbaiot; nạp numpy, pandas, "
               "công cụ hiển thị", "Thư mục dự án: …\\DT043\\src"]])

    # ------------------------------------------------------------------ 1
    R.h1("3. Mục 1 – Môi trường và dataset (ô 3–8)")
    R.para("**Mục đích:** chứng minh dùng **đúng bộ N-BaIoT** mà đề giao và dữ liệu không bị sửa.")
    cells(R, [["4", "Code", "Đọc results/env_info.json", "i7-13650HX, 14 lõi / 20 luồng, RAM 23,7 GB, Python 3.11.9, git commit"],
              ["6", "Code", "Đọc data/DOWNLOAD_INFO.json (ghi lúc tải bằng 01_download.py)",
               "Nguồn UCI, DOI 10.24432/C5RC8J, CC BY 4.0, tải 11/10/2026, zip 1,77 GB, SHA-256"],
              ["8", "Code", "Gọi hàm verify của 02_verify_manifest.py: tính lại SHA-256 của 107 file, so MANIFEST.sha256",
               "107 file – sai/thiếu 0 – Manifest OK (≈ 8 s)"]])
    say(R, "“Sao biết đúng dataset?” → chỉ ô 6 (nguồn, DOI, giấy phép) và ô 8 (107/107 file khớp checksum).")

    # ------------------------------------------------------------------ 2
    R.h1("4. Mục 2 – Chất lượng dữ liệu và EDA (ô 9–11)")
    cells(R, [["10", "Code", "Đọc file_stats.csv, device_summary.csv",
               "7.062.606 dòng (trùng số UCI công bố); 157.779 dòng trùng (2,2%); còn 6.904.827; NaN/Inf = 0; tấn công : "
               "benign = 12,4 : 1 → không dùng Accuracy"],
              ["11", "Code", "6 file trùng nhiều nhất; hình số mẫu theo thiết bị; PCA của Danmini",
               "Benign Danmini trùng 18,5%; hình cho thấy mất cân bằng và mức tách benign/tấn công"]])

    # ------------------------------------------------------------------ 3
    R.h1("5. Mục 3 – Chia dữ liệu chống rò rỉ (ô 12–14)")
    R.para("Benign của từng thiết bị chia **theo thời gian** 1/3 DStrn – 1/3 DSopt – 1/3 test, bỏ **500 dòng đệm** ở mỗi ranh giới; "
           "scaler chỉ fit trên DStrn; loại khỏi test các dòng trùng hash với DStrn/DSopt; **toàn bộ dữ liệu tấn công chỉ ở test**.")
    cells(R, [["13", "Code", "load_config(\"E4_light\"); in cấu hình split, model, threshold; ví dụ chronological_split(1000, "
               "đệm 50)", "Chia theo thời gian, purge_gap 500; ví dụ: train 0–332, opt 383–666, test 717–999"],
              ["14", "Code", "load_split cho Ennio_Doorbell, seed 42 (cố ý chọn thiết bị có lỗi chính)",
               "35.410 benign → train 11.803, opt 11.304, test 11.303; dòng trùng bị loại 0; test có thêm 5 file BASHLITE "
               "(tcp 93.903, udp 98.355 dòng)"]])
    say(R, "“Chia test thế nào?” → ô 13–14: theo thời gian, có vùng đệm, tấn công chỉ ở test; chia ngẫu nhiên sẽ rò rỉ (E6 làm FPR "
        "đẹp giả 0,0006).")

    # ------------------------------------------------------------------ 4
    R.h1("6. Mục 4 – Huấn luyện V1 và chọn ngưỡng (ô 15–19)")
    cells(R, [["16", "Code", "So kiến trúc (layer_dims, count_params); make_and_train huấn luyện V1",
               "V1 [115, 32, 8, 32, 115] = 8.059 tham số; B0 (Meidan) = 36.876 → V1 = 21,9%; huấn luyện 10 s, 66 epoch "
               "(tốt nhất 58)"],
              ["17", "Code", "Tính MSE trên DSopt và test; decide → tr*, ws*; full_eval mức cửa sổ",
               "tr* = mean + std = 23,37; ws* = 2; macro-F1 0,32, TPR 0,37, FPR 0, ROC-AUC 0,98; recall combo/junk/scan ≈ "
               "0,999, tcp/udp 0,0001 (MSE trung vị 0,24 ≪ 23,37)"],
              ["18", "Code", "Vẽ phân bố MSE (thang log) của benign, scan, tcp, udp và đường ngưỡng",
               "tcp/udp nằm lẫn vùng benign, dưới ngưỡng"],
              ["19", "Markdown", "Nhận xét: lỗi chính là flood tcp/udp giả mạo nguồn; 1 thiết bị × 1 seed chỉ minh họa", "–"]])
    img = cell_image(nb, 18)
    if img:
        R.figure(img, "Output ô 18: phân bố MSE của V1 trên Ennio_Doorbell (seed 42) – tcp/udp nằm dưới ngưỡng tr*", 14)
    R.para("**Ý nghĩa:** mô hình phân biệt tốt (ROC-AUC 0,98), vấn đề nằm ở **ngưỡng**: flood tcp/udp của BASHLITE giả mạo nguồn "
           "nên mỗi gói giống gói đầu của một luồng mới (weight = 1, variance = 0), MSE rất nhỏ – nhỏ hơn cả đuôi benign kéo "
           "ngưỡng mean + std lên cao.")
    say(R, "“Sao TPR thấp?” → ô 17–18.")

    # ------------------------------------------------------------------ 5
    R.h1("7. Mục 5 – Lượng tử hóa int8 và hiệu chỉnh ngưỡng (ô 20–23)")
    cells(R, [["21", "Code", "to_tflite fp32 và int8 (representative data từ DStrn); so: fp32 / int8 giữ ngưỡng fp32 / int8 "
               "tính lại tr*, ws* trên DSopt", "fp32 33,7 KB, int8 15,3 KB; tr* int8 hiệu chỉnh 22,74; với Ennio 3 cách cho "
               "metric như nhau"],
              ["23", "Code", "So kết quả chạy lại với lần chạy chính thức (results/raw/E4_light/…/seed=42) và gói triển khai "
               "(artifacts/deploy/…/meta.json)", "Trùng khớp: tr* 23,3673, ws* 2, macro-F1 0,3204, TPR 0,3658 – chạy lại ra "
               "đúng kết quả đã báo cáo"]])
    say(R, "“Có tái lập được không?” → ô 23: chạy lại trong notebook trùng từng số với lần chạy chính thức và gói backend.")

    # ------------------------------------------------------------------ 6
    R.h1("8. Mục 6 – Edge benchmark (ô 24–26)")
    cells(R, [["25", "Code", "bench_tflite rút gọn: 3.000 lần × 3 lượt, batch 1, 1 luồng, không ghim lõi",
               "V1 int8 p95 ≈ 3 µs, ≈ 400 nghìn mẫu/s – chỉ minh họa"],
              ["26", "Code", "Đọc bảng chính thức (05_bench_edge.py: ghim 1 lõi E-core, 10.000 lần × 5 lượt)",
               "Bảng dưới – đây là số dùng trong báo cáo"]])
    tab(R, [["V1 int8 – P1 (1 lõi E-core)", "15,3", "8,98", "10,76", "102.899", "4,64", "40,5"],
            ["V1 fp32 – P1", "33,7", "10,56", "12,70", "63.627", "3,23", "44,2"],
            ["B0 fp32 – P1", "147,8", "16,94", "21,98", "40.120", "3,08", "83,5"],
            ["V1 int8 – P0 (20 luồng, batch 1)", "15,3", "473,27", "961,09", "2.049", "6,54", "3.937"]],
        ["Cấu hình", "KB", "p50 µs", "p95 µs", "mẫu/s", "RAM +MB", "µJ/mẫu"], [5.2, 1.4, 1.7, 1.7, 2.0, 1.8, 2.2],
        "Edge benchmark chính thức (output ô 26)", font=9.5)
    R.para("Ô 25 nhanh hơn ô 26 vì không ghim lõi yếu và đo ít lần; số chính thức là ô 26. 20 luồng với batch 1 chậm gấp ≈ 50 "
           "lần → trên edge nên chạy đơn luồng.")

    # ------------------------------------------------------------------ 7
    R.h1("9. Mục 7 – Kết quả chính thức 468 lần chạy (ô 27–33)")
    cells(R, [["28", "Code", "summary_by_config.csv: 14 cấu hình, mean, KTC95",
               "B0 macro-F1 0,706, TPR 0,822, FPR 0,0025; Isolation Forest 0,886; V1 0,689; E6 rò rỉ FPR 0,0006 (đẹp giả)"],
              ["29", "Code", "recall_groups.csv + hình recall theo loại tấn công",
               "8 loại còn lại ≈ 0,9999; tcp/udp 0,42–0,47 với AE, 0,78 với IF"],
              ["30", "Code", "stat_tests.csv: Wilcoxon + hiệu chỉnh Holm",
               "RQ2 per-device > global: thắng 4/9, p = 0,285 → không có ý nghĩa thống kê"],
              ["31", "Code", "Hình độ ổn định theo seed, hình trade-off lượng tử hóa", "Kết quả dao động theo seed"],
              ["33", "Code", "criteria_check.csv – tiêu chí chốt trước", "RQ1–RQ4 không đạt, RQ5 đạt (bảng dưới)"]])
    tab(R, [["RQ1", "TPR ≥ 0,99 và FPR ≤ 0,02 (B0)", "TPR 0,8222, FPR 0,0025", "Không đạt"],
            ["RQ2", "B0 > B1 ở ≥ 7/9 thiết bị, p < 0,05", "thắng 4/9, p = 0,2852", "Không đạt"],
            ["RQ3", "V1 ≤ 25% tham số, Δmacro-F1 ≤ 0,01", "21,9%, Δ = +0,0171", "Không đạt"],
            ["RQ4", "int8 + hiệu chỉnh: Δmacro-F1 ≤ 0,005, ≤ 30% kích thước", "Δ = −0,0278, 45,5%", "Không đạt"],
            ["RQ5", "p95 ≤ 1 ms, ≤ 50 KB, RAM ≤ 50 MB", "10,8 µs, 15,3 KB, 4,6 MB", "Đạt"]],
        ["RQ", "Tiêu chí", "Giá trị đo", "Kết luận"], [1.2, 6.8, 5.0, 3.0], "Đối chiếu tiêu chí (output ô 33)", font=9.5)
    say(R, "“Đạt mục tiêu chưa?” → ô 33; tiêu chí chốt trước khi chạy, có SHA-256 trong nhật ký, không chỉnh theo kết quả.")

    # ------------------------------------------------------------------ 8
    R.h1("10. Mục 8 – MTD, mô phỏng HARM rút gọn (ô 34–35)")
    cells(R, [["35", "Code", "mtd_harm_policies.csv + hình ASP theo chu kỳ + hình trade-off MTD lai",
               "Chu kỳ 20 bước: không MTD 0,498 → shuffle 0,409, diversity 0,437, kết hợp 0,327; MTD lai: cùng chi phí lộ "
               "diện ít hơn time-based"]])

    # ------------------------------------------------------------------ 9
    R.h1("11. Mục 9 – Tái lập hai bài báo (ô 36–45)")
    R.para("Quy ước: **lệch % = (tái lập − bài báo) / bài báo × 100**; **khớp khi |lệch| ≤ 5%** (ngưỡng do đề tài chọn).")
    cells(R, [["38", "Code", "9.1 – gọi trực tiếp thư viện tharm (build, diversity, scenarios, path_metrics), so với số bài",
               "Bảng dưới"],
              ["40", "Code", "9.2 – chạy hàm của 11_paper_figures.py; Hình 6 gốc và chạy lại",
               "Diversity khớp 7/7 VM; shuffle, S+D khớp ở V5"],
              ["41", "Code", "Hình 7 gốc và chạy lại + bảng ASP 5 đường tới V8", "ASP 0,91–0,94; không tái lập được"],
              ["42", "Code", "Hình 2 (a, b) Meidan gốc và chạy lại", "FPR khớp, TPR AE thấp hơn"],
              ["44", "Code", "9.3 – bảng % khớp 10 mức, tính từ CSV, có cột file nguồn", "Bảng thứ hai dưới đây"],
              ["45", "Markdown", "Cách đọc bảng: chỗ bài cho đủ dữ liệu thì khớp, chỗ lệch là chỗ bài không công bố", "–"]])
    tab(R, [["R_V2", "16,28", "15,941", "−2,08%"], ["R_V4", "12,47", "12,473", "+0,02%"], ["R_V5", "12,58", "12,578", "−0,02%"],
            ["R_V7", "8,67", "8,667", "−0,03%"], ["R_V8", "5,62", "5,625", "+0,09%"], ["R_V5 sau diversity (Linux)", "8,90", "8,934", "+0,38%"],
            ["Đường shuffle A-V2-V7-V5-V8", "43,15", "42,811", "−0,79%"], ["Đường diversity A-V2-V4-V5-V8", "43,31", "42,973", "−0,78%"],
            ["Đường redundancy A-V2-V4-V5′-V8", "43,31", "42,973", "−0,78%"]],
        ["Giá trị", "Bài báo", "Tái lập", "Lệch"], [7.0, 2.8, 2.8, 2.6], "Chạy trực tiếp THARM so với bài (output ô 38)", font=9.5)
    tab(R, [["Masud", "Rủi ro từng VM", "6/6 (100%)", "0,4%"], ["Masud", "Rủi ro 3 đường ví dụ", "3/3 (100%)", "0,8%"],
            ["Masud", "Bảng 4 – ASP từng VM", "8/8 (100%)", "1,2%"], ["Masud", "Bảng 4 – AC, AR từng VM", "8/16 (50%)", "7,8%"],
            ["Masud", "Tổng toàn mạng R, AC, RoC", "1/9 (11%)", "190%"], ["Masud", "Hình 6 – AR (5 MTD × 7 VM)", "11/35 (31%)", "54%"],
            ["Masud", "Hình 7 – ASP theo đường", "0/8 (0%)", "–"], ["Masud", "Kết luận định tính (topology Hình 3)", "6/7 (86%)", "–"],
            ["Meidan", "FPR ≤ 0,02 theo thiết bị", "9/9 (100%)", "–"], ["Meidan", "TPR = 100% theo thiết bị", "3/9 (33%)", "17,8%"]],
        ["Bài", "Mức so sánh", "Khớp ≤ 5%", "Lệch |TB|"], [2.0, 7.2, 3.6, 3.2], "Bảng % khớp (output ô 44)", font=9.5)
    say(R, "“Giống bài bao nhiêu %, số ở đâu ra?” → ô 44 (cột nguồn ghi file CSV từng dòng). Lưu ý: số Hình 6 phía bài báo đọc "
        "bằng mắt từ hình (± 5).")

    # ------------------------------------------------------------------ 10
    R.h1("12. Mục 10 – Demo API backend (ô 46–47)")
    R.para("Ô 47 chạy backend FastAPI ngay trong notebook bằng TestClient, ghi vào **CSDL tạm** (không làm bẩn db/dt043.sqlite3): "
           "/api/health báo **9 model đã nạp, 0 lỗi gói**, rồi phát lại 2.000 mẫu mỗi trường hợp.")
    tab(R, [["Danmini_Doorbell", "mirai/syn", "2000", "1989/1989", "Có"],
            ["Ennio_Doorbell", "benign", "0", "0/1999", "Không – không báo động giả"],
            ["Ennio_Doorbell", "gafgyt/tcp", "2", "0/1999", "Không – đúng lỗi bỏ sót"]],
        ["Thiết bị", "Segment", "Mẫu vượt ngưỡng", "Cửa sổ cảnh báo", "Cảnh báo"], [3.6, 2.4, 2.8, 3.0, 4.2],
        "Output ô 47 – phát lại dữ liệu test", font=9.5)
    R.para("Bảng hành động MTD: cảnh báo Mirai **tự kích hoạt 2 hành động event-based** – shuffle IP (10.0.0.218 → 10.0.0.100) và "
           "diversity firmware (fw-A → fw-C). Suy luận V1 int8 ≈ 0,5–0,7 µs/mẫu khi chạy theo lô.")

    # ------------------------------------------------------------------ 11
    R.h1("13. Mục 11 – Kết luận (ô 48)")
    R.bullets(["AE per-device bắt gần tuyệt đối 8/10 loại tấn công với FPR rất thấp (B0 0,0025); bỏ sót flood tcp/udp giả mạo nguồn.",
               "V1 int8 ≈ 15 KB, vài µs/mẫu trên 1 lõi → khả thi cho edge (RQ5 đạt); RQ1–RQ4 không đạt, giữ nguyên tiêu chí.",
               "Kết quả dao động theo seed; MTD kết hợp shuffle + diversity cho ASP thấp nhất; MTD lai dùng cảnh báo AE giảm thời "
               "gian lộ diện."])

    R.h1("14. Thứ tự gợi ý khi demo notebook cho thầy")
    R.numbered(["**Ô 8** – đúng dataset (107/107 file khớp SHA-256).",
                "**Ô 14** – chia dữ liệu chống rò rỉ.",
                "**Ô 17–18** – lỗi tcp/udp nằm dưới ngưỡng.",
                "**Ô 23** – chạy lại khớp lần chạy chính thức.",
                "**Ô 33** – đối chiếu tiêu chí chốt trước.",
                "**Ô 44** – % khớp với hai bài báo.",
                "**Ô 47** – demo cảnh báo tự kích hoạt MTD."])

    R.save(OUT)
    print("đã ghi", OUT)


if __name__ == "__main__":
    main()
