# Tái lập paper chính – Masud et al. (2025), 3-layer THARM (thí nghiệm E11)

**Paper:** *Vulnerability defence using hybrid moving target defence in Internet of Things systems*, Computers & Security 153 (2025) 104380, DOI 10.1016/j.cose.2025.104380 (Open Access, CC BY). Toàn văn: `docs/Vulnerability defence using hybrid moving target defence in Internet of.pdf`.

**Mã nguồn:** `ai/src/nbaiot/mtd/tharm.py` · **Script:** `ai/scripts/10_tharm_paper_replication.py` · **Test:** `ai/tests/test_tharm.py` (12 test, so khớp số của paper) · **Kết quả:** `results/tables/tharm_*.csv`, `results/figures/fig_tharm_scenarios.png`, `results/tharm_replication.log`.

```powershell
.venv\Scripts\python ai/scripts/10_tharm_paper_replication.py
.venv\Scripts\python -m pytest ai/tests/test_tharm.py -q
```

## 1. Lấy gì từ paper (không tự đặt tham số)

| Thành phần | Nguồn trong paper |
|---|---|
| 18 lỗ hổng OS (Windows 11, Linux, FreeBSD): CVE, CVSS BS, Impact, Exploitability, Attack cost | Bảng 1 |
| 14 lỗ hổng dịch vụ s1–s14 | Bảng 2 |
| VM → OS (Linux: V1, V4, V7, V8; Windows 11: V2, V5; FreeBSD: V3, V6) | Hình 1 |
| VM → dịch vụ (V1: s1–s2, …, V7: s13–s14; V8 = CSDL) | Hình 3 |
| Đồ thị tấn công lớp trên (11 cạnh) | Definition 2 (Hình 3 vẽ thêm V6 → V4) |
| Shuffle: V5 di trú host 2 → host 4, sinh đường A→V2→V7→V5→V8 | Mục 4.2, Hình 4 |
| Diversity: Windows 11 → Linux, FreeBSD → Windows 11, Linux → FreeBSD | Mục 4.3 |
| Redundancy: nhân bản V5 → V5′ | Mục 4.4 |
| Công thức ASP, AR, AC, RoC, độ trung tâm, PSV | Algorithm 2–3, mục 3.5–3.6 |

## 2. Kết quả đối chiếu số liệu

### 2.1 Rủi ro mức VM và mức đường tấn công – **khớp**

| Giá trị | Paper | Tái lập | Lệch |
|---|---|---|---|
| R_V4 | 12.47 | 12.473 | 0.0% |
| R_V5 (Windows 11) | 12.58 | 12.578 | 0.0% |
| R_V5 sau diversity (Linux) | 8.9 | 8.934 | +0.4% |
| R_V7 | 8.67 | 8.667 | 0.0% |
| R_V8 | 5.62 | 5.625 | +0.1% |
| R_V2 | 16.28 | 15.941 | −2.1% (Bảng 1–2 cho 15.94; paper không giải thích) |
| Đường shuffle A→V2→V7→V5→V8 | 43.15 | 42.81 | −0.8% |
| Đường diversity A→V2→V4→V5(Linux)→V8 | 43.31 | 42.97 | −0.8% |
| Đường redundancy A→V2→V4→V5′→V8 | 43.31 | 42.97 | −0.8% |

Toàn bộ phần lệch 0.8% ở mức đường đến từ R_V2. Để khớp, phải diễn giải Eq. 2 là **tổng** R_v = Σ Exploitability × Impact. Bản in ghi "∏" (tích) nhưng mọi con số paper dùng đều là tổng.

### 2.2 Bảng 4 (chỉ số ban đầu từng VM) – **khớp một phần**

