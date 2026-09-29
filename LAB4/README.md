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
| Link video YouTube | *(dán link video quay quá trình thực hiện nếu lớp yêu cầu)* |
| Đề bài | [LAB4_Nmap_HuongDan_2026.pdf](LAB4_Nmap_HuongDan_2026.pdf) |
| Báo cáo | [Lab4_CNPM2_1150080120_HoangThanhTra.docx](Lab4_CNPM2_1150080120_HoangThanhTra.docx) |

> ⚠️ **Phạm vi pháp lý và đạo đức:** bài lab chỉ phục vụ học tập và nghiên cứu. Chỉ quét các máy ảo do chính sinh viên dựng trong mạng **VirtualBox Host-Only**. **Không** quét IP/tên miền bên ngoài, mạng cơ quan, Wi-Fi của người khác hoặc dịch vụ Internet khi chưa được ủy quyền.

## 2. Tên bài Lab

**Lab 4: Khảo sát và đánh giá bề mặt mạng bằng Nmap** – Thực hành An toàn Hệ thống thông tin.

### Mục tiêu
- Hiểu mô hình **host/guest** trong ảo hóa.
- Cài và kiểm tra **Nmap** trên Windows 10/11 và Kali Linux; hiểu vai trò của **Npcap** trên Windows.
- Tự dựng mạng **VirtualBox Host-Only**, xác định đúng IP của Kali, Metasploitable 2 và máy Windows.
- Thực hiện **host discovery, TCP/UDP scan, service detection, OS fingerprinting** và một số **NSE script** phòng thủ.
- Đọc và giải thích trạng thái **open / closed / filtered**; phân biệt kết quả giữa các kỹ thuật quét.
- Xuất kết quả, xây dựng bằng chứng và viết báo cáo kỹ thuật **có khả năng lặp lại**.

## 3. Kiến thức nền

### 3.1. Các trạng thái cổng trong Nmap

| Trạng thái | Ý nghĩa |
|---|---|
| `open` | Có ứng dụng đang lắng nghe và chấp nhận kết nối trên cổng. |
| `closed` | Cổng truy cập được (host phản hồi) nhưng không có ứng dụng lắng nghe. |
| `filtered` | Nmap không xác định được vì gói tin bị firewall/bộ lọc chặn hoặc bỏ qua. |
| `unfiltered` | (ACK scan) Cổng truy cập được nhưng không xác định được open hay closed. |
| `open\|filtered` | Không phân biệt được cổng mở hay bị lọc làm im lặng (thường gặp ở UDP, FIN/Xmas/NULL). |
| `closed\|filtered` | Không phân biệt được cổng đóng hay bị lọc (IP ID idle scan). |

### 3.2. Các kỹ thuật quét sử dụng trong bài

| Tùy chọn | Kỹ thuật | Ghi chú |
|---|---|---|
| `-sn` | Host discovery (ping scan) | Không quét cổng, chỉ xác định host "up" |
| `-sT` | TCP Connect scan | Hoàn tất bắt tay 3 bước qua system call `connect()`, không cần quyền root |
| `-sS` | SYN (half-open) scan | Gửi raw packet SYN, nhận SYN/ACK thì gửi RST; cần `sudo`/root |
| `-sF` / `-sX` / `-sN` | FIN / Xmas / NULL scan | Dựa trên hành vi TCP theo RFC 793; kết quả phụ thuộc TCP/IP stack và firewall |
| `-sA` | ACK scan | Phân biệt `filtered` / `unfiltered`, dùng để suy luận chính sách lọc |
| `-sU` | UDP scan | Chậm, nhiều `open\|filtered` do UDP không có bắt tay |
| `-sV` | Version detection | Nhận diện dịch vụ và phiên bản |
| `-O` | OS detection | Fingerprinting hệ điều hành |
| `-A` | Aggressive | `-sV` + `-O` + traceroute + default scripts |
| `--script` | NSE | Chạy Nmap Scripting Engine (vd: `smb-os-discovery`, `smb-vuln-ms17-010`) |
| `-oN` / `-oX` / `-oG` / `-oA` | Output | Normal / XML / Grepable / cả ba định dạng |

