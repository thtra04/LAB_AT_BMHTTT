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
| Báo cáo | [11CNPM2-Lab6_1150080120-HoangThanhTra.docx](11CNPM2-Lab6_1150080120-HoangThanhTra.docx) *(đặt tên theo yêu cầu `[Mã lớp]-Lab6_MSSV-TenSV.docx`)* |
| File cấu hình | `config.xml` (Diagnostics → Backup & Restore → Download configuration) |

## 2. Tên bài Lab

**Lab 6: Xác thực Active Directory và chính sách truy cập trên pfSense** – pfSense CE với bốn interface WAN / MGMT / LAN / DMZ, tích hợp Active Directory (domain `lab6.test`) qua LDAP, Captive Portal xác thực user domain, Firewall Alias, Schedule và các website mô phỏng trong DMZ.

### Mục tiêu
- Dựng một pfSense riêng cho Lab 6 (không dùng lại cấu hình Lab 5) với 4 interface: WAN, MGMT, LAN, DMZ.
- Tích hợp pfSense với Active Directory bằng LDAP, kiểm tra bằng **Diagnostics → Authentication**.
- Cấu hình **Captive Portal** trên LAN dùng Active Directory làm nguồn xác thực.
- Tạo **Alias** cho máy trạm, nhóm máy trạm và các website mô phỏng; tạo **Schedule** theo khung giờ.
- Thiết kế policy theo kịch bản: chặn site theo máy, chặn nhóm site, cho phép theo giờ, giới hạn dịch vụ, cô lập DMZ.
- Hiểu giới hạn: firewall rule chuẩn của pfSense khớp theo IP/port/interface/schedule, **không** dùng trực tiếp username LDAP làm điều kiện rule.
- Bật logging, Reset States khi cần và chứng minh kết quả bằng kiểm thử trước/sau.

## 3. Mô hình mạng

### 3.1. Bảng địa chỉ IP

| Thiết bị / interface | Địa chỉ | Gateway / DNS | Vai trò |
|---|---|---|---|
| pfSense WAN | DHCP trên 192.168.250.0/24 | Gateway của NAT Network | Ra Internet |
| pfSense MGMT | 192.168.56.254/24 | — | WebGUI riêng cho máy thật |
| Máy thật quản trị | 192.168.56.1/24 | Không gateway/DNS | Chỉ quản trị pfSense |
| pfSense LAN | 10.6.0.1/24 | — | Gateway LAN-DOMAIN |
| DC01 | 10.6.0.10/24 | GW 10.6.0.1; DNS 10.6.0.10 | AD DS + DNS, domain `lab6.test` |
| Client-A | 10.6.0.21/24 | GW 10.6.0.1; DNS 10.6.0.10 | Máy đại diện tài khoản `sv_a` |
| Client-B | 10.6.0.22/24 | GW 10.6.0.1; DNS 10.6.0.10 | Máy đại diện tài khoản `sv_b` |
| pfSense DMZ | 172.16.6.1/24 | — | Gateway DMZ |
| DMZ-WEB | 172.16.6.10/24 (+ .20/.30/.40) | GW 172.16.6.1 | Nginx, IP phụ mô phỏng nhóm website |

### 3.2. Card mạng của pfSense-LAB6 (đề bài VirtualBox ↔ thực hiện trên VMware Workstation)

| Adapter | VirtualBox (đề bài) | VMware Workstation (tương đương) | Vai trò |
|---|---|---|---|
| 1 | NAT Network `LAB6-WAN` 192.168.250.0/24, DHCP | NAT (VMnet8) – có thể đổi subnet VMnet8 thành 192.168.250.0/24 trong Virtual Network Editor | WAN |
| 2 | Host-Only 192.168.56.0/24 | Host-only VMnet mới (ví dụ VMnet3) 192.168.56.0/24, **tắt DHCP** | MGMT |
| 3 | Internal Network `lab6-lan` | LAN Segment `lab6-lan` | LAN |
| 4 | Internal Network `lab6-dmz` | LAN Segment `lab6-dmz` | DMZ |

> **Lưu ý trên máy thực hành:** card *VirtualBox Host-Only* (Ethernet 7) đang dùng sẵn 192.168.56.1 – khi làm trên VMware phải tắt card này (hoặc chỉ dùng VirtualBox) để tránh trùng subnet MGMT. Sau khi boot pfSense, dùng **Assign Interfaces** và đối chiếu **MAC address** của từng adapter thay vì học thuộc tên em0/em1.

