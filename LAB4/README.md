# LAB 4 – Khảo sát và đánh giá bề mặt mạng bằng Nmap (Network Attack Surface Assessment with Nmap)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Giảng viên biên soạn | Phạm Trọng Huynh – Bộ môn An toàn Thông tin |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | https://youtu.be/7876Zcu4GBk |
| Đề bài | [LAB4_Nmap_HuongDan_2026.pdf](LAB4_Nmap_HuongDan_2026.pdf) |
| Báo cáo | [Lab4_CNPM2_1150080120_HoangThanhTra.docx](Lab4_CNPM2_1150080120_HoangThanhTra.docx) |

> ⚠️ **Phạm vi pháp lý và đạo đức:** bài lab chỉ phục vụ học tập và nghiên cứu. Chỉ quét các máy ảo do chính sinh viên dựng trong mạng **VirtualBox Host-Only**. **Không** quét IP/tên miền bên ngoài, mạng cơ quan, Wi-Fi của người khác hoặc dịch vụ Internet khi chưa được ủy quyền.

## 2. Tên bài Lab

**Lab 4: Khảo sát và đánh giá bề mặt mạng bằng Nmap** – Thực hành An toàn Hệ thống thông tin.



### Cấu trúc thư mục dự kiến
```
LAB4/
├── README.md                                  # file này
├── LAB4_Nmap_HuongDan_2026.pdf                # đề bài
├── Lab4_CNPM2_1150080120_HoangThanhTra.docx   # báo cáo Word
├── Evidence/                                  # kết quả quét
│   ├── scan.txt, scan.xml, scan.html
│   ├── smb.txt
│   ├── before.txt, after.txt
│   ├── full_ports.txt
│   └── lab4_full.nmap, lab4_full.xml, lab4_full.gnmap
└── Images/                                    # ảnh chụp minh chứng A1 … A8
```



## Cách chạy lại

```bash
# Kali (192.168.226.130) quét Metasploitable 2 (192.168.226.134)
nmap -sn 192.168.226.0/24 -oN hostdiscovery.txt
nmap -sT 192.168.226.134 -oN scan_sT.txt
sudo nmap -sS 192.168.226.134 -oN scan_sS.txt
sudo nmap -sU --top-ports 20 192.168.226.134 -oN scan_sU.txt
nmap -sV 192.168.226.134 -oN scan_sV.txt
sudo nmap -O 192.168.226.134 -oN scan_O.txt
sudo nmap -A 192.168.226.134 -oN scan_A.txt
nmap -p445 --script smb-os-discovery 192.168.226.134
nmap -p445 --script smb-vuln-ms17-010 192.168.226.134
nmap -sV -p21,22,23,80,445,3306 192.168.226.134 -oA scan_all
xsltproc scan_all.xml -o scan_all.html
# Hardening trên máy đích: sudo iptables -A INPUT -p tcp --dport 21 -j DROP; --dport 23 -j DROP
```
