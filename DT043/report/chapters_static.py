"""Các chương không phụ thuộc kết quả thực nghiệm: bìa, mở đầu, tài liệu nền, dữ liệu, phương pháp, thiết lập."""
from __future__ import annotations

import json

import pandas as pd

from docx_helpers import Report


def cover(R: Report, root):
    R.para("Họ và tên: Hoàng Thanh Trà", justify=False)
    R.para("MSSV: 1150080120", justify=False)
    R.para("Lớp: 11CNPM2", justify=False)
    R.para("Học phần: An toàn Bảo mật Hệ thống thông tin – Bài giữa kỳ", justify=False)
    R.para("Link GitHub: https://github.com/thtra04/LAB_AT_BMHTTT (thư mục DT043)", justify=False)
    R.para("")
    R.para("ĐỀ TÀI DT043", bold=True, size=15, align="center")
    R.para("PHÁT HIỆN BOTNET IoT BẰNG AUTOENCODER NHẸ", bold=True, size=18, align="center")
    R.para("Huấn luyện theo từng thiết bị, lượng tử hóa và đánh giá khả năng triển khai edge; "
           "tái lập có chọn lọc và mở rộng theo hướng Moving Target Defence", italic=True, align="center")
    R.para("")
    R.para("Dữ liệu: N-BaIoT (UCI, CC BY 4.0) · Paper chính: Masud et al., Computers & Security 153 (2025) 104380 · "
           "Paper tham chiếu kỹ thuật: Meidan et al., IEEE Pervasive Computing (2018)", size=11, align="center")
    R.para("Tháng 10/2026", align="center")
    R.page_break()
    R.para("MỤC LỤC", bold=True, size=14, align="center")
    R.toc()
    R.page_break()