## 4. Kịch bản

**Bối cảnh:** Sinh viên là kỹ thuật viên **Blue Team** của một phòng thực hành. Quản trị viên chỉ cung cấp dải mạng `192.168.56.0/24` và yêu cầu lập **bản kiểm kê các host, cổng, dịch vụ và rủi ro cơ bản** trước khi nghiệm thu. Mọi mục tiêu đều là VM của chính sinh viên. Sinh viên **không được giả định IP máy đích** – phải phát hiện và chứng minh bằng kết quả quét.

Sau vòng rà soát đầu tiên, quản trị viên thực hiện hardening (tắt dịch vụ không cần thiết hoặc bật firewall); sinh viên phải **chứng minh thay đổi bằng hai bản quét trước/sau**, không chỉ mô tả bằng lời.

## 5. Môi trường thực hành

| Thành phần | Khuyến nghị | Ghi chú |
|---|---|---|
| Máy thật | Windows 10 hoặc Windows 11 64-bit | Tài khoản có quyền Administrator |
| RAM | Tối thiểu 8 GB; khuyến nghị 16 GB | 2–4 GB cho Kali, 1 GB cho Metasploitable 2 |
| Ổ đĩa trống | Tối thiểu 25–40 GB | Bao gồm VM và snapshot |
| Virtualization | Intel VT-x / AMD-V bật trong BIOS/UEFI | Kiểm tra: Task Manager > Performance > CPU |
| VirtualBox | Bản hiện hành tương thích hệ điều hành | Không bắt buộc Extension Pack |
| Kali Linux | VM cài sẵn hoặc ISO chính thức | Máy quét |
| Metasploitable 2 | Máy ảo mục tiêu cố ý có lỗ hổng | **Chỉ nối Host-Only** |
| Nmap + Npcap + Zenmap | Bản ổn định mới nhất từ `nmap.org/download.html` | Không dùng bản crack/repack |

### Sơ đồ mạng

```
                 VirtualBox Host-Only Network 192.168.56.0/24
   ┌──────────────────────┬──────────────────────────┬──────────────────────────┐
   │                      │                          │                          │
 Windows Host        Kali Linux VM            Metasploitable 2 VM       Windows VM (tùy chọn)
 (Host-Only adapter)  192.168.56.10 – máy quét  192.168.56.101 – máy đích   máy đích đối chiếu
```

### Bảng IP thực tế (điền sau khi kiểm tra ở mục 6.4)

| Thiết bị | IP thực tế | Subnet | Ghi chú |
|---|---|---|---|
| Windows Host | *(điền)* | *(điền)* | VirtualBox Host-Only adapter |
| Kali VM | *(điền)* | *(điền)* | Máy quét |
| Metasploitable 2 | *(điền)* | *(điền)* | Máy đích |
| Windows VM (tùy chọn) | *(điền)* | *(điền)* | Máy đích đối chiếu |

> Trong README này, IP `192.168.56.101` được dùng làm ví dụ cho Metasploitable 2 – **thay bằng IP thực tế** phát hiện được.

## 6. Cách dựng môi trường

> **Quy tắc "tự gõ lệnh":** không copy/paste câu lệnh từ LLM, chatbot hoặc web. Mỗi lệnh phải tự gõ, tự sửa lỗi nếu sai và chụp lại màn hình sau khi lệnh chạy.

