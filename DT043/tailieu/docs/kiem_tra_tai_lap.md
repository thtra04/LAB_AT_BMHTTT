# Kiểm tra mức độ tái lập bài báo chính (Masud et al., 2025)

Tài liệu này kiểm tra độc lập phần tái lập E11 (`src/ai/src/nbaiot/mtd/tharm.py`, `src/ai/scripts/10_tharm_paper_replication.py`, `src/ai/scripts/11_paper_figures.py`) bằng cách đối chiếu lại với toàn văn PDF. Phần tóm tắt kết quả tái lập trước đó nằm ở [tai_lap_paper_chinh.md](tai_lap_paper_chinh.md). Bản dịch bài báo: [ban_dich_bai_bao_chinh.md](ban_dich_bai_bao_chinh.md).

## 1. Cách kiểm tra

1. Đọc lại toàn bộ 17 trang của bài báo, phóng to Hình 1, 3, 4, 6, 7 để đọc hệ điều hành của từng VM, cạnh đồ thị và giá trị cột.
2. So từng số trong `OS_VULNS`, `SERVICE_VULNS`, `VM_OS`, `VM_SERVICES`, `EDGES_DEF2`, `BACKUP_OS`, `HOSTS` với Bảng 1, Bảng 2, Hình 1, Hình 3, Definition 2 và Mục 4.3.
3. Chạy lại `10_tharm_paper_replication.py` và `pytest ai/tests/test_tharm.py`: **14/14 test đạt**. Các file kết quả `results/tables/tharm_*.csv` sinh lại giống hệt bản đã commit (git không báo thay đổi). Sau khi sửa theo mục 4 (ngày 11/10/2026): **16/16 test đạt**, chỉ `tharm_centrality.csv` và log thay đổi.
4. Thử thêm các cách hiểu khác của bài: danh sách cạnh E′ in trong Mục 4.2, độ trung tâm trên đồ thị có hướng, số đường tấn công suy ra từ các tổng R, RoC.

## 2. Phần tái lập đúng

| Hạng mục | Kết quả kiểm tra |
|---|---|
| 18 CVE hệ điều hành (Bảng 1): CVSS BS, Impact, Exploitability, Attack cost | Khớp 100%, từng số |
| 14 CVE dịch vụ s1–s14 (Bảng 2) | Khớp 100% |
| Hệ điều hành của VM (Hình 1: Linux V1, V4, V7, V8; Windows 11 V2, V5; FreeBSD V3, V6) | Khớp với biểu tượng trong hình |
| VM nằm trên host nào (Hình 1, 4) và dịch vụ của từng VM (Hình 3) | Khớp |
| 11 cạnh của Definition 2, cạnh V6 → V4 chỉ có trong Hình 3 | Khớp; mã chạy cả hai topology |
| OS dự phòng: Windows 11 → Linux, FreeBSD → Windows 11, Linux → FreeBSD (Mục 4.3) | Khớp |
| Rủi ro từng VM R_v = Σ E·I | R_V4, R_V5, R_V5(Linux), R_V7, R_V8 khớp ±0.01 với số bài dùng |
| Rủi ro ba đường tấn công ví dụ (43.15; 43.31; 43.31) | Lệch −0.8%, toàn bộ do R_V2 (bài dùng 16.28, Bảng 1–2 cho 15.94) |
| Bảng 4: AC = Σ cost và AR = ASP × Σ CVSS BS | Khớp ở V1, V2 (AR), V8 |

Kết luận phần này: **dữ liệu đầu vào và công thức mức VM được tái lập đúng**. Cách diễn giải Eq. 2 thành tổng Σ (bản in ghi tích ∏) có cơ sở, vì mọi con số bài dùng đều khớp với tổng.

## 3. Phần chưa tái lập được (do bài thiếu thông tin)

Các điểm này đã được ghi trung thực trong `tai_lap_paper_chinh.md`:

