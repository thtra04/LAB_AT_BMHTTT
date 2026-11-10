# E12 – Tái hiện đầy đủ nhất có thể phần kết quả của Masud et al. (2025)

Thực hiện ngày 09/11/2026, sau E11 ([tai_lap_paper_chinh.md](tai_lap_paper_chinh.md)). E11 và các kết quả cũ được giữ nguyên; E12 chỉ thêm hàm và file mới.

```powershell
cd src
.venv\Scripts\python ai/scripts/12_masud_full_repro.py
.venv\Scripts\python -m pytest ai/tests/test_tharm.py -q
```

Đầu ra: `results/tables/e12_*.csv`, `results/figures/fig_e12_*.png`.

## 1. Kết luận

**Không thể tái hiện bài báo khớp hoàn toàn.** Bài không có mã nguồn hay dữ liệu, thiếu công thức và tự mâu thuẫn. E12 thu hẹp được khoảng cách, chủ yếu ở thang đo của AC và ASP. Không có số nào được chỉnh để khớp.

| Kết quả của bài | E11 | E12 | Trạng thái |
|---|---|---|---|
| Tổng AC toàn mạng (S, D, R) | Lệch −83% | Lệch −3,4% đến +2,2% | **Gần khớp** (Definition 2) |
| Tổng RoC toàn mạng | Lệch +435% đến +506% | Lệch −8,4% đến +6,3% | **Gần khớp** (Definition 2) |
| Tổng R toàn mạng | Lệch +3,7% / −13,1% / −16,6% | Không đổi | Shuffle gần khớp; D và R chưa khớp |
| 9 giá trị tổng mạng lệch ≤ 5% | 1/9 | **5/9** | Tốt hơn, chưa đủ |
| Hình 5(a) IPV | Chưa làm | IPV ≈ m/n | Khớp, nhưng m lấy từ chính hình |
| Hình 5(b) PSV | Chưa làm | Không khớp | Không tái hiện được |
| Hình 5(c) IPV+PSV | Chưa làm | Không làm | Bài không định nghĩa phép gộp |
| Hình 6 | Chỉ so AR | So cả AR, AC, RoC: 19/105 điểm (Definition 2), 16/105 (Hình 3) | Cùng thang đo, khác hình dạng |
| Hình 7 | ASP 0,91–0,94 | ASP 0,24–0,48 (bài: 0,2–0,43) | Cùng thang đo; từng đường không so được |
| Hình 8 | Chưa làm | D và S+D cùng xu hướng | Chỉ so tỷ lệ, bộ sinh mạng là giả định |
| Hình 9 | Chưa làm | Không làm | Không tái hiện được |

Số điểm Hình 6 lệch ≤ 5% theo từng chỉ số: AR 3, AC 9, RoC 7 (Definition 2); AR 11, AC 2, RoC 3 (Hình 3). Giá trị của bài đọc bằng mắt từ hình.

## 2. Hai cách tính suy ra được

### 2.1. AC theo VM = Σ CVSS BS × attack cost

Bài không in công thức này. Mục 4.2 chỉ cho AC của 4 VM.

| VM | AC bài in | Σ cost (E11) | Σ BS × cost (E12) | Lệch E12 |
|---|---|---|---|---|
| V5 | 46,4 | 7,44 | 46,66 | +0,6% |
| V7 | 43,2 | 8,37 | 43,53 | +0,8% |
| V8 | 39,4 | 6,27 | 37,77 | −4,1% |
| V2 | 37,5 | 4,84 | 24,79 | **−33,9%** |

**Mức tin cậy:** đây là giả thuyết, được chọn sau khi dò các công thức đơn giản trên 4 số này, nên có nguy cơ khớp ngẫu nhiên. Bằng chứng hỗ trợ là tổng AC toàn mạng, vốn không dùng khi chọn công thức, cũng khớp trong khoảng ±3,4%. Công thức không giải thích được V2; R_V2 của bài cũng lệch Bảng 1–2, nên số liệu V2 của bài có thể khác bảng đã in. Công thức cũng không giải thích được Bảng 4, nơi AC chỉ là 6,27–9,97.

### 2.2. ASP theo VM = Eq. 1 đúng nguyên văn

E11 bỏ Eq. 1 vì công thức có thể ra số âm và dùng OR độc lập. Với dữ liệu thật, Eq. 1 không âm nếu lấy tích dịch vụ của V8 bằng 0 (giả định, vì V8 không có dịch vụ). Khi đó ASP đường có cùng thang đo với Hình 7. Tuy vậy, cách này không giải thích được Bảng 4 (ASP 0,95–0,99).

## 3. Tổng toàn mạng (Definition 2, chỉ dùng Bảng 1–2)

