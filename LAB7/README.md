# LAB 7 – Xây dựng chính sách Web Protection trên mô hình pfSense + Web Proxy

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Đề bài | [LAB7/LAB7_pfSense_Web_Protection_2026.docx](LAB7/LAB7_pfSense_Web_Protection_2026.docx) + bộ tài nguyên [LAB7_pfSense_Web_Protection_2026.zip](LAB7/LAB7_pfSense_Web_Protection_2026.zip) |
| Báo cáo | [11CNPM2-Lab7_1150080120-HoangThanhTra.docx](11CNPM2-Lab7_1150080120-HoangThanhTra.docx) (theo mẫu `LAB7_Report_Template.docx`) |

## 2. Tên bài Lab

**Lab 7: Xây dựng chính sách Web Protection trên mô hình pfSense + Web Proxy** – chuyển bài Web Protection của Sophos sang pfSense CE: pfSense làm firewall/gateway và chống bypass, WEB-PROXY Ubuntu 24.04 chạy **E2Guardian :8080 → Squid 127.0.0.1:3128 + ClamAV** để lọc nội dung L7; 13 website mô phỏng `*.lab7.test` trên DMZ-WEB.

### Mục tiêu
- Ép mọi truy cập web của Client-A/B đi qua proxy 10.6.0.30:8080 và chặn direct TCP 80/443.
- Hard block (Geo-Sim, Job Search, game cụ thể), warning + temporary bypass 300 s (weapons, politics, religion, streaming), exception (normal, education, download).
- Entertainment/Game theo Schedule 60 phút (time-window policy), quét EICAR bằng ClamAV, giới hạn file > 100 MB (Squid `reply_body_max_size`), tùy biến trang block.
- HTTPS inspection (mở rộng) bằng CA lab, chỉ trong môi trường cô lập.

## 3. Mô hình (kế thừa LAB 6 + WEB-PROXY)

| Thành phần | IP / mạng | Vai trò |
|---|---|---|
| pfSense-LAB6 | MGMT 192.168.56.254 · LAN 10.6.0.1 · DMZ 172.16.6.1 | Firewall/gateway, ép web qua proxy |
| DC01 | 10.6.0.10/24 | AD + DNS (zone `lab7.test`) |
| Client-A / Client-B | 10.6.0.21 / 10.6.0.22 | Máy người dùng, proxy 10.6.0.30:8080 |
| **WEB-PROXY** (mới) | 10.6.0.30/24, GW 10.6.0.1, DNS 10.6.0.10 | E2Guardian + Squid + ClamAV |
| DMZ-WEB | 172.16.6.10/24 | 13 website mô phỏng `*.lab7.test` |

Ruleset LAN (first-match): DNS → DC01 · Client → proxy :8080 · mail ports · **Block client → Any 80/443** · proxy → Any 80/443 · proxy → DMZ :80 · explicit deny.

## 4. Phạm vi đã thực hiện

- [x] Đọc đề và bộ tài nguyên; soạn báo cáo theo mẫu: thông tin sinh viên, bảng IP, bảng kiểm thử 10 kịch bản (kỳ vọng), ruleset pfSense kèm giải thích thứ tự rule, cấu hình E2Guardian/Squid/Schedule.
- [x] Trả lời 4 câu hỏi của mẫu báo cáo và **10 câu hỏi phân tích** (mục I.2 của đề).
- [ ] Thực hành trên máy ảo: dựng WEB-PROXY, DNS `lab7.test`, website DMZ, alias/rule pfSense, các chính sách web.
- [ ] Dán ảnh minh chứng và kết quả thực tế vào các ô đánh dấu vàng trong báo cáo (đề yêu cầu ảnh chụp từ môi trường của chính sinh viên).

## 5. Tóm tắt câu trả lời phần câu hỏi phân tích

| Câu | Ý chính |
|---|---|
| 1 | Netgate đánh dấu Squid/SquidGuard/Lightsquid trên pfSense là deprecated (lỗ hổng upstream chưa sửa); tách proxy L7 ra VM riêng, pfSense chỉ làm firewall L3/L4. |
| 2 | pfSense: IP, cổng, giao thức, interface, state, schedule (L3/L4). Proxy: hostname/URL, method, header, MIME, kích thước, nội dung/AV, trang warning (L7). |
| 3 | Proxy cấu hình phía client có thể bị tắt; chặn direct 80/443 và chỉ cho WEB-PROXY ra web mới buộc mọi truy cập qua Web Protection. |
| 4 | CDN/cloud/shared hosting: một IP nhiều site, một site đổi IP liên tục → lọc theo IP vừa chặn nhầm vừa bỏ sót; category gắn với tên miền/URL. |
| 5 | Hard block luôn từ chối, không bypass (non-bypass list); temporary bypass hiện cảnh báo, người dùng xác nhận để mở tạm 300 s rồi hết hạn. |
| 6 | HTTPS mã hóa đầu–cuối, proxy chỉ thấy tên miền (CONNECT/SNI); muốn ClamAV quét EICAR phải SSL MITM với CA lab được client tin cậy. |
| 7 | Lộ private key CA → ký chứng chỉ hợp lệ cho mọi tên miền với các máy tin CA → MITM toàn bộ HTTPS, giả mạo website mà trình duyệt không cảnh báo. |
| 8 | Không: đó là giới hạn bộ đệm/quét của E2Guardian, file lớn hơn có thể đi qua không quét; giới hạn cứng phải dùng Squid `reply_body_max_size` và kiểm thử 100 MB/110 MB. |
| 9 | Schedule là cửa sổ giờ cố định cho mọi client; daily quota đếm thời gian dùng tích lũy theo người dùng và category – LAB 7 không có cơ chế đó. |
| 10 | Giả thuyết đầu tiên: client không thực sự dùng proxy 10.6.0.30:8080 (proxy tắt/sai cổng/HTTPS không trỏ proxy); kiểm tra cài đặt proxy, `curl -x`, Firewall log. |

## 6. Lưu ý an toàn (theo đề)
- Chỉ import CA LAB 7 vào Client-A/B của lab, không vào máy cá nhân; không nộp private key CA.
- Website Job/Politics/Weapons/Geo đều là domain mô phỏng `.lab7.test`; EICAR là chuỗi kiểm thử antivirus, không phải mã độc.