### 3.3. Tài nguyên máy ảo

| Máy ảo | Khuyến nghị | Ghi chú |
|---|---|---|
| pfSense-LAB6 | 2 GB RAM, 2 vCPU, 16 GB disk | VM mới hoặc clone từ snapshot pfSense sạch; **không** clone config Lab 5 |
| DC01 | Windows Server 2019/2022 (dùng 2025 Evaluation), 2–4 GB RAM | AD DS + DNS, domain `lab6.test` |
| Client-A | Windows 11, 4 GB RAM | Chỉ bật khi kiểm thử A |
| Client-B | Windows 11 hoặc máy trạm tương đương | Chỉ bật khi kiểm thử B |
| DMZ-WEB | Ubuntu Server 22.04/24.04, 1–2 GB RAM | Nginx + IP phụ .20/.30/.40 |

## 4. Các bước thực hiện

### 4.1. Đặt IP các interface pfSense

| Interface | IPv4 | DHCP Server | Ghi chú |
|---|---|---|---|
| WAN | DHCP | — | Nhận 192.168.250.x |
| MGMT | 192.168.56.254/24 | Tắt | Chỉ WebGUI – truy cập `https://192.168.56.254` |
| LAN | 10.6.0.1/24 | Tắt | Client dùng IP tĩnh để policy dễ kiểm chứng |
| DMZ | 172.16.6.1/24 | Tắt | DMZ-WEB dùng IP tĩnh |

### 4.2. Domain Controller DC01
1. IP 10.6.0.10/24, Gateway 10.6.0.1, Preferred DNS 10.6.0.10.
2. Cài **AD DS + DNS**, tạo forest mới `lab6.test`; cấu hình **Forwarders** tới DNS upstream.
3. Tạo OU `LAB6-Users` và hai user `sv_a`, `sv_b`.
4. Tạo service account `svc_pfsense_ldap` (mật khẩu riêng, **không** cấp Domain Admin) – dùng làm LDAP bind.

### 4.3. Client-A / Client-B và DMZ-WEB
- Client-A: 10.6.0.21/24, DNS 10.6.0.10, thử bằng `sv_a`; Client-B: 10.6.0.22/24, DNS 10.6.0.10, thử bằng `sv_b` (join domain là tùy chọn).
- DMZ-WEB: cài Nginx, gán thêm 3 IP phụ để mô phỏng nhóm website:

| Địa chỉ | Tên logic | Mô phỏng |
|---|---|---|
| 172.16.6.10 | GENERAL_SITE | Website bình thường |
| 172.16.6.20 | JOB_SITE | Nhóm Job Search |
| 172.16.6.30 | SOCIAL_SITE | Nhóm Social Media |
| 172.16.6.40 | RESTRICTED_SITE | Nhóm Restricted Content |

### 4.4. LDAP Authentication Server (System → User Manager → Authentication Servers → Add)

| Trường | Giá trị |
|---|---|
| Descriptive name | LAB6-AD |
| Type | LDAP |
| Hostname / IP | 10.6.0.10 |
| Port / Transport | 389 / TCP - Standard *(chỉ trong lab cô lập; thực tế dùng LDAPS/STARTTLS)* |
| Protocol version | 3 |
| Search scope | Entire Subtree |
| Base DN | `DC=lab6,DC=test` |
| Authentication Containers | `OU=LAB6-Users,DC=lab6,DC=test` |
| Bind DN | `CN=svc_pfsense_ldap,CN=Users,DC=lab6,DC=test` |
| Initial Template | Microsoft AD |
| User / Group Naming Attribute | samAccountName / cn |
| Group Member Attribute | memberOf |

Kiểm tra: **Diagnostics → Authentication**, chọn LAB6-AD, thử lần lượt `sv_a`, `sv_b` – chỉ làm tiếp khi cả hai thành công.

### 4.5. Captive Portal (Services → Captive Portal → Add Zone)
- Zone `LAB6_USERS`, Enable, interface **LAN**, Authentication Method: *Use an Authentication backend*, Server: **LAB6-AD** → Save/Apply.
- Kiểm thử: từ Client-A mở `http://172.16.6.10` → portal yêu cầu đăng nhập → `sv_a`; lặp lại trên Client-B với `sv_b`; xem session trên pfSense.