def ch1_intro(R: Report):
    R.h1("Chương 1. Mở đầu")
    R.h2("1.1 Bối cảnh")
    R.para("Thiết bị IoT (camera, chuông cửa, thermostat, baby monitor…) thường dùng mật khẩu mặc định, hiếm khi được vá "
           "và có tài nguyên hạn chế. Các botnet như Mirai và BASHLITE (Gafgyt) khai thác điểm yếu này để chiếm hàng loạt "
           "thiết bị rồi dùng chúng tấn công từ chối dịch vụ. Một hướng phòng thủ thực tế là đặt bộ phát hiện bất thường "
           "ngay tại gateway/edge, học hành vi bình thường của **từng** thiết bị và cảnh báo khi hành vi lệch đi. Để chạy "
           "được ở edge, bộ phát hiện phải nhỏ, nhanh và tiết kiệm năng lượng.")
    R.h2("1.2 Mục tiêu và phạm vi")
    R.para("Đề tài xây dựng và đánh giá một khung thực nghiệm phát hiện botnet IoT bằng autoencoder (AE) huấn luyện "
           "riêng cho từng thiết bị chỉ trên lưu lượng benign; chuẩn hóa theo từng thiết bị; thu nhỏ model; lượng tử hóa "
           "TensorFlow Lite; đo chi phí suy luận trong điều kiện mô phỏng edge. Đề tài đồng thời tái lập có chọn lọc bài "
           "báo chính và bổ sung một biến thể phù hợp điều kiện môn học.")
    R.bullets([
        "**Trong phạm vi:** phát hiện bất thường không giám sát trên 115 đặc trưng có sẵn của N-BaIoT; 9 thiết bị; "
        "lượng tử hóa sau huấn luyện (PTQ); đo latency/bộ nhớ/CPU; mô phỏng MTD trên máy cá nhân.",
        "**Ngoài phạm vi:** bắt gói tin thời gian thực, chạy mã độc thật, triển khai MTD trên mạng thật, phân loại "
        "đa lớp loại tấn công (chỉ dùng nhãn loại tấn công để phân tích lỗi)."])
    R.h2("1.3 Câu hỏi nghiên cứu, giả thuyết và tiêu chí thành công")
    R.para("Tiêu chí thành công được chốt **trước** khi chạy ma trận thí nghiệm (file docs/tieu_chi_thanh_cong.md, "
           "SHA-256 3ac9bfdb…7b53 được ghi trong nhật ký) để tránh điều chỉnh tiêu chí theo kết quả.")
    R.table(pd.DataFrame([
        ["RQ1", "Tái lập baseline Meidan đạt mức paper?", "TPR ≥ 0.99 và FPR ≤ 0.02 (mức cửa sổ)"],
        ["RQ2", "Per-device tốt hơn một model chung?", "B0 > B1 ở ≥ 7/9 thiết bị, Wilcoxon p < 0.05"],
        ["RQ3", "AE nhẹ giữ được chất lượng?", "≤ 25% tham số, Δmacro-F1 ≤ 0.01"],
        ["RQ4", "Lượng tử hóa int8 + hiệu chỉnh ngưỡng?", "Δmacro-F1 ≤ 0.005, kích thước ≤ 30% fp32"],
        ["RQ5", "Triển khai được trên edge?", "p95 ≤ 1 ms/mẫu, model ≤ 50 KB, RSS tăng ≤ 50 MB"],
        ["RQ6", "Chất lượng detector ảnh hưởng MTD lai thế nào?", "Báo cáo trade-off an ninh – chi phí"],
    ], columns=["RQ", "Câu hỏi", "Tiêu chí (chốt trước)"]), "Câu hỏi nghiên cứu và tiêu chí thành công",
        col_widths_cm=[1.3, 7.2, 7.5])
    R.para("**Đối tượng đánh giá:** 9 bộ phát hiện (mỗi thiết bị một bộ) × các cấu hình model/lượng tử hóa; pipeline suy "
           "luận ở profile edge giả lập; các chính sách MTD mô phỏng.")
    R.h2("1.4 Đóng góp riêng của đề tài")
    R.bullets([
        "Tái lập baseline Meidan 2018 với quy trình chặt hơn (khử trùng lặp, purge gap, nhiều seed, kiểm định thống kê) và "
        "báo cáo trung thực các điểm **không** tái lập được.",
        "Biến thể **AE nhẹ + full-int8 + hiệu chỉnh lại ngưỡng sau lượng tử hóa** cho từng thiết bị.",
        "Edge benchmark có profile 1 luồng ghim vào lõi E-core, đo latency p50/p95/p99, RSS, CPU-time và energy proxy.",
        "Cầu nối với paper chính về MTD: mô hình đồ thị tấn công rút gọn (shuffle/diversity/kết hợp) và **MTD lai kích "
        "hoạt bởi cảnh báo AE thật**, đo trade-off giữa thời gian lộ diện và số lần move.",
        "Hệ thống demo tách 4 tầng **AI / Backend / Database / Frontend** với gói triển khai có kiểm tra toàn vẹn SHA-256.",
    ])
    R.para("Đề tài **không** tuyên bố vượt các paper: điều kiện thí nghiệm khác nhau (khử trùng lặp, cách tối ưu, phần "
           "cứng), và các so sánh với paper chỉ mang tính đối chiếu.")


