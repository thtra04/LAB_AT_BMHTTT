# Kịch bản thuyết trình ≈ 4:30 (không demo trực tiếp) – DT043 · bộ 4'30 không demo, 26 slide (16 chính + 10 phụ lục)

**Đề tài:** Phát hiện botnet IoT bằng autoencoder nhẹ · **Người trình bày:** Hoàng Thanh Trà – MSSV 1150080120 – 11CNPM2  
**Tài liệu dùng:** [bộ slide 4'30 không demo, 26 slide (16 chính + 10 phụ lục)](SlideThuyetTrinh_DT043_4p30_1150080120_HoangThanhTra.pptx) (chiếu lần lượt slide 1–16 theo 5 phần: phân tích bài báo (2–4), các bước làm bài – mỗi bước có hình chạy trong notebook và kết quả (5–11), kết quả (12–13), so sánh với bài báo (14–15), dự định làm tiếp (16); phụ lục 17–26 để trả lời câu hỏi).  
**Video mẫu để tập theo:** `../video/Video_mau_thuyet_trinh_DT043_4p30.mp4` – dựng từ CÙNG dòng thời gian với kịch bản này (script `src/report/build_demo_video.py`), phụ đề trong video trùng từng chữ với lời thoại bên dưới; video không có tiếng, bạn đọc theo phụ đề và mốc giờ ở góc phải.

## 1. Phân bổ thời gian

| Thời điểm | Phần | Slide / màn hình | Thời lượng |
|---|---|---|---|
| 0:00 – 0:24 | Mở đầu | Slide 1 | 24 s |
| 0:24 – 0:42 | Bài báo tham khảo: bài toán | Slide 2 | 18 s |
| 0:42 – 0:53 | Phương pháp của bài báo | Slide 3 | 11 s |
| 0:53 – 1:15 | Kết quả, hạn chế của bài báo → hai track | Slide 4 | 22 s |
| 1:15 – 1:28 | Bước 1–2: đọc bài báo, lập kế hoạch | Slide 5 | 13 s |
| 1:28 – 1:43 | Bước 3–4: tải dữ liệu, làm sạch, EDA | Slide 6 | 15 s |
| 1:43 – 2:03 | Bước 5: chia chống rò rỉ, huấn luyện AE, chọn ngưỡng | Slide 7 | 20 s |
| 2:03 – 2:18 | Bước 6–7: chốt tiêu chí, chạy 468 lần | Slide 8 | 15 s |
| 2:18 – 2:28 | Bước 7: lượng tử hóa int8, đo trên edge | Slide 9 | 10 s |
| 2:28 – 2:45 | Bước 8–9: hệ thống 4 tầng, MTD lai | Slide 10 | 17 s |
| 2:45 – 2:54 | Bước 10: tái lập bài báo chính | Slide 11 | 9 s |
| 2:54 – 3:07 | Kết quả: FPR thấp, lỗi ở flood tcp/udp | Slide 12 | 13 s |
| 3:07 – 3:19 | Đối chiếu 6 câu hỏi nghiên cứu | Slide 13 | 12 s |
| 3:19 – 3:39 | So sánh với Meidan 2018 | Slide 14 | 20 s |
| 3:39 – 4:00 | So sánh với Masud 2025 | Slide 15 | 21 s |
| 4:00 – 4:30 | Kết luận và dự định làm tiếp | Slide 16 | 30 s |

## 2. Chuẩn bị trước khi lên trình bày (≈ 5 phút trước)

1. Mở PowerPoint ở chế độ trình chiếu (F5), để sẵn Slide 1; chỉ dùng phím → để chuyển slide, không cần bật server hay trình duyệt.
2. Bật **Presenter View** để thấy ghi chú lời thoại dưới mỗi slide.
3. Slide 5–11 là từng bước làm bài, mỗi slide có hình chạy trong notebook: nói «Làm gì» rồi chỉ vào hình khi nói «Kết quả».

## 3. Lời thoại theo mốc thời gian (trùng phụ đề trong video)

### 0:00 – Slide 1 · Mở đầu (24 s)
> **[0:00]** Em chào thầy và các bạn. Em là Hoàng Thanh Trà, đề tài DT043: phát hiện IoT nhiễm botnet ngay tại thiết bị biên bằng autoencoder nhẹ, kết hợp Moving Target Defence.
> **[0:14]** Em trình bày năm phần: phân tích bài báo, các bước làm bài, kết quả, so sánh với bài báo và dự định làm tiếp.

### 0:24 – Slide 2 · Bài báo tham khảo: bài toán (18 s)
> **[0:24]** Bài báo tham khảo chính là của Masud và cộng sự, 2025: Moving Target Defence liên tục thay đổi bề mặt tấn công, nhưng chưa có đánh giá khi kết hợp nhiều kỹ thuật MTD về rủi ro, chi phí và tài nguyên.

### 0:42 – Slide 3 · Phương pháp của bài báo (11 s)
> **[0:42]** Bài dùng mô hình đồ thị tấn công ba tầng THARM trên 8 máy ảo và 32 CVE, áp shuffle, diversity, redundancy theo chu kỳ 10 phút.

### 0:53 – Slide 4 · Kết quả, hạn chế của bài báo → hai track (22 s)
> **[0:53]** Kết quả: kết hợp shuffle và diversity cho rủi ro thấp nhất; nhưng bài chỉ mô phỏng, không có bộ phát hiện kích hoạt MTD.
> **[1:04]** Nên em chia hai track: A phát hiện bằng autoencoder theo Meidan; B tái lập THARM và dùng cảnh báo của autoencoder để kích hoạt MTD.

### 1:15 – Slide 5 · Bước 1–2: đọc bài báo, lập kế hoạch (13 s)
> **[1:15]** Bước một và hai: em đọc hai bài báo, thấy bài chính không có bộ phát hiện nên chia hai track, rồi đặt sáu câu hỏi nghiên cứu và mười một thí nghiệm.

### 1:28 – Slide 6 · Bước 3–4: tải dữ liệu, làm sạch, EDA (15 s)
> **[1:28]** Bước ba và bốn: tải N-BaIoT, 107 file khớp checksum, 7,06 triệu dòng; em loại 158 nghìn dòng trùng.
> **[1:37]** Dữ liệu mất cân bằng nặng nên em dùng macro-F1 và FPR thay cho accuracy.

### 1:43 – Slide 7 · Bước 5: chia chống rò rỉ, huấn luyện AE, chọn ngưỡng (20 s)
> **[1:43]** Bước năm: chia benign theo thời gian có vùng đệm, huấn luyện autoencoder trên benign, ngưỡng bằng trung bình cộng độ lệch chuẩn của lỗi tái tạo.
> **[1:56]** Hình cho thấy flood tcp và udp cũng nằm dưới ngưỡng – đây là lỗi bỏ sót chính.

### 2:03 – Slide 8 · Bước 6–7: chốt tiêu chí, chạy 468 lần (15 s)
> **[2:03]** Bước sáu và bảy: chốt tiêu chí trước, rồi chạy 468 lần.
> **[2:08]** Tám loại tấn công có recall gần bằng 1, chỉ tcp và udp thấp; kết quả dao động theo seed nên phải chạy nhiều lần.

### 2:18 – Slide 9 · Bước 7: lượng tử hóa int8, đo trên edge (10 s)
> **[2:18]** Lượng tử hóa int8: model V1 chỉ 15,3 KB, macro-F1 giảm nhẹ 0,028; trên một lõi E-core mất 10,8 micro-giây mỗi mẫu.

### 2:28 – Slide 10 · Bước 8–9: hệ thống 4 tầng, MTD lai (17 s)
> **[2:28]** Bước tám và chín: dựng hệ thống bốn tầng; phát lại Mirai thì 1989 trên 1989 cửa sổ bị cảnh báo và tự kích hoạt MTD.
> **[2:38]** Biểu đồ bên phải: MTD lai đạt cùng mức lộ diện với số lần đổi ít hơn khoảng 55%.

### 2:45 – Slide 11 · Bước 10: tái lập bài báo chính (9 s)
> **[2:45]** Bước mười: tái lập bài chính bằng đúng dữ liệu của bài, vẽ lại Hình 6 và dò công thức bài không in rõ.

### 2:54 – Slide 12 · Kết quả: FPR thấp, lỗi ở flood tcp/udp (13 s)
> **[2:54]** Tổng hợp kết quả: FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822 vì flood tcp/udp; Isolation Forest có macro-F1 cao nhất, em báo cáo trung thực.

### 3:07 – Slide 13 · Đối chiếu 6 câu hỏi nghiên cứu (12 s)
> **[3:07]** Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt; RQ1 đến RQ4 không đạt, và em giữ nguyên tiêu chí, không chỉnh sau khi có kết quả.

### 3:19 – Slide 14 · So sánh với Meidan 2018 (20 s)
> **[3:19]** So với Meidan: FPR của em 0,0025, thấp hơn 0,007 của bài nhưng chưa kiểm định; TPR 0,822 thay vì 100%.
> **[3:28]** Phần bỏ sót nằm ở flood tcp/udp giả mạo nguồn; chia ngẫu nhiên cũng không tăng TPR, nên em chưa tách được nguyên nhân duy nhất.

### 3:39 – Slide 15 · So sánh với Masud 2025 (21 s)
> **[3:39]** So với Masud: dữ liệu đầu vào khớp hoàn toàn, rủi ro từng máy ảo khớp tới 0,01, đường tấn công lệch 0,8%.
> **[3:48]** Với công thức em suy ra, tổng AC lệch dưới 3,4%; tổng R và nhiều hình vẫn chưa khớp vì bài thiếu công thức và có chỗ không nhất quán.

### 4:00 – Slide 16 · Kết luận và dự định làm tiếp (30 s)
> **[4:00]** Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công, báo động giả thấp, chạy được ở edge.
> **[4:09]** Dự định tiếp theo: thêm đặc trưng cho flood giả mạo nguồn, chạy trên Raspberry Pi có đo điện, đưa MTD lai lên mạng giả lập và thử trên bộ dữ liệu mới.
> **[4:22]** Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn đã lắng nghe.

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
| E12 – công thức AC suy ra | tổng AC lệch ≤ 3,4% · RoC ≤ 8,4% · tổng mạng lệch ≤ 5%: 5/9 · tổng R diversity −13,1%, redundancy −16,6% |
| Chạy lại Hình 6 (bài chính) | Hình 6(a): 11/35 điểm lệch ≤ 5% · diversity 7/7 · shuffle, S+D chỉ khớp ở V5 |
| Chạy hệ thống mirai/syn (Danmini) | 1989/1989 cửa sổ cảnh báo, cảnh báo high + 2 hành động MTD |
| Chạy hệ thống benign và gafgyt/tcp (Ennio) | 0 cửa sổ cảnh báo |

## 5. Câu hỏi có thể gặp

| Câu hỏi | Trả lời ngắn | Slide hỗ trợ |
|---|---|---|
| Sao không đạt TPR 100% như Meidan? | Phần bỏ sót là flood tcp/udp giả mạo nguồn, trông giống benign, và ngưỡng mean + std bị đuôi MSE kéo cao. Rò rỉ không giải thích được: chia ngẫu nhiên (E6) có TPR 0,804 và FPR "đẹp giả" 0,0006. Bài cũng tối ưu tham số riêng từng thiết bị, nên em chưa tách được nguyên nhân duy nhất. | 7, 12, 14, 21, 22 |
| Isolation Forest tốt hơn, sao vẫn dùng AE? | Đúng, em báo cáo trung thực. AE nhỏ hơn nhiều, lượng tử hóa int8 được và chạy vài µs/mẫu trên edge; IF làm baseline so sánh. | 9, 12, 22 |
| Hạ ngưỡng có bắt được tcp/udp không? | Có, ngưỡng p75 bắt 100% nhưng cần cửa sổ khoảng 1400 mẫu và FPR 0,02 – phát hiện chậm hơn, báo động giả nhiều hơn. Đây là hậu kiểm, không dùng để chấm tiêu chí. | 7, 12 |
| Vì sao kích thước int8 không giảm còn 25%? | Trọng số giảm 4 lần nhưng khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên file còn 45,5%. | 9 |
| Kết quả có ổn định không? | Chạy 5 seed; có 7 cặp (model, thiết bị) TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần là không đủ. | 8, 13 |
| MTD có tác động mạng thật không? | Không. MTD chỉ được mô phỏng và ghi vào CSDL; dữ liệu là bộ công khai, không chạy mã độc. | 10, 15, 26 |
| Tái lập paper chính được đến đâu? | Dùng đúng 18 CVE hệ điều hành, 14 CVE dịch vụ và 8 máy ảo của paper: rủi ro mức máy ảo khớp ±0,01, đường tấn công lệch −0,8%, độ trung tâm trên đồ thị có hướng chọn V5 như paper. Với topology Hình 3 tái lập 6/7 kết luận định tính, với Definition 2 chỉ 3/7. E12 suy ra AC theo VM bằng Σ BS × cost: tổng AC lệch dưới 3,4%, RoC dưới 8,4%, nhưng đây là giả thuyết và chưa giải thích được V2. Tổng R của diversity, redundancy và Hình 5(b), 6, 7, 9 vẫn chưa khớp vì bài thiếu công thức và có chỗ không nhất quán. | 11, 15, 20, 23, 25 |
| Bài báo tham khảo giải quyết bài toán gì, hạn chế ở đâu? | Masud 2025 đánh giá việc kết hợp shuffle, diversity, redundancy bằng mô hình THARM ba tầng; kết luận shuffle + diversity tốt nhất. Hạn chế: chỉ mô phỏng, chỉ MTD theo thời gian, không có bộ phát hiện kích hoạt MTD, không công bố mã. Bài tham chiếu Meidan 2018 chia dữ liệu một lần và không đo trên edge. | 2–4, 17 |
| Em làm bài này theo quy trình nào? | Đọc bài báo → lập kế hoạch → tải dữ liệu có checksum → làm sạch, EDA → viết pipeline kèm test → chốt tiêu chí trước khi chạy → chạy 468 lần → dựng hệ thống 4 tầng → tổng hợp thống kê, báo cáo → tái lập bài chính (E11, E12). | 5–11, 19 |
| Biểu đồ chạy lại có giống bài báo không? | Em vẽ lại đúng dạng Hình 6, Hình 7 của bài chính và Hình 2 của Meidan. Hình 6(a): 11/35 điểm lệch ≤ 5%, trong đó diversity 7/7, shuffle và S+D chỉ khớp ở V5. Hình 7: Eq. 1 cho cùng thang đo, nhưng topology chỉ có 5 đường và bài không in chuỗi VM của 8 đường, nên không so được từng cột. Hình 2 của Meidan: FPR khớp, TPR thấp hơn do flood tcp/udp. | 11, 22, 24 |

## 6. Mẹo trình bày

- Mốc chuyển phần: phần 1 – phân tích bài báo **0:24**, phần 2 – các bước làm bài **1:15**, phần 3 – kết quả **2:54**, phần 4 – so sánh với bài báo **3:19**, phần 5 – dự định làm tiếp **4:00**, kết thúc đúng **4:30**. Tập theo video mẫu 2–3 lần cho quen nhịp.
- Nếu bị chậm: bỏ câu thứ hai ở slide 1 (giới thiệu 5 phần) và câu thứ hai ở slide 6 (mất cân bằng) – tiết kiệm khoảng 12 s.
- Không đọc nguyên văn bảng số trên slide; chỉ nhấn 1–2 con số trong lời thoại.
- Nếu thầy muốn xem chạy thật sau phần trình bày: bật server theo README (uvicorn backend.app.main:app) – không nằm trong 4'30.
- Video mẫu chỉ để tập: video nộp phải do bạn tự trình bày.
