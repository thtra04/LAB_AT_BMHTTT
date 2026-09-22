# LAB 1 – Bắt gói tin Telnet – SSH (Examining SSH & Telnet in Wireshark)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | *(điền họ tên)* |
| Mã số sinh viên (MSSV) | *(điền MSSV)* |
| Lớp | *(điền lớp)* |
| Link video YouTube | *(dán link video quay quá trình thực hiện)* |

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

> Đánh dấu `[x]` vào các bước đã hoàn thành.

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

## 5. Kết quả thực hiện

> Chèn ảnh chụp màn hình từ chính bài làm vào thư mục `images/` và tham chiếu tại đây. File bắt gói `.pcapng` lưu trong `captures/`.

### 5.1. Telnet
- Ảnh chụp Wireshark phiên Telnet (Follow TCP Stream): `images/...`
- Thông tin quan sát được: *(mô tả)*
- Kết quả sau khi đổi mật khẩu phức tạp: *(mô tả)*

### 5.2. SSH
- Ảnh chụp Wireshark phiên SSH: `images/...`
- Thông tin quan sát được / không quan sát được: *(mô tả)*

### 5.3. Nhận xét so sánh
*(nhận xét ngắn gọn Telnet vs SSH dựa trên kết quả thực nghiệm)*

## 6. Cấu trúc thư mục

```
LAB1/
├── README.md                                       # File mô tả này
├── Lab1 - Examining SSH  Telnet in Wireshark.pdf   # Đề bài Lab 1
├── report/                                         # Báo cáo Word: Lab1_Lop_MSSV_TenSV.docx
├── images/                                         # Ảnh chụp màn hình kết quả
└── captures/                                       # File bắt gói Wireshark (.pcapng)
```

## 7. Lưu ý để giảng viên kiểm tra / chạy lại

- *(ghi các bước cần thiết để chạy lại: cách mở file .pcapng, filter đã dùng, tài khoản thử nghiệm, IP các máy, ...)*
- Trên virtual switch hiện đại, máy Attacker có thể không thấy toàn bộ lưu lượng unicast giữa Client và Server; nếu vậy điểm bắt gói được chuyển sang Client hoặc Server *(ghi rõ đã bắt gói ở máy nào)*.
- Telnet chỉ được bật trong mạng lab cô lập, không mở TCP/23 ra Internet.

## 8. Câu hỏi cần trả lời trong báo cáo (phần C của đề)

1. Telnet và SSH là gì và được ứng dụng trong trường hợp nào?
2. So sánh Telnet và SSH.
3. Khi sử dụng SSH, còn có cách nào để đăng nhập ngoài cách dùng username và mật khẩu truyền thống? Thực hiện demo minh họa kèm theo.
4. Phân tích sự khác biệt giữa Telnet và SSH dưới góc độ bảo mật: Confidentiality, Integrity, Authentication.
5. Dựa trên kết quả bắt gói bằng Wireshark, chỉ ra những thông tin nào của phiên Telnet có thể bị quan sát hoặc khôi phục. So sánh với SSH và cung cấp bằng chứng từ bài thực hành.
6. Tại sao mật khẩu dài và phức tạp không khắc phục được điểm yếu bảo mật của Telnet?
7. Khi sử dụng SSH, Wireshark vẫn quan sát được những thông tin nào? Metadata này có thể tạo ra rủi ro bảo mật nào?
8. Host key có vai trò gì? Điều gì xảy ra nếu chấp nhận host key mà không kiểm tra?
9. Tại sao Attacker cùng mạng chưa chắc bắt được toàn bộ lưu lượng unicast? Cần điều kiện/kỹ thuật nào để quan sát được?
10. Trình bày nguyên lý public-key authentication và ưu điểm so với xác thực bằng mật khẩu.
11. Đề xuất ít nhất ba biện pháp hardening cho SSH và giải thích mục đích của từng biện pháp.

## 9. Tài liệu tham khảo

- Wireshark 4.6.8: https://www.wireshark.org/download.html
- PuTTY 0.85: https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
- Microsoft Learn – OpenSSH for Windows: https://learn.microsoft.com/windows-server/administration/openssh/openssh_install_firstuse
- Ubuntu package inetutils-telnetd: https://packages.ubuntu.com/resolute/inetutils-telnetd
