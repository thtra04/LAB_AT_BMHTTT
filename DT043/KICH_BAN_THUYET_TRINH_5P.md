# Kịch bản thuyết trình 5 phút (có demo) – DT043

**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV 1150080120 – 11CNPM2  
**Tài liệu dùng:** [slide 17 trang](report/SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx) (chiếu 13 slide chính, các slide 8, 11, 14 để trả lời câu hỏi) + dashboard demo `http://127.0.0.1:8000/`.  
**Video mẫu để tập theo:** `video/Video_mau_thuyet_trinh_DT043.mp4` – dựng từ CÙNG dòng thời gian với kịch bản này (script `report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại bên dưới; video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.

## 1. Phân bổ thời gian

| Thời điểm | Phần | Slide / màn hình | Thời lượng |
|---|---|---|---|
| 0:00 – 0:20 | Mở đầu | Slide 1 | 20 s |
| 0:20 – 0:50 | Bài toán và câu hỏi nghiên cứu | Slide 2 | 30 s |
| 0:50 – 1:10 | Paper chính lệch chủ đề → hai track | Slide 3 | 20 s |
| 1:10 – 1:20 | Dữ liệu N-BaIoT | Slide 4 | 10 s |
| 1:20 – 1:32 | Chống rò rỉ dữ liệu | Slide 5 | 12 s |
| 1:32 – 1:40 | Pipeline và các mô hình | Slide 6 | 8 s |
| 1:40 – 1:55 | Kiến trúc 4 tầng AI · BE · DB · FE | Slide 7 | 15 s |
| 1:55 – 3:25 | **DEMO trực tiếp** | Dashboard | 90 s |
| 3:25 – 3:40 | Kết quả tổng quan | Slide 9 | 15 s |
| 3:40 – 3:55 | Lỗi chính: flood BASHLITE tcp/udp | Slide 10 | 15 s |
| 3:55 – 4:07 | Lượng tử hóa int8 | Slide 12 | 12 s |
| 4:07 – 4:20 | Edge benchmark | Slide 13 | 13 s |
| 4:20 – 4:35 | Moving Target Defence | Slide 15 | 15 s |
| 4:35 – 4:47 | Đối chiếu tiêu chí | Slide 16 | 12 s |
| 4:47 – 5:00 | Kết luận | Slide 17 | 13 s |

## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)

1. Mở PowerShell tại thư mục `DT043`, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo lại), rồi bật server:
   ```powershell
   Remove-Item db\dt043.sqlite3 -ErrorAction SilentlyContinue
   .venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
   ```
   Đợi dòng `Application startup complete`.
2. Mở trình duyệt `http://127.0.0.1:8000/`, kiểm tra góc phải hiện **9 model**.
3. Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và trình duyệt.
4. Dự phòng: nếu server không chạy, chiếu **Slide 8** (ảnh demo) và đọc kết quả ở mục 5.

## 3. Lời thoại theo mốc thời gian (trùng phụ đề trong video)

### 0:00 – Slide 1 · Mở đầu (20 s)
> **[0:00]** Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện thiết bị IoT bị nhiễm botnet ngay tại thiết bị biên.
> **[0:08]** Em dùng autoencoder huấn luyện riêng cho từng thiết bị, thu nhỏ và lượng tử hóa int8 để chạy trên phần cứng yếu, và nối với hướng Moving Target Defence của paper chính.

### 0:20 – Slide 2 · Bài toán và câu hỏi nghiên cứu (30 s)
> **[0:20]** Thiết bị IoT dùng mật khẩu mặc định, ít được vá, nên Mirai và BASHLITE chiếm hàng loạt để DDoS.
> **[0:29]** Phát hiện ở trung tâm thì chậm và tốn băng thông, nên em đặt bộ phát hiện ngay tại edge.
> **[0:37]** Em đặt sáu câu hỏi nghiên cứu; mỗi câu có tiêu chí định lượng được chốt và lưu checksum trước khi chạy, để không thể chỉnh tiêu chí theo kết quả.

### 0:50 – Slide 3 · Paper chính lệch chủ đề → hai track (20 s)
> **[0:50]** Paper chính của Masud và cộng sự năm 2025 nói về Moving Target Defence, không dùng autoencoder hay N-BaIoT.
> **[0:58]** Vì vậy em chia hai track: track A là lõi phát hiện bằng autoencoder theo Meidan; track B tái lập xu hướng MTD và dùng cảnh báo của autoencoder để kích hoạt MTD.

### 1:10 – Slide 4 · Dữ liệu N-BaIoT (10 s)
> **[1:10]** Dữ liệu N-BaIoT có 7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; nhiều dòng trùng lặp và mất cân bằng nặng.

### 1:20 – Slide 5 · Chống rò rỉ dữ liệu (12 s)
> **[1:20]** Các dòng liền kề gần giống nhau nên chia ngẫu nhiên sẽ rò rỉ. Em chia theo thời gian có vùng đệm 500 dòng, chỉ fit scaler trên tập train, và mỗi biện pháp đều có unit test.

### 1:32 – Slide 6 · Pipeline và các mô hình (8 s)
> **[1:32]** Em so sánh autoencoder của Meidan, model chung, Isolation Forest và bản V1 nhẹ chỉ 8 nghìn tham số, lượng tử hóa int8 rồi hiệu chỉnh lại ngưỡng.

### 1:40 – Slide 7 · Kiến trúc 4 tầng AI · BE · DB · FE (15 s)
> **[1:40]** Hệ thống tách bốn tầng: AI xuất gói model có checksum SHA-256; backend FastAPI nạp gói và từ chối nếu bị sửa dù chỉ một byte.
> **[1:48]** CSDL SQLite lưu cảnh báo và hành động MTD; frontend là dashboard. Bây giờ em demo trực tiếp. (Alt + Tab sang trình duyệt)

### 1:55 – DEMO trực tiếp (90 s)

| Mốc | Thao tác | Lời thoại | Kết quả phải thấy |
|---|---|---|---|
| 1:55 | Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model» | Backend đã nạp 9 model, mỗi thiết bị một model V1 int8 khoảng 15 KB, kèm ngưỡng tr* và cửa sổ ws* riêng. | 9 model, 0 lỗi gói |
| 2:10 | Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại» | Em phát lại 2000 mẫu tấn công Mirai SYN flood từ dữ liệu công khai: MSE tái tạo vượt hẳn ngưỡng, 1989/1989 cửa sổ bị cảnh báo. | 1989/1989 cửa sổ cảnh báo, đường MSE nằm trên ngưỡng |
| 2:25 | Kéo xuống bảng «Cảnh báo» và «Hành động MTD» | Hệ thống sinh cảnh báo mức high và tự kích hoạt hai hành động MTD kiểu event-based: xáo trộn IP và đổi firmware, ghi vào CSDL. | 1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware) |
| 2:40 | Kéo lên, chọn Ennio_Doorbell · benign → bấm «Phát lại» | Với lưu lượng bình thường của Ennio, không có cửa sổ nào bị cảnh báo, tức là không báo động giả. | 0 cửa sổ cảnh báo |
| 2:55 | Giữ Ennio_Doorbell, chọn gafgyt/tcp → bấm «Phát lại» | Còn đây là điểm yếu em không che giấu: flood TCP của BASHLITE bị bỏ sót, đúng như phân tích lỗi ở phần sau. | 0 cửa sổ cảnh báo |
| 3:10 | Kéo xuống bảng MTD, bấm «Chạy chu kỳ time-based» | Vì có tấn công bị bỏ sót, em giữ thêm MTD theo chu kỳ thời gian làm lưới an toàn. Em quay lại slide. (Alt + Tab về PowerPoint, Slide 9) | thêm dòng MTD kích hoạt time-based |

