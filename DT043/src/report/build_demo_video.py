"""Dựng video mẫu thuyết trình ~4 phút (khung 5 phút) (slide + demo thật trên dashboard + phụ đề lời thoại + đồng hồ)
và sinh kịch bản .md + .docx từ CÙNG một dòng thời gian, để video và kịch bản khớp nhau. Có hai dòng thời gian:
bộ slide 17 trang và bộ slide 10 trang.

Chạy (Python hệ thống có playwright, pymupdf, pillow, imageio-ffmpeg, pandas, python-docx), tại thư mục DT043/src:
    python report/build_demo_video.py                       # cả hai bộ: kịch bản + video
    python report/build_demo_video.py --deck 10             # chỉ bộ 10 slide (hoặc --deck 17)
    python report/build_demo_video.py --md-only             # chỉ sinh kịch bản (.md + .docx)
Video ra: ../tailieu/video/Video_mau_thuyet_trinh_DT043[_10slide].mp4 (không commit – video/ nằm trong .gitignore).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent / "tailieu"

W, H = 1920, 1080
CW, CH = 1564, 880            # vùng nội dung 16:9 (slide hoặc trình duyệt)
CX = (W - CW) // 2
PANEL_Y = CH                  # khung phụ đề phía dưới, cao 200 px


# ---------------------------------------------------------------- dòng thời gian (nguồn duy nhất)
def demo(start, end, back_slide):
    """Demo 5 bước trên dashboard – giống nhau ở hai bộ slide, chỉ khác slide quay về."""
    return dict(kind="demo", start=start, end=end, title="DEMO trực tiếp", steps=[
        dict(key="health", action="Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model»",
             say="Backend đã nạp 9 model, mỗi thiết bị một model V1 int8 khoảng 15 KB, kèm ngưỡng riêng.",
             expect="9 model, 0 lỗi gói"),
        dict(key="mirai", action="Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại»",
             say="Em phát lại 2000 mẫu Mirai SYN flood: MSE vượt hẳn ngưỡng, 1989/1989 cửa sổ bị cảnh báo.",
             expect="1989/1989 cửa sổ cảnh báo, đường MSE nằm trên ngưỡng"),
        dict(key="alerts", action="Kéo xuống bảng «Cảnh báo» và «Hành động MTD»",
             say="Hệ thống sinh cảnh báo mức high và tự kích hoạt hai hành động MTD: xáo trộn IP và đổi firmware.",
             expect="1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware)"),
        dict(key="benign", action="Kéo lên, chọn Ennio_Doorbell · benign → bấm «Phát lại»",
             say="Với lưu lượng bình thường của Ennio, không có cửa sổ nào bị cảnh báo, tức là không báo động giả.",
             expect="0 cửa sổ cảnh báo"),
        dict(key="tcp", action=f"Giữ Ennio_Doorbell, chọn gafgyt/tcp → bấm «Phát lại», rồi Alt + Tab về PowerPoint "
                    f"(Slide {back_slide})",
             say="Còn đây là điểm yếu em không che giấu: flood TCP của BASHLITE bị bỏ sót. Em quay lại slide.",
             expect="0 cửa sổ cảnh báo"),
    ])


def demo_short(start, end, back_slide):
    """Demo rút gọn 4 bước cho bản ngắn 8 slide."""
    return dict(kind="demo", start=start, end=end, title="DEMO trực tiếp (rút gọn)", steps=[
        dict(key="health", action="Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model»",
             say="Backend đã nạp 9 model int8, mỗi thiết bị một model.", expect="9 model, 0 lỗi gói"),
        dict(key="mirai", action="Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại»",
             say="Phát lại Mirai SYN flood: 1989 trên 1989 cửa sổ bị cảnh báo.", expect="1989/1989 cửa sổ cảnh báo"),
        dict(key="alerts", action="Kéo xuống bảng «Cảnh báo» và «Hành động MTD»",
             say="Hệ thống tự kích hoạt hai hành động MTD: đổi IP và đổi firmware.",
             expect="1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware)"),
        dict(key="tcp", action=f"Chọn Ennio_Doorbell · gafgyt/tcp → bấm «Phát lại», rồi Alt + Tab về PowerPoint "
                               f"(Slide {back_slide})",
             say="Còn flood TCP của BASHLITE thì bị bỏ sót – điểm yếu em phân tích ngay sau đây.",
             expect="0 cửa sổ cảnh báo"),
    ])


OPENING = ("Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện thiết bị IoT nhiễm botnet ngay "
           "tại thiết bị biên, bằng autoencoder nhẹ lượng tử hóa int8, kết hợp Moving Target Defence.")
PROBLEM = ["Thiết bị IoT dùng mật khẩu mặc định, ít được vá, nên Mirai và BASHLITE chiếm hàng loạt để DDoS.",
           "Phát hiện ở trung tâm thì chậm và tốn băng thông, nên em đặt bộ phát hiện ngay tại edge.",
           "Em đặt sáu câu hỏi nghiên cứu, tiêu chí định lượng được chốt và lưu checksum trước khi chạy, để không "
           "thể chỉnh tiêu chí theo kết quả."]
CRITERIA = ("Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt; RQ1 đến RQ4 không đạt, và em giữ nguyên tiêu chí, "
            "không chỉnh sau khi có kết quả.")
CONCLUSION = ("Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công, báo động giả thấp, chạy được ở edge; "
              "cần thêm đặc trưng cho flood giả mạo nguồn.")
FIG6 = ("Em chạy lại đúng Hình 6 của bài, áp từng kỹ thuật MTD lên từng máy ảo: diversity khớp cả 7 máy ảo, lệch "
        "dưới 5%; shuffle chỉ khớp ở V5 vì bài chỉ nêu host đích của V5.")
THANKS = "Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe."

def paper(start):
    """Ba slide phân tích bài báo tham khảo (slide 3–5) – giống nhau ở hai bộ slide."""
    return [
        dict(kind="slide", slide=3, start=start, end=start + 15, title="Bài báo tham khảo: bài toán", lines=[
            "Bài báo tham khảo chính là của Masud và cộng sự, 2025: Moving Target Defence liên tục thay đổi bề mặt tấn "
            "công, nhưng chưa có đánh giá khi kết hợp nhiều kỹ thuật MTD về rủi ro, chi phí và tài nguyên."]),
        dict(kind="slide", slide=4, start=start + 15, end=start + 27, title="Phương pháp của bài báo", lines=[
            "Bài dùng mô hình đồ thị tấn công ba tầng THARM trên 8 máy ảo và 32 CVE, áp shuffle, diversity, redundancy "
            "theo chu kỳ 10 phút."]),
        dict(kind="slide", slide=5, start=start + 27, end=start + 42, title="Kết quả, hạn chế của bài báo → hai track", lines=[
            "Kết quả: kết hợp shuffle và diversity cho rủi ro thấp nhất; nhưng bài chỉ mô phỏng, không có bộ phát hiện "
            "kích hoạt MTD.",
            "Nên em chia hai track: A phát hiện bằng autoencoder theo Meidan; B tái lập THARM và dùng cảnh báo của "
            "autoencoder để kích hoạt MTD."]),
    ]


SEGMENTS_17 = [
    dict(kind="slide", slide=1, start=0, end=15, title="Mở đầu", lines=[OPENING]),
    dict(kind="slide", slide=2, start=15, end=40, title="Bài toán và câu hỏi nghiên cứu", lines=PROBLEM),
    *paper(40),
    dict(kind="slide", slide=6, start=82, end=92, title="Dữ liệu N-BaIoT", lines=[
        "Dữ liệu N-BaIoT có 7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; nhiều dòng trùng lặp và mất cân bằng nặng."]),
    dict(kind="slide", slide=7, start=92, end=107, title="Chống rò rỉ dữ liệu và các mô hình", lines=[
        "Các dòng liền kề gần giống nhau nên em chia theo thời gian có vùng đệm 500 dòng, chỉ fit scaler trên tập "
        "train, và có unit test kiểm tra.",
        "Em so sánh autoencoder Meidan, Isolation Forest và bản V1 chỉ 8 nghìn tham số, lượng tử hóa int8."]),
    dict(kind="slide", slide=9, start=107, end=119, title="Kiến trúc 4 tầng AI · BE · DB · FE", lines=[
        "Hệ thống tách bốn tầng: AI xuất gói model có checksum SHA-256, backend FastAPI từ chối gói bị sửa, SQLite "
        "lưu cảnh báo và MTD, frontend là dashboard.",
        "Bây giờ em demo. (Alt + Tab sang trình duyệt)"]),
    demo(119, 194, back_slide=11),
    dict(kind="slide", slide=11, start=194, end=207, title="Kết quả tổng quan", lines=[
        "Trên 468 lần chạy, autoencoder per-device có FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822, "
        "không đạt 100% như paper."]),
    dict(kind="slide", slide=12, start=207, end=221, title="Lỗi chính: flood BASHLITE tcp/udp", lines=[
        "Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE: nguồn bị giả mạo nên mỗi gói trông như luồng mới, "
        "giống benign; tám loại còn lại có recall gần bằng 1."]),
    dict(kind="slide", slide=14, start=221, end=232, title="Lượng tử hóa int8", lines=[
        "Bản int8 chỉ còn 15,3 KB; nếu giữ ngưỡng fp32 thì sai lệch, nên em hiệu chỉnh lại ngưỡng trên tập DSopt."]),
    dict(kind="slide", slide=15, start=232, end=244, title="Edge benchmark", lines=[
        "Trên một lõi E-core: p95 chỉ 10,8 micro-giây mỗi mẫu, khoảng 103 nghìn mẫu mỗi giây, RAM tăng 4,6 MB – "
        "thừa sức chạy tại edge."]),
    dict(kind="slide", slide=17, start=244, end=256, title="Moving Target Defence", lines=[
        "Với mô hình HARM rút gọn, xác suất tấn công thành công giảm từ 0,498 xuống 0,327 khi kết hợp shuffle và "
        "diversity, khớp xu hướng paper.",
        "MTD lai kích hoạt bởi autoencoder có thời gian lộ diện thấp hơn time-based."]),
    dict(kind="slide", slide=18, start=256, end=268, title="Chạy lại Hình 6 của bài báo", lines=[FIG6]),
    dict(kind="slide", slide=19, start=268, end=278, title="Đối chiếu tiêu chí", lines=[CRITERIA]),
    dict(kind="slide", slide=20, start=278, end=293, title="Kết luận", lines=[CONCLUSION, THANKS]),
]

SEGMENTS_10 = [
    dict(kind="slide", slide=1, start=0, end=15, title="Mở đầu", lines=[OPENING]),
    dict(kind="slide", slide=2, start=15, end=40, title="Bài toán và câu hỏi nghiên cứu", lines=PROBLEM),
    *paper(40),
    dict(kind="slide", slide=6, start=82, end=100, title="Dữ liệu N-BaIoT và chống rò rỉ", lines=[
        "Dữ liệu N-BaIoT có 7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; em loại 158 nghìn dòng trùng lặp.",
        "Benign chia theo thời gian có vùng đệm 500 dòng, scaler chỉ fit trên tập train; nếu cố tình chia ngẫu nhiên "
        "thì FPR đẹp giả xuống 0,0006."]),
    dict(kind="slide", slide=7, start=100, end=119, title="Mô hình so sánh và hệ thống 4 tầng", lines=[
        "Em so sánh autoencoder Meidan, model chung, Isolation Forest và bản V1 chỉ 8 nghìn tham số, lượng tử hóa "
        "int8.",
        "Hệ thống tách bốn tầng AI, backend, CSDL, dashboard; backend từ chối gói model bị sửa, có 56 test tự động.",
        "Bây giờ em demo. (Alt + Tab sang trình duyệt)"]),
    demo(119, 194, back_slide=9),
    dict(kind="slide", slide=9, start=194, end=214, title="Kết quả: FPR thấp, lỗi ở flood tcp/udp", lines=[
        "Trên 468 lần chạy, autoencoder per-device có FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822.",
        "Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE: nguồn bị giả mạo nên mỗi gói như luồng mới; tám loại "
        "còn lại có recall gần bằng 1."]),
    dict(kind="slide", slide=10, start=214, end=230, title="Lượng tử hóa int8 và edge benchmark", lines=[
        "Bản int8 chỉ 15,3 KB, ngưỡng được hiệu chỉnh lại trên DSopt.",
        "Trên một lõi E-core, p95 chỉ 10,8 micro-giây mỗi mẫu, khoảng 103 nghìn mẫu mỗi giây – thừa sức chạy tại "
        "edge."]),
    dict(kind="slide", slide=11, start=230, end=250, title="MTD: tái lập paper chính", lines=[
        "Em tái lập paper bằng đúng CVE và topology của paper: rủi ro mức máy ảo khớp sai số 0,01, đường tấn công lệch "
        "0,8%, 6 trên 7 kết luận tái lập được.",
        "Kết hợp shuffle và diversity giảm xác suất tấn công thành công từ 0,498 xuống 0,327."]),
    dict(kind="slide", slide=12, start=250, end=262, title="Chạy lại Hình 6 của bài báo", lines=[FIG6]),
    dict(kind="slide", slide=13, start=262, end=290, title="Đối chiếu tiêu chí và kết luận", lines=[
        CRITERIA, CONCLUSION, THANKS]),
]

SEGMENTS_NGAN = [
    dict(kind="slide", slide=1, start=0, end=12, title="Mở đầu", lines=[
        "Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện IoT nhiễm botnet ngay tại thiết bị biên "
        "bằng autoencoder nhẹ."]),
    dict(kind="slide", slide=2, start=12, end=30, title="Bài toán và mục tiêu", lines=[
        "IoT dễ bị Mirai và BASHLITE chiếm; bộ phát hiện đặt tại edge nên phải nhỏ và nhanh.",
        "Mục tiêu: autoencoder nhẹ chạy tại edge, tái lập bài báo chính, và dùng cảnh báo để kích hoạt MTD."]),
    dict(kind="slide", slide=3, start=30, end=50, title="Bài báo tham khảo", lines=[
        "Bài của Masud 2025 đánh giá kết hợp shuffle, diversity, redundancy trên mô hình THARM ba tầng; shuffle cộng "
        "diversity tốt nhất.",
        "Nhưng bài chỉ mô phỏng, không có bộ phát hiện kích hoạt MTD, nên em làm thêm phần phát hiện bằng autoencoder."]),
    dict(kind="slide", slide=4, start=50, end=68, title="Dữ liệu và phương pháp", lines=[
        "N-BaIoT có 7,06 triệu dòng; em loại 158 nghìn dòng trùng và chia theo thời gian có vùng đệm để không rò rỉ.",
        "Baseline là autoencoder của Meidan; bản nhẹ V1 chỉ 8 nghìn tham số, lượng tử hóa int8."]),
    dict(kind="slide", slide=5, start=68, end=80, title="Hệ thống 4 tầng", lines=[
        "Hệ thống tách bốn tầng: AI, backend, CSDL và dashboard.",
        "Bây giờ em demo. (Alt + Tab sang trình duyệt)"]),
    demo_short(80, 128, back_slide=6),
    dict(kind="slide", slide=6, start=128, end=148, title="Kết quả phát hiện và edge", lines=[
        "Kết quả: FPR chỉ 0,0025 nhưng TPR 0,822, vì flood tcp/udp giả mạo nguồn trông giống benign.",
        "Bản int8 chỉ 15,3 KB, 10,8 micro-giây mỗi mẫu trên một lõi – đạt tiêu chí edge."]),
    dict(kind="slide", slide=7, start=148, end=166, title="Tái lập bài báo", lines=[
        "Tái lập bằng đúng dữ liệu của bài: rủi ro từng máy ảo khớp tới 0,01, 6 trên 7 kết luận đúng; vẽ lại Hình 6, "
        "đường diversity khớp cả 7 máy ảo."]),
    dict(kind="slide", slide=8, start=166, end=192, title="Kết luận", lines=[
        "RQ5 về edge đạt, RQ1 đến RQ4 không đạt và em giữ nguyên tiêu chí.", CONCLUSION, THANKS]),
]

# Mỗi bộ slide: dòng thời gian + phần chữ riêng (tên file, slide dự phòng, slide trả lời câu hỏi)
DECKS = {
    "17": dict(segments=SEGMENTS_17, suffix="", label="đầy đủ 30 slide (20 chính + 10 phụ lục)", fallback=10, explain=12,
               shown="chiếu 16 slide chính; slide 8, 10, 13, 16 và phụ lục 21–30 để trả lời câu hỏi",
               qa_slides=["7, 12, 26, 27", "11, 15, 27", "13", "14", "16", "17, 30", "18, 25, 28", "3–5, 21", "22, 24",
                          "18, 27, 29"]),
    "10": dict(segments=SEGMENTS_10, suffix="_10slide", label="rút gọn 23 slide (13 chính + 10 phụ lục)", fallback=8,
               explain=9,
               shown="chiếu slide 1–7 và 9–13; slide 8 là ảnh demo, chỉ chiếu khi server lỗi; phụ lục 14–23 để trả "
                     "lời câu hỏi",
               qa_slides=["6, 9, 19, 20", "9, 10, 20", "9", "10", "13", "11, 23", "11, 12, 18, 21", "3–5, 14", "15, 17",
                          "12, 20, 22"]),
    "ngan": dict(segments=SEGMENTS_NGAN, suffix="_ngan", label="ngắn 8 slide", fallback=5, explain=6,
                 shown="chiếu cả 8 slide; slide 5 có ảnh dashboard, dùng khi server lỗi",
                 qa_slides=["6", "6", "6", "6, 8", "8", "3, 5", "7", "3", "2, 4", "7"]),
}


def use_deck(key):
    """Chọn bộ slide: đặt các biến toàn cục mà phần sinh kịch bản và dựng video dùng chung."""
    global DECK, SEGMENTS, TOTAL, SLIDES_PDF, OUT_MD, OUT_DOCX, OUT_MP4
    DECK = DECKS[key]
    SEGMENTS = DECK["segments"]
    TOTAL = SEGMENTS[-1]["end"]
    sfx = DECK["suffix"]
    SLIDES_PDF = DOCS / "thuyet_trinh" / f"SlideThuyetTrinh_DT043{sfx}_1150080120_HoangThanhTra.pdf"
    OUT_MD = DOCS / "thuyet_trinh" / f"KICH_BAN_THUYET_TRINH_5P{sfx}.md"
    OUT_DOCX = DOCS / "thuyet_trinh" / f"KichBanThuyetTrinh_DT043{sfx}_1150080120_HoangThanhTra.docx"
    OUT_MP4 = DOCS / "video" / f"Video_mau_thuyet_trinh_DT043{sfx}.mp4"


# ---------------------------------------------------------------- nội dung dùng chung cho kịch bản .md và .docx
NUMBERS = [
    ("Dữ liệu", "N-BaIoT · 7,06 triệu dòng · 115 đặc trưng · 9 thiết bị · 10 loại tấn công"),
    ("Số lần chạy", "468 (thiết bị × seed × cấu hình), 5 seed cố định"),
    ("B0 (AE Meidan)", "macro-F1 0,706 · TPR 0,822 · FPR 0,0025 (Meidan: FPR 0,007)"),
    ("Isolation Forest", "macro-F1 0,886"),
    ("V1 int8 + hiệu chỉnh ngưỡng", "8.059 tham số · 15,3 KB · macro-F1 0,717 · FPR 0,0016"),
    ("Edge (1 E-core)", "p95 10,8 µs/mẫu · ~103.000 mẫu/s · RAM +4,6 MB"),
    ("MTD (ASP)", "không MTD 0,498 · shuffle 0,409 · diversity 0,437 · kết hợp 0,327"),
    ("Tái lập paper chính", "rủi ro mức máy ảo khớp ±0,01 · đường tấn công −0,8% · chọn V5 như paper · "
                            "6/7 kết luận định tính (topology Hình 3; Definition 2: 3/7)"),
    ("Chạy lại Hình 6 (bài chính)", "diversity khớp 7/7 máy ảo (lệch ≤ 5%) · shuffle, S+D khớp ở V5"),
    ("Demo mirai/syn (Danmini)", "1989/1989 cửa sổ cảnh báo, cảnh báo high + 2 hành động MTD"),
    ("Demo benign và gafgyt/tcp (Ennio)", "0 cửa sổ cảnh báo"),
]

QA = [  # slide hỗ trợ lấy theo bộ slide (DECK["qa_slides"])
    ("Sao không đạt TPR 100% như Meidan?",
     "Em chia theo thời gian có vùng đệm và loại trùng lặp để không rò rỉ; thí nghiệm cố tình cho rò rỉ (E6) làm "
     "FPR \"đẹp giả\" xuống 0,0006, cho thấy cách chia ảnh hưởng lớn đến kết quả. Phần bỏ sót là flood tcp/udp "
     "giả mạo nguồn."),
    ("Isolation Forest tốt hơn, sao vẫn dùng AE?",
     "Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm "
     "baseline so sánh."),
    ("Hạ ngưỡng có bắt được tcp/udp không?",
     "Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả "
     "nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí."),
    ("Vì sao kích thước int8 không giảm còn 25%?",
     "Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%."),
    ("Kết quả có ổn định không?",
     "Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không "
     "đủ."),
    ("MTD có tác động mạng thật không?",
     "Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc."),
    ("Tái lập paper chính được đến đâu?",
     "Dùng đúng 18 CVE hệ điều hành, 14 CVE dịch vụ và 8 máy ảo của paper: rủi ro mức máy ảo khớp ±0,01, đường tấn "
     "công lệch −0,8%, độ trung tâm trên đồ thị có hướng chọn V5 như paper. Với topology Hình 3 tái lập 6/7 kết luận "
     "định tính, với Definition 2 chỉ 3/7. Tổng rủi ro toàn mạng không khớp vì paper cắt danh sách cạnh và công thức "
     "in ra mâu thuẫn."),
    ("Bài báo tham khảo giải quyết bài toán gì, hạn chế ở đâu?",
     "Masud 2025 đánh giá việc kết hợp shuffle, diversity, redundancy bằng mô hình THARM ba tầng; kết luận shuffle + "
     "diversity tốt nhất. Hạn chế: chỉ mô phỏng, chỉ MTD theo thời gian, không có bộ phát hiện kích hoạt MTD, không "
     "công bố mã. Bài tham chiếu Meidan 2018 chia dữ liệu một lần và không đo trên edge."),
    ("Em làm bài này theo quy trình nào?",
     "Đọc bài báo → lập kế hoạch → tải dữ liệu có checksum → làm sạch, EDA → viết pipeline kèm test → chốt tiêu chí "
     "trước khi chạy → chạy 468 lần → dựng hệ thống 4 tầng → tổng hợp thống kê, báo cáo → tái lập bài chính (E11)."),
    ("Biểu đồ chạy lại có giống bài báo không?",
     "Em vẽ lại đúng dạng Hình 6, Hình 7 của bài chính và Hình 2 của Meidan. Hình 6: diversity khớp 7/7 máy ảo, shuffle "
     "và S+D khớp ở V5, redundancy cao hơn. Hình 7 không khớp vì topology bài công bố chỉ có 5 đường và bài không nêu "
     "cách tính ASP đường. Hình 2 của Meidan: FPR khớp, TPR thấp hơn do flood tcp/udp."),
]


def qa_rows():
    return [(q, a, s) for (q, a), s in zip(QA, DECK["qa_slides"])]


def tips():
    d = next(s for s in SEGMENTS if s["kind"] == "demo")
    return [
        f"Tập theo video mẫu 2–3 lần: đến **{fmt(d['start'])} phải bắt đầu demo**, đến **{fmt(d['end'])} phải quay "
        f"lại slide**, kết thúc khoảng **{fmt(TOTAL)}** – còn ~{300 - TOTAL} s dự phòng trong khung 5 phút. Nếu chậm, "
        f"ở bước cuối của demo chỉ nói một câu vì slide {DECK['explain']} sẽ giải thích lại.",
        "Nếu thầy hỏi về MTD time-based: kéo xuống bảng MTD trên dashboard, bấm «Chạy chu kỳ time-based».",
        "Khi demo, nói trong lúc chờ kết quả, không im lặng chờ.",
        "Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.",
        "Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày và tự thao tác demo.",
    ]


def fmt(t):
    return f"{int(t) // 60}:{int(t) % 60:02d}"


def cues():
    """Danh sách (bắt đầu, kết thúc, segment, chỉ số dòng/bước, text) – chia thời gian theo độ dài câu."""
    out = []
    for seg in SEGMENTS:
        if seg["kind"] == "demo":
            dur = (seg["end"] - seg["start"]) / len(seg["steps"])
            for i, st in enumerate(seg["steps"]):
                a = seg["start"] + i * dur
                out.append((a, a + dur, seg, i, st["say"]))
            continue
        total = sum(len(x) for x in seg["lines"])
        a = seg["start"]
        for i, line in enumerate(seg["lines"]):
            b = seg["end"] if i == len(seg["lines"]) - 1 else round(a + (seg["end"] - seg["start"]) * len(line) / total)
            out.append((a, b, seg, i, line))
            a = b
    return out


# ---------------------------------------------------------------- kịch bản Markdown
def build_md():
    sfx = DECK["suffix"]
    L = []
    L.append(f"# Kịch bản thuyết trình ≈ {fmt(TOTAL)} (khung 5 phút, có demo) – DT043 · bộ {DECK['label']}\n")
    L.append("**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV "
             "1150080120 – 11CNPM2  ")
    L.append(f"**Tài liệu dùng:** [bộ slide {DECK['label']}](SlideThuyetTrinh_DT043{sfx}_1150080120_HoangThanhTra.pptx) "
             f"({DECK['shown']}) + dashboard demo `http://127.0.0.1:8000/`.  ")
    L.append(f"**Video mẫu để tập theo:** `../video/Video_mau_thuyet_trinh_DT043{sfx}.mp4` – dựng từ CÙNG dòng thời gian "
             "với kịch bản này (script `src/report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại "
             "bên dưới; video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.\n")
    L.append("## 1. Phân bổ thời gian\n")
    L.append("| Thời điểm | Phần | Slide / màn hình | Thời lượng |")
    L.append("|---|---|---|---|")
    for s in SEGMENTS:
        where = "Dashboard" if s["kind"] == "demo" else f"Slide {s['slide']}"
        name = f"**{s['title']}**" if s["kind"] == "demo" else s["title"]
        L.append(f"| {fmt(s['start'])} – {fmt(s['end'])} | {name} | {where} | {s['end'] - s['start']} s |")
    L.append("")
    L.append("## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)\n")
    L.append("1. Mở PowerShell tại thư mục `DT043\\src`, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo lại), "
             "rồi bật server:")
    L.append("   ```powershell")
    L.append("   Remove-Item db\\dt043.sqlite3 -ErrorAction SilentlyContinue")
    L.append("   .venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000")
    L.append("   ```")
    L.append("   Đợi dòng `Application startup complete`.")
    L.append("2. Mở trình duyệt `http://127.0.0.1:8000/`, kiểm tra góc phải hiện **9 model**.")
    L.append("3. Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và trình "
             "duyệt.")
    L.append(f"4. Dự phòng: nếu server không chạy, chiếu **Slide {DECK['fallback']}** (ảnh demo) và đọc kết quả ở mục 4.\n")
    L.append("## 3. Lời thoại theo mốc thời gian (trùng phụ đề trong video)\n")
    for a, b, seg, i, text in cues():
        if seg["kind"] == "demo":
            if i == 0:
                L.append(f"### {fmt(seg['start'])} – DEMO trực tiếp ({seg['end'] - seg['start']} s)\n")
                L.append("| Mốc | Thao tác | Lời thoại | Kết quả phải thấy |")
                L.append("|---|---|---|---|")
            st = seg["steps"][i]
            L.append(f"| {fmt(a)} | {st['action']} | {st['say']} | {st['expect']} |")
            if i == len(seg["steps"]) - 1:
                L.append("")
            continue
        if i == 0:
            L.append(f"### {fmt(seg['start'])} – Slide {seg['slide']} · {seg['title']} ({seg['end'] - seg['start']} s)")
        L.append(f"> **[{fmt(a)}]** {text}")
        if i == len(seg["lines"]) - 1:
            L.append("")
    L.append("## 4. Số liệu cần nhớ\n")
    L.append("| Nội dung | Giá trị |")
    L.append("|---|---|")
    for k, v in NUMBERS:
        L.append(f"| {k} | {v} |")
    L.append("")
    L.append("## 5. Câu hỏi có thể gặp\n")
    L.append("| Câu hỏi | Trả lời ngắn | Slide hỗ trợ |")
    L.append("|---|---|---|")
    for q, a, s in qa_rows():
        L.append(f"| {q} | {a} | {s} |")
    L.append("")
    L.append("## 6. Mẹo trình bày\n")
    L += ["- " + t for t in tips()]
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("đã ghi", OUT_MD)


# ---------------------------------------------------------------- kịch bản Word (cùng nội dung với .md)
def build_docx():
    import pandas as pd
    sys.path.insert(0, str(Path(__file__).parent))
    from docx_helpers import Report
    R = Report()
    R.para("KỊCH BẢN THUYẾT TRÌNH ĐỀ TÀI DT043", bold=True, size=16, align="center")
    R.para(f"Phát hiện botnet IoT bằng autoencoder nhẹ – bộ {DECK['label']} – khung 5 phút, nói ≈ {fmt(TOTAL)}, có demo",
           italic=True, align="center")
    R.para("Người trình bày: **Hoàng Thanh Trà** – MSSV 1150080120 – Lớp 11CNPM2", align="center")
    R.para(f"Tài liệu dùng: bộ slide {DECK['label']} ({DECK['shown']}) + dashboard demo http://127.0.0.1:8000/. "
           f"Video mẫu để tập: tailieu/video/Video_mau_thuyet_trinh_DT043{DECK['suffix']}.mp4 (phụ đề trùng từng chữ "
           "với lời thoại bên dưới).", justify=False)

    R.h1("1. Phân bổ thời gian")
    R.table(pd.DataFrame([{"Thời điểm": f"{fmt(s['start'])} – {fmt(s['end'])}", "Phần": s["title"],
                           "Slide / màn hình": "Dashboard" if s["kind"] == "demo" else f"Slide {s['slide']}",
                           "Thời lượng": f"{s['end'] - s['start']} s"} for s in SEGMENTS]),
            font=11, col_widths_cm=[3.0, 8.0, 3.0, 2.0])

    R.h1("2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)")
    R.numbered(["Mở PowerShell tại thư mục DT043\\src, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo "
                "lại), rồi bật server và đợi dòng «Application startup complete»:"])
    R.code("Remove-Item db\\dt043.sqlite3 -ErrorAction SilentlyContinue\n"
           ".venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000")
    R.numbered(["Mở trình duyệt http://127.0.0.1:8000/, kiểm tra góc phải hiện **9 model**.",
                "Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và "
                "trình duyệt.",
                f"Dự phòng: nếu server không chạy, chiếu **Slide {DECK['fallback']}** (ảnh demo) và đọc kết quả ở "
                "mục 4."], start=2)

    R.h1("3. Lời thoại theo mốc thời gian")
    for seg in SEGMENTS:
        if seg["kind"] == "demo":
            R.h2(f"{fmt(seg['start'])} – DEMO trực tiếp ({seg['end'] - seg['start']} s)")
            step = (seg["end"] - seg["start"]) / len(seg["steps"])
            R.table(pd.DataFrame([{"Mốc": fmt(seg["start"] + i * step), "Thao tác": st["action"],
                                   "Lời thoại": st["say"], "Kết quả phải thấy": st["expect"]}
                                  for i, st in enumerate(seg["steps"])]),
                    font=10.5, col_widths_cm=[1.3, 4.7, 6.0, 4.0])
            continue
        R.h2(f"{fmt(seg['start'])} – Slide {seg['slide']} · {seg['title']} ({seg['end'] - seg['start']} s)")
        for a, b, s2, i, text in cues():
            if s2 is seg:
                R.para(f"**[{fmt(a)}]** {text}")

    R.h1("4. Số liệu cần nhớ")
    R.table(pd.DataFrame(NUMBERS, columns=["Nội dung", "Giá trị"]), font=11, col_widths_cm=[5.0, 11.0])
    R.h1("5. Câu hỏi có thể gặp")
    R.table(pd.DataFrame(qa_rows(), columns=["Câu hỏi", "Trả lời ngắn", "Slide"]), font=10.5,
            col_widths_cm=[4.5, 10.0, 1.5])
    R.h1("6. Mẹo trình bày")
    R.bullets(tips())
    R.save(OUT_DOCX)
    print("đã ghi", OUT_DOCX)


# ---------------------------------------------------------------- dựng hình
def fonts():
    from PIL import ImageFont
    f = "C:/Windows/Fonts/"
    return {"text": ImageFont.truetype(f + "segoeui.ttf", 34), "bold": ImageFont.truetype(f + "segoeuib.ttf", 30),
            "small": ImageFont.truetype(f + "segoeui.ttf", 26), "act": ImageFont.truetype(f + "segoeuib.ttf", 30)}


def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def panel_frame(t, seg, cue_text, content=None, action=None):
    """Khung 1920x1080 tại giây t: nội dung phía trên (hoặc trong suốt cho demo) + khung phụ đề."""
    from PIL import Image, ImageDraw
    F = fonts()
    img = Image.new("RGBA", (W, H), (17, 17, 17, 255) if content is not None else (0, 0, 0, 0))
    if content is not None:
        img.paste(content, (CX, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, PANEL_Y, W, H], fill=(24, 28, 36, 255))
    d.rectangle([0, PANEL_Y, int(W * t / TOTAL), PANEL_Y + 6], fill=(56, 189, 248, 255))
    label = f"DEMO · bước {seg['steps'].index(action) + 1}/{len(seg['steps'])}" if action else \
        f"Slide {seg['slide']} · {seg['title']}"
    d.text((40, PANEL_Y + 16), label, font=F["bold"], fill=(56, 189, 248, 255))
    clock = f"{fmt(t)} / {fmt(TOTAL)}"
    d.text((W - 40 - d.textlength(clock, font=F["bold"]), PANEL_Y + 16), clock, font=F["bold"],
           fill=(250, 204, 21, 255))
    y = PANEL_Y + 60
    if action:
        d.text((40, y), "Thao tác: " + action["action"], font=F["act"], fill=(250, 204, 21, 255))
        y += 42
        lines = wrap(d, "Nói: " + cue_text, F["small"], W - 80)[:2]
        for ln in lines:
            d.text((40, y), ln, font=F["small"], fill=(255, 255, 255, 255))
            y += 34
    else:
        for ln in wrap(d, cue_text, F["text"], W - 80)[:3]:
            d.text((40, y), ln, font=F["text"], fill=(255, 255, 255, 255))
            y += 42
    return img


def render_slides(tmp):
    import fitz
    from PIL import Image
    doc = fitz.open(SLIDES_PDF)
    out = {}
    for s in SEGMENTS:
        if s["kind"] != "slide":
            continue
        page = doc[s["slide"] - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(CW / page.rect.width, CH / page.rect.height))
        out[s["slide"]] = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).resize((CW, CH))
    return out


def record_demo(tmp, port=8010):
    """Bật backend (CSDL tạm), dùng Playwright thao tác dashboard và quay video phần demo; trả về (đường dẫn, giây bắt đầu)."""
    from playwright.sync_api import sync_playwright
    env = dict(os.environ, DT043_DB=str(Path(tmp) / "demo.sqlite3"), PYTHONIOENCODING="utf-8")
    py = ROOT / ".venv" / "Scripts" / "python.exe"
    srv = subprocess.Popen([str(py), "-m", "uvicorn", "backend.app.main:app", "--port", str(port)], cwd=ROOT, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(120):
            try:
                if json.load(urllib.request.urlopen(base + "/api/health"))["models_loaded"] == 9:
                    break
            except Exception:  # noqa: BLE001
                time.sleep(1)
        else:
            raise RuntimeError("backend không lên")
        demo = next(s for s in SEGMENTS if s["kind"] == "demo")
        step_len = (demo["end"] - demo["start"]) / len(demo["steps"])
        with sync_playwright() as p:
            br = p.chromium.launch(channel="msedge")  # dùng Edge có sẵn, không cần tải trình duyệt
            ctx = br.new_context(viewport={"width": CW, "height": CH}, record_video_dir=tmp,
                                 record_video_size={"width": CW, "height": CH})
            page = ctx.new_page()
            t_video = time.time()
            page.goto(base + "/")
            page.wait_for_selector("#devices tbody tr")
            page.evaluate("document.body.style.zoom='1.25'")  # chữ đủ lớn khi xem video
            page.add_style_tag(content="#fc{position:fixed;z-index:9999;width:26px;height:26px;border-radius:50%;"
                                       "background:rgba(239,68,68,.85);border:3px solid #fff;pointer-events:none;"
                                       "transition:left .7s ease,top .7s ease;left:760px;top:420px;"
                                       "box-shadow:0 0 0 6px rgba(239,68,68,.25)}")
            page.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=fc></div>')")

            def point(sel):
                box = page.locator(sel).first.bounding_box()
                page.evaluate(f"(()=>{{const c=document.getElementById('fc');c.style.left='{box['x'] + box['width'] / 2 - 13}px';"
                              f"c.style.top='{box['y'] + box['height'] / 2 - 13}px'}})()")
                time.sleep(1.0)

            def scroll(sel):
                page.locator(sel).first.scroll_into_view_if_needed()
                page.evaluate(f"document.querySelector('{sel}').scrollIntoView({{behavior:'smooth',block:'start'}})")
                time.sleep(1.2)

            def replay(device, segment):
                point("#r-device")
                page.select_option("#r-device", device)
                time.sleep(0.6)
                point("#r-segment")
                page.select_option("#r-segment", segment)
                time.sleep(0.6)
                point("#replay-form button")
                page.click("#replay-form button")
                page.wait_for_function("!document.querySelector('#replay-summary').textContent.includes('Đang chạy')")

            actions = {
                "health": lambda: (point("#health"), time.sleep(3), point("#devices tbody tr")),
                "mirai": lambda: (scroll("#replay-form"), replay("Danmini_Doorbell", "mirai/syn"), point("#replay-summary")),
                "alerts": lambda: (scroll("#alerts"), point("#alerts tbody tr"), time.sleep(3), point("#mtd tbody tr")),
                "benign": lambda: (scroll("#replay-form"), replay("Ennio_Doorbell", "benign"), point("#replay-summary")),
                "tcp": lambda: (scroll("#replay-form"), replay("Ennio_Doorbell", "gafgyt/tcp"), point("#replay-summary")),
            }
            steps = [actions[st["key"]] for st in demo["steps"]]
            t_start = time.time()
            for i, fn in enumerate(steps):
                target = t_start + i * step_len
                time.sleep(max(0, target - time.time()))
                fn()
            time.sleep(max(0, t_start + len(steps) * step_len - time.time()) + 1)
            video = page.video.path()
            ctx.close()
            br.close()
        return video, t_start - t_video
    finally:
        srv.terminate()


def build_video():
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = tempfile.mkdtemp(prefix="dt043_video_")
    slides = render_slides(tmp)
    cue_list = cues()

    def cue_at(t):
        return next(c for c in cue_list if c[0] <= t + 0.5 < c[1] or (c[1] == TOTAL and t + 0.5 >= c[0]))

    demo = next(s for s in SEGMENTS if s["kind"] == "demo")
    parts = []
    for name, a, b in [("p1", 0, demo["start"]), ("demo", demo["start"], demo["end"]), ("p2", demo["end"], TOTAL)]:
        fdir = Path(tmp) / name
        fdir.mkdir()
        for k, t in enumerate(range(a, b)):
            ca, cb, seg, i, text = cue_at(t)
            if seg["kind"] == "demo":
                frame = panel_frame(t, seg, text, None, seg["steps"][i])
            else:
                frame = panel_frame(t, seg, text, slides[seg["slide"]]).convert("RGB")
            frame.save(fdir / f"f{k:04d}.png")
        parts.append((name, fdir, b - a))

    video, offset = record_demo(tmp)
    seg_files = []
    for name, fdir, dur in parts:
        out = Path(tmp) / f"{name}.mp4"
        if name == "demo":
            cmd = [ff, "-y", "-i", video, "-framerate", "1", "-i", str(fdir / "f%04d.png"), "-filter_complex",
                   f"[0:v]trim=start={offset:.2f}:duration={dur},setpts=PTS-STARTPTS,fps=30,"
                   f"pad={W}:{H}:{CX}:0:color=0x111111[b];[1:v]fps=30[o];[b][o]overlay=0:0,format=yuv420p",
                   "-t", str(dur), "-c:v", "libx264", "-crf", "20", "-preset", "medium", str(out)]
        else:
            cmd = [ff, "-y", "-framerate", "1", "-i", str(fdir / "f%04d.png"), "-vf", "fps=30,format=yuv420p",
                   "-t", str(dur), "-c:v", "libx264", "-crf", "20", "-preset", "medium", str(out)]
        subprocess.run(cmd, check=True, capture_output=True)
        seg_files.append(out)
    lst = Path(tmp) / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in seg_files), encoding="utf-8")
    OUT_MP4.parent.mkdir(exist_ok=True)
    subprocess.run([ff, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart",
                    str(OUT_MP4)], check=True, capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("đã ghi", OUT_MP4, f"{OUT_MP4.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    keys = [sys.argv[sys.argv.index("--deck") + 1]] if "--deck" in sys.argv else list(DECKS)
    for key in keys:
        use_deck(key)
        build_md()
        build_docx()
        if "--md-only" not in sys.argv:
            build_video()