### Bước 1. Cài Nmap + Npcap + Zenmap trên Windows 10/11
1. Tự nhập địa chỉ `nmap.org/download.html`, mục **Microsoft Windows binaries**, chọn **Latest stable release self-installer**.
2. Nhấp phải tệp cài đặt → **Run as administrator**.
3. Giữ các thành phần: **Nmap Core Files, Register Nmap Path, Npcap, Zenmap**.
4. Khi trình cài Npcap xuất hiện, giữ cấu hình mặc định; hoàn thành Npcap rồi tiếp tục Nmap.
5. Đóng các cửa sổ Terminal cũ để nạp lại `PATH`, mở Terminal mới (Administrator) và kiểm tra:
```powershell
nmap --version
```
- Kết quả đạt: hiển thị dòng `Nmap version ...` và thông tin platform. Nếu báo `nmap is not recognized...` → mở lại Terminal hoặc cài lại với tùy chọn đăng ký PATH.

### Bước 2. Kiểm tra IP Host-Only trên Windows
```powershell
ipconfig
```
- Tìm adapter **VirtualBox Host-Only Network**, ghi IPv4 Address và Subnet Mask. **Không** dùng IP Wi-Fi/Ethernet thật để quét.

### Bước 3. Cài Nmap (và Zenmap – tùy chọn) trên Kali Linux
Tạm bật **Adapter 1 = NAT** để Kali có Internet khi cài gói:
```bash
sudo apt update
sudo apt install -y nmap
nmap --version
sudo apt install -y zenmap        # tùy chọn – giao diện đồ họa
```
- Sau khi cài xong: **tắt Kali, ngắt NAT**, chỉ giữ Host-Only Adapter trước khi quét.
- Nếu Zenmap không mở được: không coi là lỗi Nmap; hoàn thành lab bằng Terminal.

### Bước 4. Thiết lập Host-Only trong VirtualBox
1. VirtualBox Manager → **Tools / Network** → tạo Host-Only Network (nếu chưa có), dải `192.168.56.0/24`, có thể bật DHCP.
2. **Kali VM:** Adapter 1 = Host-Only Adapter (NAT chỉ bật tạm khi cập nhật).
3. **Metasploitable 2:** chỉ dùng Host-Only Adapter – **tuyệt đối không Bridge** vào mạng thật.
4. Tạo snapshot **`Before-LAB4`** cho từng VM trước khi thực hành.

### Bước 5. Lấy IP thật của từng máy
```bash
# Trên Kali
ip -br addr
# Trên Metasploitable 2 (msfadmin/msfadmin)
ifconfig
```

### Bước 6. Kiểm tra kết nối trước khi quét
```bash
ping -c 4 192.168.56.101
```
Nếu ping thất bại, **không chuyển sang bước quét**. Kiểm tra: (1) hai VM cùng Host-Only Network; (2) subnet mask; (3) IP có trùng không; (4) máy đích đã khởi động; (5) firewall máy đích có chặn ICMP không. Nếu ICMP bị chặn nhưng địa chỉ đúng → dùng thêm `-Pn` ở các bài sau.

## 7. Nội dung đã thực hiện

Tạo thư mục lưu kết quả trên Kali:
```bash
mkdir -p ~/LAB4/Evidence && cd ~/LAB4/Evidence
```

### 7.1. Nhiệm vụ 1 – Phát hiện các host đang hoạt động
- [ ] Xác nhận IP Host-Only của máy quét (`ip -br addr`).
- [ ] Host discovery toàn dải /24:
```bash
sudo nmap -sn 192.168.56.0/24
```
- [ ] Ghi từng host "up", MAC và vendor NIC; đối chiếu số host với số VM đang bật. Host dư có thể là adapter máy thật hoặc DHCP server của VirtualBox.

| STT | IP phát hiện | MAC/Vendor | Vai trò suy đoán | Bằng chứng |
|---|---|---|---|---|
| 1 | *(điền)* | | | |
| 2 | *(điền)* | | | |
| 3 | *(điền)* | | | |

### 7.2. Khảo sát cổng TCP và so sánh kỹ thuật quét

#### 7.2.1. TCP Connect scan (`-sT`)
```bash
nmap -sT 192.168.56.101
```
- [ ] Ghi tổng số cổng open/closed/filtered; chọn ít nhất 3 cổng open và ghi dịch vụ Nmap suy đoán.
- [ ] Nhận xét vì sao `-sT` không cần raw packet privileges như `-sS`.