### 3:25 – Slide 9 · Kết quả tổng quan (15 s)
> **[3:25]** Trên 468 lần chạy, autoencoder per-device có FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822, không đạt 100% như paper.

### 3:40 – Slide 10 · Lỗi chính: flood BASHLITE tcp/udp (15 s)
> **[3:40]** Kiểm tra trên dữ liệu thô: toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE.
> **[3:46]** Nguồn bị giả mạo liên tục nên mỗi gói trông như luồng mới, giống benign; tám loại tấn công còn lại có recall gần bằng 1.

### 3:55 – Slide 12 · Lượng tử hóa int8 (12 s)
> **[3:55]** Bản int8 chỉ còn 15,3 KB; nếu giữ ngưỡng fp32 thì sai lệch, nên em hiệu chỉnh lại ngưỡng trên tập DSopt.

### 4:07 – Slide 13 · Edge benchmark (13 s)
> **[4:07]** Trên một lõi E-core: p95 chỉ 10,8 micro-giây mỗi mẫu, khoảng 103 nghìn mẫu mỗi giây, RAM tăng 4,6 MB – thừa sức chạy tại edge.

### 4:20 – Slide 15 · Moving Target Defence (15 s)
> **[4:20]** Với mô hình HARM rút gọn, xác suất tấn công thành công giảm từ 0,498 xuống 0,327 khi kết hợp shuffle và diversity, khớp xu hướng paper chính.
> **[4:29]** MTD lai kích hoạt bởi autoencoder có thời gian lộ diện thấp hơn time-based ở cùng chi phí.

