# Tiêu chí thành công (chốt TRƯỚC khi chạy ma trận thí nghiệm)

Chốt ngày 11/10/2026, trước khi chạy ma trận E1–E10. SHA-256 của file này được ghi trong `NHAT_KY_THUC_HIEN.md`. Không sửa file sau khi có kết quả; nếu cần điều chỉnh phải ghi rõ lý do và thời điểm ở cuối file.

Trước thời điểm chốt chỉ có **1 lần chạy smoke test** (E1, Danmini_Doorbell, seed 42) để kiểm tra pipeline. Tiêu chí dưới đây giống hệt bảng ở `KE_HOACH.md` mục 2.3 (viết trước khi có bất kỳ kết quả nào).

| RQ | Tiêu chí | Cách đo |
|---|---|---|
| RQ1 – Tái lập baseline | TPR trung bình ≥ 0.99 **và** FPR trung bình ≤ 0.02 (mức cửa sổ, 9 thiết bị × 5 seed) | E1, `tr* = mean + std`, `ws*` |
| RQ2 – Per-device vs global | macro-F1 (mức cửa sổ) của B0 cao hơn B1 ở ≥ 7/9 thiết bị **và** Wilcoxon một phía p < 0.05 | E1 vs E2_global |
| RQ3 – Model nhẹ | V1 có ≤ 25% tham số của B0 **và** macro-F1 trung bình giảm ≤ 0.01 (tuyệt đối) | E4_light vs E1 |
| RQ4 – Lượng tử hóa | full-int8 + hiệu chỉnh ngưỡng: macro-F1 giảm ≤ 0.005 so với fp32 cùng model; kích thước ≤ 30% bản TFLite fp32 | E5 (trong E1/E4) |
| RQ5 – Edge | Profile P1 (1 luồng, 1 E-core, batch 1): p95 latency ≤ 1 ms/mẫu; file model ≤ 50 KB; RSS tăng thêm khi nạp + chạy ≤ 50 MB | E8 |
| RQ6 – MTD lai | Báo cáo trade-off; giả thuyết: với cùng số lần move, hybrid có thời gian lộ diện thấp hơn time-based | E10 |

Quy tắc chung:
- Metric chính là **macro-F1 và FPR ở mức cửa sổ**. Accuracy chỉ để tham khảo.
- Mọi so sánh cặp dùng Wilcoxon signed-rank trên 9 thiết bị (trung bình 5 seed), hiệu chỉnh Holm khi so nhiều cặp.
- Không chọn seed/cấu hình theo kết quả test. Mọi lần chạy đều được báo cáo.