#### 7.2.2. SYN scan (`-sS`)
```bash
sudo nmap -sS 192.168.56.101
```

| Tiêu chí | `-sT` | `-sS` | Nhận xét |
|---|---|---|---|
| Cổng open | | | |
| Cổng closed | | | |
| Cổng filtered | | | |
| Thời gian quét | | | |
| Quyền cần thiết | user thường | root/sudo | |

#### 7.2.3. FIN / Xmas / NULL scan
Chỉ chạy vào Metasploitable 2 và Windows VM của chính sinh viên.
```bash
sudo nmap -sF 192.168.56.101
sudo nmap -sX 192.168.56.101
sudo nmap -sN 192.168.56.101
```
- [ ] **Không** ghi đơn giản "`open|filtered` = open". Trạng thái này nghĩa là Nmap không phân biệt được cổng mở hay bị bộ lọc làm im lặng; kết quả phụ thuộc TCP/IP stack và firewall của mục tiêu.

#### 7.2.4. ACK scan – quan sát chính sách lọc
```bash
sudo nmap -sA 192.168.56.101
```
- [ ] ACK scan phân biệt `filtered` / `unfiltered`, **không** khẳng định cổng open.
- [ ] So sánh với SYN scan trên cùng mục tiêu; giải thích ý nghĩa cổng `unfiltered` (gói ACK đi qua được bộ lọc).

### 7.3. Quét UDP có kiểm soát
Chỉ quét nhóm cổng phổ biến để bài lab đủ thời gian:
```bash
sudo nmap -sU --top-ports 20 192.168.56.101
```

| Cổng UDP | Trạng thái | Dịch vụ | Giải thích/quan sát |
|---|---|---|---|
| *(điền)* | | | |

### 7.4. Nhận diện dịch vụ và hệ điều hành

#### 7.4.1. Version detection (`-sV`)
```bash
nmap -sV 192.168.56.101
```

| Port | Protocol | Service | Version Nmap phát hiện | Ghi chú rủi ro |
|---|---|---|---|---|
| 21 | tcp | ftp | *(điền)* | |
| 22 | tcp | ssh | *(điền)* | |
| 80 | tcp | http | *(điền)* | |
| 445 | tcp | smb | *(điền)* | |
| 3306 | tcp | mysql | *(điền)* | |

#### 7.4.2. OS detection (`-O`)
```bash
sudo nmap -O 192.168.56.101
```

#### 7.4.3. Aggressive scan (`-A`) – dùng để tổng hợp, không thay thế phân tích
```bash
sudo nmap -A 192.168.56.101
```
- [ ] Ghi các thành phần `-A` cung cấp: version detection, OS detection, traceroute, default scripts.
- [ ] So sánh lượng thông tin và thời gian với `-sV` / `-O` riêng lẻ; giải thích vì sao scan "nhiều thông tin" tạo nhiều lưu lượng và dễ bị phát hiện hơn.

### 7.5. NSE – kiểm tra thông tin và lỗ hổng SMB trong lab
Chỉ chạy NSE vào Metasploitable 2 hoặc Windows VM do chính sinh viên quản lý. Mục tiêu là **nhận biết dấu hiệu rủi ro để đề xuất phòng thủ, không khai thác**.

#### 7.5.1. Thu thập thông tin SMB
```bash
nmap -p 445 --script smb-os-discovery 192.168.56.101
```
- [ ] Ghi OS / tên máy / domain nếu script trả về. Nếu 445 đóng hoặc bị lọc, giải thích vì sao script không thu thập được.

#### 7.5.2. Kiểm tra MS17-010
```bash
nmap -p 445 --script smb-vuln-ms17-010 192.168.56.101
```
- [ ] Chỉ ghi "có dấu hiệu dễ bị ảnh hưởng" khi script báo **VULNERABLE**. Nếu script báo không kết nối được, timed out hoặc không xác định → **không** tự suy diễn là đã vá.

