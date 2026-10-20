# Bộ câu hỏi phòng hờ khi bảo vệ – DT043

Cách dùng: đọc to câu trả lời ngắn (1–3 câu), chỉ nói phần "nếu hỏi tiếp" khi giảng viên hỏi sâu. Số liệu lấy từ `results/tables/` và báo cáo; slide tương ứng ghi trong ngoặc.

## A. Chứng minh dùng đúng dataset được giao (chuẩn bị kỹ nhất)

**A1. Làm sao biết em chạy đúng bộ N-BaIoT thầy cho, không phải bộ khác hay bản đã sửa?**
> Em tải đúng file từ link UCI trong đề (DOI 10.24432/C5RC8J, CC BY 4.0), ghi lại URL, ngày tải, kích thước và SHA-256 của file zip trong `data/DOWNLOAD_INFO.json`, rồi lập manifest SHA-256 cho cả 107 file CSV. Chạy lệnh kiểm tra là thấy ngay mọi file khớp.

Chứng minh trực tiếp (≈ 1 phút):
```powershell
.venv\Scripts\python ai/scripts/02_verify_manifest.py     # → "Manifest OK – mọi file khớp SHA-256."
Get-Content data\DOWNLOAD_INFO.json                        # URL, DOI, ngày tải, zip_sha256, n_files = 107
```
| Bằng chứng | Giá trị |
|---|---|
| URL tải | `https://archive.ics.uci.edu/static/public/442/detection+of+iot+botnet+attacks+n+baiot.zip` (trùng link trong đề) |
| Ngày tải | 11/10/2026 04:41 UTC |
| Kích thước zip | 1.772.922.927 byte |
| SHA-256 zip | `64929678b081d8e5…5de9b` |
| Số file CSV | 107 (9 thiết bị; 2 thiết bị không có Mirai) |
| Tổng số dòng | **7.062.606** – trùng số instances UCI công bố |
| Số đặc trưng | 115, đúng tên và thứ tự cột ở 100% file |

**A2. Người khác chạy lại có ra đúng kết quả của em không?**
> Có. README hướng dẫn chạy từ đầu: tải dữ liệu bằng `01_download.py`, kiểm tra manifest, rồi chạy các script theo thứ tự. Seed cố định (42, 1337, 2024, 7, 123), cấu hình lưu trong `ai/configs/`, phiên bản thư viện khóa trong `requirements-lock.txt`, nên chạy lại sẽ ra cùng số (sai lệch rất nhỏ do số thực trên CPU khác nhau).

**A3. Sao em không nộp kèm dữ liệu?**
> Dữ liệu thô 1,7 GB và giấy phép yêu cầu ghi nguồn; em chỉ nộp manifest, thống kê chất lượng và script tải lại, người chấm tải từ UCI rồi kiểm tra checksum.

**A4. Dữ liệu có vấn đề gì? Em xử lý ra sao?**
> Có 157.779 dòng trùng lặp chính xác (2,2%), nhiều nhất ở benign của Danmini (18,5%) và gafgyt tcp/udp; em khử trùng còn 6.904.827 dòng. Dữ liệu mất cân bằng nặng (tấn công gấp khoảng 12 lần benign), nên em không dùng Accuracy mà dùng macro-F1, TPR, FPR. (Slide 4)

## B. Đề bài và paper

**B1. Paper chính nói về MTD, sao đề tài lại là autoencoder?**
> Đúng, khi đọc em thấy paper Masud 2025 về hybrid Moving Target Defence, không dùng autoencoder hay N-BaIoT. Em không gượng ép mà chia hai track: track A làm phát hiện bằng autoencoder theo Meidan 2018 (bài gốc của N-BaIoT), track B tái lập xu hướng MTD và dùng cảnh báo của AE để kích hoạt MTD. (Slide 3)

**B2. Em trích được những hạn chế nào của paper?**
> Em đọc toàn văn và lập phiếu với 7 điểm: chỉ mô phỏng, chưa đo QoS; xác suất khai thác gán tĩnh theo CVSS; chỉ xét time-based, không mô hình detector kích hoạt MTD; không đo chi phí MTD trên thiết bị; công thức bản in mâu thuẫn (Eq. 1 có thể âm, Eq. 2–3 ghi tích nhưng số là tổng, danh sách cạnh sau shuffle bị cắt); không công bố mã nguồn/dữ liệu; Definition 2 và Hình 3 vẽ topology không thống nhất. Hai điểm cuối em phát hiện khi tái lập. (`docs/phieu_tai_lap_paper.md`)

