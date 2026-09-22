# LAB 1 – Bắt gói tin Telnet – SSH (Examining SSH & Telnet in Wireshark)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Link video YouTube |  |

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
| Server | *(vd: Ubuntu Server 26.04 / Windows Server)* | Telnet Server, OpenSSH Server | *(điền IP)* |
| Client | *(vd: Windows 11)* | PuTTY 0.85 | *(điền IP)* |
| Attacker | *(vd: Kali Linux / Windows 11)* | Wireshark 4.6.8 (kèm Npcap) | *(điền IP)* |

Công cụ ảo hóa: VMware Workstation *(hoặc VirtualBox)*.

## 4. Nội dung đã thực hiện

### 4.1. Thiết lập môi trường
- [ ] Dựng 3 máy ảo (Server, Client, Attacker) theo mô hình Hình 1, kiểm tra kết nối bằng `ping`.
- [ ] Cài Wireshark (cho phép cài Npcap) trên máy Attacker, cài PuTTY trên máy Client.
- [ ] Tạo tài khoản trên Server: username = Tên sinh viên, mật khẩu = MSSV.

### 4.2. Bắt gói tin khi sử dụng Telnet
- [ ] Bước 1: Bật dịch vụ Telnet trên Server, kiểm tra cổng 23 đang lắng nghe.
- [ ] Bước 2: Cấp quyền Telnet cho tài khoản (Windows: thêm vào nhóm TelnetClients; Linux: chỉ cần tài khoản hợp lệ).
- [ ] Bước 3: Bật Wireshark trên Attacker, chọn đúng interface, dùng display filter `tcp.port == 23`.
- [ ] Bước 4: Client dùng PuTTY/Command Prompt kết nối Telnet đến Server, thực hiện `dir`, `mkdir`.
- [ ] Bước 5: Dừng bắt gói, dùng Analyze > Follow > TCP Stream để tìm thông tin đăng nhập và dữ liệu trao đổi.
- [ ] Bước 6: Đổi mật khẩu phức tạp hơn (>10 ký tự, gồm chữ, số, ký tự đặc biệt), lặp lại bước 3–5.

### 4.3. Bắt gói tin khi sử dụng SSH
- [ ] Bước 1–2: Cài đặt và khởi động SSH Server (OpenSSH / Cygwin), kiểm tra cổng 22.
- [ ] Bước 3: Bật Wireshark trên Attacker, dùng display filter `tcp.port == 22`.
- [ ] Bước 4: Client dùng PuTTY kết nối SSH đến Server, kiểm tra host-key fingerprint ở lần kết nối đầu.
- [ ] Bước 5: Dừng bắt gói, phân tích dữ liệu trao đổi và so sánh với phiên Telnet.