| Mục tiêu | 445/tcp | Kết quả script | Kết luận | Biện pháp phòng thủ |
|---|---|---|---|---|
| Metasploitable 2 | *(điền)* | | | |
| Windows VM (nếu có) | *(điền)* | | | |

### 7.6. Xuất kết quả và tạo hồ sơ bằng chứng
```bash
# Normal text
nmap -sV 192.168.56.101 -oN scan.txt
# XML
nmap -sV 192.168.56.101 -oX scan.xml
# Grepable + lọc nhanh cổng 445 (phải tạo file trước, nếu không grep báo "No such file")
nmap -p 445 192.168.56.0/24 -oG smb.txt
grep "445/open" smb.txt
# Chuyển XML thành HTML
xsltproc scan.xml -o scan.html
```

### 7.7. Tình huống – Trước và sau khi hardening
1. Chọn Windows VM của chính mình hoặc dịch vụ test do giảng viên cung cấp trong Host-Only.
2. Chạy `-sV` và lưu kết quả **before**:
```bash
nmap -sV <IP_Windows_VM> -oN before.txt
```
3. Thực hiện một thay đổi phòng thủ hợp pháp: tắt dịch vụ test, đóng một rule firewall hoặc cập nhật cấu hình mạng.
4. Chạy lại **đúng cùng câu lệnh** và lưu kết quả **after**, sau đó so sánh:
```bash
nmap -sV <IP_Windows_VM> -oN after.txt
diff before.txt after.txt
```
5. Khôi phục snapshot nếu thay đổi làm hỏng môi trường.

| Chỉ tiêu | Before | After | Giải thích |
|---|---|---|---|
| Số cổng open | | | |
| Số cổng filtered | | | |
| Dịch vụ bị thay đổi | | | |
| Tác động an toàn | | | |

### 7.8. Bài tập bổ sung
1. So sánh `-sT`, `-sS` và `-sA` trên cùng Metasploitable 2; lập bảng số cổng open/closed/filtered và giải thích khác biệt.
2. Quét toàn bộ 65535 cổng và so sánh với lần quét mặc định (1000 cổng):
```bash
sudo nmap -p- 192.168.56.101 -oN full_ports.txt
```
3. Chạy `-sV`, tra cứu ít nhất một dịch vụ có phiên bản cũ và ghi CVE tương ứng (nếu có).
4. Chạy `smb-vuln-ms17-010` trên Metasploitable 2 và một Windows đã cập nhật (nếu có), so sánh và giải thích.
5. Quét có decoy và quét thường, quan sát log/kết quả, nêu ý nghĩa phòng thủ của kỹ thuật né tránh:
```bash
sudo nmap -sS -D RND:5 192.168.56.101
```
6. Xuất cả ba định dạng và so sánh cách trình bày của `.nmap`, `.xml`, `.gnmap`:
```bash
sudo nmap -sV 192.168.56.101 -oA lab4_full
```

**Tình huống mở rộng – Lập bản đồ dịch vụ:** host discovery toàn dải `192.168.56.0/24`, quét `-sV` từng host tìm được, tổng hợp vào bảng; nêu **3 dịch vụ rủi ro nhất** và đề xuất biện pháp khắc phục.

| Host | Cổng mở | Dịch vụ / phiên bản | Mức rủi ro | Biện pháp khắc phục |
|---|---|---|---|---|
| *(điền)* | | | | |

## 8. Danh sách ảnh chụp bằng chứng (bắt buộc)