**B2b. Em tái lập paper chính có ra đúng số của paper không?**
> Em dựng lại 3-layer THARM bằng đúng dữ liệu paper công bố: 18 CVE hệ điều hành, 14 CVE dịch vụ, 8 VM, topology và ba kỹ thuật shuffle, diversity, redundancy (thí nghiệm E11). Rủi ro từng VM khớp tới ±0,01 (ví dụ R_V5 = 12,58) và rủi ro ba đường tấn công ví dụ lệch 0,8%. Tổng toàn mạng thì không ra đúng số vì paper cắt danh sách cạnh và không nêu công thức cost theo VM; xu hướng thì tái lập được 6/7 kết luận với topology Hình 3, trong đó có kết luận chính "shuffle + diversity tốt nhất". (Mục 6.8 báo cáo, `docs/tai_lap_paper_chinh.md`)

> Nếu hỏi tiếp "vì sao phải hiểu ∏ thành Σ?": vì chỉ khi cộng E × I của các lỗ hổng thì mới ra đúng các con số paper tự dùng ở mục 4.2–4.3; nhân thì ra số rất nhỏ, không khớp con số nào.

**B3. Câu hỏi nghiên cứu và giả thuyết của em là gì?**
> Sáu câu: RQ1 tái lập baseline Meidan; RQ2 per-device có hơn model chung không; RQ3 model nhẹ có giữ chất lượng không; RQ4 lượng tử hóa int8; RQ5 chạy được trên edge không; RQ6 MTD lai có thời gian lộ diện thấp hơn time-based không. Tiêu chí chốt ngày 11/10, lưu SHA-256 trước khi chạy ma trận thí nghiệm. (Slide 2, `docs/tieu_chi_thanh_cong.md`)

## C. Chống rò rỉ và thiết kế thí nghiệm

**C1. Rò rỉ train/test ở đây là gì? Em chặn bằng cách nào?**
> Các dòng liền kề gần như giống nhau, chia ngẫu nhiên thì test "đã thấy" train. Em chia benign của từng thiết bị theo thời gian 1/3 train, 1/3 DSopt, 1/3 test, bỏ 500 dòng đệm ở mỗi ranh giới, chỉ fit scaler trên train và loại khỏi test mọi dòng trùng hash với train. Mỗi biện pháp có unit test. (Slide 5)

**C2. Có chứng minh rò rỉ thật sự ảnh hưởng không?**
> Có, thí nghiệm E6 cố tình chia ngẫu nhiên và fit scaler trên toàn bộ benign: FPR "đẹp giả" xuống 0,0006 so với 0,0025 khi chia đúng.

**C3. Chạy bao nhiêu lần? Có chọn seed đẹp không?**
> 5 seed cố định cho cấu hình chính (3 seed cho biến thể V2), tổng 468 kết quả theo thiết bị × seed, báo cáo tất cả, không chọn kết quả tốt nhất. Có 7 cặp (model, thiết bị) mà TPR dao động hơn 0,05 chỉ vì đổi seed, nên chạy một lần như Meidan là không đủ. (Slide 14)

**C4. Ngưỡng và cửa sổ được chọn thế nào?**
> Theo Meidan: ngưỡng tr* = trung bình + độ lệch chuẩn của MSE trên DSopt; cửa sổ ws* là cửa sổ majority vote nhỏ nhất làm FPR = 0 trên DSopt (tối đa 1000). Tập test không được dùng để chọn ngưỡng.

**C5. Vì sao dùng macro-F1 chứ không phải Accuracy?**
> Tấn công nhiều gấp khoảng 12 lần benign, đoán "tất cả là tấn công" đã có Accuracy cao. Metric chính chốt trước là macro-F1 và FPR mức cửa sổ; em báo thêm TPR, F1 cân bằng, MCC, ROC-AUC, PR-AUC.

