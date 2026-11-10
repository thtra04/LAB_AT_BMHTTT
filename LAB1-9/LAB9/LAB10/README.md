# LAB 10 – Remote DNS Cache Poisoning (tấn công đầu độc cache DNS từ xa)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Ngày thực hành | 03/11/2026 |
| Đề bài / mẫu báo cáo | [LAB10_HuongDan.docx](LAB10_HuongDan.docx) · [LAB10_MauBaoCao.docx](LAB10_MauBaoCao.docx) |
| Báo cáo | [baocao/11CNPM2-Lab10_1150080120-HoangThanhTra.docx](baocao/11CNPM2-Lab10_1150080120-HoangThanhTra.docx) |
| Script & cấu hình | [trien_khai/](trien_khai/) · [LAB10_Resources/](LAB10_Resources/) |
| Runbook (các bước chạy) | [trien_khai/RUNBOOK_LAB10.md](trien_khai/RUNBOOK_LAB10.md) |
| Ảnh minh chứng | [baocao/hinh/](baocao/hinh/) |

> **Link video YouTube:** chưa cập nhật (sẽ bổ sung sau khi quay).

## 2. Tên bài Lab

**Lab 10: Remote DNS Cache Poisoning** – tái lập tấn công kiểu **Kaminsky** đầu độc cache của một
DNS resolver từ **một mạng khác** (attacker không nằm cùng mạng với resolver), rồi khôi phục BIND9 hiện đại
và phân tích phòng thủ. Toàn bộ chỉ chạy với tên miền `.test` trong mạng ảo cô lập, **không đụng Internet
hay mạng thật**.

Bài này kế thừa hạ tầng DNS của **LAB 9 – Local DNS Attack** (thư mục [`../../LAB8/`](../../LAB8/)).

## 3. Khác biệt với LAB 9

| | LAB 9 (Local) | LAB 10 (Remote) |
|---|---|---|
| Vị trí attacker | Cùng một mạng L2 với resolver | Tách sang mạng riêng **ATTACKNET**, qua pfSense |
| Nghe lén (sniff) | Bật promiscuous, **đọc được** Transaction ID | **Không** đọc được gói resolver ↔ AUTH-DNS |
| Cách tấn công | Giả mạo trả lời vì biết sẵn TXID | Phải **đoán TXID 16-bit** bằng kỹ thuật đua (race) |
| Phòng thủ | Lọc, DNSSEC nội bộ | BIND9 hiện đại: random source port + TXID, hardening |

Tính "remote" nằm ở chỗ: Kali bị pfSense chặn không cho nghe lén đường giữa resolver và máy chủ tên miền
có thẩm quyền, nên kẻ tấn công buộc phải đoán mù định danh giao dịch.

## 4. Sơ đồ mạng (2 phân đoạn sau pfSense)

```
┌──────────────── DNSLAB segment (L2) ───────────────┐
│  DNS-SERVER  ens37 10.9.0.10   (resolver/cache)     │
│  VICTIM      ens37 10.9.0.100  (DNS = 10.9.0.10)    │
│  AUTH-DNS    ens37 172.16.6.20 (+ alias web .10)    │
│  pfSense NIC-A: 10.9.0.1/24  + VIP 172.16.6.1/24    │
└──────────────────────┬─────────────────────────────┘
                       │  pfSense (định tuyến + firewall)
┌──────────────────────┴──── ATTACKNET segment (L2) ─┐
│  Kali  eth1 10.10.0.200   (máy tấn công)            │
│  pfSense NIC-B: 10.10.0.1/24                        │
└─────────────────────────────────────────────────────┘
```

- **DNS-SERVER** và **AUTH-DNS** cùng phân đoạn DNSLAB → nói chuyện trực tiếp (không qua pfSense) nên đua nhanh.
- **Kali** ở ATTACKNET → mọi lưu lượng sang DNSLAB đều qua pfSense → không nghe lén được. Đây chính là điểm "remote".

## 5. Các máy ảo và tài khoản