### 4.6. Alias (Firewall → Aliases) và Schedule (Firewall → Schedules)

| Alias | Type | Giá trị |
|---|---|---|
| CLIENT_A | Host | 10.6.0.21 |
| CLIENT_B | Host | 10.6.0.22 |
| POLICY_CLIENTS | Host(s) | 10.6.0.21, 10.6.0.22 |
| GENERAL_SITE / JOB_SITE / SOCIAL_SITE / RESTRICTED_SITE | Host | 172.16.6.10 / .20 / .30 / .40 |
| WEB_PORTS | Port(s) | 80, 443 |

| Schedule | Khung giờ | Mục đích |
|---|---|---|
| LUNCH_WINDOW | 11:30–13:00, Thứ 2–Thứ 6 | Cho phép SOCIAL_SITE với Client-B |
| WORK_HOURS | 08:00–17:00, Thứ 2–Thứ 6 | Giới hạn dịch vụ Internet trong giờ hành chính |
| TEST_NOW | 10–15 phút quanh thời điểm thực hành | Chỉ để kiểm chứng nhanh, sau đó xóa/disable |

Kiểm tra alias đã nạp: **Diagnostics → Tables**.

## 5. Các kịch bản chính sách

Trước mỗi kịch bản: **Apply Changes**, tạo kết nối mới; nếu vừa đổi rule quan trọng thì **Diagnostics → States → Reset States**. Rule trên tab LAN xét từ trên xuống, **first-match**.

| # | Kịch bản | Rule chính | Kiểm thử mong đợi |
|---|---|---|---|
| 1 | Client-A bị chặn JOB_SITE | Block CLIENT_A → JOB_SITE TCP/80 (Log); Pass CLIENT_A → GENERAL_SITE TCP/80 | A mở được .10, bị chặn .20; log có 10.6.0.21 → 172.16.6.20 |
| 2 | Cấm RESTRICTED_SITE cho A và B | Block POLICY_CLIENTS → RESTRICTED_SITE TCP/80 (Log); Pass POLICY_CLIENTS → GENERAL_SITE | Cả A và B bị chặn .40, vẫn vào .10 |
| 3 | Client-B chỉ vào SOCIAL_SITE giờ nghỉ | Pass CLIENT_B → SOCIAL_SITE + LUNCH_WINDOW; Block CLIENT_B → SOCIAL_SITE (Always) | Gắn TEST_NOW: trong giờ vào được .30; ra ngoài giờ bị Block; cuối cùng gắn lại LUNCH_WINDOW |
| 4 | Chỉ HTTP/HTTPS trong giờ hành chính | Pass POLICY_CLIENTS → Any WEB_PORTS + WORK_HOURS; Block POLICY_CLIENTS → Any | Trong giờ: web chạy, ping bị chặn; ngoài giờ: tất cả bị chặn |
| 5 | Cô lập DMZ khỏi LAN | Tab DMZ: Block DMZ net → LAN net; Tab LAN: Pass POLICY_CLIENTS → GENERAL_SITE | Client-A → .10 Pass; DMZ-WEB → 10.6.0.10 Block |
| 6 | So sánh Block và Reject | Cùng source/destination, lần 1 Block, lần 2 Reject | Block: client chờ timeout; Reject: báo lỗi ngay |
| 7 | Firewall Log và State Table | Bật log rule Block, tạo một phép thử mới | Status → System Logs → Firewall lọc theo IP client; Diagnostics → States |

### Ruleset tổng hợp trên LAN (thứ tự là một phần của đáp án)

| Ưu tiên | Rule | Mục đích |
|---|---|---|
| 1 | Block CLIENT_A → JOB_SITE TCP/80 + Log | A không truy cập Job site |
| 2 | Block POLICY_CLIENTS → RESTRICTED_SITE TCP/80 + Log | A và B đều bị chặn Restricted |
| 3 | Pass CLIENT_B → SOCIAL_SITE TCP/80 + LUNCH_WINDOW | B được Social trong giờ nghỉ |
| 4 | Block CLIENT_B → SOCIAL_SITE TCP/80 | Ngoài giờ nghỉ B bị chặn |
| 5 | Pass POLICY_CLIENTS → GENERAL_SITE TCP/80 | Site thường được phép |
| 6 | Pass POLICY_CLIENTS → Any WEB_PORTS + WORK_HOURS | Web Internet trong giờ hành chính |
| 7 | Block POLICY_CLIENTS → Any + Log | Explicit deny cuối ruleset |