## D. Mô hình và kết quả

**D1. Các mô hình em so sánh?**
> B0 là autoencoder của Meidan (115-86-58-38-29 rồi đối xứng, 36.876 tham số) huấn luyện riêng từng thiết bị; B1 là model chung (một bản dùng chuẩn hóa chung, một bản chuẩn hóa và ngưỡng riêng); B2 là Isolation Forest; V1 là AE nhẹ 115-32-8 (8.059 tham số, 21,9% của B0); V2 chỉ dùng 23 đặc trưng của một cửa sổ thời gian (699 tham số). (Slide 6)

**D2. Sao không đạt TPR gần 100% như Meidan?**
> Em chia không rò rỉ và báo cáo trên 5 seed. Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE (recall khoảng 0,47); tám loại còn lại recall gần 1,0. FPR của em 0,0025, thấp hơn Meidan 0,007. (Slide 9, 10)

**D3. Vì sao flood tcp/udp bị bỏ sót?**
> Em kiểm tra trên dữ liệu thô: nguồn bị giả mạo liên tục nên mỗi gói giống một "luồng mới" (weight = 1, variance = 0, 60 byte), MSE khoảng 0,17 – cao hơn phần lớn benign nhưng thấp hơn ngưỡng mean + std vì phân phối benign có đuôi dài kéo ngưỡng lên. (Slide 10)

**D4. Hạ ngưỡng thì sao?**
> Hậu kiểm cho thấy ngưỡng p75 bắt được 100% tcp/udp, nhưng cần cửa sổ khoảng 1400 mẫu và FPR test khoảng 0,02 – phát hiện chậm và báo động giả nhiều hơn. Em ghi rõ đây là hậu kiểm, không dùng để chấm tiêu chí. (Slide 11)

**D5. Isolation Forest tốt hơn (macro-F1 0,886), sao vẫn chọn AE?**
> Em báo cáo đúng là IF tốt hơn về chất lượng. AE được chọn vì tái lập Meidan và vì triển khai edge: model V1 int8 chỉ 15,3 KB, chạy khoảng 10 µs/mẫu trên một lõi. IF là baseline để so sánh, không phải đối tượng triển khai. Hướng tiếp theo có thể đưa IF lên edge để so chi phí.

**D6. Per-device có thật sự tốt hơn model chung không?**
> Chưa chứng minh được: B0 chỉ thắng model chung 4/9 thiết bị, Wilcoxon p = 0,285, nên RQ2 không đạt. Thú vị là model chung nhưng chuẩn hóa và ngưỡng riêng từng thiết bị đạt macro-F1 0,775, cao hơn B0 – tức phần quan trọng của "per-device" là chuẩn hóa và ngưỡng, nhưng cũng chưa có ý nghĩa thống kê.

**D7. Em kiểm định thống kê thế nào?**
> Wilcoxon signed-rank trên 9 thiết bị (trung bình 5 seed), hiệu chỉnh Holm khi so nhiều cặp, kèm khoảng tin cậy 95%. Không có so sánh nào có ý nghĩa sau hiệu chỉnh, nên em không tuyên bố mô hình nào "vượt" paper.

**D8. Em có thử tấn công chống lại bộ phát hiện không?**
> Có, offline: né tránh bằng cách kéo mẫu tấn công về phía tâm benign – phải bắt chước rất sát (α = 0,99) recall mới tụt còn khoảng 0,49, tức là phải giảm cường độ tấn công; thêm nhiễu σ = 0,5 làm báo động giả tăng mạnh; đầu độc 1%/5% dữ liệu train làm macro-F1 V1 giảm còn 0,47/0,44. (Slide 14)

## E. Lượng tử hóa và edge

**E1. Lượng tử hóa em làm thế nào?**
> Xuất Keras qua SavedModel rồi dùng TFLiteConverter sinh 4 bản fp32, fp16, dynamic-range và full-int8 (có tập hiệu chỉnh từ DStrn). Sau khi lượng tử hóa, em tính lại ngưỡng và cửa sổ trên DSopt bằng chính model int8. (Slide 12)

