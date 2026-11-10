# RUNBOOK LAB 10 — Remote DNS Cache Poisoning (bản thực thi trên VMware)

> SV: Hoàng Thanh Trà — MSSV 1150080120 — Lớp 11CNPM2 — Ngày thực hành: **03/11/2026**
> 📹 = cảnh **cần quay màn hình** làm minh chứng. Mỗi mục ánh xạ tới một ảnh trong báo cáo (xem bảng cuối).
> ✅ **Toàn bộ chuỗi tấn công đã được chạy thử & kiểm chứng thành công** (baseline→PENDING→HIT→CACHE→redirect→Fake Site). Ảnh log thực tế đã chèn sẵn vào báo cáo (Ảnh 5,7,8,9,10, thư mục `baocao/hinh/`). Khi quay, bạn chạy lại theo runbook này để có video + có thể thay ảnh bằng ảnh chụp của bạn.

## 0. Tư tưởng bài & khác biệt với LAB 9
- LAB 9 (folder `LAB8/`) là **local** attack: attacker cùng 1 L2, bật promiscuous, sniff được Transaction ID.
- LAB 10 là **remote**: Kali bị tách sang **ATTACKNET** riêng, **không** sniff được đường resolver↔AUTH-DNS. Phải **đoán TXID 16-bit** qua race relay. Sau đó khôi phục BIND9 hiện đại + hardening.

## 1. Sơ đồ triển khai (2 segment sau pfSense)
```
        ┌──────────────── DNSLAB segment (L2) ───────────────┐
        │  DNS-SERVER ens37 10.9.0.10                         │
        │  VICTIM     ens37 10.9.0.100   (DNS=10.9.0.10)      │
        │  AUTH-DNS   ens37 172.16.6.20  (+alias 172.16.6.10) │
        │  pfSense NIC-A: 10.9.0.1/24  + VIP 172.16.6.1/24    │
        └──────────────────────┬─────────────────────────────┘
                               │ pfSense (định tuyến + firewall)
        ┌──────────────────────┴──── ATTACKNET segment (L2) ─┐
        │  Kali  eth1 10.10.0.200                            │
        │  pfSense NIC-B: 10.10.0.1/24                        │
        └────────────────────────────────────────────────────┘
```
- DNS-SERVER và AUTH-DNS **cùng** DNSLAB segment → nói chuyện on-link (giống LAB9), KHÔNG qua pfSense ⇒ race nhanh.
- Kali ở ATTACKNET ⇒ mọi lưu lượng Kali→DNSLAB/DMZ phải qua pfSense ⇒ **không sniff được** resolver↔AUTH-DNS. Đây là tính "remote".

## 2. Tài khoản (đã kiểm chứng)
| VM | NAT (SSH) | admin | hostkey SHA256 |
|---|---|---|---|
| DNS-SERVER | 192.168.226.132 | thtra / 123456 | EV+sCn6XJ2L3F0/Z7u0V+Ws44i+cbBANARy+EAxofSE |
| VICTIM | 192.168.226.137 | thtra / 123456 | (như trên) |
| AUTH-DNS | 192.168.226.138 | thtra / 123456 | (như trên) |
| Kali | 192.168.226.136 | hoangthanhtra / 1150080120 | BzUdYRoywWPS8VLYAAb4Zo0CfhJU6x99t8gPXA6Ds9s |
| pfSense | WebGUI https://10.0.0.1 | admin / 1150080120 | — |

> Đã snapshot `LAB10_START` cho 5 VM — lỗi gì cứ revert.

---

## 3. 📹 BƯỚC A — Đấu card mạng trong VMware (LAN Segment)
> Quay toàn bộ thao tác VM Settings → Network Adapter.
1. Tạo 2 LAN Segment: mỗi VM đang tắt → **VM > Settings > Network Adapter > LAN Segments… > Add**: tạo `DNSLAB` và `ATTACKNET`.
2. Gán NIC **lab** (card thứ 2, KHÔNG phải NAT) của từng VM:
   - DNS-SERVER (ens37), VICTIM (ens37), AUTH-DNS (ens37) → **LAN Segment = DNSLAB**.
   - Kali (eth1) → **LAN Segment = ATTACKNET**, và **Advanced… > Promiscuous = Deny** (hoặc để mặc định không cho sniff).
3. pfSense: thêm/gán 2 card:
   - NIC-A → **LAN Segment = DNSLAB**.
   - NIC-B → **LAN Segment = ATTACKNET**.