def ch2_background(R: Report, root):
    R.h1("Chương 2. Tài liệu nền và phiếu tái lập")
    R.h2("2.1 Paper chính: hybrid Moving Target Defence trong IoT")
    R.para("Masud, Keshk, Moustafa, Turnbull và Susilo (2025) nghiên cứu Moving Target Defence (MTD) – liên tục thay đổi "
           "bề mặt tấn công để kẻ tấn công khó khai thác. Bài báo chỉ ra khoảng trống: thiếu đánh giá hiệu quả **kết hợp** "
           "nhiều kỹ thuật MTD theo thời gian, chi phí, công sức, đặc biệt trong IoT không đồng nhất; đồng thời MTD có thể "
           "tiêu tốn quá mức tài nguyên. Phương pháp \"Vulnerability Defence\" dựa trên mô hình **3-layer Temporal Hierarchical "
           "Attack Representation Model (3-layer-THARM)**, đánh giá an toàn của các trạng thái mạng gộp theo thời gian với "
           "các metric an ninh (xác suất tấn công thành công, rủi ro, chi phí tấn công) và nhận diện đường tấn công. Kết luận: "
           "kết hợp kỹ thuật MTD khác nhóm (shuffle + diversity) thường cho xác suất tấn công thành công và rủi ro thấp hơn, "
           "chi phí tấn công cao hơn.")
    R.para("**Nhận xét quan trọng:** paper chính **không** dùng autoencoder, N-BaIoT, lượng tử hóa hay đo edge, tức là lệch "
           "với tên đề tài. Vì vậy đề tài chia làm hai track: Track A (lõi, ~70%) làm phần phát hiện botnet bằng AE nhẹ, lấy "
           "Meidan 2018 làm baseline kỹ thuật; Track B (~30%) tái lập **có chọn lọc xu hướng** của paper chính bằng mô hình "
           "đồ thị tấn công rút gọn, rồi nối hai track bằng biến thể MTD lai kích hoạt bởi cảnh báo của AE.")
    R.table(pd.DataFrame([
        ["Bài toán", "Hiệu quả MTD kết hợp trong IoT; chi phí tài nguyên của MTD"],
        ["Pipeline", "3-layer THARM: trạng thái mạng theo thời gian → đồ thị tiếp cận → cây lỗ hổng → metric"],
        ["Kỹ thuật", "Shuffle, diversity và tổ hợp (cần đối chiếu toàn văn về redundancy, chu kỳ)"],
        ["Metric", "Xác suất tấn công thành công, attack risk, attack cost, đường tấn công"],
        ["Kết quả mục tiêu", "Kết hợp shuffle + diversity tốt hơn dùng riêng"],
        ["Liên hệ DT043", "Detector AE đóng vai trò bộ kích hoạt event-based của MTD lai"],
    ], columns=["Mục", "Nội dung"]), "Phiếu tái lập rút gọn – paper chính", col_widths_cm=[3.5, 12.5])
    R.h3("Hạn chế và điểm cần tái lập (≥ 5)")
    R.numbered([
        "Đánh giá bằng mô hình đồ thị tấn công (mô phỏng), không triển khai trên thiết bị thật.",
        "Xác suất khai thác thường gán tĩnh theo CVSS, không phản ánh kẻ tấn công thích nghi.",
        "Không mô hình hóa bộ phát hiện kích hoạt MTD và sai số của nó (FP gây move vô ích, FN/độ trễ gây lộ diện) – "
        "khoảng trống Track B khai thác.",
        "Chi phí tài nguyên của MTD được nêu là vấn đề nhưng chưa có số đo trên thiết bị edge cụ thể.",
        "Khả năng mở rộng khi số node/lỗ hổng tăng (bùng nổ số đường tấn công).",
        "Sự sẵn có của mã nguồn/cấu hình topology quyết định khả năng tái lập số liệu tuyệt đối; DT043 chỉ tái lập xu hướng.",
        "Độ nhạy của kết quả theo chu kỳ MTD.",
    ])
    R.para("Các mục 2, 4, 5, 6, 7 được đánh dấu cần đối chiếu với toàn văn (xem docs/phieu_tai_lap_paper.md), vì khi lập "
           "phiếu chỉ truy cập được metadata và abstract chính thức.", italic=True, size=11)

    R.h2("2.2 Paper tham chiếu kỹ thuật: N-BaIoT (Meidan et al., 2018)")
    R.para("Meidan và cộng sự lây nhiễm Mirai và BASHLITE vào 9 thiết bị IoT thương mại, trích 115 đặc trưng thống kê cho "
           "mỗi gói tin và huấn luyện một deep autoencoder **riêng cho từng thiết bị** chỉ trên dữ liệu benign. Dữ liệu benign "
           "mỗi thiết bị được chia theo thời gian thành ba phần bằng nhau: DStrn (huấn luyện), DSopt (tối ưu η, epochs, ngưỡng, "
           "cửa sổ) và phần benign của DStst. Ngưỡng tr* = mean(MSE_DSopt) + std(MSE_DSopt); quyết định cuối dựa trên "
           "majority vote trên cửa sổ trượt ws*, là cửa sổ ngắn nhất cho FPR = 0 trên DSopt. Kiến trúc: các lớp encoder 75%, "
           "50%, 33%, 25% kích thước đầu vào, decoder đối xứng.")
    R.table(pd.DataFrame([
        ["TPR", "100% với mọi thiết bị"],
        ["FPR trung bình", "0.007 ± 0.01 (SVM 0.026 ± 0.029; Isolation Forest 0.027 ± 0.041; LOF 0.086 ± 0.081)"],
        ["Thời gian phát hiện", "174 ± 212 ms"],
        ["tr* / ws* theo thiết bị", "0.004–0.074 / 20–82"],
        ["Kích thước model", "172 kB (Keras object)"],
    ], columns=["Chỉ số", "Kết quả công bố"]), "Kết quả mục tiêu của Meidan 2018", col_widths_cm=[4.5, 11.5])
    R.para("Hạn chế đã xác nhận khi đọc toàn văn: chỉ một lần chia dữ liệu, không có khoảng tin cậy; siêu tham số tối ưu "
           "riêng từng thiết bị (epochs 100–800) nên khó tái lập chính xác; ws* chọn để FPR = 0 trên DSopt; không lượng tử "
           "hóa và không đo suy luận trên edge; tập test mất cân bằng; môi trường lab với 9 thiết bị, 2 botnet.")
    R.h2("2.3 Kỹ thuật nền")
    R.bullets([
        "**Autoencoder phát hiện bất thường:** mạng nén – giải nén học tái tạo dữ liệu benign; mẫu lạ có lỗi tái tạo (MSE) cao.",
        "**Lượng tử hóa sau huấn luyện (TFLite):** float16; dynamic-range int8 (chỉ trọng số int8); full-integer int8 "
        "(trọng số + kích hoạt + vào/ra int8, cần representative dataset để hiệu chỉnh dải giá trị).",
        "**Majority vote trên cửa sổ trượt:** giảm cảnh báo giả do các mẫu benign đơn lẻ có MSE cao, đổi lại độ trễ phát hiện.",
        "**Wilcoxon signed-rank:** kiểm định phi tham số cho so sánh cặp trên 9 thiết bị; hiệu chỉnh Holm cho nhiều so sánh.",
    ])


