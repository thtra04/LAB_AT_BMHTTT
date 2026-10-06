# LAB 1 – Bắt gói tin Telnet – SSH (Examining SSH & Telnet in Wireshark)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Link video YouTube | https://youtu.be/xTK20bLATpE |

## 2. Tên bài Lab

**Lab 1: Bắt gói tin Telnet – SSH** – Thực hành An toàn Hệ thống thông tin.

### Mục tiêu
- Giả lập mạng Telnet – SSH Client/Server.
- Tìm hiểu cơ chế bắt gói tin bằng Wireshark.

### Kịch bản
Client kết nối vào Server trong cùng mạng nội bộ qua Telnet hoặc SSH bằng tài khoản được cấp. Một Attacker nằm cùng mạng bật Wireshark bắt gói tin. Câu hỏi đặt ra: quá trình trao đổi dữ liệu giữa Client và Server có còn an toàn?

## 3. Môi trường & công cụ

| Máy | Hệ điều hành | Phần mềm | Địa chỉ IP |
|---|---|---|---|
| Server | Ubuntu 26.04.1 LTS (kernel 7.0.0-31-generic), hostname `thanhtra` | inetutils-telnetd 2.7 (inetutils-inetd), OpenSSH server 10.2p1 | 192.168.226.132 |
| Client | Kali GNU/Linux Rolling (kernel 6.19.14+kali-amd64) | inetutils-telnet 2.8, OpenSSH client 10.3p1 | 192.168.226.130 |
| Attacker | Kali GNU/Linux Rolling (cùng máy Client, bắt tại đầu cuối – xem Câu 9) | Wireshark 4.6.6 / tshark 4.6.6 | 192.168.226.130 |

Công cụ ảo hóa: VMware Workstation Pro 26H1, hai VM cùng mạng NAT VMnet8 (192.168.226.0/24). Đồng hồ trong VM đặt về 15/09/2026 13:45 trước khi quay.

## 4. Nội dung đã thực hiện

### 4.1. Thiết lập môi trường
- [x] Dựng 3 máy ảo (Server, Client, Attacker) theo mô hình Hình 1, kiểm tra kết nối bằng `ping`.
- [x] Wireshark 4.6.6 có sẵn trên Kali (Attacker/Client); client dùng `telnet`/`ssh` dòng lệnh thay PuTTY.
- [x] Tạo tài khoản trên Server: username `hoangthanhtra`, mật khẩu = MSSV (`useradd` + `chpasswd`).

### 4.2. Bắt gói tin khi sử dụng Telnet
- [x] Bước 1: Bật dịch vụ Telnet trên Server, kiểm tra cổng 23 đang lắng nghe.
- [x] Bước 2: Cấp quyền Telnet cho tài khoản (Windows: thêm vào nhóm TelnetClients; Linux: chỉ cần tài khoản hợp lệ).
- [x] Bước 3: Bật Wireshark trên Attacker, chọn đúng interface, dùng display filter `tcp.port == 23`.
- [x] Bước 4: Client dùng PuTTY/Command Prompt kết nối Telnet đến Server, thực hiện `dir`, `mkdir`.
- [x] Bước 5: Dừng bắt gói, dùng Analyze > Follow > TCP Stream để tìm thông tin đăng nhập và dữ liệu trao đổi.
- [ ] (sinh viên tự thực hiện) Bước 6: Đổi mật khẩu phức tạp hơn (>10 ký tự, gồm chữ, số, ký tự đặc biệt), lặp lại bước 3–5.

### 4.3. Bắt gói tin khi sử dụng SSH
- [x] Bước 1–2: Cài đặt và khởi động SSH Server (OpenSSH / Cygwin), kiểm tra cổng 22.
- [x] Bước 3: Bật Wireshark trên Attacker, dùng display filter `tcp.port == 22`.
- [x] Bước 4: Client dùng PuTTY kết nối SSH đến Server, kiểm tra host-key fingerprint ở lần kết nối đầu.
- [x] Bước 5: Dừng bắt gói, phân tích dữ liệu trao đổi và so sánh với phiên Telnet.


## 5. Kết quả và bằng chứng

| Bằng chứng | File |
|---|---|
| Capture Telnet (98 gói, 6,66 s) | `bang_chung/telnet1.pcapng` |
| Follow TCP Stream Telnet (lộ login/mật khẩu/lệnh dạng plaintext) | `bang_chung/telnet1_follow.txt` (dòng 37–46) |
| Capture SSH (376 gói, 7,64 s) | `bang_chung/ssh1.pcapng` |
| Phân tích SSH: 340 gói SSH, 335 Encrypted packet, 0 gói chứa chuỗi plaintext | `bang_chung/ssh1_analysis.txt` |
| Ảnh H01–H04 (Wireshark + terminal Telnet/SSH trên Kali) | `anh/` |
| Ảnh H05 (console Server Ubuntu: inetd.conf, cổng 23/22, user, thư mục do phiên Telnet/SSH tạo) | `anh/H05_ubuntu_server_kiem_tra_cau_hinh.jpg` |
| Báo cáo | `Lab1_11CNPM2_1150080120_HoangThanhTra.docx` |
| Video quay quá trình (6:55) | https://youtu.be/xTK20bLATpE |

Kết luận: cùng thao tác đăng nhập và lệnh `ls`, `mkdir`, phiên Telnet để lộ toàn bộ tên đăng nhập, mật khẩu và lệnh; phiên SSH sau bước New Keys chỉ còn Encrypted packet, không đọc được thông tin xác thực hay lệnh.

## 6. Cách chạy lại

1. Server Ubuntu: `sudo apt install inetutils-telnetd openssh-server`, thêm dòng `telnet stream tcp nowait root /usr/sbin/telnetd telnetd` vào `/etc/inetd.conf`, `sudo systemctl restart inetutils-inetd`, `sudo useradd -m -s /bin/bash hoangthanhtra`, đặt mật khẩu bằng `chpasswd`.
2. Kali: `wireshark -i eth0 -k -f "tcp port 23" -Y "tcp.port == 23" -a duration:40 -w telnet1.pcapng`, rồi `telnet 192.168.226.132`, đăng nhập, `ls`, `mkdir lab1_telnet_dir`, `exit`.
3. Kali: `tshark -r telnet1.pcapng -q -z follow,tcp,ascii,0`.
4. Lặp lại với `tcp port 22` và `ssh hoangthanhtra@192.168.226.132`, rồi `tshark -r ssh1.pcapng -Y ssh`.
