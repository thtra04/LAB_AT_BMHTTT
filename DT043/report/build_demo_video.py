"""Dựng video mẫu thuyết trình 5 phút (slide + demo thật trên dashboard + phụ đề lời thoại + đồng hồ)
và sinh kịch bản KICH_BAN_THUYET_TRINH_5P.md từ CÙNG một dòng thời gian, để video và kịch bản khớp nhau.

Chạy (Python hệ thống có playwright, pymupdf, pillow, imageio-ffmpeg), tại thư mục DT043:
    python report/build_demo_video.py            # sinh kịch bản + video
    python report/build_demo_video.py --md-only  # chỉ sinh kịch bản
Video ra: video/Video_mau_thuyet_trinh_DT043.mp4 (không commit – thư mục video/ nằm trong .gitignore).
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
SLIDES_PDF = ROOT / "report" / "SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pdf"
OUT_MD = ROOT / "KICH_BAN_THUYET_TRINH_5P.md"
OUT_MP4 = ROOT / "video" / "Video_mau_thuyet_trinh_DT043.mp4"
TOTAL = 300

W, H = 1920, 1080
CW, CH = 1564, 880            # vùng nội dung 16:9 (slide hoặc trình duyệt)
CX = (W - CW) // 2
PANEL_Y = CH                  # khung phụ đề phía dưới, cao 200 px

# ---------------------------------------------------------------- dòng thời gian (nguồn duy nhất)
SEGMENTS = [
    dict(kind="slide", slide=1, start=0, end=20, title="Mở đầu", lines=[
        "Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện thiết bị IoT bị nhiễm botnet "
        "ngay tại thiết bị biên.",
        "Em dùng autoencoder huấn luyện riêng cho từng thiết bị, thu nhỏ và lượng tử hóa int8 để chạy trên phần cứng "
        "yếu, và nối với hướng Moving Target Defence của paper chính."]),
    dict(kind="slide", slide=2, start=20, end=50, title="Bài toán và câu hỏi nghiên cứu", lines=[
        "Thiết bị IoT dùng mật khẩu mặc định, ít được vá, nên Mirai và BASHLITE chiếm hàng loạt để DDoS.",
        "Phát hiện ở trung tâm thì chậm và tốn băng thông, nên em đặt bộ phát hiện ngay tại edge.",
        "Em đặt sáu câu hỏi nghiên cứu; mỗi câu có tiêu chí định lượng được chốt và lưu checksum trước khi chạy, "
        "để không thể chỉnh tiêu chí theo kết quả."]),
    dict(kind="slide", slide=3, start=50, end=70, title="Paper chính lệch chủ đề → hai track", lines=[
        "Paper chính của Masud và cộng sự năm 2025 nói về Moving Target Defence, không dùng autoencoder hay N-BaIoT.",
        "Vì vậy em chia hai track: track A là lõi phát hiện bằng autoencoder theo Meidan; track B tái lập xu hướng "
        "MTD và dùng cảnh báo của autoencoder để kích hoạt MTD."]),
    dict(kind="slide", slide=4, start=70, end=80, title="Dữ liệu N-BaIoT", lines=[
        "Dữ liệu N-BaIoT có 7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; nhiều dòng trùng lặp và mất cân bằng nặng."]),
    dict(kind="slide", slide=5, start=80, end=92, title="Chống rò rỉ dữ liệu", lines=[
        "Các dòng liền kề gần giống nhau nên chia ngẫu nhiên sẽ rò rỉ. Em chia theo thời gian có vùng đệm 500 dòng, "
        "chỉ fit scaler trên tập train, và mỗi biện pháp đều có unit test."]),
    dict(kind="slide", slide=6, start=92, end=100, title="Pipeline và các mô hình", lines=[
        "Em so sánh autoencoder của Meidan, model chung, Isolation Forest và bản V1 nhẹ chỉ 8 nghìn tham số, "
        "lượng tử hóa int8 rồi hiệu chỉnh lại ngưỡng."]),
    dict(kind="slide", slide=7, start=100, end=115, title="Kiến trúc 4 tầng AI · BE · DB · FE", lines=[
        "Hệ thống tách bốn tầng: AI xuất gói model có checksum SHA-256; backend FastAPI nạp gói và từ chối nếu bị "
        "sửa dù chỉ một byte.",
        "CSDL SQLite lưu cảnh báo và hành động MTD; frontend là dashboard. Bây giờ em demo trực tiếp. "
        "(Alt + Tab sang trình duyệt)"]),
    dict(kind="demo", start=115, end=205, title="DEMO trực tiếp", steps=[
        dict(action="Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model»",
             say="Backend đã nạp 9 model, mỗi thiết bị một model V1 int8 khoảng 15 KB, kèm ngưỡng tr* và cửa sổ ws* "
                 "riêng.",
             expect="9 model, 0 lỗi gói"),
        dict(action="Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại»",
             say="Em phát lại 2000 mẫu tấn công Mirai SYN flood từ dữ liệu công khai: MSE tái tạo vượt hẳn ngưỡng, "
                 "1989/1989 cửa sổ bị cảnh báo.",
             expect="1989/1989 cửa sổ cảnh báo, đường MSE nằm trên ngưỡng"),
        dict(action="Kéo xuống bảng «Cảnh báo» và «Hành động MTD»",
             say="Hệ thống sinh cảnh báo mức high và tự kích hoạt hai hành động MTD kiểu event-based: xáo trộn IP và "
                 "đổi firmware, ghi vào CSDL.",
             expect="1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware)"),
        dict(action="Kéo lên, chọn Ennio_Doorbell · benign → bấm «Phát lại»",
             say="Với lưu lượng bình thường của Ennio, không có cửa sổ nào bị cảnh báo, tức là không báo động giả.",
             expect="0 cửa sổ cảnh báo"),
        dict(action="Giữ Ennio_Doorbell, chọn gafgyt/tcp → bấm «Phát lại»",
             say="Còn đây là điểm yếu em không che giấu: flood TCP của BASHLITE bị bỏ sót, đúng như phân tích lỗi ở "
                 "phần sau.",
             expect="0 cửa sổ cảnh báo"),
        dict(action="Kéo xuống bảng MTD, bấm «Chạy chu kỳ time-based»",
             say="Vì có tấn công bị bỏ sót, em giữ thêm MTD theo chu kỳ thời gian làm lưới an toàn. "
                 "Em quay lại slide. (Alt + Tab về PowerPoint, Slide 9)",
             expect="thêm dòng MTD kích hoạt time-based"),
    ]),
    dict(kind="slide", slide=9, start=205, end=220, title="Kết quả tổng quan", lines=[
        "Trên 468 lần chạy, autoencoder per-device có FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822, "
        "không đạt 100% như paper."]),
    dict(kind="slide", slide=10, start=220, end=235, title="Lỗi chính: flood BASHLITE tcp/udp", lines=[
        "Kiểm tra trên dữ liệu thô: toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE.",
        "Nguồn bị giả mạo liên tục nên mỗi gói trông như luồng mới, giống benign; tám loại tấn công còn lại có "
        "recall gần bằng 1."]),
    dict(kind="slide", slide=12, start=235, end=247, title="Lượng tử hóa int8", lines=[
        "Bản int8 chỉ còn 15,3 KB; nếu giữ ngưỡng fp32 thì sai lệch, nên em hiệu chỉnh lại ngưỡng trên tập DSopt."]),
    dict(kind="slide", slide=13, start=247, end=260, title="Edge benchmark", lines=[
        "Trên một lõi E-core: p95 chỉ 10,8 micro-giây mỗi mẫu, khoảng 103 nghìn mẫu mỗi giây, RAM tăng 4,6 MB – "
        "thừa sức chạy tại edge."]),
    dict(kind="slide", slide=15, start=260, end=275, title="Moving Target Defence", lines=[
        "Với mô hình HARM rút gọn, xác suất tấn công thành công giảm từ 0,498 xuống 0,327 khi kết hợp shuffle và "
        "diversity, khớp xu hướng paper chính.",
        "MTD lai kích hoạt bởi autoencoder có thời gian lộ diện thấp hơn time-based ở cùng chi phí."]),
    dict(kind="slide", slide=16, start=275, end=287, title="Đối chiếu tiêu chí", lines=[
        "Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt với biên rất lớn; RQ1 đến RQ4 không đạt, và em giữ nguyên "
        "tiêu chí, không chỉnh sau khi có kết quả."]),
    dict(kind="slide", slide=17, start=287, end=300, title="Kết luận", lines=[
        "Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công với báo động giả rất thấp và chạy được trên "
        "edge, nhưng cần thêm đặc trưng cho flood giả mạo nguồn.",
        "Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe."]),
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
    L = []
    L.append("# Kịch bản thuyết trình 5 phút (có demo) – DT043\n")
    L.append("**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV "
             "1150080120 – 11CNPM2  ")
    L.append("**Tài liệu dùng:** [slide 17 trang](report/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx) (chiếu 13 "
             "slide chính, các slide 8, 11, 14 để trả lời câu hỏi) + dashboard demo `http://127.0.0.1:8000/`.  ")
    L.append("**Video mẫu để tập theo:** `video/Video_mau_thuyet_trinh_DT043.mp4` – dựng từ CÙNG dòng thời gian với kịch "
             "bản này (script `report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại bên dưới; "
             "video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.\n")
    L.append("## 1. Phân bổ thời gian\n")
    L.append("| Thời điểm | Phần | Slide / màn hình | Thời lượng |")
    L.append("|---|---|---|---|")
    for s in SEGMENTS:
        where = "Dashboard" if s["kind"] == "demo" else f"Slide {s['slide']}"
        name = f"**{s['title']}**" if s["kind"] == "demo" else s["title"]
        L.append(f"| {fmt(s['start'])} – {fmt(s['end'])} | {name} | {where} | {s['end'] - s['start']} s |")
    L.append("")
    L.append("## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)\n")
    L.append("1. Mở PowerShell tại thư mục `DT043`, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo lại), "
             "rồi bật server:")
    L.append("   ```powershell")
    L.append("   Remove-Item db\\dt043.sqlite3 -ErrorAction SilentlyContinue")
    L.append("   .venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000")
    L.append("   ```")
    L.append("   Đợi dòng `Application startup complete`.")
    L.append("2. Mở trình duyệt `http://127.0.0.1:8000/`, kiểm tra góc phải hiện **9 model**.")
    L.append("3. Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và trình "
             "duyệt.")
    L.append("4. Dự phòng: nếu server không chạy, chiếu **Slide 8** (ảnh demo) và đọc kết quả ở mục 5.\n")
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
    for k, v in [
        ("Dữ liệu", "N-BaIoT · 7,06 triệu dòng · 115 đặc trưng · 9 thiết bị · 10 loại tấn công"),
        ("Số lần chạy", "468 (thiết bị × seed × cấu hình), 5 seed cố định"),
        ("B0 (AE Meidan)", "macro-F1 0,706 · TPR 0,822 · FPR 0,0025 (Meidan: FPR 0,007)"),
        ("Isolation Forest", "macro-F1 0,886"),
        ("V1 int8 + hiệu chỉnh ngưỡng", "8.059 tham số · 15,3 KB · macro-F1 0,717 · FPR 0,0016"),
        ("Edge (1 E-core)", "p95 10,8 µs/mẫu · ~103.000 mẫu/s · RAM +4,6 MB"),
        ("MTD (ASP)", "không MTD 0,498 · shuffle 0,409 · diversity 0,437 · kết hợp 0,327"),
        ("Demo mirai/syn (Danmini)", "1989/1989 cửa sổ cảnh báo, cảnh báo high + 2 hành động MTD"),
        ("Demo benign và gafgyt/tcp (Ennio)", "0 cửa sổ cảnh báo"),
    ]:
        L.append(f"| {k} | {v} |")
    L.append("")
    L.append("## 5. Câu hỏi có thể gặp\n")
    L.append("| Câu hỏi | Trả lời ngắn | Slide hỗ trợ |")
    L.append("|---|---|---|")
    for q, a, s in [
        ("Sao không đạt TPR 100% như Meidan?",
         "Em chia theo thời gian có vùng đệm và loại trùng lặp để không rò rỉ; thí nghiệm cố tình cho rò rỉ (E6) làm "
         "FPR \"đẹp giả\" xuống 0,0006, cho thấy cách chia ảnh hưởng lớn đến kết quả. Phần bỏ sót là flood tcp/udp "
         "giả mạo nguồn.", "5, 10"),
        ("Isolation Forest tốt hơn, sao vẫn dùng AE?",
         "Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm "
         "baseline so sánh.", "9, 13"),
        ("Hạ ngưỡng có bắt được tcp/udp không?",
         "Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả "
         "nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí.", "11"),
        ("Vì sao kích thước int8 không giảm còn 25%?",
         "Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%.", "12"),
        ("Kết quả có ổn định không?",
         "Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không "
         "đủ.", "14"),
        ("MTD có tác động mạng thật không?",
         "Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc.", "15"),
    ]:
        L.append(f"| {q} | {a} | {s} |")
    L.append("")
    L.append("## 6. Mẹo trình bày\n")
    L.append("- Tập theo video mẫu 2–3 lần: đến **1:55 phải bắt đầu demo**, đến **3:25 phải quay lại slide**. Nếu chậm, "
             "bỏ bước 6 của demo.")
    L.append("- Khi demo, nói trong lúc chờ kết quả, không im lặng chờ.")
    L.append("- Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.")
    L.append("- Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày và tự thao tác demo.")
    OUT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("đã ghi", OUT_MD)


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
    """Bật backend (CSDL tạm), dùng Playwright thao tác dashboard và quay video 90 s; trả về (đường dẫn, giây bắt đầu)."""
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

            steps = [
                lambda: (point("#health"), time.sleep(3), point("#devices tbody tr")),
                lambda: (scroll("#replay-form"), replay("Danmini_Doorbell", "mirai/syn"), point("#replay-summary")),
                lambda: (scroll("#alerts"), point("#alerts tbody tr"), time.sleep(3), point("#mtd tbody tr")),
                lambda: (scroll("#replay-form"), replay("Ennio_Doorbell", "benign"), point("#replay-summary")),
                lambda: (replay("Ennio_Doorbell", "gafgyt/tcp"), point("#replay-summary")),
                lambda: (scroll("#mtd"), point("#tick"), page.click("#tick"), time.sleep(1.5), point("#mtd tbody tr")),
            ]
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
    build_md()
    if "--md-only" not in sys.argv:
        build_video()