def ch3_data(R: Report, root):
    R.h1("Chương 3. Dữ liệu, EDA và threat model")
    info = json.loads((root / "data" / "DOWNLOAD_INFO.json").read_text(encoding="utf-8"))
    R.h2("3.1 Nguồn, giấy phép, phiên bản và tính toàn vẹn")
    R.table(pd.DataFrame([
        ["Nguồn", info["source_page"]],
        ["DOI / Giấy phép", f"{info['doi']} / {info['license']} (bắt buộc ghi nguồn)"],
        ["Ngày đóng góp UCI", info["uci_donated"]],
        ["Thời điểm tải", info["downloaded_at_utc"][:19] + " UTC"],
        ["Kích thước zip", f"{info['zip_bytes']:,} byte"],
        ["SHA-256 zip", info["zip_sha256"]],
        ["Manifest", f"data/MANIFEST.sha256 – {info['n_files']} file; kiểm lại bằng 02_verify_manifest.py"],
    ], columns=["Mục", "Giá trị"]), "Thông tin phiên bản dữ liệu", font=9.5, col_widths_cm=[3.5, 12.5])
    R.para("Mỗi dòng là một \"ảnh chụp hành vi\" khi một gói tin đến, gồm 23 thống kê (weight, mean, variance/std, "
           "magnitude, radius, covariance, pcc) của 5 nhóm luồng (MI_dir, H, HH, HH_jit, HpHp) trên 5 cửa sổ thời gian suy "
           "giảm (L5 ≈ 100 ms đến L0.01 ≈ 1 phút) – tổng 115 đặc trưng. Nhãn theo file: benign, 5 kiểu BASHLITE (combo, "
           "junk, scan, tcp, udp), 5 kiểu Mirai (ack, scan, syn, udp, udpplain); Ennio Doorbell và Samsung Webcam không có Mirai. "
           "Dữ liệu không chứa IP/MAC thô, payload hay thông tin cá nhân.")
    R.h2("3.2 Chất lượng dữ liệu")
    fs = pd.read_csv(root / "results" / "data_quality" / "file_stats.csv")
    ds = pd.read_csv(root / "results" / "data_quality" / "device_summary.csv")
    ben = fs[fs.segment == "benign"].set_index("device")
    t = pd.DataFrame({
        "Thiết bị": ds.device,
        "Benign gốc": [int(ben.loc[d, "rows_raw"]) for d in ds.device],
        "Trùng (%)": [100 * ben.loc[d, "dup_ratio"] for d in ds.device],
        "Benign sạch": ds.rows_dedup_benign.astype(int),
        "Attack sạch": ds.rows_dedup_attack.astype(int),
        "Attack:Benign": ds.attack_to_benign_ratio,
    })
    R.table(t, "Thống kê chất lượng dữ liệu theo thiết bị (sau khử trùng lặp trong từng file)", font=9.5,
            fmt={"Trùng (%)": lambda v: f"{v:.1f}", "Attack:Benign": lambda v: f"{v:.1f}×",
                 "Benign gốc": lambda v: f"{v:,}", "Benign sạch": lambda v: f"{v:,}", "Attack sạch": lambda v: f"{v:,}"})
    R.para(f"Tổng cộng {int(fs.rows_raw.sum()):,} dòng gốc, còn {int(fs.rows_dedup.sum()):,} dòng sau khi bỏ "
           f"{int(fs.exact_duplicates.sum()):,} dòng trùng lặp chính xác. Không có NaN, ±inf hay cột hằng. Trùng lặp tập "
           "trung ở benign (Danmini 18.5%) và gafgyt tcp/udp; Mirai không có dòng trùng. Có giá trị cực lớn (tới 5.88e17 "
           "ở các cột variance/covariance), nên lỗi tái tạo được tính bằng float64 để tránh tràn số.")
    R.h2("3.3 EDA")
    ac = pd.read_csv(root / "results" / "tables" / "eda_autocorrelation.csv")
    R.figure(root / "results" / "figures" / "eda_class_counts.png", "Số mẫu theo thiết bị và botnet (thang log)", 14)
    R.para(f"**Mất cân bằng:** tập tấn công lớn gấp {ds.attack_to_benign_ratio.min():.1f}–{ds.attack_to_benign_ratio.max():.1f} "
           "lần benign. Nếu dùng Accuracy hoặc F1 của lớp tấn công, một bộ phát hiện báo động mọi thứ vẫn đạt điểm rất "
           "cao. Vì vậy metric chính là **macro-F1 và FPR ở mức cửa sổ**, kèm F1 khi giả định test cân bằng.")
    R.para(f"**Tự tương quan theo thời gian:** hệ số tự tương quan bậc 1 trung bình của các đặc trưng benign theo thứ tự gốc "
           f"là {ac.lag1_autocorr_ordered.min():.2f}–{ac.lag1_autocorr_ordered.max():.2f}, trong khi sau khi xáo trộn chỉ còn "
           "≈ 0.00. Hai dòng liền kề gần giống nhau, nên chia ngẫu nhiên sẽ đưa \"anh em sinh đôi\" của mẫu test vào tập "
           "train (rò rỉ). Đây là bằng chứng định lượng cho việc chia theo thời gian và thêm purge gap.")
    R.figure(root / "results" / "figures" / "eda_feature_by_device.png",
             "Cùng một đặc trưng (HH_L0.1_mean) có phân phối rất khác giữa các thiết bị", 14)
    R.para("Phân phối đặc trưng khác nhau rõ rệt giữa các thiết bị, là cơ sở cho chuẩn hóa và mô hình **theo từng thiết bị**.")
    R.h2("3.4 Chống rò rỉ train–test")
    R.numbered([
        "Khử trùng lặp chính xác trong từng file, giữ thứ tự thời gian.",
        "Chia benign theo thời gian 1/3 – 1/3 – 1/3 (DStrn, DSopt, test) như Meidan, bỏ 500 dòng đệm ở mỗi ranh giới.",
        "Loại khỏi test các dòng trùng hash với DStrn/DSopt (thực tế 0 dòng sau bước 1 – có unit test kiểm tra).",
        "Scaler z-score fit chỉ trên DStrn của đúng thiết bị; scaler gắn tên thiết bị để không dùng nhầm.",
        "Ngưỡng, cửa sổ và early stopping chỉ dùng DSopt (benign); dữ liệu tấn công chỉ xuất hiện ở test.",
        "Majority vote không trượt qua ranh giới giữa các file.",
        "Thí nghiệm đối chứng E6 cố tình làm sai (chia ngẫu nhiên, không purge, không khử trùng, scaler fit cả test) để đo mức sai lệch.",
    ])
    R.h2("3.5 Threat model")
    R.code("""
[Thiết bị IoT] --LAN--> [Edge gateway: trích đặc trưng + AE per-device, int8, 1 luồng]
 (không tin cậy)  TB1                          |
                                               | TB2 (REST/JSON, kiểm tra đầu vào)
                                               v
               [Backend/SOC: FastAPI + SQLite] <-- TB3 -- [Dashboard trên trình duyệt]
""")
    R.table(pd.DataFrame([
        ["Sửa model triển khai", "SHA-256 trong meta.json, từ chối nạp nếu lệch", "test_tampered_bundle_rejected"],
        ["Sửa dữ liệu", "Manifest SHA-256 cho 107 file", "test_manifest_detects_tampering"],
        ["Đầu vào giả/sai", "Pydantic: số chiều, hữu hạn, ≤ 20.000 mẫu/lô", "test_wrong_dimension_422, …"],
        ["Path traversal", "Whitelist regex cho segment/tên thiết bị", "test_bad_segment_and_device_name_422"],
        ["Né tránh (evasion)", "Đo TPR khi kéo mẫu tấn công về phía benign", "E9 robust"],
        ["Đầu độc (poisoning)", "Đo suy giảm khi lẫn 1–5% tấn công vào DStrn", "E9 poison"],
        ["Rò rỉ khi đánh giá", "Mục 3.4", "test_no_leakage_between_splits"],
    ], columns=["Mối đe dọa", "Biện pháp", "Kiểm thử"]), "Mối đe dọa chính và biện pháp", font=9.5,
        col_widths_cm=[3.8, 7.0, 5.2])
    R.para("**Đạo đức và an toàn:** chỉ dùng dữ liệu công khai trên máy cá nhân; không chạy mã độc, không quét hay tấn công "
           "hệ thống thật; các \"tấn công\" trong E9 chỉ là biến đổi dữ liệu offline; MTD chỉ được mô phỏng và ghi vào CSDL.")


