# Kịch bản thuyết trình ≈ 3:12 (khung 5 phút, có demo) – DT043 · bộ ngắn 8 slide

**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV 1150080120 – 11CNPM2  
**Tài liệu dùng:** [bộ slide ngắn 8 slide](SlideThuyetTrinh_DT043_ngan_1150080120_HoangThanhTra.pptx) (chiếu cả 8 slide; slide 5 có ảnh dashboard, dùng khi server lỗi) + dashboard demo `http://127.0.0.1:8000/`.  
**Video mẫu để tập theo:** `../video/Video_mau_thuyet_trinh_DT043_ngan.mp4` – dựng từ CÙNG dòng thời gian với kịch bản này (script `src/report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại bên dưới; video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.

## 1. Phân bổ thời gian

| Thời điểm | Phần | Slide / màn hình | Thời lượng |
|---|---|---|---|
| 0:00 – 0:12 | Mở đầu | Slide 1 | 12 s |
| 0:12 – 0:30 | Bài toán và mục tiêu | Slide 2 | 18 s |
| 0:30 – 0:50 | Bài báo tham khảo | Slide 3 | 20 s |
| 0:50 – 1:08 | Dữ liệu và phương pháp | Slide 4 | 18 s |
| 1:08 – 1:20 | Hệ thống 4 tầng | Slide 5 | 12 s |
| 1:20 – 2:08 | **DEMO trực tiếp (rút gọn)** | Dashboard | 48 s |
| 2:08 – 2:28 | Kết quả phát hiện và edge | Slide 6 | 20 s |
| 2:28 – 2:46 | Tái lập bài báo | Slide 7 | 18 s |
| 2:46 – 3:12 | Kết luận | Slide 8 | 26 s |

## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)

1. Mở PowerShell tại thư mục `DT043\src`, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo lại), rồi bật server:
   ```powershell
   Remove-Item db\dt043.sqlite3 -ErrorAction SilentlyContinue
   .venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
   ```
   Đợi dòng `Application startup complete`.
2. Mở trình duyệt `http://127.0.0.1:8000/`, kiểm tra góc phải hiện **9 model**.
3. Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và trình duyệt.
4. Dự phòng: nếu server không chạy, chiếu **Slide 5** (ảnh demo) và đọc kết quả ở mục 4.

## 3. Lời thoại theo mốc thời gian (trùng phụ đề trong video)

### 0:00 – Slide 1 · Mở đầu (12 s)
> **[0:00]** Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện IoT nhiễm botnet ngay tại thiết bị biên bằng autoencoder nhẹ.

### 0:12 – Slide 2 · Bài toán và mục tiêu (18 s)
> **[0:12]** IoT dễ bị Mirai và BASHLITE chiếm; bộ phát hiện đặt tại edge nên phải nhỏ và nhanh.
> **[0:20]** Mục tiêu: autoencoder nhẹ chạy tại edge, tái lập bài báo chính, và dùng cảnh báo để kích hoạt MTD.

### 0:30 – Slide 3 · Bài báo tham khảo (20 s)
> **[0:30]** Bài của Masud 2025 đánh giá kết hợp shuffle, diversity, redundancy trên mô hình THARM ba tầng; shuffle cộng diversity tốt nhất.
> **[0:41]** Nhưng bài chỉ mô phỏng, không có bộ phát hiện kích hoạt MTD, nên em làm thêm phần phát hiện bằng autoencoder.

### 0:50 – Slide 4 · Dữ liệu và phương pháp (18 s)
> **[0:50]** N-BaIoT có 7,06 triệu dòng; em loại 158 nghìn dòng trùng và chia theo thời gian có vùng đệm để không rò rỉ.
> **[1:00]** Baseline là autoencoder của Meidan; bản nhẹ V1 chỉ 8 nghìn tham số, lượng tử hóa int8.

### 1:08 – Slide 5 · Hệ thống 4 tầng (12 s)
> **[1:08]** Hệ thống tách bốn tầng: AI, backend, CSDL và dashboard.
> **[1:15]** Bây giờ em demo. (Alt + Tab sang trình duyệt)

### 1:20 – DEMO trực tiếp (48 s)

| Mốc | Thao tác | Lời thoại | Kết quả phải thấy |
|---|---|---|---|
| 1:20 | Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model» | Backend đã nạp 9 model int8, mỗi thiết bị một model. | 9 model, 0 lỗi gói |
| 1:32 | Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại» | Phát lại Mirai SYN flood: 1989 trên 1989 cửa sổ bị cảnh báo. | 1989/1989 cửa sổ cảnh báo |
| 1:44 | Kéo xuống bảng «Cảnh báo» và «Hành động MTD» | Hệ thống tự kích hoạt hai hành động MTD: đổi IP và đổi firmware. | 1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware) |
| 1:56 | Chọn Ennio_Doorbell · gafgyt/tcp → bấm «Phát lại», rồi Alt + Tab về PowerPoint (Slide 6) | Còn flood TCP của BASHLITE thì bị bỏ sót – điểm yếu em phân tích ngay sau đây. | 0 cửa sổ cảnh báo |

