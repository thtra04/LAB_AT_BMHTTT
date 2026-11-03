# Kịch bản thuyết trình ≈ 4:50 (khung 5 phút, có demo) – DT043 · bộ rút gọn 23 slide (13 chính + 10 phụ lục)

**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV 1150080120 – 11CNPM2  
**Tài liệu dùng:** [bộ slide rút gọn 23 slide (13 chính + 10 phụ lục)](SlideThuyetTrinh_DT043_10slide_1150080120_HoangThanhTra.pptx) (chiếu slide 1–7 và 9–13; slide 8 là ảnh demo, chỉ chiếu khi server lỗi; phụ lục 14–23 để trả lời câu hỏi) + dashboard demo `http://127.0.0.1:8000/`.  
**Video mẫu để tập theo:** `../video/Video_mau_thuyet_trinh_DT043_10slide.mp4` – dựng từ CÙNG dòng thời gian với kịch bản này (script `src/report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại bên dưới; video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.

## 1. Phân bổ thời gian

| Thời điểm | Phần | Slide / màn hình | Thời lượng |
|---|---|---|---|
| 0:00 – 0:15 | Mở đầu | Slide 1 | 15 s |
| 0:15 – 0:40 | Bài toán và câu hỏi nghiên cứu | Slide 2 | 25 s |
| 0:40 – 0:55 | Bài báo tham khảo: bài toán | Slide 3 | 15 s |
| 0:55 – 1:07 | Phương pháp của bài báo | Slide 4 | 12 s |
| 1:07 – 1:22 | Kết quả, hạn chế của bài báo → hai track | Slide 5 | 15 s |
| 1:22 – 1:40 | Dữ liệu N-BaIoT và chống rò rỉ | Slide 6 | 18 s |
| 1:40 – 1:59 | Mô hình so sánh và hệ thống 4 tầng | Slide 7 | 19 s |
| 1:59 – 3:14 | **DEMO trực tiếp** | Dashboard | 75 s |
| 3:14 – 3:34 | Kết quả: FPR thấp, lỗi ở flood tcp/udp | Slide 9 | 20 s |
| 3:34 – 3:50 | Lượng tử hóa int8 và edge benchmark | Slide 10 | 16 s |
| 3:50 – 4:10 | MTD: tái lập paper chính | Slide 11 | 20 s |
| 4:10 – 4:22 | Chạy lại Hình 6 của bài báo | Slide 12 | 12 s |
| 4:22 – 4:50 | Đối chiếu tiêu chí và kết luận | Slide 13 | 28 s |

## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)

1. Mở PowerShell tại thư mục `DT043\src`, xóa CSDL demo cũ để bảng cảnh báo và MTD trống (file tự tạo lại), rồi bật server:
   ```powershell
   Remove-Item db\dt043.sqlite3 -ErrorAction SilentlyContinue
   .venv\Scripts\python -m uvicorn backend.app.main:app --port 8000
   ```
   Đợi dòng `Application startup complete`.
2. Mở trình duyệt `http://127.0.0.1:8000/`, kiểm tra góc phải hiện **9 model**.
3. Mở PowerPoint ở chế độ trình chiếu, để sẵn Slide 1. Dùng **Alt + Tab** để chuyển giữa slide và trình duyệt.
4. Dự phòng: nếu server không chạy, chiếu **Slide 8** (ảnh demo) và đọc kết quả ở mục 4.

## 3. Lời thoại theo mốc thời gian (trùng phụ đề trong video)

### 0:00 – Slide 1 · Mở đầu (15 s)
> **[0:00]** Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện thiết bị IoT nhiễm botnet ngay tại thiết bị biên, bằng autoencoder nhẹ lượng tử hóa int8, kết hợp Moving Target Defence.

### 0:15 – Slide 2 · Bài toán và câu hỏi nghiên cứu (25 s)
> **[0:15]** Thiết bị IoT dùng mật khẩu mặc định, ít được vá, nên Mirai và BASHLITE chiếm hàng loạt để DDoS.
> **[0:22]** Phát hiện ở trung tâm thì chậm và tốn băng thông, nên em đặt bộ phát hiện ngay tại edge.
> **[0:29]** Em đặt sáu câu hỏi nghiên cứu, tiêu chí định lượng được chốt và lưu checksum trước khi chạy, để không thể chỉnh tiêu chí theo kết quả.

### 0:40 – Slide 3 · Bài báo tham khảo: bài toán (15 s)
> **[0:40]** Bài báo tham khảo chính là của Masud và cộng sự, 2025: Moving Target Defence liên tục thay đổi bề mặt tấn công, nhưng chưa có đánh giá khi kết hợp nhiều kỹ thuật MTD về rủi ro, chi phí và tài nguyên.

### 0:55 – Slide 4 · Phương pháp của bài báo (12 s)
> **[0:55]** Bài dùng mô hình đồ thị tấn công ba tầng THARM trên 8 máy ảo và 32 CVE, áp shuffle, diversity, redundancy theo chu kỳ 10 phút.

### 1:07 – Slide 5 · Kết quả, hạn chế của bài báo → hai track (15 s)
> **[1:07]** Kết quả: kết hợp shuffle và diversity cho rủi ro thấp nhất; nhưng bài chỉ mô phỏng, không có bộ phát hiện kích hoạt MTD.
> **[1:14]** Nên em chia hai track: A phát hiện bằng autoencoder theo Meidan; B tái lập THARM và dùng cảnh báo của autoencoder để kích hoạt MTD.

### 1:22 – Slide 6 · Dữ liệu N-BaIoT và chống rò rỉ (18 s)
> **[1:22]** Dữ liệu N-BaIoT có 7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; em loại 158 nghìn dòng trùng lặp.
> **[1:29]** Benign chia theo thời gian có vùng đệm 500 dòng, scaler chỉ fit trên tập train; nếu cố tình chia ngẫu nhiên thì FPR đẹp giả xuống 0,0006.

### 1:40 – Slide 7 · Mô hình so sánh và hệ thống 4 tầng (19 s)
> **[1:40]** Em so sánh autoencoder Meidan, model chung, Isolation Forest và bản V1 chỉ 8 nghìn tham số, lượng tử hóa int8.
> **[1:48]** Hệ thống tách bốn tầng AI, backend, CSDL, dashboard; backend từ chối gói model bị sửa, có 56 test tự động.
> **[1:56]** Bây giờ em demo. (Alt + Tab sang trình duyệt)

### 1:59 – DEMO trực tiếp (75 s)

| Mốc | Thao tác | Lời thoại | Kết quả phải thấy |
|---|---|---|---|
| 1:59 | Chỉ vào ô trạng thái góc phải và bảng «Thiết bị & model» | Backend đã nạp 9 model, mỗi thiết bị một model V1 int8 khoảng 15 KB, kèm ngưỡng riêng. | 9 model, 0 lỗi gói |
| 2:14 | Chọn Danmini_Doorbell · mirai/syn · 2000 mẫu → bấm «Phát lại» | Em phát lại 2000 mẫu Mirai SYN flood: MSE vượt hẳn ngưỡng, 1989/1989 cửa sổ bị cảnh báo. | 1989/1989 cửa sổ cảnh báo, đường MSE nằm trên ngưỡng |
| 2:29 | Kéo xuống bảng «Cảnh báo» và «Hành động MTD» | Hệ thống sinh cảnh báo mức high và tự kích hoạt hai hành động MTD: xáo trộn IP và đổi firmware. | 1 cảnh báo high; 2 dòng MTD (shuffle IP, đổi firmware) |
| 2:44 | Kéo lên, chọn Ennio_Doorbell · benign → bấm «Phát lại» | Với lưu lượng bình thường của Ennio, không có cửa sổ nào bị cảnh báo, tức là không báo động giả. | 0 cửa sổ cảnh báo |
| 2:59 | Giữ Ennio_Doorbell, chọn gafgyt/tcp → bấm «Phát lại», rồi Alt + Tab về PowerPoint (Slide 9) | Còn đây là điểm yếu em không che giấu: flood TCP của BASHLITE bị bỏ sót. Em quay lại slide. | 0 cửa sổ cảnh báo |

### 3:14 – Slide 9 · Kết quả: FPR thấp, lỗi ở flood tcp/udp (20 s)
> **[3:14]** Trên 468 lần chạy, autoencoder per-device có FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822.
> **[3:22]** Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE: nguồn bị giả mạo nên mỗi gói như luồng mới; tám loại còn lại có recall gần bằng 1.

### 3:34 – Slide 10 · Lượng tử hóa int8 và edge benchmark (16 s)
> **[3:34]** Bản int8 chỉ 15,3 KB, ngưỡng được hiệu chỉnh lại trên DSopt.
> **[3:40]** Trên một lõi E-core, p95 chỉ 10,8 micro-giây mỗi mẫu, khoảng 103 nghìn mẫu mỗi giây – thừa sức chạy tại edge.

### 3:50 – Slide 11 · MTD: tái lập paper chính (20 s)
> **[3:50]** Em tái lập paper bằng đúng CVE và topology của paper: rủi ro mức máy ảo khớp sai số 0,01, đường tấn công lệch 0,8%, 6 trên 7 kết luận tái lập được.
> **[4:03]** Kết hợp shuffle và diversity giảm xác suất tấn công thành công từ 0,498 xuống 0,327.

### 4:10 – Slide 12 · Chạy lại Hình 6 của bài báo (12 s)
> **[4:10]** Em chạy lại đúng Hình 6 của bài, áp từng kỹ thuật MTD lên từng máy ảo: diversity khớp cả 7 máy ảo, lệch dưới 5%; shuffle chỉ khớp ở V5 vì bài chỉ nêu host đích của V5.

### 4:22 – Slide 13 · Đối chiếu tiêu chí và kết luận (28 s)
> **[4:22]** Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt; RQ1 đến RQ4 không đạt, và em giữ nguyên tiêu chí, không chỉnh sau khi có kết quả.
> **[4:32]** Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công, báo động giả thấp, chạy được ở edge; cần thêm đặc trưng cho flood giả mạo nguồn.
> **[4:43]** Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe.

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
| Sao không đạt TPR 100% như Meidan? | Em chia theo thời gian có vùng đệm và loại trùng lặp để không rò rỉ; thí nghiệm cố tình cho rò rỉ (E6) làm FPR "đẹp giả" xuống 0,0006, cho thấy cách chia ảnh hưởng lớn đến kết quả. Phần bỏ sót là flood tcp/udp giả mạo nguồn. | 6, 9, 19, 20 |
| Isolation Forest tốt hơn, sao vẫn dùng AE? | Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm baseline so sánh. | 9, 10, 20 |
| Hạ ngưỡng có bắt được tcp/udp không? | Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí. | 9 |
| Vì sao kích thước int8 không giảm còn 25%? | Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%. | 10 |
| Kết quả có ổn định không? | Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không đủ. | 13 |
| MTD có tác động mạng thật không? | Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc. | 11, 23 |
| Tái lập paper chính được đến đâu? | Dùng đúng 18 CVE hệ điều hành, 14 CVE dịch vụ và 8 máy ảo của paper: rủi ro mức máy ảo khớp ±0,01, đường tấn công lệch −0,8%, độ trung tâm trên đồ thị có hướng chọn V5 như paper. Với topology Hình 3 tái lập 6/7 kết luận định tính, với Definition 2 chỉ 3/7. Tổng rủi ro toàn mạng không khớp vì paper cắt danh sách cạnh và công thức in ra mâu thuẫn. | 11, 12, 18, 21 |
| Bài báo tham khảo giải quyết bài toán gì, hạn chế ở đâu? | Masud 2025 đánh giá việc kết hợp shuffle, diversity, redundancy bằng mô hình THARM ba tầng; kết luận shuffle + diversity tốt nhất. Hạn chế: chỉ mô phỏng, chỉ MTD theo thời gian, không có bộ phát hiện kích hoạt MTD, không công bố mã. Bài tham chiếu Meidan 2018 chia dữ liệu một lần và không đo trên edge. | 3–5, 14 |
| Em làm bài này theo quy trình nào? | Đọc bài báo → lập kế hoạch → tải dữ liệu có checksum → làm sạch, EDA → viết pipeline kèm test → chốt tiêu chí trước khi chạy → chạy 468 lần → dựng hệ thống 4 tầng → tổng hợp thống kê, báo cáo → tái lập bài chính (E11). | 15, 17 |
| Biểu đồ chạy lại có giống bài báo không? | Em vẽ lại đúng dạng Hình 6, Hình 7 của bài chính và Hình 2 của Meidan. Hình 6: diversity khớp 7/7 máy ảo, shuffle và S+D khớp ở V5, redundancy cao hơn. Hình 7 không khớp vì topology bài công bố chỉ có 5 đường và bài không nêu cách tính ASP đường. Hình 2 của Meidan: FPR khớp, TPR thấp hơn do flood tcp/udp. | 12, 20, 22 |

## 6. Mẹo trình bày

- Tập theo video mẫu 2–3 lần: đến **1:59 phải bắt đầu demo**, đến **3:14 phải quay lại slide**, kết thúc khoảng **4:50** – còn ~10 s dự phòng trong khung 5 phút. Nếu chậm, ở bước cuối của demo chỉ nói một câu vì slide 9 sẽ giải thích lại.
- Nếu thầy hỏi về MTD time-based: kéo xuống bảng MTD trên dashboard, bấm «Chạy chu kỳ time-based».
- Khi demo, nói trong lúc chờ kết quả, không im lặng chờ.
- Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.
- Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày và tự thao tác demo.