def ch4_method(R: Report, root):
    R.h1("Chương 4. Phương pháp và hệ thống")
    R.h2("4.1 Pipeline")
    R.numbered([
        "Nạp parquet, kiểm tra schema; chia benign theo thời gian + purge gap; z-score per-device (fit trên DStrn).",
        "Huấn luyện AE: Adam lr 1e-3, batch 256, early stopping (patience 8) trên DSopt, tối đa 100 epoch.",
        "Tính MSE trên DSopt → tr* = mean + std; ws* = cửa sổ nhỏ nhất cho FPR = 0 trên DSopt.",
        "Đánh giá trên test ở mức mẫu và mức cửa sổ (majority vote trong từng file).",
        "Chuyển TFLite fp32/fp16/dynamic/int8; với mỗi bản, đánh giá cả khi giữ ngưỡng fp32 và khi hiệu chỉnh lại "
        "tr*, ws* trên DSopt; lưu config, log, metric, model.",
    ])
    R.h2("4.2 Baseline và biến thể")
    R.table(pd.DataFrame([
        ["B0", "AE Meidan 115-86-58-38-29-38-58-86-115, per-device", "36,876", "Baseline tái lập"],
        ["B1 global", "Như B0 nhưng 1 model + 1 scaler + 1 ngưỡng cho cả 9 thiết bị", "36,876", "Kiểm tra giả thuyết per-device"],
        ["B1 chung+pdnorm", "1 model chung, scaler và ngưỡng riêng từng thiết bị", "36,876", "Tách tác dụng chuẩn hóa"],
        ["B2", "Isolation Forest per-device (100 cây, cùng cách chọn tr*, ws*)", "–", "Baseline không phải mạng nơ-ron"],
        ["V1", "AE nhẹ 115-32-8-32-115", "8,059", "Biến thể nhẹ (21.9% tham số)"],
        ["V2", "AE siêu nhẹ 23-12-4-12-23 trên 23 đặc trưng của 1 cửa sổ (chạy cả 5 cửa sổ)", "~700", "Giảm cả đặc trưng"],
        ["V1 int8 + hiệu chỉnh", "V1 full-integer int8, tính lại tr*, ws* trên DSopt bằng model int8", "8,059", "Cải tiến chính"],
    ], columns=["Mã", "Mô tả", "Tham số", "Vai trò"]), "Baseline và biến thể", font=9.5, col_widths_cm=[2.6, 8.0, 1.8, 3.6])
    R.para("**Vì sao cần hiệu chỉnh ngưỡng sau lượng tử hóa:** lượng tử hóa làm thay đổi phân phối lỗi tái tạo, nên ngưỡng "
           "tính trên model fp32 không còn \"đúng chỗ\" với model int8. Vì ngưỡng chỉ phụ thuộc DSopt (benign), có thể tính "
           "lại bằng chính model int8 mà không chạm vào dữ liệu test hay dữ liệu tấn công.")
    R.h2("4.3 Edge benchmark")
    R.bullets([
        "**P0:** máy đầy đủ (20 luồng), batch 1 và batch 256 – tham chiếu.",
        "**P1 – edge giả lập:** 1 luồng TFLite, process ghim vào **1 lõi E-core** (logical CPU 19, xác định bằng "
        "GetSystemCpuSetInformation – EfficiencyClass), batch 1.",
        "Mỗi cấu hình chạy trong process riêng để đo RSS sạch; warm-up 200 lần; 10.000 lần × 5 lượt; báo cáo p50/p95/p99, "
        "thời gian riêng invoke(), throughput, RSS tăng thêm.",
        "**Energy proxy:** CPU-time mỗi lần suy luận × 55 W / 14 lõi (Processor Base Power của i7-13650HX chia đều) – là cận "
        "trên thô, không phải đo điện; kèm số MAC/suy luận độc lập phần cứng.",
    ])
    R.h2("4.4 Mô phỏng MTD (Track B)")
    R.bullets([
        "**Phần 1 – HARM rút gọn:** internet → gateway → 9 thiết bị → cloud; mỗi node có các lỗ hổng (OR) với xác suất khai "
        "thác giả định; kẻ tấn công có ngân sách 20 bước; shuffle làm kẻ tấn công mất các vị trí đã chiếm và phải trinh sát "
        "lại; diversity làm exploit đã chuẩn bị chỉ còn 30% hiệu quả đến khi thích nghi; Monte Carlo 2.000 lần × 5 seed.",
        "**Phần 2 – MTD lai kích hoạt bởi AE:** dùng chuỗi quyết định thật của V1 trên luồng test (benign rồi các đợt tấn "
        "công); so sánh time-based (chu kỳ T), event-based (move khi có cửa sổ cảnh báo) và hybrid; đo thời gian lộ diện, "
        "số move/10.000 mẫu, move vô ích do cảnh báo giả.",
    ])
    R.h2("4.5 Kiến trúc hệ thống demo: AI / BE / DB / FE")
    R.code("""
AI (ai/)       huấn luyện, đánh giá, lượng tử hóa, benchmark
   |           xuất gói: artifacts/deploy/<thiết bị>/{model.tflite, scaler.json, meta.json}
   v
BE (backend/)  FastAPI: nạp gói (kiểm SHA-256), suy luận TFLite 1 luồng
   |   ^       API: /api/detect, /api/replay, /api/alerts, /api/mtd, /api/experiments
   v   |
DB (db/)       SQLite: devices, models, detection_batches, alerts, mtd_actions
FE (frontend/) HTML/CSS/JS: thiết bị, phát lại, biểu đồ MSE, cảnh báo, nhật ký MTD
""")
    R.para("Tầng AI và tầng BE chỉ giao tiếp qua \"gói triển khai\" nên có thể thay model mà không sửa backend. CSDL chỉ "
           "lưu metadata và kết quả suy luận, không lưu dữ liệu thô. Khi có cửa sổ cảnh báo, backend tạo bản ghi alert và "
           "gọi MTD event-based (shuffle địa chỉ ảo + đổi biến thể firmware ảo); endpoint /api/mtd/tick chạy MTD time-based.")
    R.figure(root / "results" / "figures" / "demo_dashboard.png",
             "Dashboard demo: phát lại 2.000 mẫu mirai/syn của Danmini → 100% cửa sổ cảnh báo, sinh cảnh báo và 2 hành "
             "động MTD (event-based); suy luận V1 int8 vài µs/mẫu", 15)
    R.para("Demo cũng tái hiện đúng các kết quả nghiên cứu: phát lại benign (phần test) không sinh cảnh báo, còn gafgyt/tcp "
           "trên Ennio_Doorbell không vượt ngưỡng – đúng lỗi bỏ sót được phân tích ở Chương 7.")