### 2:08 – Slide 6 · Kết quả phát hiện và edge (20 s)
> **[2:08]** Kết quả: FPR chỉ 0,0025 nhưng TPR 0,822, vì flood tcp/udp giả mạo nguồn trông giống benign.
> **[2:19]** Bản int8 chỉ 15,3 KB, 10,8 micro-giây mỗi mẫu trên một lõi – đạt tiêu chí edge.

### 2:28 – Slide 7 · Tái lập bài báo (18 s)
> **[2:28]** Tái lập bằng đúng dữ liệu của bài: rủi ro từng máy ảo khớp tới 0,01, 6 trên 7 kết luận đúng; vẽ lại Hình 6, đường diversity khớp cả 7 máy ảo.

### 2:46 – Slide 8 · Kết luận (26 s)
> **[2:46]** RQ5 về edge đạt, RQ1 đến RQ4 không đạt và em giữ nguyên tiêu chí.
> **[2:52]** Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công, báo động giả thấp, chạy được ở edge; cần thêm đặc trưng cho flood giả mạo nguồn.
> **[3:05]** Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe.

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
| Tái lập paper chính | rủi ro mức máy ảo khớp ±0,01 · đường tấn công −0,8% · chọn V5 như paper · 6/7 kết luận định tính (topology Hình 3; Definition 2: 3/7) |
| Chạy lại Hình 6 (bài chính) | diversity khớp 7/7 máy ảo (lệch ≤ 5%) · shuffle, S+D khớp ở V5 |
| Demo mirai/syn (Danmini) | 1989/1989 cửa sổ cảnh báo, cảnh báo high + 2 hành động MTD |
| Demo benign và gafgyt/tcp (Ennio) | 0 cửa sổ cảnh báo |

## 5. Câu hỏi có thể gặp

| Câu hỏi | Trả lời ngắn | Slide hỗ trợ |
|---|---|---|
| Sao không đạt TPR 100% như Meidan? | Em chia theo thời gian có vùng đệm và loại trùng lặp để không rò rỉ; thí nghiệm cố tình cho rò rỉ (E6) làm FPR "đẹp giả" xuống 0,0006, cho thấy cách chia ảnh hưởng lớn đến kết quả. Phần bỏ sót là flood tcp/udp giả mạo nguồn. | 6 |
| Isolation Forest tốt hơn, sao vẫn dùng AE? | Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm baseline so sánh. | 6 |
| Hạ ngưỡng có bắt được tcp/udp không? | Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí. | 6 |
| Vì sao kích thước int8 không giảm còn 25%? | Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%. | 6, 8 |
| Kết quả có ổn định không? | Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không đủ. | 8 |
| MTD có tác động mạng thật không? | Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc. | 3, 5 |
| Tái lập paper chính được đến đâu? | Dùng đúng 18 CVE hệ điều hành, 14 CVE dịch vụ và 8 máy ảo của paper: rủi ro mức máy ảo khớp ±0,01, đường tấn công lệch −0,8%, độ trung tâm trên đồ thị có hướng chọn V5 như paper. Với topology Hình 3 tái lập 6/7 kết luận định tính, với Definition 2 chỉ 3/7. Tổng rủi ro toàn mạng không khớp vì paper cắt danh sách cạnh và công thức in ra mâu thuẫn. | 7 |
| Bài báo tham khảo giải quyết bài toán gì, hạn chế ở đâu? | Masud 2025 đánh giá việc kết hợp shuffle, diversity, redundancy bằng mô hình THARM ba tầng; kết luận shuffle + diversity tốt nhất. Hạn chế: chỉ mô phỏng, chỉ MTD theo thời gian, không có bộ phát hiện kích hoạt MTD, không công bố mã. Bài tham chiếu Meidan 2018 chia dữ liệu một lần và không đo trên edge. | 3 |
| Em làm bài này theo quy trình nào? | Đọc bài báo → lập kế hoạch → tải dữ liệu có checksum → làm sạch, EDA → viết pipeline kèm test → chốt tiêu chí trước khi chạy → chạy 468 lần → dựng hệ thống 4 tầng → tổng hợp thống kê, báo cáo → tái lập bài chính (E11). | 2, 4 |
| Biểu đồ chạy lại có giống bài báo không? | Em vẽ lại đúng dạng Hình 6, Hình 7 của bài chính và Hình 2 của Meidan. Hình 6: diversity khớp 7/7 máy ảo, shuffle và S+D khớp ở V5, redundancy cao hơn. Hình 7 không khớp vì topology bài công bố chỉ có 5 đường và bài không nêu cách tính ASP đường. Hình 2 của Meidan: FPR khớp, TPR thấp hơn do flood tcp/udp. | 7 |

## 6. Mẹo trình bày

- Tập theo video mẫu 2–3 lần: đến **1:20 phải bắt đầu demo**, đến **2:08 phải quay lại slide**, kết thúc khoảng **3:12** – còn ~108 s dự phòng trong khung 5 phút. Nếu chậm, ở bước cuối của demo chỉ nói một câu vì slide 6 sẽ giải thích lại.
- Nếu thầy hỏi về MTD time-based: kéo xuống bảng MTD trên dashboard, bấm «Chạy chu kỳ time-based».
- Khi demo, nói trong lúc chờ kết quả, không im lặng chờ.
- Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.
- Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày và tự thao tác demo.