| VM | AC paper | AC tái lập (Σ cost) | AR paper | ASP paper × Σ CVSS BS |
|---|---|---|---|---|
| V1 | 8.17 | **8.17** | 47.19 | **47.19** |
| V2 | 6.54 | 4.84 | 36.68 | **36.68** |
| V8 | 6.27 | **6.27** | 33.73 | **33.63** |
| V3–V7 | 7.34–9.97 | lệch 0.1–2.0 | 40.7–52.12 | lệch 1.7–7.7 |

- **AC** = tổng attack cost và **AR** = ASP × tổng điểm CVSS khớp ở các VM nêu trên. Ở các VM còn lại thì lệch, và paper không nêu đủ cách tính để kiểm tra.
- **ASP** không tái lập được: Eq. 1 bản in "1 − (∏ + ∏)" có thể ra số âm. Dùng OR độc lập 1 − ∏(1 − E) thì ra 0.96–0.9999, so với Bảng 4 là 0.95–0.99.

### 2.3 Tổng toàn mạng – **không tái lập được số tuyệt đối**

| MTD trên V5 | R paper | R tái lập | AC paper | AC tái lập | RoC paper | RoC tái lập |
|---|---|---|---|---|---|---|
| Shuffle | 167.38 | 173.63 | 666.2 | 113.94 | 1.01 | 6.12 |
| Diversity | 163.73 | 142.26 | 624.73 | 101.99 | 1.04 | 5.57 |
| Redundancy | 260.84 | 217.58 | 878.3 | 150.99 | 1.46 | 8.60 |

Nguyên nhân:
- Danh sách cạnh sau shuffle trong paper bị cắt bằng "…".
- AC theo VM mà paper dùng ở mục 4.2 (37.5, 43.2, 46.4, 39.4) lớn gấp khoảng 5–8 lần tổng cost trong Bảng 1–2 và không có công thức đi kèm.
- RoC toàn mạng của paper không bằng R/AC của chính paper (167.38 / 666.2 = 0.25, trong khi paper ghi 1.01).

Vì vậy chỉ so được **xu hướng**.

### 2.4 Xu hướng định tính – **tái lập được với topology Hình 3**

| Kết luận của paper | Definition 2 | Hình 3 (+V6→V4) |
|---|---|---|
| Shuffle giảm rủi ro mạng | ✗ (149.6 → 173.6) | ✓ (213.4 → 173.6) |
| Diversity giảm rủi ro mạng | ✓ | ✓ |
| Redundancy tăng rủi ro (thêm VM, thêm lỗ hổng) | ✓ | ✓ |
| Rủi ro diversity < redundancy | ✓ | ✓ |
| **Shuffle + Diversity có rủi ro mạng thấp nhất** | ✗ | **✓** (166.3) |
| S+D có ASP trung bình thấp hơn S và D riêng | ✗ | ✗ |
| S+D+R giảm rủi ro so với chỉ R | ✗ | ✓ |

**Kết luận E11:**
- Với dữ liệu lỗ hổng và topology vẽ trong Hình 3, **6/7 kết luận định tính** của paper tái lập được, trong đó có kết luận chính "shuffle + diversity tốt nhất".
- Nếu dùng đúng danh sách cạnh trong Definition 2 thì chỉ còn 3/7. Kết luận của paper **nhạy với một cạnh** (V6 → V4) mà phần định nghĩa và hình vẽ của paper ghi không thống nhất.
- Chọn VM bằng độ trung tâm (Eq. 8) ra **V2**, trong khi paper chọn V5. Paper không nêu cách gộp 3 độ đo.

## 3. Giới hạn của lần tái lập
- Không có mã nguồn hay dữ liệu gốc ("No data was used"). Mọi số được dựng lại từ bảng, hình và văn bản.
- Chưa tái lập Hình 5 (IPV/PSV theo kích thước mạng n = 10–200), Hình 8 (mạng 400 VM) và Hình 9 (theo thời gian), vì paper không mô tả đủ cách sinh các mạng đó.
- Chỉ áp MTD lên V5 như ví dụ của paper. Hình 6 áp lên từng VM nhưng không có số liệu dạng bảng để so.