- **Tổng toàn mạng R, AC, RoC** sau shuffle, diversity, redundancy không khớp số tuyệt đối. Nguyên nhân chính là AC theo VM bài dùng ở Mục 4.2 (37.5; 43.2; 46.4; 39.4) không suy ra được từ Bảng 1–2.
- **ASP của Bảng 4**: Eq. 1 bản in có thể ra số âm; cách OR độc lập 1 − ∏(1 − E) cho 0.96–0.9999, so với 0.95–0.99 của bài.
- **Hình 5, 8, 9** (mạng 10–400 VM, chỉ số theo thời gian) chưa tái lập, vì bài không mô tả cách sinh các mạng này. **Hình 7** không tái lập được.

## 4. Phát hiện mới khi kiểm tra lại (chưa có trong tài liệu tái lập)

### 4.1. Chọn VM cần bảo vệ (Eq. 8) tái lập được V5 nếu tính trên đồ thị có hướng

`Tharm.centrality()` chuyển đồ thị tấn công sang **vô hướng** (`to_undirected()`) trước khi tính closeness, degree, betweenness, nên ra **V2**. Tài liệu tái lập kết luận "paper không nêu cách gộp 3 độ đo". Khi tính trên **đồ thị có hướng**, đúng bản chất đồ thị tấn công (kẻ tấn công chỉ đi theo chiều cạnh), kết quả như sau:

| Độ đo (đồ thị có hướng) | Definition 2 | Hình 3 (+V6→V4) |
|---|---|---|
| Closeness (khoảng cách tới nút) | **V5** = V7, rồi V3 | **V5**, V7, V4 |
| In-degree | **V5**, V7, V1 | **V5**, V7, V4 |
| Betweenness | V2, V1, V5 | V2, V5, V4 |
| Tổng closeness + in-degree + betweenness | **V5** = V7 (0.628) | **V5** (0.703) |

Như vậy lựa chọn V5 của bài **tái lập được**. **Đã sửa:** `centrality()` dùng đồ thị có hướng và in-degree; khi V5 và V7 hòa (Definition 2) thì lấy VM có chỉ số nhỏ hơn. Thêm test `test_select_vm_is_v5_like_paper` cho cả hai topology; cập nhật `tai_lap_paper_chinh.md` và README.

### 4.2. RoC toàn mạng của bài là tổng RoC theo từng đường, không mâu thuẫn

`tai_lap_paper_chinh.md` ghi "RoC toàn mạng của paper không bằng R/AC của chính paper (167.38 / 666.2 = 0.25, trong khi paper ghi 1.01)". Thực ra bài cộng RoC của từng đường, giống cách `network_metrics()` đang tính. Ví dụ RoC_ap1 = 0.259 và 1.01 ≈ 4 × 0.25. **Đã sửa** câu này trong `tai_lap_paper_chinh.md` và trong báo cáo Word (mục 6.8).

### 4.3. Số liệu của bài gợi ý họ dùng topology Definition 2, không phải Hình 3

Chia tổng toàn mạng của bài cho giá trị của một đường ví dụ sẽ ước lượng được số đường tấn công bài đã cộng:

| MTD trên V5 | R mạng / R đường | RoC mạng / RoC đường | Số đường: Definition 2 | Số đường: Hình 3 |
|---|---|---|---|---|
| Shuffle | 167.38 / 43.15 ≈ 3.9 | 1.01 / 0.259 ≈ 3.9 | 4 | 4 |
| Diversity | 163.73 / 43.31 ≈ 3.8 | 1.04 / 0.32 ≈ 3.3 | 4 | **5** |
| Redundancy | 260.84 / 43.31 ≈ 6.0 | 1.46 / 0.32 ≈ 4.6 | 6 | **8** |

Đây chỉ là ước lượng, vì các đường có giá trị khác nhau. Dù vậy, số liệu nghiêng về **Definition 2** (4/4/6 đường). Với Definition 2, phần tái lập chỉ khớp **3/7** kết luận định tính. Con số 6/7 chỉ đạt được với topology Hình 3. Vì vậy kết luận "Shuffle + Diversity tốt nhất" **chỉ tái lập được với topology Hình 3**, còn số liệu nội tại của bài gợi ý họ tính trên Definition 2. **Đã ghi rõ** điều này trong `tai_lap_paper_chinh.md`, README, báo cáo Word, hỏi – đáp và kịch bản thuyết trình.