4. Giữ card NAT (ens33/eth0) của các VM Linux **nguyên** để còn SSH/Internet.

📸 **Ảnh 1**: Kali Settings cho thấy chỉ còn ATTACKNET + Promiscuous=Deny.

---

## 4. 📹 BƯỚC B — Cấu hình pfSense (WebGUI https://10.0.0.1, admin/1150080120)
> Quay các trang Interfaces + Firewall.
1. **Interfaces > Assignments**: gán NIC-A và NIC-B thành 2 interface mới, ví dụ **DNSLAB** và **ATTACKNET**.
2. **Interfaces > DNSLAB**: Enable; IPv4 Static; địa chỉ **10.9.0.1/24**; **KHÔNG** Upstream Gateway.
3. **Interfaces > ATTACKNET**: Enable; IPv4 Static; địa chỉ **10.10.0.1/24**; **KHÔNG** Upstream Gateway.
4. **Firewall > Virtual IPs > Add**: Type **IP Alias**, Interface **DNSLAB**, địa chỉ **172.16.6.1/24** (để pfSense định tuyến được tới DMZ 172.16.6.20 nằm trên DNSLAB segment).
5. **Firewall > Rules** — tạo theo `firewall_policy_matrix.csv`:
   - **DNSLAB** interface:
     - Pass UDP/TCP 53: src 10.9.0.100 → dst 10.9.0.10
     - Pass UDP 53: src 10.9.0.10 → dst 172.16.6.20
     - Pass UDP 53: src 10.9.0.10 → dst 10.10.0.200  (sau poison)
     - Pass TCP 80: src 10.9.0.0/24 → dst 10.10.0.200
     - Block+Log: src 10.9.0.0/24 → 10.6.0.0/24, 192.168.56.0/24, rồi Any (cô lập)
   - **ATTACKNET** interface:
     - Pass UDP/TCP 53: src 10.10.0.200 → dst 10.9.0.10
     - Pass UDP 5300: src 10.10.0.200 → dst 172.16.6.20
     - Block+Log: src 10.10.0.0/24 → 10.6.0.0/24, 192.168.56.0/24, rồi Any
6. **Apply Changes** rồi **Diagnostics > States > Reset States**.

📸 **Ảnh 2**: trang Interfaces (DNSLAB 10.9.0.1, ATTACKNET 10.10.0.1). 📸 **Ảnh 3**: ruleset ATTACKNET.

---

## 5. 📹 BƯỚC C — Chạy script setup trong từng VM
> Mở terminal từng VM (hoặc SSH), quay cảnh chạy script + kết quả IP. Script đã có sẵn trong home.
- **DNS-SERVER**: `sudo bash lab10_dns_server.sh`  → ens37=10.9.0.10, BIND baseline OK.
- **VICTIM**: `sudo bash lab10_victim.sh`  → ens37=10.9.0.100, DNS=10.9.0.10.
- **AUTH-DNS**: `sudo bash lab10_auth_dns.sh`  → ens37=172.16.6.20(+.10), web hợp lệ chạy.
- **Kali**: `sudo bash lab10_kali.sh`  → eth1=10.10.0.200, routes qua 10.10.0.1.

📸 **Ảnh 4**: `ip -br addr` 4 máy đúng IP.

---

## 6. 📹 BƯỚC D — Baseline (trước tấn công)
> ⚠️ **Quan trọng (đã kiểm chứng thực tế):** `auth_dns_relay` **chỉ trả lời query đến từ 10.9.0.10 source-port 33333** (chữ ký của resolver mô phỏng). Vì vậy baseline phải chạy **qua resolver mô phỏng**, không phải BIND thường. Trình tự:
> 1. **AUTH-DNS**: `bash ~/lab10_auth_start.sh` (chạy AUTH-DNS hợp lệ + relay).
> 2. **DNS-SERVER**: `bash ~/lab10_dns_attack.sh` (dừng BIND, chạy resolver mô phỏng cổng 33333).
> 3. **VICTIM**: `bash ~/lab10_victim_check.sh` → **www.example.lab10.test = 172.16.6.10**, mở trang "LAB10 LEGIT".

📸 **Ảnh 5 (baseline)**: dig trả 172.16.6.10 + trang hợp lệ.
> (Giữ nguyên AUTH-DNS + resolver đang chạy để sang bước tấn công.)