**E2. Sao phải hiệu chỉnh lại ngưỡng?**
> MSE của model int8 lệch so với fp32, giữ ngưỡng cũ làm điểm hoạt động thay đổi. Hiệu chỉnh trên DSopt giảm FPR (V1: 0,0016) và rút ngắn cửa sổ phát hiện; nó cải thiện FPR và độ trễ, không phải macro-F1.

**E3. Sao int8 không nhỏ còn 25% như lý thuyết? (RQ4 không đạt)**
> Trọng số giảm 4 lần nhưng file TFLite còn khung flatbuffer và metadata cố định; với model nhỏ phần này chiếm tỷ trọng lớn nên file còn 45,5% bản fp32 (15,3 KB).

**E4. Đo edge thế nào? Có thiết bị thật không?**
> Không có thiết bị IoT thật; em mô phỏng bằng cách ghim 1 luồng vào 1 lõi E-core (lõi tiết kiệm điện) của i7-13650HX, batch 1, mỗi cấu hình chạy trong process riêng, 10.000 lần × 5 lượt, báo p50/p95/p99. V1 int8: p95 10,8 µs/mẫu, khoảng 103.000 mẫu/s, RAM tăng 4,6 MB. Đây là giới hạn em ghi rõ; hướng tiếp theo là đo trên Raspberry Pi. (Slide 13)

**E5. Energy proxy tính thế nào?**
> Thời gian CPU mỗi mẫu × công suất ước lượng một lõi (55 W công suất cơ sở / 14 lõi ≈ 3,93 W). V1 int8 khoảng 40 µJ/mẫu. Đây chỉ là ước lượng tương đối để so giữa các cấu hình, không phải đo điện năng thật.

**E6. Chạy nhiều luồng có nhanh hơn không?**
> Với batch 1, chạy 20 luồng chậm hơn khoảng 50 lần (p50 khoảng 470 µs) vì chi phí đồng bộ luồng lớn hơn phép tính; 1 luồng ghim lõi là cấu hình đúng cho edge.

## F. MTD

**F1. MTD là gì, em mô phỏng ra sao?**
> MTD thay đổi bề mặt tấn công liên tục để kẻ tấn công mất thông tin: shuffle (đổi địa chỉ IP), diversity (đổi phiên bản firmware). Em dựng mô hình HARM rút gọn 11 node, 9 đường tấn công, tham số giả định, chu kỳ 20 bước; chỉ so xu hướng với paper, không so số tuyệt đối. (Slide 15)

**F2. Kết quả MTD?**
> Xác suất tấn công thành công: không MTD 0,498; shuffle 0,409; diversity 0,437; kết hợp 0,327 – kết hợp thấp nhất, khớp xu hướng paper chính.

**F3. MTD lai kích hoạt bởi AE khác gì?**
> Event-based chỉ "move" khi AE báo động, ít tốn nhưng tấn công AE bỏ sót thì không được xử lý (lộ diện trung bình 11.835 mẫu). Hybrid thêm move theo chu kỳ làm lưới an toàn: với cùng chi phí, thời gian lộ diện thấp hơn time-based thuần.

**F4. MTD có chạy trên mạng thật không?**
> Không. Hành động MTD chỉ được mô phỏng và ghi vào CSDL, không tác động mạng thật – đúng ràng buộc an toàn của đề.

## G. Hệ thống demo, kiểm thử, bảo mật

**G1. Kiến trúc demo?**
> Bốn tầng: AI huấn luyện và xuất gói `model.tflite + scaler.json + meta.json` có SHA-256; backend FastAPI nạp gói, cung cấp API phát hiện, phát lại, cảnh báo, MTD; SQLite lưu cảnh báo và hành động MTD; frontend HTML/JS thuần. (Slide 7)

**G2. Nếu ai đó sửa model trên thiết bị thì sao?**
> Backend kiểm tra SHA-256 trong `meta.json`, lệch dù 1 byte là từ chối nạp – có test negative cho trường hợp này.

**G3. Em viết những loại test nào?**
> 54 test: unit (chia dữ liệu, đệm, scaler, ngưỡng, cửa sổ, 12 test so khớp THARM với số của paper chính), integration (pipeline end-to-end), negative (gói bị sửa, path traversal kiểu `../../etc`, sai số chiều đặc trưng, lô quá lớn, thiết bị không tồn tại). Chạy: `.venv\Scripts\python -m pytest ai/tests backend/tests -q`.

