# LAB 6 – Xác thực Active Directory và chính sách truy cập trên pfSense (pfSense AD Authentication & Access Policies)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | *(cập nhật sau khi quay)* |
| Đề bài | [LAB6_pfSense_AD_Access_Policies_2026.pdf](LAB6_pfSense_AD_Access_Policies_2026.pdf) |
| Báo cáo hoàn chỉnh | [11CNPM2-Lab6_1150080120-HoangThanhTra_HoanChinh.docx](11CNPM2-Lab6_1150080120-HoangThanhTra_HoanChinh.docx) – đã dán 51 ảnh minh chứng, điền kết quả thực tế |
| Báo cáo bản cũ (khung) | [11CNPM2-Lab6_1150080120-HoangThanhTra.docx](11CNPM2-Lab6_1150080120-HoangThanhTra.docx) |
| Ảnh minh chứng | thư mục [hinh/](hinh/) |
| File cấu hình | [config.xml](config.xml) (Diagnostics → Backup & Restore → Download configuration, hostname `ThanhTra-Lab6`) |

## 2. Tên bài Lab

**Lab 6: Xác thực Active Directory và chính sách truy cập trên pfSense** – pfSense CE với bốn interface WAN / MGMT / LAN / DMZ, tích hợp Active Directory (domain `lab6.test`) qua LDAP, Captive Portal xác thực user domain, Firewall Alias, Schedule và các website mô phỏng trong DMZ.
