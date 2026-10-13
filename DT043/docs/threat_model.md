# Threat model – DT043

## 1. Hệ thống và ranh giới tin cậy
```
 [Thiết bị IoT] ──LAN──▶ [Edge gateway]  ──────────────▶ [Backend/SOC]  ◀── [Frontend dashboard]
  (không tin cậy)     TB1  trích đặc trưng + AE per-device  TB2  FastAPI + SQLite      TB3  trình duyệt quản trị
                           (model int8, 1 luồng)                cảnh báo, điều phối MTD
```
- **TB1** – giữa thiết bị và gateway: thiết bị có thể đã bị chiếm, mọi lưu lượng từ thiết bị là dữ liệu không tin cậy.
- **TB2** – giữa gateway và backend: đầu vào API luôn được kiểm tra (Pydantic: tên thiết bị, số chiều, số dòng tối đa; giá trị hữu hạn).
- **TB3** – giữa trình duyệt và backend: dashboard chỉ đọc + xác nhận cảnh báo; nội dung hiển thị được escape để chống XSS.

## 2. Tài sản
| Tài sản | Vì sao quan trọng |
|---|---|
| Thiết bị IoT | đích chiếm quyền của botnet, nguồn DDoS |
| Model + scaler + ngưỡng (gói triển khai) | sửa được gói = tắt được phát hiện → kiểm tra SHA-256 khi nạp |
| Luồng cảnh báo / CSDL | là căn cứ để kích hoạt MTD và điều tra |
| Dữ liệu huấn luyện benign | bị đầu độc → model học "tấn công là bình thường" |

## 3. Kẻ tấn công
- Botnet Mirai / BASHLITE: dò quét Telnet, brute-force mật khẩu mặc định, chiếm thiết bị, flood (UDP/TCP/SYN/ACK…).
- Mục tiêu với bộ phát hiện: **né tránh** (làm lưu lượng giống benign), **đầu độc** dữ liệu huấn luyện, **làm trôi** hành vi theo thời gian.
- Ngoài phạm vi: kẻ tấn công chiếm được gateway/backend; tấn công vật lý.

## 4. Mối đe dọa (STRIDE rút gọn) và biện pháp
| Mối đe dọa | Ví dụ | Biện pháp trong dự án | Kiểm thử |
|---|---|---|---|
| Tampering – sửa model | thay model.tflite | SHA-256 trong meta.json, từ chối nạp nếu lệch | `test_tampered_bundle_rejected` |
| Tampering – sửa dữ liệu | dataset bị thay đổi | manifest SHA-256 | `test_manifest_detects_tampering` |
| Spoofing đầu vào | gửi đặc trưng sai chiều / NaN / lô khổng lồ | Pydantic + kiểm tra hữu hạn + giới hạn 20k mẫu | `test_wrong_dimension_422`, `test_oversized_request_rejected` |
| Path traversal | `segment=../../etc` | regex whitelist segment/tên thiết bị | `test_bad_segment_and_device_name_422` |
| Evasion | kéo đặc trưng tấn công về phía benign | đo TPR theo mức kéo α (E9) | `fig_evasion.png` |
| Poisoning | lẫn 1–5% tấn công vào DStrn | đo suy giảm TPR/FPR (E9) | `E9_poison_*` |
| DoS lên bộ phát hiện | gửi lô lớn liên tục | giới hạn kích thước lô; suy luận µs/mẫu | benchmark E8 |
| Information disclosure | lộ dữ liệu người dùng | đặc trưng thống kê, không payload/IP; DB không lưu dữ liệu thô | – |

## 5. Rò rỉ dữ liệu trong đánh giá (leakage)
- Chia theo thời gian + purge gap; scaler chỉ fit DStrn; ngưỡng chỉ từ DSopt; loại trùng hash giữa các tập. Thí nghiệm E6 cố tình làm sai để đo mức "đẹp giả".

## 6. Mất cân bằng lớp
- Attack nhiều gấp 5.5–61.8 lần benign trên test → Accuracy/F1-attack bị thổi phồng. Metric chính: **macro-F1, FPR**, kèm F1 khi giả định test cân bằng.

## 7. Đạo đức và an toàn
- Chỉ dùng dữ liệu công khai N-BaIoT (CC BY 4.0) trên máy cá nhân.
- Không chạy mã độc thật, không quét/tấn công hệ thống thật. "Tấn công" trong E9 chỉ là biến đổi dữ liệu offline.
- MTD chỉ được **mô phỏng/ghi nhận** trong CSDL (địa chỉ IP ảo, biến thể firmware ảo), không thay đổi mạng thật.