---

## 7. 📹 BƯỚC E — Chứng minh Kali KHÔNG sniff được DNSLAB
Trên **Kali**: `sudo tcpdump -ni eth1 'udp port 53'`.  Đồng thời trên VICTIM query `dig www.example.lab10.test`.
→ Kali **không** thấy gói 10.9.0.10 ↔ 172.16.6.20 (khác hẳn LAB9). Chỉ thấy gói do chính Kali gửi.

📸 **Ảnh 6**: tcpdump Kali trống (không có traffic DNSLAB).

---

## 8. 📹 BƯỚC F — Tấn công (Kaminsky remote)
AUTH-DNS + resolver mô phỏng đã chạy từ BƯỚC D. Giờ thêm trên **Kali**:
1. Kali T1: `bash ~/lab10_evil_dns.sh`  (malicious DNS 10.10.0.200:53).
2. Kali T2: `bash ~/lab10_fakeweb.sh`  (fake web 10.10.0.200:80).
3. Kali T3: `bash ~/lab10_kaminsky.sh`  (gửi query ngẫu nhiên + 16 batch TXID tới relay, rồi verify).

**Thành công (đã kiểm chứng)**: AUTH-DNS log `[PENDING]`→`[HIT] batch ... contains txid=...`, resolver log `[CACHE] delegation poisoned ... -> 10.10.0.200`, Kali in `www.example.lab10.test A = ['10.10.0.200']` + `SUCCESS`.

📸 **Ảnh 7**: log [PENDING]+[HIT] (AUTH-DNS). 📸 **Ảnh 8**: [CACHE] (resolver). 📸 **Ảnh 9 (packet)**: tcpdump trên DNS-SERVER/AUTH-DNS cho thấy 10.9.0.10:33333 → 172.16.6.20:53 và forged response ngược lại (chạy `sudo tcpdump -ni ens37 udp and port 53 or port 33333` trong lúc tấn công).

---

## 9. 📹 BƯỚC G — Hậu quả trên VICTIM
Trên **VICTIM**: `bash ~/lab10_victim_check.sh`  → giờ **www.example.lab10.test = 10.10.0.200**, mở ra **LAB10 Fake Site**.

📸 **Ảnh 10**: victim trả 10.10.0.200 + mở Fake Site.

---

## 10. 📹 BƯỚC H — Khôi phục BIND9 + Hardening
Trên **DNS-SERVER**: Ctrl+C tắt resolver mô phỏng → `bash ~/lab10_dns_restore.sh`.
- BIND9 chạy lại (baseline), chỉ cho 10.9.0.0/24 recursion ⇒ Kali ATTACKNET không dùng được như open resolver.
- Chứng minh **source-port randomization**: `sudo tcpdump -ni ens37 'udp and port 53'` rồi dig nhiều lần từ VICTIM → source port **đổi ngẫu nhiên**, không còn 33333.
- Sau buổi lab: disable rule UDP/5300, tắt interface ATTACKNET (hoặc revert snapshot).

📸 **Ảnh 11**: BIND9 chạy lại + source port ngẫu nhiên (khác 33333).

---

## 11. Ánh xạ ảnh → mục nộp bài (mục L đề)
| Yêu cầu nộp | Ảnh |
|---|---|
| pfSense ATTACKNET + ruleset cô lập | Ảnh 2, 3 |
| Kali chỉ còn ATTACKNET, Promiscuous=Deny | Ảnh 1 |
| Baseline victim → 172.16.6.10 | Ảnh 5 |
| AUTH-DNS [PENDING]/[HIT] | Ảnh 7 |
| Resolver [CACHE] | Ảnh 8 |
| Packet 10.9.0.10:33333→172.16.6.20 + forged | Ảnh 9 |
| Victim sau poison → 10.10.0.200 + Fake Site | Ảnh 10 |
| Hardening: BIND9 + source port ngẫu nhiên | Ảnh 11 |
| Bảng so sánh baseline/attack/restore | (trong báo cáo) |

## 12. Lưu ý giữ giờ giả (nếu cần khớp ngày 03/11)
- Tắt NTP trước khi quay để giữ ngày hệ thống: `sudo timedatectl set-ntp false` rồi `sudo timedatectl set-time "2026-11-03 HH:MM:SS"` trên các VM (và pfSense chỉnh giờ tương ứng). Giữ VMware ở foreground khi OBS quay.