| Ảnh | Nội dung cần chụp | Tên tệp đề nghị |
|---|---|---|
| 1 | `ip -br addr` trên Kali, thấy rõ interface Host-Only và IP | `A1_Kali_IP.png` |
| 2 | `ifconfig`/`ip` trên Metasploitable 2, thấy IP thật của máy đích | `A2_Metasploitable_IP.png` |
| 3 | Kết quả host discovery `-sn` | `A3_HostDiscovery.png` |
| 4 | Kết quả `-sS` hoặc `-sT` | `A4_TCP_Scan.png` |
| 5 | Kết quả `-sV` | `A5_Version_Detection.png` |
| 6 | Kết quả `-O` hoặc `-A` | `A6_OS_Aggressive.png` |
| 7 | Một NSE script và kết luận dựa trên chính output | `A7_NSE_SMB.png` |
| 8 | Tệp kết quả được lưu (`.txt`/`.xml`) và/hoặc HTML | `A8_Output_Files.png` |

Ảnh bổ sung nên có: `nmap --version` trên Windows và Kali, cấu hình Host-Only trong VirtualBox, ping Kali → Metasploitable 2, FIN/Xmas/NULL, ACK, UDP, before/after hardening.

## 9. Kết quả PASS/FAIL

| Nhiệm vụ | Điều kiện PASS | Kết quả | Ghi chú |
|---|---|---|---|
| Cài đặt | `nmap --version` chạy được trên Windows và Kali | *(PASS/FAIL)* | |
| Môi trường | Kali & Metasploitable 2 cùng Host-Only, ping thông, không Bridge/NAT khi quét | *(PASS/FAIL)* | |
| Host discovery | Liệt kê đủ host "up", giải thích host dư | *(PASS/FAIL)* | |
| TCP scan | Có bảng so sánh `-sT`/`-sS`; phân tích đúng FIN/Xmas/NULL và ACK | *(PASS/FAIL)* | |
| UDP scan | Quét top 20 cổng UDP, giải thích `open\|filtered` | *(PASS/FAIL)* | |
| Service/OS | Bảng version `-sV`, kết quả `-O`/`-A` | *(PASS/FAIL)* | |
| NSE | Kết luận MS17-010 dựa đúng output script | *(PASS/FAIL)* | |
| Output | Có tệp `.txt`, `.xml`, `.gnmap`, `.html` | *(PASS/FAIL)* | |
| Hardening | Có before/after cùng lệnh, chứng minh thay đổi port state | *(PASS/FAIL)* | |

## 10. Lỗi gặp phải và cách khắc phục

| # | Lỗi / hiện tượng | Nguyên nhân | Cách khắc phục |
|---|---|---|---|
| 1 | `nmap is not recognized...` trên Windows | Chưa nạp lại `PATH` hoặc bỏ chọn Register Nmap Path | Mở lại Terminal; cài lại và chọn Register Nmap Path |
| 2 | Ping Kali → Metasploitable 2 thất bại | Hai VM khác mạng Host-Only, sai subnet, trùng IP hoặc máy đích chưa bật | Kiểm tra lại cấu hình adapter, `ip -br addr`/`ifconfig` |
| 3 | Host hiển thị "down" dù IP đúng | Firewall máy đích chặn ICMP | Thêm `-Pn` để bỏ qua host discovery |
| 4 | `-sS`, `-O`, `-sU` báo *requires root privileges* | Cần raw socket | Chạy với `sudo` |
| 5 | `grep "445/open" smb.txt` báo *No such file* | Chưa chạy lệnh `nmap ... -oG smb.txt` | Chạy bước tạo tệp trước rồi mới `grep` |
| 6 | Zenmap không mở trên Kali | Thiếu DISPLAY/desktop session hoặc gói GTK | Không ảnh hưởng bài lab; dùng Terminal |
| 7 | UDP scan chạy rất lâu | UDP không bắt tay, Nmap phải chờ timeout/rate limit ICMP | Giới hạn `--top-ports 20` |
| … | *(bổ sung lỗi thực tế gặp phải khi thực hành)* | | |

## 11. Câu hỏi phân tích cần trả lời trong báo cáo