**G4. Demo phát lại dữ liệu từ đâu? Có rò rỉ dữ liệu train không?**
> Phát lại từ dữ liệu công khai đã chuẩn bị; benign chỉ lấy phần test, nên demo không dùng dữ liệu model đã học.

**G5. Threat model của em?**
> Ba ranh giới tin cậy: TB1 thiết bị IoT → edge gateway (lưu lượng từ thiết bị coi là không tin cậy), TB2 gateway → backend (mọi đầu vào API được kiểm tra bằng Pydantic), TB3 trình duyệt → backend (dashboard chỉ đọc và xác nhận cảnh báo, nội dung được escape chống XSS). Tài sản cần bảo vệ là thiết bị, gói model, CSDL cảnh báo và dữ liệu benign; kẻ tấn công nhắm tới né tránh, đầu độc, làm trôi hành vi. Dữ liệu N-BaIoT chỉ là thống kê lưu lượng, không có thông tin cá nhân. (`docs/threat_model.md`)

## H. Tái lập, đóng góp, giới hạn

**H1. Đóng góp riêng của em là gì?**
> (1) Tái lập Meidan có chống rò rỉ và nhiều seed, chỉ ra rò rỉ làm FPR đẹp giả; (2) phân tích nguyên nhân bỏ sót flood tcp/udp trên dữ liệu thô; (3) V1 nhẹ + int8 + hiệu chỉnh ngưỡng và đo edge; (4) MTD lai dùng cảnh báo AE làm bộ kích hoạt; (5) hệ thống demo 4 tầng có kiểm tra toàn vẹn model.

**H2. Giới hạn lớn nhất?**
> Bỏ sót flood giả mạo nguồn; edge chỉ mô phỏng trên laptop; MTD dùng tham số giả định; dữ liệu là lab 2018 với 9 thiết bị và 2 botnet, chưa kiểm tra trên lưu lượng mới.

**H3. Chi phí tính toán?**
> Ma trận thí nghiệm khoảng 4–5 giờ CPU với 2 worker; triển khai mỗi thiết bị 15,3 KB model, khoảng 10 µs và 40 µJ mỗi mẫu.

**H4. Hướng phát triển?**
> Thêm đặc trưng/luật cho flood giả mạo nguồn, chọn ngưỡng có kiểm định trên dữ liệu mới, đo trên Raspberry Pi với đồng hồ điện thật.

## I. Câu hỏi "khó" – trả lời thẳng

**I1. Nhiều tiêu chí không đạt, vậy bài có thất bại không?**
> Tiêu chí được chốt trước và em giữ nguyên để kết quả đáng tin; RQ5 đạt với biên lớn, RQ1–RQ4 không đạt và em giải thích được nguyên nhân bằng dữ liệu. Đề yêu cầu tái lập trung thực và không tuyên bố vượt paper khi chưa kiểm định, em làm đúng tinh thần đó.

**I2. Sao không dùng model lớn hơn để tăng TPR?**
> Mục tiêu đề là model nhẹ cho edge; hơn nữa lỗi tcp/udp nằm ở đặc trưng (gói giả mạo trông như benign), model lớn hơn không giải quyết được – Isolation Forest cũng chỉ bắt khoảng 0,78.

**I3. Em có tự làm không? Có dùng công cụ AI không?**
> Trả lời trung thực theo đúng những gì bạn đã làm và đã dùng. Điều quan trọng là bạn giải thích được từng phần: chạy lại được một bước bất kỳ trước mặt thầy (ví dụ lệnh kiểm tra manifest ở A1, hoặc `pytest`), và trả lời được các câu ở file này bằng lời của mình.

**I4. Chạy thử một phần ngay bây giờ được không?**
> Được. Nhanh nhất là A1 (`02_verify_manifest.py`, ~1 phút), `pytest` (~1 phút), hoặc một lần chạy nhỏ: `.venv\Scripts\python ai/scripts/04_run_matrix.py E1_baseline --devices Danmini_Doorbell --seeds 42 --workers 1`.