### 4:35 – Slide 16 · Đối chiếu tiêu chí (12 s)
> **[4:35]** Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt với biên rất lớn; RQ1 đến RQ4 không đạt, và em giữ nguyên tiêu chí, không chỉnh sau khi có kết quả.

### 4:47 – Slide 17 · Kết luận (13 s)
> **[4:47]** Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công với báo động giả rất thấp và chạy được trên edge, nhưng cần thêm đặc trưng cho flood giả mạo nguồn.
> **[4:55]** Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe.

## 4. Số liệu cần nhớ

| Nội dung | Giá trị |
|---|---|
| Dữ liệu | N-BaIoT · 7,06 triệu dòng · 115 đặc trưng · 9 thiết bị · 10 loại tấn công |
| Số lần chạy | 468 (thiết bị × seed × cấu hình), 5 seed cố định |
| B0 (AE Meidan) | macro-F1 0,706 · TPR 0,822 · FPR 0,0025 (Meidan: FPR 0,007) |
| Isolation Forest | macro-F1 0,886 |
| V1 int8 + hiệu chỉnh ngưỡng | 8.059 tham số · 15,3 KB · macro-F1 0,717 · FPR 0,0016 |
| Edge (1 E-core) | p95 10,8 µs/mẫu · ~103.000 mẫu/s · RAM +4,6 MB |
| MTD (ASP) | không MTD 0,498 · shuffle 0,409 · diversity 0,437 · kết hợp 0,327 |
| Demo mirai/syn (Danmini) | 1989/1989 cửa sổ cảnh báo, cảnh báo high + 2 hành động MTD |
| Demo benign và gafgyt/tcp (Ennio) | 0 cửa sổ cảnh báo |

## 5. Câu hỏi có thể gặp

| Câu hỏi | Trả lời ngắn | Slide hỗ trợ |
|---|---|---|
| Sao không đạt TPR 100% như Meidan? | Em chia theo thời gian có vùng đệm và loại trùng lặp để không rò rỉ; thí nghiệm cố tình cho rò rỉ (E6) làm FPR "đẹp giả" xuống 0,0006, cho thấy cách chia ảnh hưởng lớn đến kết quả. Phần bỏ sót là flood tcp/udp giả mạo nguồn. | 5, 10 |
| Isolation Forest tốt hơn, sao vẫn dùng AE? | Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm baseline so sánh. | 9, 13 |
| Hạ ngưỡng có bắt được tcp/udp không? | Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí. | 11 |
| Vì sao kích thước int8 không giảm còn 25%? | Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%. | 12 |
| Kết quả có ổn định không? | Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không đủ. | 14 |
| MTD có tác động mạng thật không? | Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc. | 15 |

## 6. Mẹo trình bày

- Tập theo video mẫu 2–3 lần: đến **1:55 phải bắt đầu demo**, đến **3:25 phải quay lại slide**. Nếu chậm, bỏ bước 6 của demo.
- Khi demo, nói trong lúc chờ kết quả, không im lặng chờ.
- Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.
- Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày và tự thao tác demo.