| VM | IP lab | Tài khoản | Vai trò |
|---|---|---|---|
| DNS-SERVER | ens37 10.9.0.10 | thtra / 123456 | Resolver/cache bị tấn công (BIND9 + resolver mô phỏng lỗ hổng) |
| VICTIM | ens37 10.9.0.100 | thtra / 123456 | Máy nạn nhân truy vấn qua resolver |
| AUTH-DNS | ens37 172.16.6.20 (+ alias .10 web hợp lệ) | thtra / 123456 | Máy chủ tên miền có thẩm quyền + web thật |
| Kali | eth1 10.10.0.200 | hoangthanhtra / 1150080120 | Máy tấn công (ở ATTACKNET) |
| pfSense | WebGUI https://10.0.0.1 | admin / 1150080120 | Định tuyến + firewall giữa hai phân đoạn |

> Mỗi máy còn một card NAT để SSH/Internet. Có snapshot `LAB10_START` cho cả 5 máy để khôi phục khi cần.

## 6. Nội dung thư mục

```
LAB10/
├── README.md                     # file này
├── LAB10_HuongDan.docx           # đề bài / hướng dẫn
├── LAB10_MauBaoCao.docx          # mẫu báo cáo
├── baocao/
│   ├── 11CNPM2-Lab10_1150080120-HoangThanhTra.docx   # báo cáo
│   └── hinh/                      # ảnh minh chứng (anh1..anh11)
├── trien_khai/                   # script setup + runbook để chạy lại
│   ├── RUNBOOK_LAB10.md           # các bước chi tiết (đánh dấu cảnh cần quay)
│   ├── lab10_dns_server.sh
│   ├── lab10_auth_dns.sh
│   ├── lab10_victim.sh
│   └── lab10_kali.sh
└── LAB10_Resources/              # bộ tài nguyên gốc theo từng vai trò
    ├── 01_DNS_SERVER/            # cấu hình BIND baseline + vuln_resolver_lab10.py
    ├── 03_ATTACKER/              # kaminsky_remote_lab10.py, evil_dns_lab10.py, fake_index.html
    ├── 04_AUTH_DNS_RELAY/        # auth_dns_relay_lab10.py
    ├── 05_PFSENSE/              # firewall_policy_matrix.csv
    ├── 06_WIRESHARK/            # bộ lọc gói
    └── README_FIRST.txt
```

## 7. Cách chạy lại

Làm theo [trien_khai/RUNBOOK_LAB10.md](trien_khai/RUNBOOK_LAB10.md). Tóm tắt các bước:

1. **Đấu mạng trong VMware:** tạo 2 LAN Segment `DNSLAB`, `ATTACKNET`; gán card lab cho từng máy; Kali để Promiscuous = Deny.
2. **Cấu hình pfSense:** gán 2 interface 10.9.0.1/24 và 10.10.0.1/24, thêm VIP 172.16.6.1/24, dựng luật firewall theo `firewall_policy_matrix.csv`.
3. **Baseline:** truy vấn hợp lệ qua resolver để thấy cache sạch, chứng minh Kali không nghe lén được.
4. **Tấn công:** chạy bộ script Kaminsky (đoán TXID bằng đua relay) đến khi đầu độc được cache resolver.
5. **Kiểm chứng:** VICTIM truy cập tên miền bị trỏ sang web giả của attacker.
6. **Phòng thủ:** khôi phục BIND9 hiện đại (random port + TXID), hardening, rồi chạy lại để thấy tấn công thất bại.

> **Lưu ý kỹ thuật:** dịch vụ nền nên chạy qua `systemd-run --unit=lab10-*` (chạy bằng `nohup`/`setsid` sẽ
> chết khi đóng SSH). `auth_dns_relay` chỉ trả lời truy vấn từ `10.9.0.10:33333`, nên baseline phải đi qua
> `vuln_resolver` chứ không phải BIND thường.

## 8. Ràng buộc an toàn / đạo đức

- Chỉ chạy trong mạng ảo cô lập do sinh viên sở hữu. Không chạy trên Wi-Fi, mạng trường, mạng doanh nghiệp,
  Internet hay hệ thống của người khác.
- Chỉ dùng tên miền `.test`. Các script đã hard-code IP và tên miền riêng của lab.
