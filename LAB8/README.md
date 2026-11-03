# LAB 8 – Local DNS Attack (DNS Spoofing & Cache Poisoning)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | *(cập nhật sau khi đăng)* |
| Đề bài | [đề/LAB8_Local_DNS_Attack_pfSense_2026.docx](đề/LAB8_Local_DNS_Attack_pfSense_2026.docx) + bộ tài nguyên [đề/LAB8_Local_DNS_Attack_pfSense_2026_FINAL.zip](đề/LAB8_Local_DNS_Attack_pfSense_2026_FINAL.zip) |
| Báo cáo | [Baocao/11CNPM2-Lab8_1150080120-HoangThanhTra.docx](Baocao/11CNPM2-Lab8_1150080120-HoangThanhTra.docx) |
| Cấu hình & script | [cau_hinh_dns/](cau_hinh_dns/) |
| Ảnh minh chứng | [hinh/](hinh/) · Log & pcap: [ketqua/](ketqua/) |

## 2. Tên bài Lab

**Lab 8: Local DNS Attack** (tài liệu đề ghi "LAB 9 – Local DNS Attack", theo SEED Labs) – dựng DNS-SERVER
BIND9 làm resolver/cache riêng cho một mạng ảo **cô lập**, rồi minh hoạ ba kỹ thuật tấn công DNS nội bộ và
phân tích phòng thủ. Toàn bộ chỉ chạy với tên miền `.test` trong mạng ảo, không đụng Internet/mạng thật.

## 3. Mô hình (rút gọn, tái dùng VM VMware sẵn có)

Một phân đoạn mạng riêng **DNS-LAB 10.9.0.0/24** (VMware private segment, bật promiscuous):

| Vai trò | IP | Mô tả |
|---|---|---|
| DNS-SERVER | 10.9.0.10 | BIND9 recursive/cache + authoritative `lab9.test`; uỷ quyền `external.lab9.test` → 172.16.6.20 |
| VICTIM (kiêm DMZ) | 10.9.0.100 | client DNS; alias `172.16.6.10` = web thật (Apache), alias `172.16.6.20` = AUTH-DNS mô phỏng (trễ 1.5s) |
| ATTACKER | 10.9.0.200 | Ubuntu + Scapy, promiscuous, web giả + `dns_spoof_lab9.py` |

> **Điều chỉnh so với đề (được phép):** đề viết cho VirtualBox + pfSense kế thừa "LAB 8"; máy thực tế dùng
> VMware nên mô hình được rút gọn về một phân đoạn cô lập, gộp vai trò DMZ-WEB/AUTH-DNS lên máy VICTIM qua
> IP alias, và dùng Ubuntu+Scapy thay cho Kali. Dải địa chỉ, tên miền `.test` và toàn bộ cấu hình/script giữ
> đúng theo bộ tài nguyên của đề.

## 4. Ba nhiệm vụ đã thực hiện

1. **Task 1 – /etc/hosts redirect:** thêm `10.9.0.200 www.lab9.test` vào `/etc/hosts` của VICTIM → `curl/getent`
   trỏ về trang giả, trong khi `dig @10.9.0.10` vẫn trả 172.16.6.10 (DNS không dùng /etc/hosts).
2. **Task 2 – Direct DNS spoofing:** attacker nghe truy vấn Victim→Resolver, giả phản hồi (đúng Transaction ID +
   cổng, giả nguồn 10.9.0.10) gửi thẳng tới Victim → Victim nhận 10.9.0.200.
3. **Task 3 – Cache poisoning:** attacker giả phản hồi từ AUTH (172.16.6.20) tới Resolver → cache BIND9 bị đầu độc
   (`A 10.9.0.200`, TTL 120s), vẫn còn sau khi dừng attacker; `rndc dumpdb` xác nhận.

Khôi phục: `rndc flush`, phục hồi `/etc/hosts`, trả promiscuous về Deny.

## 5. Nội dung thư mục

- [cau_hinh_dns/](cau_hinh_dns/) – `named.conf.options`, `named.conf.local`, `db.lab9.test`, `db.10.9.0`,
  `auth_dns_delayed.py`, `dns_spoof_lab9.py`, `fake_index.html`, `filters.txt`; script dựng máy
  (`setup_*.sh`) và kịch bản demo (`demo_lab8.sh`, `sec_lab8.sh`).
- [hinh/](hinh/) – sơ đồ mô hình + ảnh kết quả 3 task (chụp từ output thật của các VM).
- [ketqua/](ketqua/) – `lab8_demo_log.txt` (log chạy đầy đủ) và `task2.pcap`, `task3.pcap` (gói bắt được).
- [Baocao/](Baocao/) – báo cáo Word.
- [đề/](đề/) – đề bài gốc và bộ tài nguyên.