## 6. Bảng kiểm thử bắt buộc

| Nguồn | Đích | Trong schedule | Ngoài schedule | Kết quả thực tế |
|---|---|---|---|---|
| Client-A | GENERAL_SITE .10 | Allow | Allow | *(chưa thực hiện)* |
| Client-A | JOB_SITE .20 | Block | Block | *(chưa thực hiện)* |
| Client-A | RESTRICTED_SITE .40 | Block | Block | *(chưa thực hiện)* |
| Client-B | SOCIAL_SITE .30 | Allow trong LUNCH | Block | *(chưa thực hiện)* |
| Client-B | RESTRICTED_SITE .40 | Block | Block | *(chưa thực hiện)* |
| DMZ-WEB | DC01 10.6.0.10 | Block | Block | *(chưa thực hiện)* |

## 7. Xử lý sự cố theo trình tự

| Hiện tượng | Kiểm tra |
|---|---|
| Không vào được WebGUI | Host-only MGMT → IP máy thật 192.168.56.1/24 → pfSense MGMT 192.168.56.254 → anti-lockout/rule MGMT |
| LDAP test fail | Routing pfSense → 10.6.0.10 → port 389 → Base DN/OU → Bind DN/password → trạng thái user |
| Captive Portal không hiện | Zone/interface → DNS → dùng trang HTTP để test → session cũ → IPv6 |
| Rule chặn không có tác dụng | Thứ tự rule → state cũ → đúng interface → alias source/destination → protocol/port |
| Schedule không đúng | Time zone pfSense → schedule Active/Inactive → có rule Block phía dưới hay không |
| DMZ site không mở | Dịch vụ Nginx → IP .10/.20/.30/.40 → route/gateway → rule LAN → firewall trên DMZ-WEB |
| Log không thấy packet | Đã bật log đúng rule → tạo traffic mới → lọc log theo đúng IP client |

## 8. Tóm tắt câu trả lời phần J (12 câu hỏi)

| Câu | Ý chính |
|---|---|
| 1 | Lab 6 cần 4 interface (thêm MGMT), subnet khác (10.6.0.0/24, 172.16.6.0/24) và ruleset mới; dùng chung topology Lab 5 sẽ lẫn rule/NAT cũ, trùng IP và làm hỏng minh chứng của Lab 5 – topology riêng giúp tái lập và kiểm chứng độc lập. |
| 2 | LDAP dùng để **xác thực người dùng** (Captive Portal, đăng nhập WebGUI, VPN). Firewall rule chuẩn **không** dùng được username AD làm Source; rule chỉ khớp IP/port/interface/schedule, nên phải ánh xạ user → IP tĩnh (alias CLIENT_A/CLIENT_B). |
| 3 | Captive Portal chặn và bắt đăng nhập lưu lượng của người dùng trên LAN; WebGUI tách sang MGMT để kênh quản trị không đi qua portal, không bị người dùng LAN tiếp cận và không bị mất quyền quản trị khi cấu hình portal/rule sai. |
| 4 | Entire Subtree tìm trong Base DN **và mọi OU con** bên dưới, nên user nằm trong OU lồng nhau vẫn được tìm thấy; One Level chỉ tìm ở cấp ngay dưới Base DN. |
| 5 | Mật khẩu bind được lưu trên firewall (config.xml); dùng service account chỉ có quyền đọc theo nguyên tắc đặc quyền tối thiểu – nếu lộ chỉ đọc được thư mục, còn lộ Domain Admin là mất toàn bộ domain. |
| 6 | Khi LUNCH_WINDOW không active, rule Pass có schedule coi như **không tồn tại** (không tự đảo thành Block); thiếu rule Block bên dưới thì lưu lượng rơi xuống rule sau (ví dụ Pass WEB_PORTS trong WORK_HOURS) và vẫn được cho qua. |
| 7 | Client và DC01 cùng subnet 10.6.0.0/24 nên truy vấn DNS đi trực tiếp ở lớp 2, **không qua pfSense**; firewall chỉ xử lý lưu lượng đi qua interface của nó. Chỉ DC01 cần được phép truy vấn DNS upstream ra ngoài. |
| 8 | Client-A truy cập 172.16.6.20:80: rule 1 (Block CLIENT_A → JOB_SITE) khớp trước nên bị chặn, dù rule 6 (Pass Any WEB_PORTS) cũng khớp. Nếu đưa rule 6 lên đầu, A sẽ vào được JOB_SITE trong giờ hành chính. |
| 9 | pfSense là firewall **stateful**: kết nối đã có state được cho qua mà không xét lại rule; rule mới chỉ áp cho kết nối mới, nên phải mở kết nối mới hoặc Reset States để kết quả phản ánh đúng rule. |
| 10 | Mô hình lab lọc ở L3/L4 theo IP cố định của từng "site"; Web Category Filtering thật hoạt động ở L7 – phân loại URL/domain/SNI theo cơ sở dữ liệu danh mục, xử lý HTTPS và IP CDN thay đổi liên tục (cần proxy/DNS filter như Squid/SquidGuard, pfBlockerNG). |
| 11 | **Block** âm thầm bỏ gói, client chờ đến timeout; **Reject** trả TCP RST (hoặc ICMP unreachable với UDP), client báo lỗi ngay "connection refused". Reject tiện trong LAN, Block phù hợp với WAN vì không lộ thông tin. |
| 12 | Kiểm tra theo thứ tự: rule đã bật *Log packets* và Apply → lưu lượng có thật sự đi qua pfSense (route/gateway, không cùng subnet) → đúng tab interface → có rule nào phía trên khớp trước → state cũ (gói thuộc state không bị log lại) → nội dung alias (Diagnostics → Tables) → protocol/port → bộ lọc và số dòng hiển thị của Firewall Log. |

