# LAB 8 – Local DNS Attack (DNS Spoofing & Cache Poisoning)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | *(cập nhật sau khi đăng)* |
| Đề bài | [đề/LAB8_Local_DNS_Attack_pfSense_2026.docx](đề/LAB8_Local_DNS_Attack_pfSense_2026.docx) + bộ tài nguyên [đề/LAB8_Local_DNS_Attack_pfSense_2026_FINAL.zip](đề/LAB8_Local_DNS_Attack_pfSense_2026_FINAL.zip) |
| Báo cáo | [Baocao/11CNPM2-Lab8_1150080120-HoangThanhTra.docx](Baocao/11CNPM2-Lab8_1150080120-HoangThanhTra.docx) |
| Cấu hình & script | [cau_hinh_dns/](cau_hinh_dns/) |
| Ảnh minh chứng | [hinh/](hinh/) · Log & pcap: [ketqua/](ketqua/) |

## 2. Tên bài Lab

**Lab 8: Local DNS Attack** (tài liệu đề ghi "LAB 9 – Local DNS Attack", theo SEED Labs) – dựng DNS-SERVER
BIND9 làm resolver/cache riêng cho một mạng ảo **cô lập**, rồi minh hoạ ba kỹ thuật tấn công DNS nội bộ và
phân tích phòng thủ. Toàn bộ chỉ chạy với tên miền `.test` trong mạng ảo, không đụng Internet/mạng thật.