1. Sự khác nhau giữa open, closed và filtered là gì? Nêu một tình huống cho mỗi trạng thái.
2. Tại sao `-sS` thường cần quyền cao hơn `-sT`? Hai kỹ thuật khác nhau ở cơ chế thiết lập kết nối như thế nào?
3. Vì sao FIN/Xmas/NULL có thể cho kết quả khó diễn giải trên một số hệ điều hành hoặc firewall?
4. ACK scan trả lời câu hỏi gì khác với SYN scan?
5. Tại sao UDP scan thường chậm và dễ xuất hiện `open|filtered`?
6. `-sV` đóng vai trò gì trong quản lý lỗ hổng? Tại sao chỉ biết port 80 là chưa đủ?
7. OS fingerprinting có những giới hạn nào? Vì sao không nên coi kết quả `-O` là tuyệt đối?
8. NSE script báo timeout có đồng nghĩa "không có lỗ hổng" không? Giải thích.
9. So sánh before/after hardening: thay đổi nào trong port state chứng minh biện pháp phòng thủ có hiệu lực?
10. Nêu ba cấu hình phòng thủ giúp giảm bề mặt tấn công mà không dựa vào "ẩn mình" trước Nmap.
11. Vì sao quét toàn bộ 65535 cổng tốn nhiều thời gian hơn hẳn quét mặc định? Khi nào cần quét đầy đủ?
12. Kỹ thuật decoy (`-D`) và fragmentation (`-f`) giúp kẻ tấn công né tránh thế nào, và IDS/firewall cần làm gì để chống lại?
13. Giải thích vì sao `-oA` (xuất cả ba định dạng) hữu ích khi làm hồ sơ bằng chứng cho một cuộc đánh giá.
14. Nếu một host trả về toàn bộ cổng ở trạng thái filtered, điều đó gợi ý gì về cấu hình firewall của host đó?

## 12. Yêu cầu nộp bài và cấu trúc thư mục LAB4

### Yêu cầu nộp bài
- Báo cáo Word (.docx) đặt tên `[MãLớp]-LAB4_MSSV-HoTen.docx`; đầu báo cáo ghi môi trường thực hành, bảng IP thực tế và link video (nếu lớp yêu cầu).
- Repository GitHub cá nhân `LAB_AT_BMHTTT` ở chế độ **Public**, có thư mục `LAB4` riêng.
- `LAB4/` tối thiểu gồm: `README.md`, báo cáo, ảnh minh chứng và các tệp kết quả Nmap (`.nmap`/`.txt`, `.xml`, `.gnmap`, `.html`).
- **Không** đưa installer Nmap/Npcap, file ISO/OVA máy ảo vào repo.
- **Không** đưa kết quả quét mạng thật hoặc IP/tên miền bên ngoài phạm vi lab.
- Trước hạn nộp: commit/push toàn bộ, mở URL repo trong trình duyệt không đăng nhập để kiểm tra quyền truy cập, dán URL vào Google Classroom.

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

## 13. Tài liệu tham khảo

1. Nmap Project. *Download the Free Nmap Security Scanner for Linux/Mac/Windows*. https://nmap.org/download.html
2. Nmap Project. *Windows – Nmap Network Scanning*. https://nmap.org/book/inst-windows.html
3. Nmap Project. *Nmap Reference Guide*. https://nmap.org/book/man.html
4. Kali Linux. *nmap | Kali Linux Tools*. https://www.kali.org/tools/nmap/
5. Kali Linux Documentation. *Kali inside VirtualBox (Guest VM)*. https://www.kali.org/docs/virtualization/install-virtualbox-guest-vm/
6. Rapid7. *Metasploitable 2* – máy ảo mục tiêu cố ý dễ bị tổn thương cho học tập. https://docs.rapid7.com/metasploit/metasploitable-2/
7. Microsoft. *Security Bulletin MS17-010 – Security Update for Microsoft Windows SMB Server*. https://learn.microsoft.com/security-updates/securitybulletins/2017/ms17-010
