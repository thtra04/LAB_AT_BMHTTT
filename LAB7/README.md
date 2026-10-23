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
| Báo cáo hoàn chỉnh | [11CNPM2-Lab7_1150080120-HoangThanhTra_HoanChinh.docx](11CNPM2-Lab7_1150080120-HoangThanhTra_HoanChinh.docx) – 39 hình, đủ kết quả 10 kịch bản |
| Cấu hình | [config_lab7.xml](config_lab7.xml) (pfSense) · [cau_hinh_web_proxy/](cau_hinh_web_proxy/) (squid.conf, e2guardian*.conf, site.story, danh sách, trang block, script) |
| Ảnh minh chứng | [hinh/](hinh/) |

## 2. Tên bài Lab

**Lab 7: Xây dựng chính sách Web Protection trên mô hình pfSense + Web Proxy** – chuyển bài Web Protection của Sophos sang pfSense CE: pfSense làm firewall/gateway và chống bypass, WEB-PROXY Ubuntu 24.04 chạy **E2Guardian :8080 → Squid 127.0.0.1:3128 + ClamAV** để lọc nội dung L7; 13 website mô phỏng `*.lab7.test` trên DMZ-WEB.

