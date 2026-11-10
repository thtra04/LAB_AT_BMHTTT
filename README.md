# LAB_AT_BMHTTT – An toàn Bảo mật Hệ thống thông tin

Repository lưu trữ các bài thực hành của học phần **An toàn Bảo mật Hệ thống thông tin**.

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |

## Danh sách bài Lab

| Thư mục | Tên bài Lab |
|---|---|
| [LAB1-9/LAB1](LAB1-9/LAB1/) | Bắt gói tin Telnet – SSH (Examining SSH & Telnet in Wireshark) |
| [LAB1-9/LAB3](LAB1-9/LAB3/) | Nhận diện và ứng phó các mối đe dọa đến an toàn thông tin (Identifying and Responding to Information Security Threats) |
| [LAB1-9/LAB4](LAB1-9/LAB4/) | Khảo sát và đánh giá bề mặt mạng bằng Nmap (Network Attack Surface Assessment with Nmap) |
| [LAB1-9/LAB5](LAB1-9/LAB5/) | Thiết lập mô hình tường lửa pfSense (pfSense Firewall Configuration) |
| [LAB1-9/LAB6](LAB1-9/LAB6/) | Xác thực Active Directory và chính sách truy cập trên pfSense (pfSense AD Authentication & Access Policies) |
| [LAB1-9/LAB7](LAB1-9/LAB7/) | Xây dựng chính sách Web Protection trên mô hình pfSense + Web Proxy (E2Guardian, Squid, ClamAV) |
| [LAB1-9/LAB8](LAB1-9/LAB8/) | Local DNS Attack (DNS Spoofing & Cache Poisoning) |
| [LAB1-9/LAB9/LAB10](LAB1-9/LAB9/LAB10/) | Remote DNS Cache Poisoning (pfSense + Kali, runbook trong `trien_khai/`) |
| [LAB10-15](LAB10-15/) | Các bài Lab 10–15 (chưa có) |
| [DT043](DT043/) | Bài giữa kỳ – Phát hiện botnet IoT bằng autoencoder nhẹ (N-BaIoT, per-device AE, lượng tử hóa int8, edge benchmark, MTD lai, tái lập bài báo Masud 2025; hệ thống AI / BE / DB / FE) |

## Cấu trúc Repository

```
LAB_AT_BMHTTT/
├── README.md
├── LAB1-9/                # các bài Lab 1–9
│   ├── LAB1/  LAB3/  LAB4/  LAB5/  LAB6/  LAB7/  LAB8/
│   │   ├── README.md
│   │   └── báo cáo Word, hình, bằng chứng, cấu hình
│   └── LAB9/
│       └── LAB10/         # Remote DNS Cache Poisoning: baocao/, trien_khai/, LAB10_Resources/
├── LAB10-15/              # các bài Lab 10–15
└── DT043/                 # bài giữa kỳ
    ├── README.md          # hướng dẫn chạy lại từ đầu
    ├── src/               # mã nguồn: ai/ backend/ db/ frontend/ data/ results/ artifacts/ report/
    └── tailieu/           # báo cáo, slide, kịch bản, hỏi – đáp, docs/ (bài báo, bản dịch, tái lập)
```

Mỗi thư mục Lab có file `README.md` (hoặc báo cáo) mô tả: họ tên, MSSV, tên bài Lab, nội dung đã thực hiện, kết quả và các lưu ý để giảng viên kiểm tra hoặc chạy lại bài làm. Video quay màn hình không đưa lên repository vì dung lượng lớn.