def ch5_setup(R: Report, root):
    R.h1("Chương 5. Thiết lập thực nghiệm")
    env = json.loads((root / "results" / "env_info.json").read_text(encoding="utf-8"))
    p = env["packages"]
    R.table(pd.DataFrame([
        ["CPU", f"{env['cpu']} – {env['physical_cores']} lõi vật lý (6 P-core + 8 E-core), {env['logical_cpus']} luồng"],
        ["RAM / OS", f"{env['ram_gb']} GB / {env['os']}"],
        ["Python", env["python"] + " (venv riêng)"],
        ["Thư viện", f"TensorFlow {p['tensorflow']}, Keras {p['keras']}, NumPy {p['numpy']}, pandas {p['pandas']}, "
                     f"scikit-learn {p['scikit-learn']}, SciPy {p['scipy']}"],
        ["Khóa phiên bản", "requirements.txt (trực tiếp) + requirements-lock.txt (pip freeze)"],
        ["Seed", "42, 1337, 2024, 7, 123 (V2 và E6/E9: 3 seed đầu); PYTHONHASHSEED, NumPy, TF + op determinism"],
        ["Luồng", "2 luồng TF mỗi process, 2 process song song"],
    ], columns=["Mục", "Giá trị"]), "Môi trường thực nghiệm", font=9.5, col_widths_cm=[3.2, 12.8])
    R.table(pd.DataFrame([
        ["E1", "B0 – tái lập baseline", "9 × 5", "RQ1"],
        ["E2", "B1 global; B1 chung+pdnorm", "9 × 5 × 2", "RQ2"],
        ["E3", "B2 Isolation Forest", "9 × 5", "baseline"],
        ["E4", "V1; V2 × 5 cửa sổ", "9 × 5 + 9 × 3 × 5", "RQ3"],
        ["E5", "Lượng tử hóa {fp32, fp16, dyn, int8} × {giữ, hiệu chỉnh}", "trong E1, E4", "RQ4"],
        ["E6", "Đối chứng rò rỉ", "9 × 3", "chống rò rỉ"],
        ["E7", "Ablation 4 quy tắc ngưỡng × ws ∈ {1, ws*, 2ws*}", "trong E1, E4", "ablation"],
        ["E8", "Edge benchmark P0/P1", "3 model × 4 kiểu × 3 profile × 5 lượt", "RQ5"],
        ["E9", "Robustness: evasion, nhiễu, poisoning 1%/5%", "9 × 3 × 3", "an toàn"],
        ["E10", "MTD: HARM rút gọn + MTD lai kích hoạt bởi AE", "5 seed Monte Carlo; 9 thiết bị", "RQ6"],
    ], columns=["ID", "Nội dung", "Số lần chạy", "Phục vụ"]), "Ma trận thí nghiệm", font=9.5,
        col_widths_cm=[1.2, 8.3, 4.3, 2.2])
    R.para("Nguyên tắc: mọi cấu hình được định nghĩa sẵn trong ai/configs/exp/*.yaml; mỗi lần chạy lưu config đã hợp nhất, "
           "seed, git commit, thời gian, log huấn luyện, metric (results/raw/<exp>/<thiết bị>/seed=<s>/); không xóa lần chạy "
           "xấu, không chọn seed đẹp; test chỉ dùng để đánh giá cuối. Thống kê: mỗi seed lấy trung bình 9 thiết bị, báo cáo "
           "mean, std và khoảng tin cậy 95% (phân phối t); so sánh cặp dùng Wilcoxon signed-rank trên 9 thiết bị (trung bình "
           "các seed), hiệu chỉnh Holm.")
