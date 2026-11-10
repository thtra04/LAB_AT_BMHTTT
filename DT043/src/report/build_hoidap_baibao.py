"""Sinh file Word tổng hợp câu hỏi – trả lời về bài báo, tái lập và mục tiêu đề tài (chuẩn bị bảo vệ).

Chạy tại DT043/src:  .venv\\Scripts\\python report/build_hoidap_baibao.py
Đầu ra: ../tailieu/thuyet_trinh/HoiDap_BaiBao_DT043_1150080120_HoangThanhTra.docx
Số liệu lấy từ results/tables/ (tharm_*.csv, paper_fig*.csv, e12_*.csv, per_device_B0_vs_meidan.csv) và notebook mục 9.
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from docx_helpers import Report  # noqa: E402

OUT = HERE.parent.parent / "tailieu" / "thuyet_trinh" / "HoiDap_BaiBao_DT043_1150080120_HoangThanhTra.docx"
N = [0]


def q(R, question, short):
    """Tiêu đề câu hỏi + câu trả lời ngắn (để nói)."""
    N[0] += 1
    R.h2(f"Câu {N[0]}. {question}")
    R.para(f"**Trả lời ngắn:** “{short}”")


def table(R, rows, cols, widths, caption=None):
    R.table(pd.DataFrame(rows, columns=cols), caption, font=10, col_widths_cm=widths)


def main() -> None:
    R = Report()
    R.para("HỎI – ĐÁP VỀ BÀI BÁO VÀ ĐỀ TÀI DT043", bold=True, size=16, align="center")
    R.para("Phát hiện botnet IoT bằng autoencoder nhẹ – chuẩn bị trả lời khi bảo vệ", italic=True, align="center")
    R.para("Người trình bày: **Hoàng Thanh Trà** – MSSV 1150080120 – Lớp 11CNPM2", align="center")
    R.para("Mỗi câu gồm **trả lời ngắn** (nói trong 15–30 giây) và phần chi tiết khi thầy hỏi thêm. Bài báo chính: Masud et al. "
           "(2025), Computers & Security 153, 104380. Bài tham chiếu kỹ thuật: Meidan et al. (2018), N-BaIoT, IEEE Pervasive "
           "Computing. Số liệu lấy từ src/results/tables/ và notebook src/DT043_walkthrough.ipynb (mục 9).", justify=False)

    # ================================================================ A. Bài báo
    R.h1("A. Về bài báo")
    q(R, "Tác giả của bài báo là ai?",
      "Bài chính của Masud, Keshk, Moustafa, Turnbull và Susilo, năm 2025, trên Computers & Security. Bốn tác giả đầu ở "
      "University of New South Wales Canberra, tác giả cuối ở University of Wollongong, Úc.")
    table(R, [["Mohammed Tanvir Masud (tác giả liên hệ)", "UNSW Canberra, Úc"], ["Marwa Keshk", "UNSW Canberra, Úc"],
              ["Nour Moustafa (tác giả liên hệ)", "UNSW Canberra, Úc"], ["Benjamin Turnbull", "UNSW Canberra, Úc"],
              ["Willy Susilo", "University of Wollongong, Úc"]], ["Tác giả", "Đơn vị"], [9.0, 7.0])
    R.para("Tên bài: Vulnerability defence using hybrid moving target defence in Internet of Things systems. Computers & "
           "Security 153 (2025) 104380, DOI 10.1016/j.cose.2025.104380, Open Access (CC BY). Bài tham chiếu kỹ thuật: Meidan, "
           "Bohadana, Mathov, Mirsky, Breitenbacher, Shabtai, Elovici (2018), N-BaIoT, IEEE Pervasive Computing.", justify=False)

    q(R, "Mục tiêu của bài báo gốc là gì?",
      "Bài đánh giá nên kết hợp các kỹ thuật Moving Target Defence thế nào để bảo vệ mạng IoT tốt nhất, xét cả rủi ro, chi "
      "phí tấn công và tài nguyên tiêu tốn.")
    R.numbered(["**Đề xuất phương pháp đánh giá:** mô hình đồ thị tấn công 3-layer THARM, đo mức an toàn của mạng theo từng "
                "thời điểm sau mỗi lần MTD.",
                "**So sánh 3 kỹ thuật MTD và tổ hợp:** shuffle (di trú VM, đổi IP), diversity (đổi hệ điều hành), redundancy "
                "(nhân bản VM); các tổ hợp S+D, S+D+R.",
                "**Đo bằng chỉ số an ninh:** ASP, rủi ro AR, chi phí tấn công AC, RoC = R/AC; độ trung tâm để chọn VM cần bảo vệ.",
                "**Xét tài nguyên:** MTD tốn tài nguyên, IoT hạn chế → quy trình xếp hàng và kiểm tra tài nguyên (Hình 2)."])
    R.para("Kết luận của bài: **shuffle + diversity** cho rủi ro và xác suất tấn công thấp nhất, chi phí tấn công cao hơn. "
           "Hạn chế: chỉ mô phỏng, chỉ kích hoạt MTD theo chu kỳ 10 phút, không có bộ phát hiện tấn công.")

    q(R, "Bài báo nói gì?",
      "Bài của Masud 2025 đánh giá việc kết hợp shuffle, diversity, redundancy bằng mô hình đồ thị tấn công ba tầng THARM "
      "trên 8 máy ảo, 32 CVE; kết luận shuffle + diversity cho rủi ro thấp nhất. Nhưng bài chỉ mô phỏng, chỉ đổi cấu hình theo "
      "chu kỳ 10 phút và không có bộ phát hiện tấn công để kích hoạt MTD.")

    q(R, "Kiến trúc mô hình của bài báo là gì?",
      "Bài không dùng học máy; mô hình là đồ thị tấn công ba tầng 3-layer THARM, TH = (N, U, S, L, C).")
    table(R, [["N", "Các trạng thái mạng theo thời gian (mỗi lần MTD tạo một trạng thái mới)"],
              ["U – tầng trên", "Đồ thị tấn công giữa 8 máy ảo, từ kẻ tấn công tới V8 (CSDL đích)"],
              ["S – tầng dịch vụ", "Đồ thị tấn công giữa 14 dịch vụ s1–s14, mỗi VM 2 dịch vụ"],
              ["L – tầng dưới", "Cây tấn công cổng OR gồm lỗ hổng hệ điều hành + dịch vụ của từng VM"],
              ["C", "Liên kết giữa các tầng: dịch vụ ↔ VM ↔ cây tấn công"]], ["Thành phần", "Ý nghĩa"], [4.0, 12.0])
    R.para("Phần autoencoder của đề tài lấy kiến trúc từ Meidan 2018: B0 115-86-58-38-29-38-58-86-115 (36.876 tham số), "
           "bản nhẹ V1 115-32-8-32-115 (8.059 tham số); ngưỡng tr* = mean + std của MSE trên DSopt, vote cửa sổ ws*.")

    q(R, "Kiến trúc gốc của bài báo là hình nào? Phân tích.",
      "Kiến trúc nằm ở ba hình: Hình 1 là hạ tầng mạng, Hình 2 là quy trình vận hành MTD, Hình 3 là mô hình 3-layer THARM – "
      "quan trọng nhất vì mọi kết quả tính trên mô hình này.")
    R.bullets(["**Hình 1 – hạ tầng:** 4 host, 8 VM. Host 1: V1 (Linux), V2 (Windows 11); Host 2: V3 (FreeBSD), V4 (Linux), "
               "V5 (Windows 11); Host 3: V6 (FreeBSD), V7 (Linux); Host 4: V8 (Linux, CSDL đích). Nhiều hệ điều hành → có chỗ "
               "cho diversity; nhiều host → có chỗ cho shuffle.",
               "**Hình 2 – vận hành MTD:** sự kiện kích hoạt → hàng đợi MTD / hàng đợi tạm dừng → kiểm tra tài nguyên → hết tài "
               "nguyên thì tạm dừng, còn thì triển khai và thực thi MTD, giải phóng tài nguyên, cắt ngang kẻ tấn công. Bài chỉ "
               "dùng kích hoạt theo thời gian; ô “sự kiện kích hoạt” không nối với bộ phát hiện nào – đề tài nối cảnh báo AE vào đây.",
               "**Hình 3 – 3-layer THARM:** tầng trên là đồ thị VM và dịch vụ (kẻ tấn công vào V1, V2 rồi đi tới V8), tầng dưới "
               "là cây OR của lỗ hổng. Hình vẽ thêm cạnh V6 → V4 không có trong Definition 2; theo Hình 3 tái lập được 6/7 kết "
               "luận, theo Definition 2 chỉ còn 3/7.",
               "**Meidan 2018:** Hình 1 chỉ là sơ đồ phòng lab (thiết bị IoT – access point – switch – Wireshark, máy chủ C&C); "
               "kiến trúc autoencoder chỉ mô tả bằng chữ (75%, 50%, 33%, 25% số chiều đầu vào)."])

    # ================================================================ B. Đề tài
    R.h1("B. Về đề tài của em")
    q(R, "Mục tiêu của đề tài là làm gì?",
      "Xây dựng bộ phát hiện botnet IoT đủ nhẹ để chạy ngay tại thiết bị biên, và dùng cảnh báo của nó để kích hoạt Moving "
      "Target Defence – phần bài báo chính còn thiếu.")
    R.numbered(["**Phát hiện botnet (≈ 70%):** tái lập autoencoder Meidan 2018 trên N-BaIoT (9 thiết bị, Mirai và BASHLITE), "
                "thu nhỏ, lượng tử hóa int8 để chạy trên edge.",
                "**Tái lập bài chính (≈ 30%):** dựng lại 3-layer THARM bằng đúng dữ liệu bài, kiểm tra “shuffle + diversity tốt nhất”.",
                "**Nối hai phần:** cảnh báo của AE kích hoạt MTD lai; đo thời gian lộ diện so với MTD theo chu kỳ."])
    table(R, [["RQ1", "Tái lập Meidan", "TPR ≥ 0,99 và FPR ≤ 0,02", "TPR 0,822 – không đạt"],
              ["RQ2", "Per-device hơn model chung", "≥ 7/9 thiết bị, p < 0,05", "4/9, p = 0,285 – không đạt"],
              ["RQ3", "Model nhẹ", "≤ 25% tham số, Δmacro-F1 ≤ 0,01", "21,9%, Δ = 0,017 – không đạt"],
              ["RQ4", "int8 + hiệu chỉnh ngưỡng", "Δmacro-F1 ≤ 0,005, ≤ 30% kích thước", "45,5% – không đạt"],
              ["RQ5", "Chạy trên edge", "p95 ≤ 1 ms, ≤ 50 KB, RAM ≤ 50 MB", "10,8 µs, 15,3 KB, 4,6 MB – đạt"],
              ["RQ6", "MTD lai do AE kích hoạt", "báo cáo trade-off", "cùng chi phí, lộ diện ít hơn"]],
          ["RQ", "Câu hỏi", "Tiêu chí (chốt trước)", "Kết quả"], [1.3, 4.2, 5.5, 5.0])

    q(R, "Nghiên cứu chính của đề tài là gì?",
      "Phát hiện thiết bị IoT nhiễm botnet ngay tại thiết bị biên bằng autoencoder nhẹ, rồi dùng chính cảnh báo đó để kích "
      "hoạt Moving Target Defence. Đề tài nối hai bài báo mà mỗi bài chỉ làm một nửa.")
    table(R, [["Phát hiện botnet", "Có (autoencoder)", "Không", "Có – AE nhẹ int8"],
              ["Phòng thủ MTD", "Không", "Có – chỉ theo chu kỳ thời gian", "MTD lai: theo chu kỳ + khi AE cảnh báo"],
              ["Chạy trên edge", "Không đo", "Không", "15,3 KB, 10,8 µs/mẫu trên 1 lõi"]],
          ["", "Meidan 2018", "Masud 2025 (bài chính)", "Đề tài DT043"], [3.2, 3.6, 4.4, 4.8])

    q(R, "Khoảng trống nghiên cứu là gì?",
      "Bài chính có MTD nhưng không có bộ phát hiện để kích hoạt MTD; bài Meidan có bộ phát hiện nhưng đánh giá lạc quan và "
      "không kiểm tra trên edge; chưa ai ghép thành vòng phát hiện → cảnh báo → MTD ngay tại edge.")
    R.numbered(["**Masud 2025 – có MTD, thiếu detector:** MTD đổi theo chu kỳ cố định 10 phút kể cả khi không có tấn công – vừa "
                "tốn chi phí, vừa để kẻ tấn công hoạt động trong khoảng chờ. Bài chỉ mô phỏng, không công bố mã.",
                "**Meidan 2018 – có detector, đánh giá lạc quan:** chia dữ liệu một lần, không khử trùng lặp, không chống rò rỉ "
                "chặt nên TPR 100% có thể “đẹp giả”; không đo mô hình có chạy nổi trên thiết bị yếu không.",
                "**Chưa ai nối hai phần** thành vòng khép kín tại edge: phát hiện → cảnh báo → MTD."])

    q(R, "Thiết bị biên (edge) là gì? Vì sao đặt bộ phát hiện ở edge?",
      "Thiết bị biên là thiết bị đặt sát nguồn dữ liệu, như router hay gateway cạnh camera IoT, thay vì máy chủ trung tâm. "
      "Phát hiện ở đó thì nhanh, không tốn băng thông, không lộ dữ liệu; nhưng thiết bị yếu nên em phải làm mô hình nhẹ: "
      "15 KB, khoảng 11 micro-giây mỗi mẫu.")
    R.para("Vị trí trong mạng: thiết bị IoT (camera, chuông cửa) → **thiết bị biên** (router, gateway, Raspberry Pi trong nhà) "
           "→ Internet → đám mây / trung tâm dữ liệu. Đôi khi chính thiết bị IoT cũng được coi là edge.", justify=False)
    table(R, [["Phải gửi toàn bộ lưu lượng lên mạng, tốn băng thông", "Xử lý tại chỗ, không cần gửi đi"],
              ["Chậm vì phải truyền đi và nhận về", "Phát hiện gần như tức thì"],
              ["Mất Internet là mất bảo vệ", "Vẫn chạy khi mất kết nối"],
              ["Lộ dữ liệu riêng tư ra ngoài", "Dữ liệu ở lại trong nhà"]],
          ["Đặt ở trung tâm (cloud)", "Đặt ở edge"], [8.0, 8.0])
    R.para("Nhược điểm của edge: CPU nhỏ, ít RAM, có khi chạy pin → mô hình phải rất nhỏ và nhanh. Vì vậy đề tài thu nhỏ AE "
           "còn 8.059 tham số (V1), lượng tử hóa int8 còn 15,3 KB, đo trên 1 lõi E-core: p95 10,8 µs/mẫu, ~103.000 mẫu/s, "
           "RAM +4,6 MB – RQ5 đạt, là câu hỏi nghiên cứu duy nhất đạt tiêu chí.")

    q(R, "Em làm được gì?",
      "Em tái lập được phần lớn kết quả bài chính, bổ sung autoencoder nhẹ chạy được trên edge, và dùng cảnh báo của nó kích "
      "hoạt MTD lai.")
    R.numbered(["**Tái lập bài chính:** rủi ro từng VM khớp tới 0,01, đường tấn công lệch 0,8%, 6/7 kết luận; vẽ lại Hình 6 – "
                "đường diversity khớp cả 7 VM. E12 thử công thức AC suy ra (giả thuyết): tổng AC, RoC toàn mạng về trong "
                "±3,4% và ±8,4%, nhưng tổng R của diversity, redundancy vẫn lệch −13%, −17% và Hình 7 vẫn không so được "
                "từng đường. Không thể tái hiện khớp hoàn toàn vì bài không công bố đủ công thức.",
                "**Bộ phát hiện:** autoencoder trên N-BaIoT, bản int8 15 KB, ~10 µs/mẫu trên 1 lõi, FPR 0,0025; bỏ sót flood "
                "tcp/udp giả mạo nguồn (TPR 0,822).",
                "**Nối hai phần:** cảnh báo AE kích hoạt MTD lai – cùng chi phí, thời gian lộ diện ít hơn time-based; hệ thống "
                "demo 4 tầng AI / Backend / CSDL / Dashboard, 66 test tự động."])

    q(R, "Đóng góp chính em muốn nhấn mạnh là gì?",
      "MTD lai dùng cảnh báo của autoencoder đạt cùng mức an toàn với MTD theo thời gian nhưng chi phí chỉ khoảng một nửa; "
      "và bộ phát hiện đủ nhẹ để chạy ngay tại edge.")
    table(R, [["Chỉ theo thời gian, T = 500", "251 mẫu", "20,0"],
              ["Lai, T = 2000", "263 mẫu", "8,9"],
              ["Chỉ theo cảnh báo AE", "11.835 mẫu", "15,3"]],
          ["Chính sách MTD", "Thời gian lộ diện TB", "Số lần đổi / 10k mẫu"], [6.0, 5.0, 5.0],
          "So sánh chính sách MTD (results/tables/mtd_hybrid_policy.csv)")
    R.bullets(["**Lai thắng:** lộ diện gần bằng nhau, số lần đổi giảm ≈ 55%.",
               "**Chỉ dựa vào cảnh báo thì không đủ** vì AE bỏ sót flood tcp/udp → phần theo thời gian là “lưới an toàn”; điểm "
               "yếu của detector lại ủng hộ thiết kế lai.",
               "**Điều kiện tiên quyết đã đạt:** detector 15,3 KB, 10,8 µs/mẫu (RQ5).",
               "**Điểm phụ:** đánh giá chống rò rỉ, tiêu chí chốt trước, 468 lần chạy / 5 seed (E6 cho thấy chia ngẫu nhiên làm "
               "kết quả đẹp giả); tái lập bài chính có kiểm chứng và chỉ ra chỗ bài tự mâu thuẫn (Hình 7, danh sách cạnh E′, 4 mâu thuẫn mới ở E12)."])

    # ================================================================ C. Tái lập
    R.h1("C. Về tái lập bài báo")
    q(R, "Tái lập kiểu nào?",
      "Em dựng lại mô hình của bài từ đúng dữ liệu bài công bố rồi so từng con số với bài, không tự đặt tham số.")
    R.numbered(["**Lấy dữ liệu từ bài:** 18 CVE hệ điều hành, 14 CVE dịch vụ, VM → hệ điều hành và host, dịch vụ, cạnh tấn công.",
                "**Dựng THARM bằng code** (ai/src/nbaiot/mtd/tharm.py): cây lỗ hổng từng VM, đồ thị tấn công giữa VM; 24 test "
                "khóa các con số của bài.",
                "**Tính theo công thức bài:** rủi ro VM = Σ E·I, rủi ro đường = tổng rủi ro VM trên đường; áp shuffle, diversity, "
                "redundancy như mục 4.2–4.4.",
                "**So với bài** ở mức VM, đường, toàn mạng; vẽ lại Hình 6, Hình 7 đúng dạng để so trực tiếp (E11).",
                "**Tái hiện thêm (E12):** thử cách tính AC theo VM khớp các số bài in, dùng Eq. 1 đúng nguyên văn; so lại tổng "
                "toàn mạng và Hình 5–8 (ai/scripts/12_masud_full_repro.py). Không chỉnh số nào để khớp."])
    R.para("Phần Meidan: dùng chính bộ N-BaIoT, cùng kiến trúc AE, cùng ngưỡng mean + std và vote cửa sổ; chặt hơn ở chống rò rỉ "
           "dữ liệu và 5 seed.")

    q(R, "Lấy dữ liệu gì từ bài báo?",
      "Em lấy toàn bộ đầu vào của mô hình từ chính bài báo, gồm 5 nhóm, không tự đặt số nào.")
    table(R, [["Lỗ hổng hệ điều hành", "Bảng 1", "18 CVE (6 mỗi OS: Windows 11, Linux, FreeBSD): CVSS, Impact, Exploitability, cost"],
              ["Lỗ hổng dịch vụ", "Bảng 2", "14 CVE cho dịch vụ s1–s14"],
              ["VM – hệ điều hành – host", "Hình 1", "8 VM trên 4 host"],
              ["Dịch vụ, đồ thị tấn công", "Hình 3, Definition 2", "mỗi VM 2 dịch vụ; 11 cạnh tới V8 (Hình 3 thêm V6 → V4)"],
              ["Cách áp MTD", "Mục 4.2–4.4, Hình 4", "shuffle V5 host 2 → 4; đổi OS dự phòng; nhân bản V5"]],
          ["Dữ liệu", "Nguồn", "Cụ thể"], [4.0, 3.3, 8.7])
    R.para("Số dùng để đối chiếu (không đưa vào mô hình): Bảng 4 (ASP, AC, AR từng VM); rủi ro V4 12,47, V5 12,58, V7 8,67, V8 "
           "5,62; ba đường 43,15 và 43,31; tổng mạng R_s 167,38, R_d 163,73, R_r 260,84; Hình 6, Hình 7. Bài ghi “No data was "
           "used” – không có dataset, chỉ có mạng mô phỏng.")

    q(R, "Dữ liệu nào bài báo không công bố?",
      "Bài công bố đủ đầu vào nhưng không công bố mã nguồn và nhiều bước tính ra kết quả.")
    table(R, [["1", "Mã nguồn", "Không kiểm chứng được cách bài tính"],
              ["2", "Eq. 1 (ASP) in “1 − (∏ + ∏)”, có thể âm", "E12 dùng nguyên văn (V8 không có dịch vụ → tích = 0): ASP đường "
                     "0,24–0,48, cùng thang Hình 7, nhưng không ra ASP Bảng 4 (E11 dùng OR độc lập "
                     "thì Bảng 4 lệch 0,8–1,7%)"],
              ["3", "Eq. 2 in tích ∏ nhưng số trong bài là tổng", "Diễn giải lại là tổng → rủi ro VM khớp"],
              ["4", "Công thức AC từng VM (AC mục 4.2 gấp 5–8 lần Σ cost Bảng 1–2)", "E11 lệch ≈ −83%; E12 giả thuyết AC = Σ CVSS × "
                     "cost: khớp V5, V7, V8, V2 lệch −33,9%; tổng AC lệch ≤ 3,4%"],
              ["5", "RoC toàn mạng là tổng RoC theo đường (bài không nói rõ)", "E11 lệch +435% đến +506%; E12 lệch ≤ 8,4%"],
              ["6", "Cách ra AC, AR Bảng 4 cho V2–V7", "Chỉ V1, V8 khớp"],
              ["7", "Vì sao R_V2 = 16,28 (tính ra 15,94)", "Ba đường lệch 0,8%"],
              ["8", "Danh sách cạnh sau shuffle bị cắt “…”", "Không tính lại tổng toàn mạng"],
              ["9", "Topology Hình 3 ≠ Definition 2 (cạnh V6 → V4)", "6/7 với Hình 3, 3/7 với Definition 2; số tổng của bài gợi ý Definition 2"],
              ["10", "Host đích khi shuffle các VM ngoài V5 (và V2)", "Hình 6: shuffle, S+D chỉ khớp ở V5"],
              ["11", "Bản sao redundancy nối vào đâu, chạy OS gì", "Redundancy, S+D+R cao hơn bài"],
              ["12", "8 đường của Hình 7 (topology chỉ có 5)", "Từng đường không so được; E12 chỉ cùng thang đo"],
              ["13", "Bảng số của Hình 6", "Đọc số bằng mắt, sai số ≈ ±5"],
              ["14", "Cách sinh mạng 50–400 VM (Hình 8)", "E12 tự giả định bộ sinh mạng, chỉ so tỷ lệ; D và S+D cùng xu hướng"],
              ["15", "Quy tắc chọn host đích của PSV (Hình 5b), phép gộp IPV+PSV (Hình 5c)", "5(a) khớp nhưng m lấy từ chính "
                     "hình; 5(b) không khớp; 5(c) không làm"],
              ["16", "Mô hình theo thời gian của Hình 9 (trục ASP 200–400 trái với ASP ∈ [0, 1])", "Không làm – tự dựng sẽ là làm "
                     "giả kết quả"]],
          ["#", "Không công bố / không rõ", "Ảnh hưởng"], [0.8, 8.2, 7.0], "Những chỗ bài Masud 2025 không công bố")
    R.para("Meidan 2018 có công bố dataset; không công bố mã nguồn, seed, ranh giới chia dữ liệu, việc khử trùng lặp; dataset "
           "không có timestamp (không đo được thời gian phát hiện theo giây) và lưu lượng theo giờ (Hình 2c, d).")

    q(R, "Chạy lại mô hình giống bài báo chưa? Chạy đúng chưa?",
      "Có, cả hai mô hình đã chạy lại. Bài chạy đúng quy trình – 468 lần chạy, 66/66 test qua – nhưng chỉ phần bài công bố đủ "
      "dữ liệu là ra giống bài.")
    table(R, [["Rủi ro V4 / V5 / V7 / V8", "12,47 / 12,58 / 8,67 / 5,62", "12,473 / 12,578 / 8,667 / 5,625", "< 0,1%"],
              ["Rủi ro V2", "16,28", "15,941", "−2,1%"],
              ["V5 sau diversity", "8,90", "8,934", "+0,4%"],
              ["3 đường tấn công ví dụ", "43,15 / 43,31 / 43,31", "42,81 / 42,97 / 42,97", "−0,8%"]],
          ["Giá trị", "Bài báo", "Chạy lại", "Lệch"], [4.6, 4.2, 4.6, 2.6], "Chạy trực tiếp THARM so với số trong bài (notebook mục 9.1)")
    R.para("Biểu đồ vẽ lại đúng dạng hình gốc (báo cáo mục 6.9, notebook mục 9.2): Hình 6 – diversity khớp 7/7 VM, shuffle và "
           "S+D khớp ở V5, redundancy cao hơn; Hình 7 – không tái lập được; Hình 2 Meidan – FPR khớp, TPR của AE thấp hơn do "
           "flood tcp/udp. E12 (báo cáo mục 6.10) chạy thêm phần tổng toàn mạng và Hình 5–8, xem câu tiếp theo.")

    q(R, "Đã tái hiện đúng bài báo chưa? E12 là gì?",
      "Chưa thể tái hiện khớp hoàn toàn, và em nghĩ không ai làm được vì bài không có mã nguồn, thiếu công thức chi phí và tự "
      "mâu thuẫn. E12 là lần em cố tái hiện tối đa: nhờ một công thức AC em suy ra, tổng AC và RoC toàn mạng về gần bài, số "
      "giá trị tổng khớp trong 5% tăng từ 1/9 lên 5/9. Nhưng công thức đó là giả thuyết của em, không phải của tác giả.")
    table(R, [["Tổng AC toàn mạng (S, D, R)", "Lệch −83%", "Lệch −3,4% đến +2,2%", "Gần khớp"],
              ["Tổng RoC toàn mạng", "Lệch +435% đến +506%", "Lệch −8,4% đến +6,3%", "Gần khớp"],
              ["Tổng R toàn mạng", "+3,7% / −13,1% / −16,6%", "Không đổi", "Shuffle khớp; D, R chưa"],
              ["Tổng mạng lệch ≤ 5%", "1/9", "5/9", "Tốt hơn, chưa đủ"],
              ["Hình 5(a) IPV", "Chưa làm", "IPV ≈ m/n", "Khớp, nhưng m lấy từ hình"],
              ["Hình 5(b) PSV", "Chưa làm", "Không khớp", "Không tái hiện được"],
              ["Hình 6", "Chỉ so AR", "AR, AC, RoC: 19/105 điểm", "Cùng thang, khác hình dạng"],
              ["Hình 7", "ASP 0,91–0,94", "ASP 0,24–0,48 (bài 0,2–0,43)", "Cùng thang đo"],
              ["Hình 8", "Chưa làm", "Chỉ so tỷ lệ", "Bộ sinh mạng là giả định"],
              ["Hình 9", "Chưa làm", "Không làm", "Không tái hiện được"]],
          ["Kết quả của bài", "E11", "E12", "Trạng thái"], [4.4, 3.8, 4.6, 3.2], "E12 so với E11 (Definition 2)")
    R.bullets(["**Công thức AC theo VM = Σ CVSS × attack cost** (bài không in): khớp V5 +0,6%, V7 +0,8%, V8 −4,1%, nhưng V2 "
               "lệch −33,9%. Công thức được chọn sau khi dò thử trên 4 số này nên có thể khớp ngẫu nhiên; bằng chứng hỗ trợ là "
               "tổng AC toàn mạng – không dùng khi chọn công thức – cũng khớp trong ±3,4%.",
               "**ASP dùng Eq. 1 nguyên văn:** không âm nếu lấy tích dịch vụ của V8 bằng 0 (giả định vì V8 không có dịch vụ).",
               "**Tìm vét cạn** các tập 4 đường hợp lệ: không tập nào cho đồng thời R_s = 167,38 và AC_s = 666,2 → chỉ đổi đồ "
               "thị thì chưa giải thích được số của bài.",
               "**4 mâu thuẫn mới:** không topology nào giải thích được cả Hình 6; R_d = 163,73 trong văn bản khác Hình 6 "
               "(≈ 203); Hình 6 vẫn cho V6 giá trị khác nhau dù V6 là ngõ cụt; AC_ap = 134,134 ở mục 4.3 không khớp cách tính "
               "nào và thấp hơn đường ở mục 4.2 dù bài nói diversity làm tăng AC.",
               "**Đổi V5 sang Linux làm ASP tăng** (0,296 → 0,330 ở đường A-V1-V5-V8), ngược lời bình của bài."])
    R.para("Nếu thầy hỏi “sao không chỉnh cho khớp”: em không chỉnh số nào để khớp; giá trị của bài ở các hình đọc bằng mắt, "
           "ngưỡng 5% chỉ là quy ước. Chi tiết: tailieu/docs/tai_lap_E12_day_du.md.", italic=True)

    q(R, "Kết quả giống bài báo bao nhiêu %?",
      "Phần cốt lõi khớp gần 100%, kết luận định tính khớp 86% (6/7); tổng toàn mạng khớp 5/9 sau E12 nhưng dựa trên công "
      "thức AC em suy ra. Nên đọc theo từng mức thay vì một con số chung.")
    table(R, [["Masud", "Rủi ro từng VM", "6/6 (100%)", "5/6 lệch < 0,1%; V2 −2,1%"],
              ["Masud", "Rủi ro 3 đường ví dụ", "3/3 (100%)", "đều −0,8%"],
              ["Masud", "Bảng 4 – ASP từng VM", "8/8 (100%)", "lệch 0,8–1,7%"],
              ["Masud", "Bảng 4 – AC, AR từng VM", "8/16 (50%)", "V1, V8 khớp hoàn toàn"],
              ["Masud", "Tổng mạng R, AC, RoC", "E11 1/9 (11%) → E12 5/9 (56%)", "E12: AC ≤ 3,4%, RoC ≤ 8,4%; R của D, R vẫn lệch"],
              ["Masud", "Hình 6 – AR (5 MTD × 7 VM)", "11/35 (31%)", "diversity 7/7"],
              ["Masud", "Hình 6 – AC, RoC (E12, Definition 2)", "AC 9/35, RoC 7/35", "cùng thang, khác hình dạng"],
              ["Masud", "Hình 7 – từng đường", "0%", "E12 chỉ cùng thang 0,24–0,48 (bài 0,2–0,43)"],
              ["Masud", "Kết luận định tính", "6/7 (86%)", "gồm “S+D tốt nhất”"],
              ["Meidan", "FPR ≤ 0,02 theo thiết bị", "9/9 (100%)", "TB 0,0025 (bài 0,007)"],
              ["Meidan", "TPR = 100% theo thiết bị", "3/9 (33%)", "TPR TB 0,822"]],
          ["Bài", "Mức so sánh", "Khớp (lệch ≤ 5%)", "Ghi chú"], [1.8, 5.6, 3.6, 5.0], "Mức khớp theo từng mức so sánh")

    q(R, "Con số % đó lấy ở đâu ra?",
      "Tính từ các bảng kết quả trong src/results/tables do script tái lập sinh ra; notebook mục 9.3 tính lại trực tiếp và ghi "
      "file nguồn từng dòng.")
    R.bullets(["**Công thức:** lệch % = (tái lập − bài báo) / bài báo × 100; “khớp” khi |lệch| ≤ 5% (ngưỡng do em chọn).",
               "**Nguồn:** tharm_vm_vs_paper.csv, tharm_paths_vs_paper.csv, tharm_network_vs_paper.csv, tharm_trends.csv "
               "(script 10_tharm_paper_replication.py); paper_fig6_masud_vs_paper.csv (script 11_paper_figures.py); "
               "e12_network_totals.csv, e12_fig6.csv, e12_vm_ac.csv (script 12_masud_full_repro.py); "
               "per_device_B0_vs_meidan.csv (script 06_aggregate.py).",
               "**Lưu ý:** số Hình 6 phía bài báo đọc bằng mắt từ hình (sai số ≈ ±5); “82%” của Meidan là TPR trung bình 0,822 "
               "quy ra %; tỷ lệ gộp tất cả các mức (37/77 ≈ 48%) phụ thuộc việc chọn số đem so nên không dùng làm kết luận."])

    q(R, "Kết quả của em khác bài báo ở đâu? Vì sao khác?",
      "Dữ liệu và công thức ở mức máy ảo, mức đường tấn công em tái lập khớp, sai số dưới 1%; tổng AC, RoC chỉ gần khớp khi "
      "dùng công thức AC em suy ra (E12), còn tổng R của diversity, redundancy và Hình 7 vẫn không khớp vì bài thiếu công "
      "thức và số liệu tự mâu thuẫn. Với Meidan, FPR khớp, còn TPR thấp hơn vì em "
      "chia dữ liệu chống rò rỉ chặt hơn và flood tcp/udp giả mạo nguồn trông giống lưu lượng bình thường.")
    table(R, [["FPR", "0,007", "0,0025", "Khớp, còn tốt hơn"],
              ["TPR", "100%", "0,822", "Thấp hơn"],
              ["Thời gian phát hiện", "ms", "số mẫu", "CSV không có timestamp"],
              ["Edge, int8", "không đo", "15,3 KB, 10,8 µs/mẫu", "Phần mở rộng"]],
          ["Chỉ số", "Meidan 2018", "Đề tài (B0)", "Kết quả"], [3.6, 3.2, 4.4, 4.8], "So với Meidan 2018")
    R.numbered(["**Chia dữ liệu chặt hơn:** benign chia theo thời gian, đệm 500 dòng, bỏ 158 nghìn dòng trùng, scaler chỉ fit "
                "trên train. Cố tình chia ngẫu nhiên như Meidan (E6) thì FPR “đẹp giả” xuống 0,0006.",
                "**Toàn bộ phần bỏ sót là flood tcp/udp của BASHLITE:** nguồn bị giả mạo liên tục nên mỗi gói như “luồng mới”, "
                "MSE dưới ngưỡng, giống benign; 8 loại còn lại recall ≈ 1 (Ennio Doorbell chỉ TPR 0,37).",
                "**Khác biệt cài đặt có chủ đích:** lr cố định, early stopping, 5 seed thay vì 1."])
    table(R, [["Đầu vào: 32 CVE, 8 VM, topology, OS", "Khớp 100%"],
              ["Rủi ro từng VM", "Khớp ±0,01"],
              ["Rủi ro 3 đường ví dụ", "Lệch −0,8% (bài dùng R_V2 = 16,28, Bảng 1–2 cho 15,94)"],
              ["Chọn VM cần bảo vệ", "Ra V5 như bài (đồ thị có hướng)"],
              ["Hình 6 – diversity", "Khớp 7/7 VM, lệch < 5%"],
              ["Hình 6 – shuffle, S+D", "Chỉ khớp ở V5 – bài chỉ nêu host đích của V5"],
              ["Tổng AC, RoC toàn mạng", "E11 không khớp; E12 lệch ≤ 3,4% và ≤ 8,4% với công thức AC giả thuyết (V2 lệch −33,9%)"],
              ["Tổng R toàn mạng", "Shuffle +3,7%; diversity −13,1%, redundancy −16,6% – kể cả E12"],
              ["“Shuffle + Diversity tốt nhất”", "6/7 với topology Hình 3, 3/7 với Definition 2 – phụ thuộc cạnh V6 → V4"],
              ["Hình 7", "Từng đường không tái lập được – bài tự mâu thuẫn (Path 5 tăng nhưng lời bình nói giảm; ASP đường không "
                         "khớp Bảng 4), không in chuỗi VM của 8 đường; E12 với Eq. 1 nguyên văn chỉ cùng thang đo"]],
          ["Hạng mục", "Kết quả và lý do"], [5.5, 10.5], "So với Masud 2025")
    R.para("Tóm lại: phần không khớp đều do bài thiếu thông tin hoặc tự mâu thuẫn, không phải do cách tái lập. Chi tiết: "
           "tailieu/docs/kiem_tra_tai_lap.md (E11) và tailieu/docs/tai_lap_E12_day_du.md (E12).", italic=True)

    # ================================================================ D. Hướng tiếp theo
    R.h1("D. Hướng tiếp theo")
    q(R, "Mục tiêu tiếp theo là làm gì?",
      "Bước tiếp theo là bắt được flood giả mạo nguồn, chạy trên Raspberry Pi thật có đo điện, và thử MTD trên mạng thật có đo "
      "chi phí dịch vụ.")
    R.numbered(["**Bắt flood tcp/udp giả mạo nguồn:** thêm đặc trưng cho kiểu “mỗi gói như luồng mới” hoặc luật chạy song song AE; "
                "chọn ngưỡng có kiểm định trên dữ liệu mới.",
                "**Chạy trên edge thật:** Raspberry Pi, đo độ trễ và điện năng thật, tính cả bước trích đặc trưng từ gói tin.",
                "**MTD trên mạng thật:** testbed máy ảo + SDN, đo chi phí gián đoạn dịch vụ (QoS), tối ưu chu kỳ MTD.",
                "**Hoàn thiện tái lập:** chạy LOF, One-class SVM; liên hệ tác giả xin công thức / mã để xác nhận công thức AC giả "
                "thuyết của E12 và tái lập tổng R, Hình 7, 8, 9.",
                "**Dữ liệu mới hơn:** thử trên bộ IoT mới (ví dụ CICIoT2023) để kiểm tra khả năng tổng quát."])
    R.para("Ý 1, 2 đã có trong báo cáo mục 8.3; ý 4, 5 bổ sung sau khi vẽ lại biểu đồ của bài báo.", italic=True)

    R.save(OUT)
    print("đã ghi", OUT)


if __name__ == "__main__":
    main()