| MTD | Chỉ số | Bài báo | E12 | Lệch |
|---|---|---|---|---|
| Shuffle | R | 167,38 | 173,63 | +3,7% |
| | AC | 666,2 | 654,28 | −1,8% |
| | RoC | 1,01 | 1,07 | +6,3% |
| Diversity | R | 163,73 | 142,26 | −13,1% |
| | AC | 624,73 | 603,50 | −3,4% |
| | RoC | 1,04 | 0,95 | −8,4% |
| Redundancy | R | 260,84 | 217,58 | −16,6% |
| | AC | 878,3 | 897,38 | +2,2% |
| | RoC | 1,46 | 1,46 | −0,1% |

Tìm vét cạn các tập 4 đường có đường ví dụ của bài và xuất phát từ V1 hoặc V2 không cho tập nào khớp đồng thời R_s = 167,38 (±0,05) và AC_s = 666,2 (±1). Vì vậy, chỉ đổi đồ thị thì chưa giải thích được số của bài, trong phạm vi các giá trị VM đang dùng.

## 4. Các hình

- **Hình 5(a):** chạy đúng công thức IPV mục 3.6.1. Mức trung bình 0,857 / 0,429 / 0,169 / 0,091 / 0,042 với n = 10 / 20 / 50 / 100 / 200, giống hình của bài. Hình của bài cho thấy mỗi chu kỳ đổi khoảng 8–10 IP, và m ∈ {8, 9, 10} được suy ra chính từ hình, nên đây chỉ là kiểm tra công thức, không phải bằng chứng độc lập.
- **Hình 5(b):** không khớp. Bài không nêu đồ thị của từng "Edge set" và không có quy tắc chọn host đích.
- **Hình 6:** thang đo AC, RoC nay cùng bậc với bài, nhưng hình dạng khác. Ở bài, AR và AC của Redundancy gần như không đổi theo VM, S+D+R rất gần S+D; E12 không tạo ra được hai đặc điểm này.
- **Hình 7:** bài không in chuỗi VM của 8 đường. Hơn nữa, đổi V5 sang Linux làm ASP tăng (0,296 → 0,330 ở đường A-V1-V5-V8), ngược với lời bình của bài.
- **Hình 8:** tỷ lệ so với trước MTD ở n = 400 như dưới đây. Riêng D không phụ thuộc bộ sinh mạng vì chỉ đổi OS mọi VM. Các hàng còn lại phụ thuộc giả định (10% VM được shuffle hoặc nhân bản) nên không nên xem là khớp.

| MTD | AR E12 / bài | AC E12 / bài | RoA E12 / bài |
|---|---|---|---|
| D | 0,61 / 0,65 | 1,63 / 1,38 | 0,37 / 0,48 |
| S+D | 0,54 / 0,62 | 1,45 / 1,38 | 0,34 / 0,48 |
| S+D+R | 0,77 / 0,92 | 2,07 / 2,07 | 0,48 / 0,47 |
| R | 1,46 / 2,85 | 1,57 / 1,52 | 1,39 / 1,00 |
| S | 0,89 / 1,00 | 0,89 / 0,97 | 0,91 / 0,98 |

- **Hình 9:** không chạy. Bài không có mô hình theo thời gian, và trục ASP 200–400 trái với định nghĩa ASP ∈ [0, 1] của chính bài. Tự dựng đường cho giống hình sẽ là làm giả kết quả.

## 5. Mâu thuẫn mới phát hiện trong bài

1. **Không một topology nào giải thích được cả Hình 6.** Diversity V5 có AR ≈ 203 khớp Hình 3 (203,5), trong khi AC ≈ 625 lại gần Definition 2 (635) hơn Hình 3 (865).
2. **R_d trong văn bản khác Hình 6.** Mục 4.3 ghi R_d = 163,73, còn Hình 6(a) vẽ AR_d của V5 ≈ 203. Con số 163,73 lại gần điểm S+D của V5 (≈ 165; E12: 166–167).
3. **Definition 2 mâu thuẫn với điểm V6 trên Hình 6.** Trong Definition 2, V6 là ngõ cụt nên MTD lên V6 không đổi AR, AC, RoC, nhưng Hình 6 vẫn cho các giá trị khác nhau.
4. **AC_ap = 134,134 ở mục 4.3 không khớp cách tính của E12.** Với V2 và V8 theo số bài in, phần còn lại cho V4 và V5(Linux) chỉ là 57,2, trong khi công thức E12 cho 111,3. Con số này cũng thấp hơn 166,5 của đường ở mục 4.2, dù bài nhận định diversity làm tăng AC.

## 6. Giới hạn

- Giá trị đọc từ hình có sai số; ngưỡng 5% chỉ là quy ước so sánh.
- Công thức AC là giả thuyết của đề tài, không phải công thức do tác giả xác nhận.
- Đã đưa vào báo cáo Word (mục 6.10) và bộ slide 4'30 (slide 11, 14, 15, 16, 24, 25) và tài liệu hỏi – đáp (câu 16). Các bộ slide khác và video mẫu 4'30 chưa cập nhật theo E12.