## 9. Phạm vi đã thực hiện

- [x] Đọc đề, tổng hợp mô hình, bảng IP, cấu hình LDAP/Captive Portal/Alias/Schedule, 7 kịch bản và ruleset tổng hợp vào README.
- [x] Soạn tóm tắt trả lời 12 câu hỏi phần J.
- [x] Báo cáo Word: đủ các phần B–K theo đề, trả lời đầy đủ 12 câu hỏi, giải thích thứ tự ruleset tổng hợp; 33 vị trí dán ảnh minh chứng và các ô kết quả thực tế đánh dấu vàng.
- [ ] Dựng môi trường riêng Lab 6 (pfSense-LAB6 4 adapter, DC01, Client-A/B, DMZ-WEB).
- [ ] Thực hiện LDAP, Captive Portal, Alias, Schedule và 7 kịch bản; chụp ảnh rule + ảnh kiểm thử cho từng kịch bản, Firewall Log, State Table.
- [ ] Điền bảng kết quả thực tế, hoàn thiện báo cáo Word, xuất `config.xml` và quay video.

## 10. Yêu cầu nộp bài (theo đề)

- Thực hiện cá nhân trên đúng mô hình Lab 6.
- Tên file: `[Mã lớp]-Lab6_MSSV-TenSV.docx`.
- Ảnh minh chứng chụp trực tiếp trên máy sinh viên, thấy rõ IP/rule liên quan.
- Bắt buộc có: topology 4 adapter của pfSense-LAB6; LDAP test `sv_a` và `sv_b`; Captive Portal login; Alias; Schedule; mỗi kịch bản ít nhất 1 ảnh rule + 1 ảnh kiểm thử; Firewall Log; State Table.
- Điền đủ bảng kết quả và trả lời 12 câu hỏi.
- Nộp kèm `config.xml` cuối cùng (Diagnostics → Backup & Restore → Download configuration).

## 11. Tài liệu tham khảo

1. Netgate, *pfSense Documentation* – User Management and Authentication; LDAP Authentication Servers; Diagnostics > Authentication.
2. Netgate, *pfSense Documentation* – Captive Portal and Zone Configuration Options.
3. Netgate, *pfSense Documentation* – Firewall Fundamentals, Rule Methodology, Aliases and Time Based Rules.
4. Microsoft Learn – Active Directory Domain Services and DNS on Windows Server.