### 4.4. Danh sách cạnh sau shuffle (E′, Mục 4.2) mâu thuẫn với đường ví dụ

E′ in trong bài vẫn còn cạnh vào V5 (V1→V5, V2→V5, V4→V5). Danh sách không có A→V2 và V7→V5, trong khi đường mới được nêu ngay sau đó là A→V2→V7→V5→V8. Mã tái lập chọn quy tắc "bỏ mọi cạnh vào V5, thêm V7→V5" theo đường ví dụ. Đây là lựa chọn hợp lý nhưng là một cách diễn giải. Dùng nguyên văn E′ thì R mạng = 188.87 (4 đường), cũng không khớp 167.38. **Đã ghi** lựa chọn này vào mục giới hạn của `tai_lap_paper_chinh.md`.

### 4.5. Hình 7 tự mâu thuẫn trong bài

- Lời bình nói Path 3, 5, 6 giảm ASP sau diversity, nhưng trên hình cột Path 5 (và Path 2) lại **tăng**.
- ASP theo đường trên Hình 7 (0.2–0.43) không tương thích với ASP theo VM ở Bảng 4 (0.95–0.99). Nếu nhân ASP các VM trên đường thì kết quả ≥ 0.8.
- Trong tái lập, diversity V5 (Windows 11 → Linux) **tăng** ASP các đường qua V5 (0.914 → 0.936), vì lỗ hổng Linux có exploitability cao hơn. Kết quả này ngược với kết luận của bài.

Kết luận "Hình 7 không tái lập được" trong README là đúng; nên bổ sung hai lý do trên.

### 4.6. Gợi ý về AC theo VM

AC theo VM bài dùng ở Mục 4.2 gần với **tổng điểm CVSS BS** của VM: V2 37.5 so với 37.2; V7 43.2 so với 41.1; V5 46.4 so với 43.5; V8 39.4 so với 35.4. Mức lệch 0.3–4.0 nên chưa khớp hẳn, nhưng có thể nêu như một giả thuyết về cách bài tính AC.

## 5. Paper tham chiếu kỹ thuật (Meidan et al., 2018)

Phần lõi autoencoder đúng phương pháp của Meidan:

- Kiến trúc 75% – 50% – 33% – 25% (`models.py`).
- Ngưỡng tr* = mean + std của MSE trên DSopt (`threshold.py`).
- ws* là cửa sổ nhỏ nhất cho FPR = 0 trên DSopt.
- Benign chia theo thời gian thành 3 phần bằng nhau (`split.py`, `configs/base.yaml`).

Các khác biệt có chủ đích đều đã ghi trong `phieu_tai_lap_paper.md` mục C: Adam lr cố định, early stopping, khử trùng lặp, purge gap 500 dòng, 5 seed. Về kết quả, FPR tái lập được (B0: 0.0025, bài: 0.007). TPR 100% không tái lập được (B0 trung bình 0.82; Ennio Doorbell chỉ 0.37 do flood BASHLITE tcp/udp). Thời gian phát hiện đo theo số mẫu thay vì ms, vì CSV không có timestamp. README báo cáo đúng các điểm này.

## 6. Kết luận

| Câu hỏi | Trả lời |
|---|---|
| Dữ liệu và mô hình có lấy đúng từ bài không? | **Đúng.** Mọi CVE, điểm số, topology, OS và quy tắc MTD đều khớp bài |
| Công thức có đúng không? | **Đúng ở mức VM và mức đường** (lệch ≤ 0.8%). Độ trung tâm nay tính trên đồ thị có hướng nên chọn đúng V5 như bài |
| Số tổng toàn mạng có khớp không? | **Không.** Bài thiếu công thức AC theo VM; RoC của bài là tổng theo đường |
| Kết luận "Shuffle + Diversity tốt nhất" có tái lập được không? | **Chỉ với topology Hình 3** (6/7 kết luận). Với Definition 2 là 3/7, và số liệu của bài gợi ý họ dùng Definition 2 |
| Đánh giá chung | **Tái lập một phần, trung thực.** Phần làm được đúng; phần không khớp đều do bài thiếu hoặc mâu thuẫn thông tin. Ba chỗ ở mục 4.1–4.3 đã được sửa trong mã và tài liệu |
