# LAB 5 – Thiết lập mô hình tường lửa pfSense (pfSense Firewall Configuration)

## 1. Thông tin sinh viên

| Mục | Nội dung |
|---|---|
| Họ và tên | Hoàng Thanh Trà |
| Mã số sinh viên (MSSV) | 1150080120 |
| Lớp | 11_ĐHCNPM_2 |
| Học phần | Thực hành An toàn Bảo mật Hệ thống thông tin – Năm học 2026–2027 |
| Repository | https://github.com/thtra04/LAB_AT_BMHTTT |
| Link video YouTube | https://youtu.be/lk4EdLtkH1o |
| Đề bài | [LAB5_pfSense_HuongDan_2026.docx](LAB5_pfSense_HuongDan_2026.docx) |
| Báo cáo | [Lab5_11CNPM2_1150080120_HoangThanhTra.docx](Lab5_11CNPM2_1150080120_HoangThanhTra.docx) |

## 2. Tên bài Lab

**Lab 5: Thiết lập mô hình tường lửa pfSense** – pfSense CE 2.7.2, mô hình WAN / LAN 10.0.0.0/8 / DMZ 172.16.0.0/16 với Windows Server làm Domain Controller trong LAN và DMZ-Web chạy IIS.

### Mục tiêu
- Xây dựng mô hình mạng có tường lửa pfSense bảo vệ LAN và vùng DMZ.
- Cấu hình WAN, LAN, DMZ, Outbound NAT, Port Forward và firewall rule.
- Thực hành các tình huống firewall: chặn ICMP nhưng cho Web/DNS, chỉ cho một host ra Internet, cô lập DMZ khỏi LAN, Port Forward WAN → DMZ, bật logging.

## 3. Nội dung nộp trong thư mục này

| Nội dung | File |
|---|---|
| Đề bài (bản giảng viên phát) | `LAB5_pfSense_HuongDan_2026.docx` |
| Báo cáo: trả lời phần **D. CÂU HỎI** (6 câu) | `Lab5_11CNPM2_1150080120_HoangThanhTra.docx` |

## 4. Phạm vi đã thực hiện

- [x] Trả lời đầy đủ 6 câu hỏi phần D (NAT và firewall rule, lý do dùng DMZ, thứ tự rule, chặn ping nhưng cho web, logging, hardening pfSense) dựa trên mô hình và các tình huống trong đề.
- [x] Báo cáo đã có khung phần B (thực hành) và C (5 tình huống): bảng ánh xạ mạng VMware ↔ VirtualBox, bảng IP, bảng rule từng tình huống, phần giải thích kết quả và 18 vị trí dán ảnh minh chứng (đánh dấu vàng).
- [x] Quay video quá trình thực hành trên VMware Workstation (pfSense CE 2.7.2 – ISO đã kiểm tra SHA-256 khớp đề): https://youtu.be/lk4EdLtkH1o – đã ghi link vào đầu báo cáo.
- [ ] Dán ảnh minh chứng (các vị trí đánh dấu vàng) và đối chiếu kết quả thực tế vào báo cáo.

## 5. Tóm tắt câu trả lời

| Câu | Ý chính |
|---|---|
| 1 | NAT đổi địa chỉ để gói đi/về được (Outbound NAT, Port Forward); firewall rule quyết định cho phép/chặn theo interface, nguồn, đích, giao thức, thứ tự. Có NAT nhưng không có rule Pass thì vẫn không đi được. |
| 2 | Dịch vụ công khai dễ bị tấn công nhất; đặt trong DMZ để khi bị chiếm, kẻ tấn công không lan sang LAN/Domain Controller (phân vùng, Block DMZ → LAN). |
| 3 | pfSense xét rule từ trên xuống, khớp đầu tiên thì dừng: Block nằm dưới Pass rộng sẽ không bao giờ được xét, lưu lượng vẫn đi qua; state cũ cũng phải Reset. |
| 4 | Trên tab LAN: Block ICMP LAN net → Any ở trên; Pass TCP/UDP 53; Pass TCP 80/443; tắt Default allow LAN to any; Apply + Reset States. |
| 5 | Log cho biết rule nào, interface nào, nguồn/đích nào bị chặn hay được pass → tìm đúng nguyên nhân, phân biệt lỗi firewall với lỗi DNS/Windows Firewall, làm bằng chứng và phát hiện tấn công. |
| 6 | Đổi mật khẩu admin mạnh, giới hạn WebGUI chỉ từ LAN quản trị qua HTTPS, chính sách default-deny với rule tối thiểu, bật Block private/bogon trên WAN khi ra Internet thật, bật log và cập nhật phiên bản, tắt dịch vụ không dùng, sao lưu cấu hình. |
