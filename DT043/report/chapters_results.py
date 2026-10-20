"""Chương 6–8: kết quả, phân tích, kết luận. Mọi con số đọc từ results/tables (sinh bởi ai/scripts/06,07,09)."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from docx_helpers import Report

SHORT = {"Danmini_Doorbell": "Danmini", "Ecobee_Thermostat": "Ecobee", "Ennio_Doorbell": "Ennio",
         "Philips_B120N10_Baby_Monitor": "Philips", "Provision_PT_737E_Security_Camera": "PT-737E",
         "Provision_PT_838_Security_Camera": "PT-838", "Samsung_SNH_1011_N_Webcam": "Samsung",
         "SimpleHome_XCS7_1002_WHT_Security_Camera": "SH-1002", "SimpleHome_XCS7_1003_WHT_Security_Camera": "SH-1003"}


def pm(m, s, d=4):
    return f"{m:.{d}f} ± {s:.{d}f}"


class Results:
    def __init__(self, root):
        T = root / "results" / "tables"
        self.root, self.T, self.F = root, T, root / "results" / "figures"
        self.summ = pd.read_csv(T / "summary_by_config.csv").set_index("exp")
        self.runs = pd.read_csv(T / "runs_long.csv")
        self.tests = pd.read_csv(T / "stat_tests.csv")
        self.crit = pd.read_csv(T / "criteria_check.csv")
        self.quant = pd.read_csv(T / "quantization_summary.csv")
        self.pa = pd.read_csv(T / "recall_per_attack.csv").set_index("attack")
        self.groups = pd.read_csv(T / "recall_groups.csv", header=[0, 1], index_col=0)
        self.b0 = pd.read_csv(T / "per_device_B0_vs_meidan.csv").set_index("device")
        self.abl = pd.read_csv(T / "ablation_threshold_window.csv")
        self.post = pd.read_csv(T / "posthoc_threshold.csv")
        self.bench = pd.read_csv(root / "results" / "raw" / "E8_edge" / "bench.csv")
        self.ev = pd.read_csv(T / "robust_evasion.csv")
        self.nz = pd.read_csv(T / "robust_noise.csv")
        self.harm = pd.read_csv(T / "mtd_harm_policies.csv")
        self.hyb = pd.read_csv(T / "mtd_hybrid_policy.csv")
        self.th_vm = pd.read_csv(T / "tharm_vm_vs_paper.csv")
        self.th_paths = pd.read_csv(T / "tharm_paths_vs_paper.csv")
        self.th_net = pd.read_csv(T / "tharm_network_vs_paper.csv")
        self.th_scen = pd.read_csv(T / "tharm_scenarios.csv")
        self.th_trend = pd.read_csv(T / "tharm_trends.csv")

    def s(self, exp, key):
        return self.summ.loc[exp, f"{key}_mean"], self.summ.loc[exp, f"{key}_std"], self.summ.loc[exp, f"{key}_ci95"]

    def test(self, name, metric="macro_f1"):
        r = self.tests[(self.tests.test == name) & (self.tests.metric == metric)]
        return r.iloc[0] if len(r) else None


def ch6_results(R: Report, X: Results):
    R.h1("Chương 6. Kết quả")
    R.para("Trừ khi ghi khác, số liệu là trung bình 9 thiết bị, mean ± std qua các seed và khoảng tin cậy 95% (KTC95), ở "
           "**mức cửa sổ** (sau majority vote). Bảng đầy đủ: results/tables/summary_by_config.csv.")
    R.h2("6.1 Tổng quan các cấu hình")
    order = [e for e in ["E1_baseline", "E2_global", "E2_shared_pdnorm", "E3_iforest", "E4_light", "E4_tiny_L5",
                         "E4_tiny_L3", "E4_tiny_L1", "E4_tiny_L01", "E4_tiny_L001", "E6_leak"] if e in X.summ.index]
    t = X.summ.loc[order]
    df = pd.DataFrame({
        "Cấu hình": t.config, "Seed": t.n_seeds.astype(int),
        "Tham số": [("–" if pd.isna(v) else f"{int(v):,}") for v in t.params],
        "macro-F1 (KTC95)": [f"{a:.3f} ± {b:.3f}" for a, b in zip(t.macro_f1_mean, t.macro_f1_ci95)],
        "TPR": t.tpr_mean, "FPR": t.fpr_mean, "F1 cân bằng": t.f1_balanced_mean, "ROC-AUC": t.roc_auc_mean,
        "ws* TB": t.ws_mean})
    R.table(df, "Kết quả tổng hợp theo cấu hình (mức cửa sổ)", font=8.5, decimals=4,
            fmt={"ws* TB": lambda v: f"{v:.0f}"})
    R.para("Ghi chú: E6 là đối chứng rò rỉ, không phải kết quả hiệu năng. Accuracy chỉ có trong file CSV, không dùng để "
           "kết luận vì tập test mất cân bằng nặng.", italic=True, size=11)

    R.h2("6.2 RQ1 – Tái lập baseline Meidan (B0)")
    tpr, tprs, _ = X.s("E1_baseline", "tpr")
    fpr, fprs, _ = X.s("E1_baseline", "fpr")
    R.para(f"B0 đạt TPR = {pm(tpr, tprs)} và FPR = {pm(fpr, fprs)}. **FPR thấp hơn mức của Meidan (0.007)**, nhưng **TPR "
           f"không đạt 100%** như paper → tiêu chí RQ1 (TPR ≥ 0.99) **không đạt**. ROC-AUC mức mẫu vẫn cao "
           f"({X.s('E1_baseline', 'roc_auc')[0]:.4f}), tức là điểm MSE phân tách tốt; vấn đề nằm ở **ngưỡng** chứ không phải "
           "ở khả năng biểu diễn của AE (phân tích ở Chương 7).")
    b = X.b0
    df = pd.DataFrame({
        "Thiết bị": [SHORT[d] for d in b.index], "TPR": b.tpr_mean, "FPR": b.fpr_mean,
        "macro-F1": [pm(m, s, 3) for m, s in zip(b.macro_f1_mean, b.macro_f1_std.fillna(0))],
        "tr* (DT043)": b.thr_mean, "tr* Meidan": b.meidan_thr,
        "ws* (min–max)": [f"{int(a)}–{int(c)}" for a, c in zip(b.ws_min, b.ws_max)], "ws* Meidan": b.meidan_ws})
    R.table(df, "B0 theo thiết bị, đối chiếu tr*/ws* của Meidan 2018 (tr* phụ thuộc cách chuẩn hóa nên chỉ để tham khảo)",
            font=8.5, decimals=4, fmt={"tr* (DT043)": lambda v: f"{v:.3g}", "tr* Meidan": lambda v: f"{v:.3f}",
                                        "ws* Meidan": lambda v: str(int(v))})
    R.figure(X.F / "fig_macro_f1_per_device.png", "macro-F1 theo thiết bị cho các cấu hình chính (mean ± std qua seed)")

    R.h2("6.3 RQ2 – Per-device so với model chung")
    for name, lab in (("RQ2: per-device > global", "B0 so với B1 global"),
                      ("RQ2b: model riêng > model chung (cùng pdnorm)", "B0 so với model chung + chuẩn hóa riêng"),
                      ("RQ2c: pdnorm > global norm (cùng model chung)", "Chuẩn hóa riêng so với chung (cùng model chung)")):
        r = X.test(name)
        if r is not None:
            R.bullets([f"**{lab}:** chênh lệch macro-F1 trung bình {r.mean_diff:+.4f}, thắng {int(r.wins)}/9 thiết bị, "
                       f"Wilcoxon một phía p = {r.p:.4f} (Holm {r.p_holm:.4f})."])
    if "E2_global" in X.summ.index:
        R.para(f"B1 global có FPR = {X.s('E2_global', 'fpr')[0]:.4f} và cửa sổ trung bình "
               f"{X.summ.loc['E2_global', 'ws_mean']:.0f} mẫu (B0: {X.summ.loc['E1_baseline', 'ws_mean']:.0f}). Ngưỡng chung "
               "phải đủ cao cho thiết bị \"ồn\" nhất, nên với các thiết bị khác nó vừa dễ bỏ sót vừa cần cửa sổ dài hơn. "
               "Kết quả RQ2 được trình bày đúng như kiểm định ở trên, kể cả khi không ủng hộ giả thuyết.")
    if "E2_shared_pdnorm" in X.summ.index:
        R.para(f"Phát hiện ngoài dự kiến: **một model dùng chung nhưng chuẩn hóa và ngưỡng riêng từng thiết bị** đạt macro-F1 "
               f"{X.s('E2_shared_pdnorm', 'macro_f1')[0]:.4f}, cao hơn B0 ({X.s('E1_baseline', 'macro_f1')[0]:.4f}) và B1 global "
               f"({X.s('E2_global', 'macro_f1')[0]:.4f}). Điều này gợi ý rằng phần \"per-device\" quan trọng là **chuẩn hóa và "
               "ngưỡng**, còn bản thân model có thể dùng chung (được học trên nhiều dữ liệu hơn). Tuy nhiên với 9 thiết bị và "
               "hiệu chỉnh Holm, không so sánh nào đạt ý nghĩa thống kê, nên đây chỉ là xu hướng cần kiểm chứng thêm.")

    R.h2("6.4 RQ3 – Model nhẹ")
    r = X.test("RQ3: V1 vs B0")
    c = X.crit.set_index("RQ")
    R.para(f"V1 có 8,059 tham số (21.9% của B0), file TFLite fp32 {X.quant[(X.quant.exp == 'E4_light') & (X.quant['mode'] == 'fp32')].size_bytes_mean.iloc[0] / 1024:.1f} KB. "
           f"macro-F1 của V1 = {pm(*X.s('E4_light', 'macro_f1')[:2])} so với B0 {pm(*X.s('E1_baseline', 'macro_f1')[:2])}"
           + (f"; Wilcoxon hai phía p = {r.p:.4f}" if r is not None else "") + f". Tiêu chí RQ3: {c.loc['RQ3', 'value']} → "
           f"**{'đạt' if c.loc['RQ3', 'pass'] else 'không đạt'}**.")
    tiny = [e for e in X.summ.index if e.startswith("E4_tiny")]
    if tiny:
        t = X.summ.loc[tiny]
        R.table(pd.DataFrame({"Cửa sổ thời gian": [e.replace("E4_tiny_", "") for e in tiny], "Seed": t.n_seeds.astype(int),
                              "macro-F1": t.macro_f1_mean, "TPR": t.tpr_mean, "FPR": t.fpr_mean,
                              "F1 cân bằng": t.f1_balanced_mean}),
                "V2 – AE 23-12-4-12-23 trên 23 đặc trưng của từng cửa sổ thời gian (báo cáo cả 5, không chọn lọc)", font=9)
        best = t.macro_f1_mean.idxmax()
        R.para(f"Với chỉ ~700 tham số, V2 dùng cửa sổ {best.replace('E4_tiny_', '')} đạt macro-F1 "
               f"{t.loc[best, 'macro_f1_mean']:.4f} – cao hơn B0 – nhờ bắt được tcp/udp ở nhiều thiết bị hơn; các cửa sổ ngắn "
               "hơn thì kém hơn. Vì đây là 1 trong 5 cấu hình được thử đồng thời và chỉ có 3 seed, kết quả này **không** được "
               "dùng để tuyên bố V2 tốt hơn; nó chỉ cho thấy thông tin dài hạn (cửa sổ 1 phút) có ích cho flood giả mạo nguồn.")

    R.h2("6.5 RQ4 – Lượng tử hóa và hiệu chỉnh ngưỡng")
    q = X.quant[X.quant.exp.isin(["E1_baseline", "E4_light"])].copy()
    q["Model"] = q.exp.map({"E1_baseline": "B0", "E4_light": "V1"})
    R.table(pd.DataFrame({"Model": q.Model, "Kiểu": q["mode"], "Ngưỡng": q.calib.map({"keep": "giữ fp32", "recal": "hiệu chỉnh"}),
                          "KB": q.size_bytes_mean / 1024, "macro-F1": q.macro_f1_mean, "TPR": q.tpr_mean,
                          "FPR": q.fpr_mean, "ws* TB": q.ws_mean}),
            "Lượng tử hóa TFLite: kích thước và chất lượng (trung bình 9 thiết bị × 5 seed)", font=9,
            fmt={"KB": lambda v: f"{v:.1f}", "ws* TB": lambda v: f"{v:.0f}"})
    v1 = q[q.Model == "V1"].set_index(["mode", "calib"])
    R.para(f"Full-int8 giảm kích thước file V1 từ {v1.loc[('fp32', 'keep'), 'size_bytes_mean'] / 1024:.1f} KB xuống "
           f"{v1.loc[('int8', 'keep'), 'size_bytes_mean'] / 1024:.1f} KB "
           f"({v1.loc[('int8', 'keep'), 'size_bytes_mean'] / v1.loc[('fp32', 'keep'), 'size_bytes_mean']:.0%}); trọng số "
           "giảm đúng 4 lần nhưng phần khung flatbuffer và tham số lượng tử hóa chiếm tỷ trọng lớn ở model nhỏ, nên tỷ lệ "
           "file không đạt mức 30% đã đặt ra. Fp16 và dynamic-range gần như không đổi chất lượng.")
    R.para(f"**Hiệu chỉnh ngưỡng sau int8** giảm FPR của V1 từ {v1.loc[('int8', 'keep'), 'fpr_mean']:.4f} xuống "
           f"{v1.loc[('int8', 'recal'), 'fpr_mean']:.4f} và rút cửa sổ từ {v1.loc[('int8', 'keep'), 'ws_mean']:.0f} xuống "
           f"{v1.loc[('int8', 'recal'), 'ws_mean']:.0f} mẫu (phát hiện nhanh hơn). Tuy nhiên macro-F1 lại giảm "
           f"({v1.loc[('int8', 'keep'), 'macro_f1_mean']:.4f} → {v1.loc[('int8', 'recal'), 'macro_f1_mean']:.4f}): khi giữ "
           "ngưỡng fp32, nhiễu lượng tử hóa làm MSE của gafgyt tcp/udp ở một số thiết bị \"vô tình\" vượt ngưỡng; hiệu chỉnh "
           "lại ngưỡng một cách đúng quy trình làm mất phần may mắn này. Vì vậy không thể kết luận hiệu chỉnh ngưỡng là cải "
           f"tiến về macro-F1; nó là cải tiến về FPR và độ trễ. Tiêu chí RQ4: {c.loc['RQ4', 'value']} → "
           f"**{'đạt' if c.loc['RQ4', 'pass'] else 'không đạt'}**.")
    R.figure(X.F / "fig_quantization_tradeoff.png", "Kích thước file và macro-F1 theo kiểu lượng tử hóa", 13)

    R.h2("6.6 RQ5 – Edge benchmark")
    b = X.bench.copy()
    p1 = b[b.profile == "P1_edge"].sort_values(["model", "mode"])
    R.table(pd.DataFrame({"Model": p1.model, "Kiểu": p1["mode"], "KB": p1.size_kb, "p50 µs": p1.p50_us,
                          "p95 µs": p1.p95_us, "p99 µs": p1.p99_us, "invoke p50 µs": p1.invoke_p50_us,
                          "mẫu/s": p1.throughput_samples_s, "ΔRSS MB": p1.rss_delta_mb, "µJ/mẫu*": p1.energy_proxy_uJ,
                          "MAC": p1.macs}),
            "Profile P1 – edge giả lập (1 luồng, ghim 1 E-core, batch 1)", font=8,
            fmt={"KB": lambda v: f"{v:.1f}", "p50 µs": lambda v: f"{v:.1f}", "p95 µs": lambda v: f"{v:.1f}",
                 "p99 µs": lambda v: f"{v:.1f}", "invoke p50 µs": lambda v: f"{v:.1f}", "mẫu/s": lambda v: f"{v:,.0f}",
                 "ΔRSS MB": lambda v: f"{v:.1f}", "µJ/mẫu*": lambda v: f"{v:.1f}", "MAC": lambda v: f"{int(v):,}"})
    R.para("(*) Energy proxy = CPU-time mỗi mẫu × 55 W/14 lõi – cận trên thô, không phải đo điện; MAC là số phép nhân-cộng "
           "mỗi lần suy luận, độc lập phần cứng.", italic=True, size=10)
    p0 = b[(b.profile == "P0_b1") & (b["mode"] == "int8") & (b.model == "V1")]
    pb = b[(b.profile == "P0_b256") & (b["mode"] == "int8") & (b.model == "V1")]
    v1p1 = p1[(p1.model == "V1") & (p1["mode"] == "int8")].iloc[0]
    R.para(f"V1 int8 ở P1: p95 = {v1p1.p95_us:.1f} µs, ~{v1p1.throughput_samples_s:,.0f} mẫu/giây trên một lõi E-core, "
           f"RSS tăng {v1p1.rss_delta_mb:.1f} MB → **đạt** các ngưỡng thời gian và bộ nhớ của RQ5 với biên rất lớn. "
           f"Kích thước {v1p1.size_kb:.1f} KB ≤ 50 KB. Phần lớn thời gian mỗi lần gọi là chi phí Python "
           f"(set_tensor/get_tensor); riêng invoke() chỉ ~{v1p1.invoke_p50_us:.1f} µs."
           + (f" Đáng chú ý, chạy batch 1 với 20 luồng (P0) **chậm hơn** nhiều (p50 = {p0.p50_us.iloc[0]:.0f} µs) do chi phí "
              "đồng bộ luồng – với model nhỏ nên chạy đơn luồng; đa luồng chỉ có lợi khi xử lý lô"
              + (f" (batch 256: {pb.throughput_samples_s.iloc[0]:,.0f} mẫu/s)." if len(pb) else ".") if len(p0) else ""))
    R.para("Giới hạn: không có Raspberry Pi; P1 là giả lập trên lõi E-core của CPU laptop (mạnh hơn CPU edge thực tế), nên "
           "con số tuyệt đối lạc quan hơn thực tế, nhưng thứ tự tương đối giữa các model vẫn có ý nghĩa.")

    R.h2("6.7 RQ6 – Mô phỏng MTD")
    h = X.harm
    h20 = h[h.period == 20].set_index("policy")
    R.table(pd.DataFrame({"Chu kỳ": h.period, "Chính sách": h.policy, "ASP": h.asp_mean, "± std": h.asp_std,
                          "Chi phí tấn công": h.attack_cost_mean_mean, "Số move/đợt": h.mtd_moves_per_run_mean}),
            "HARM rút gọn: xác suất tấn công thành công (ASP) trong ngân sách 20 bước", font=9,
            fmt={"Chu kỳ": lambda v: str(int(v)), "Chi phí tấn công": lambda v: f"{v:.1f}", "Số move/đợt": lambda v: f"{v:.2f}"})
    R.para(f"Ở chu kỳ 20 bước: không MTD ASP = {h20.loc['none', 'asp_mean']:.3f}, shuffle {h20.loc['shuffle', 'asp_mean']:.3f}, "
           f"diversity {h20.loc['diversity', 'asp_mean']:.3f}, **kết hợp {h20.loc['combined', 'asp_mean']:.3f}** – tái lập được "
           "**xu hướng** của paper chính (kết hợp hai nhóm kỹ thuật cho ASP thấp nhất). Ở chu kỳ ngắn, shuffle một mình đã "
           "chặn hoàn toàn nhưng số lần move tăng tương ứng; mô hình rút gọn không tính chi phí gián đoạn dịch vụ nên không "
           "phản ánh đầy đủ mặt trái này. Đây là tái lập xu hướng định tính, không so số tuyệt đối với paper.")
    R.figure(X.F / "fig_mtd_harm.png", "ASP theo chu kỳ MTD và chính sách", 12)
    hy = X.hyb
    R.table(pd.DataFrame({"Chính sách": hy.policy, "Chu kỳ T": hy.period, "Lộ diện TB (mẫu)": hy.exposure_mean,
                          "Lộ diện p95": hy.exposure_p95, "Move/10k mẫu": hy.moves_per_10k,
                          "Move vô ích/10k benign": hy.wasted_moves_per_10k_benign}),
            "MTD lai kích hoạt bởi cảnh báo AE (V1, seed 42, trung bình 9 thiết bị)", font=9,
            fmt={"Chu kỳ T": lambda v: "–" if v == 0 else str(int(v)), "Lộ diện TB (mẫu)": lambda v: f"{v:.0f}",
                 "Lộ diện p95": lambda v: f"{v:.0f}", "Move/10k mẫu": lambda v: f"{v:.2f}",
                 "Move vô ích/10k benign": lambda v: f"{v:.2f}"})
    ev = hy[hy.policy == "event"].iloc[0]
    tm = hy[(hy.policy == "time")].set_index("period")
    hb = hy[(hy.policy == "hybrid")].set_index("period")
    R.para(f"Chỉ dùng event-based (move khi AE cảnh báo), thời gian lộ diện trung bình là {ev.exposure_mean:.0f} mẫu với "
           f"{ev.moves_per_10k:.2f} move/10.000 mẫu; các đợt tấn công AE bỏ sót (gafgyt tcp/udp ở một số thiết bị) bị lộ "
           f"diện suốt đợt, kéo p95 lên {ev.exposure_p95:.0f}. Hybrid với T = 2000 có lộ diện "
           f"{hb.loc[2000, 'exposure_mean']:.0f} mẫu với chi phí {hb.loc[2000, 'moves_per_10k']:.2f} move/10k, trong khi "
           f"time-based phải dùng T = 500 ({tm.loc[500, 'moves_per_10k']:.0f} move/10k, nhiều hơn) mới đạt lộ diện tương đương "
           f"({tm.loc[500, 'exposure_mean']:.0f} mẫu). Nói cách khác, **ở cùng mức chi phí, đường hybrid nằm dưới đường "
           "time-based** trong vùng chi phí thấp–trung bình; khi move rất dày (T = 100) hai chiến lược hội tụ vì đồng hồ đã "
           "đủ nhanh. Thành phần time-based là \"lưới an toàn\" cho các tấn công detector bỏ sót, thành phần event-based rút "
           "ngắn lộ diện khi detector bắt được – đúng tinh thần MTD lai và ủng hộ giả thuyết H6. Move vô ích do cảnh báo giả "
           "rất thấp nhờ FPR mức cửa sổ thấp.")
    R.figure(X.F / "fig_mtd_hybrid_tradeoff.png", "Trade-off an ninh (thời gian lộ diện) và chi phí (số move) của MTD", 12)

    R.page_break()
    R.h2("6.8 E11 – Tái lập 3-layer THARM bằng đúng số liệu của paper chính")
    R.para("Sau khi có toàn văn, mô hình 3-layer THARM được dựng lại bằng **dữ liệu của chính paper**: 18 CVE hệ điều hành "
           "(Bảng 1) và 14 CVE dịch vụ (Bảng 2) với exploitability E, impact I, cost; gán OS cho 8 VM theo Hình 1, dịch vụ "
           "theo Hình 3, đồ thị tấn công theo Definition 2; shuffle (V5 di trú host 2 → host 4), diversity (đổi OS dự phòng) "
           "và redundancy (nhân bản V5) theo mục 4.2–4.4 (ai/src/nbaiot/mtd/tharm.py, 12 test so khớp số của paper).")
    vm = X.th_vm
    keep = vm[vm["R_paper(mục 4.2–4.3)"].notna()]
    rows = [[r.VM, f"{r['R_paper(mục 4.2–4.3)']:.2f}", f"{r['R_ours(ΣE·I)']:.3f}"] for _, r in keep.iterrows()]
    rows += [[p["đường (ví dụ của paper)"], f"{p.R_paper:.2f}", f"{p.R_ours:.2f} ({p['lệch %']:+.1f}%)"]
             for _, p in X.th_paths.iterrows()]
    R.table(pd.DataFrame(rows, columns=["Rủi ro (VM / đường tấn công)", "Paper", "Tái lập"]),
            "Rủi ro mức VM và mức đường tấn công so với số paper công bố", font=9, col_widths_cm=[7.5, 3.0, 5.5])
    R.para("Rủi ro mức VM khớp tới ±0.01 khi diễn giải Eq. 2 là **tổng** R = Σ E·I (bản in ghi tích); chỉ R_V2 lệch "
           "(paper 16.28, Bảng 1–2 cho 15.94) và chính sai khác này tạo ra mức lệch −0.8% ở cả ba đường tấn công ví dụ. "
           "Attack cost từng VM khớp Bảng 4 ở V1 (8.17) và V8 (6.27); ASP của Bảng 4 không tái lập được vì Eq. 1 bản in có thể "
           "âm và paper không công bố mã nguồn.")
    net = X.th_net.pivot(index="MTD", columns="chỉ số", values=["paper", "ours"])
    R.table(pd.DataFrame([[m, f"{net.loc[m, ('paper', 'R')]:.2f}", f"{net.loc[m, ('ours', 'R')]:.2f}",
                           f"{net.loc[m, ('paper', 'AC')]:.1f}", f"{net.loc[m, ('ours', 'AC')]:.1f}"]
                          for m in ("shuffle", "diversity", "redundancy")],
                         columns=["MTD trên V5", "R paper", "R tái lập", "AC paper", "AC tái lập"]),
            "Tổng toàn mạng: không tái lập được số tuyệt đối", font=9)
    tr = X.th_trend.pivot(index="kết luận của paper", columns="topology", values="tái lập")
    tr = tr.loc[X.th_trend["kết luận của paper"].drop_duplicates()]
    R.table(pd.DataFrame({"Kết luận của paper": tr.index,
                          "Definition 2": tr["Definition 2"].map({True: "Tái lập", False: "Không"}).values,
                          "Hình 3 (+V6→V4)": tr["Hình 3 (+V6→V4)"].map({True: "Tái lập", False: "Không"}).values}),
            "Xu hướng định tính của paper trên hai topology", font=9, col_widths_cm=[9.5, 3.2, 3.3])
    n_fig3 = int(X.th_trend[X.th_trend.topology != "Definition 2"]["tái lập"].sum())
    n_def2 = int(X.th_trend[X.th_trend.topology == "Definition 2"]["tái lập"].sum())
    R.para(f"Tổng toàn mạng của paper không suy ra được từ dữ liệu công bố (danh sách cạnh sau shuffle bị cắt; AC theo VM "
           f"ở mục 4.2 lớn gấp 5–8 lần tổng cost của Bảng 1–2; RoC toàn mạng không bằng R/AC của chính paper), nên chỉ so "
           f"xu hướng. Với topology vẽ trong Hình 3, **{n_fig3}/7 kết luận định tính** tái lập được, gồm kết luận chính "
           f"\"shuffle + diversity có rủi ro thấp nhất\"; với đúng danh sách cạnh của Definition 2 chỉ còn {n_def2}/7 – kết "
           "luận của paper nhạy với một cạnh (V6 → V4) mà định nghĩa và hình vẽ ghi không thống nhất. Chi tiết: "
           "docs/tai_lap_paper_chinh.md.")
    R.figure(X.F / "fig_tharm_scenarios.png", "Tái lập 3-layer THARM: rủi ro, chi phí và ASP theo kịch bản MTD", 15.5)

    R.h2("6.9 Bảng đối chiếu tiêu chí đã chốt trước")
    R.table(pd.DataFrame({"RQ": X.crit.RQ, "Tiêu chí": X.crit.criterion, "Giá trị đo": X.crit.value,
                          "Kết luận": X.crit["pass"].map({True: "Đạt", False: "Không đạt"})}),
            "Kết quả so với tiêu chí thành công (docs/tieu_chi_thanh_cong.md)", font=9,
            col_widths_cm=[1.2, 6.3, 6.0, 2.5])


def ch7_analysis(R: Report, X: Results):
    R.h1("Chương 7. Phân tích lỗi, độ ổn định, ablation và chi phí")
    R.h2("7.1 Phân tích lỗi: bỏ sót BASHLITE tcp/udp")
    g = X.groups
    rows = []
    for exp, lab in (("E1_baseline", "B0"), ("E4_light", "V1"), ("E2_global", "B1 global"), ("E3_iforest", "B2 IF")):
        if exp in g.index:
            rows.append([lab, g.loc[exp, ("mean", "tcp_udp")], g.loc[exp, ("mean", "8_loai_con_lai")]])
    R.table(pd.DataFrame(rows, columns=["Cấu hình", "Recall tcp/udp", "Recall 8 loại còn lại"]),
            "Recall trung bình theo nhóm tấn công", font=10)
    R.para("Tám loại tấn công còn lại được phát hiện gần như tuyệt đối ở mọi cấu hình AE; toàn bộ suy giảm TPR/macro-F1 "
           "đến từ **gafgyt/tcp và gafgyt/udp**. Với mỗi thiết bị, hai loại này hoặc bị phát hiện hoàn toàn hoặc bị bỏ sót "
           "hoàn toàn. Nguyên nhân (kiểm tra trên dữ liệu thô): trong flood của BASHLITE, địa chỉ nguồn bị giả mạo liên tục "
           "nên mỗi gói trông như **gói đầu tiên của một luồng mới** – weight = 1, variance = 0, mean = 60 byte – gần như mọi "
           "vector đặc trưng giống hệt nhau và nằm sát vùng benign (benign cũng có các bản ghi \"luồng mới\" như vậy). MSE "
           "của chúng (≈ 0.17 ở Ennio) chỉ cao hơn phần lớn benign chứ không cao hơn đuôi phân phối benign; trong khi ngưỡng "
           "mean + std bị đuôi dài của MSE trên DSopt kéo lên rất cao (vd. 22.5 ở Ennio).")
    R.figure(X.F / "fig_error_mse_hist.png",
             "Phân phối MSE của B0 trên Ennio: tcp và udp trùng nhau ở MSE ≈ 0.17, dưới ngưỡng mean+std", 14)
    R.figure(X.F / "fig_recall_per_attack.png", "Recall theo loại tấn công", 14)
    R.para("**Vì sao Meidan đạt TPR 100% còn DT043 thì không?** Các khác biệt có thể giải thích: (1) DT043 khử trùng lặp "
           "và thêm purge gap; (2) DT043 dùng Adam + early stopping thống nhất thay vì tối ưu η/epochs (100–800) riêng từng "
           "thiết bị; (3) cách chuẩn hóa của paper không được mô tả, trong khi z-score làm các cột gần hằng có độ lệch rất "
           "lớn ở mẫu bất thường, làm đuôi MSE dài hơn; (4) 5 seed thay vì 1 lần chạy. DT043 không đủ dữ kiện để chỉ ra "
           "nguyên nhân duy nhất; đây là điểm \"không tái lập được\" được báo cáo trung thực.")
    R.h3("Phân tích khám phá hậu kiểm (không thuộc tiêu chí chốt trước)")
    p = X.post
    R.table(pd.DataFrame({"Model": p.exp.map({"E1_baseline": "B0", "E4_light": "V1"}), "Quy tắc ngưỡng": p.rule,
                          "TPR": p.tpr, "FPR": p.fpr, "macro-F1": p.macro_f1, "Recall tcp/udp": p.recall_tcp_udp,
                          "ws* TB": p.ws}),
            "Hậu kiểm: ngưỡng theo percentile DSopt + ws* (FPR=0 trên DSopt, tối đa 5000) – seed 42", font=9,
            fmt={"ws* TB": lambda v: f"{v:.0f}"})
    best = p[(p.exp == "E4_light") & (p.rule == "p75")].iloc[0]
    R.para(f"Hạ ngưỡng xuống percentile 75 của DSopt (vẫn chọn hoàn toàn trên DSopt) làm V1 bắt được 100% tcp/udp và macro-F1 "
           f"tăng lên {best.macro_f1:.4f}, nhưng cần cửa sổ ~{best.ws:.0f} mẫu (phát hiện chậm hơn nhiều) và FPR trên test "
           f"tăng lên {best.fpr:.4f} dù FPR trên DSopt = 0 – dấu hiệu **trôi phân phối benign theo thời gian** (DSopt và test "
           "là hai đoạn thời gian khác nhau). Kết luận: lỗi chủ yếu nằm ở lựa chọn ngưỡng/cửa sổ và có trade-off rõ giữa "
           "phát hiện tấn công \"giống benign\" với độ trễ và cảnh báo giả. Vì quy tắc này được đề xuất **sau khi** đã xem "
           "kết quả test, đề tài không tuyên bố đây là cải tiến; muốn khẳng định cần đánh giá trên dữ liệu mới.")

    R.h2("7.2 Độ ổn định theo seed")
    sd = X.runs[X.runs.exp.isin(["E1_baseline", "E4_light"])].groupby(["exp", "device"])["tpr"].agg(["min", "max", "std"])
    unstable = sd[sd["max"] - sd["min"] > 0.05].reset_index()
    R.figure(X.F / "fig_seed_stability.png", "Phân bố macro-F1 qua 5 seed theo thiết bị (B0 và V1)", 14)
    if len(unstable):
        R.table(pd.DataFrame({"Model": unstable.exp.map({"E1_baseline": "B0", "E4_light": "V1"}),
                              "Thiết bị": unstable.device.map(SHORT), "TPR min": unstable["min"], "TPR max": unstable["max"]}),
                "Các thiết bị có TPR dao động > 0.05 giữa các seed", font=9.5)
    R.para("Cùng dữ liệu và cấu hình, chỉ đổi seed khởi tạo đã có thể lật kết quả phát hiện tcp/udp của một thiết bị (TPR "
           "nhảy giữa ~0.77 và 1.00). Đây là lý do một lần chạy (như Meidan) không đủ để kết luận, và vì sao đề tài báo cáo "
           "mean ± std, KTC95 và kiểm định thay vì một con số tốt nhất. KTC95 của macro-F1 rộng (Bảng tổng hợp) phản ánh đúng "
           "độ bất định này.")

    R.h2("7.3 Ablation")
    a = X.abl[X.abl.exp == "E1_baseline"]
    R.table(pd.DataFrame({"Quy tắc": a.rule, "Cửa sổ": a.ws_kind, "ws TB": a.ws_mean, "TPR": a.tpr_mean, "FPR": a.fpr_mean,
                          "macro-F1": a.macro_f1_mean, "F1 cân bằng": a.f1_balanced_mean}),
            "B0: quy tắc ngưỡng × kích thước cửa sổ (trung bình 9 thiết bị × 5 seed)", font=9,
            fmt={"ws TB": lambda v: f"{v:.0f}"})
    R.figure(X.F / "fig_ablation_threshold.png", "Ablation quy tắc ngưỡng và cửa sổ (B0)", 14)
    R.bullets([
        "**Cửa sổ:** ws = 1 (quyết định từng mẫu) cho FPR cao hơn rõ rệt; ws* giảm FPR nhiều lần; 2ws* gần như triệt tiêu "
        "FPR nhưng tăng gấp đôi độ trễ – majority vote là thành phần quan trọng như Meidan mô tả.",
        "**Quy tắc ngưỡng:** ngưỡng càng cao càng ít cảnh báo giả nhưng càng dễ bỏ sót các tấn công \"giống benign\".",
        "**Per-device normalization và model riêng:** xem 6.3 (B0, B1 global, model chung + chuẩn hóa riêng).",
        "**Số đặc trưng / cửa sổ thời gian:** xem bảng V2 ở 6.4.",
        "**Lượng tử hóa và hiệu chỉnh ngưỡng:** xem 6.5.",
    ])
    if "E6_leak" in X.summ.index:
        r = X.test("Rò rỉ: chia đúng vs chia sai")
        R.h3("Đối chứng rò rỉ (E6)")
        R.para(f"Khi cố tình chia ngẫu nhiên, không purge, không khử trùng và fit scaler trên cả test, FPR là "
               f"{X.s('E6_leak', 'fpr')[0]:.4f} (so với {X.s('E1_baseline', 'fpr')[0]:.4f} khi làm đúng) và cửa sổ trung bình "
               f"{X.summ.loc['E6_leak', 'ws_mean']:.0f} mẫu (so với {X.summ.loc['E1_baseline', 'ws_mean']:.0f})."
               + (f" Chênh lệch macro-F1 (đúng − sai) {r.mean_diff:+.4f}, p = {r.p:.4f}." if r is not None else "")
               + " Rò rỉ làm tập test benign \"giống\" tập train hơn, nên các con số đánh giá trở nên lạc quan giả tạo "
                 "về cảnh báo giả – minh chứng cho việc phải chia theo thời gian.")

    R.h2("7.4 Robustness (tấn công được phép, offline)")
    ev = X.ev.set_index("alpha")
    nz = X.nz.set_index("sigma")
    R.table(pd.DataFrame({"α": ev.index, "TPR TB": ev["mean"].values, "TPR min": ev["min"].values}),
            "Né tránh kiểu mimicry: x' = (1−α)·x + α·μ_benign (V1, 3 seed)", font=10)
    R.para(f"Kéo mẫu tấn công dần về tâm benign làm TPR giảm từ {ev['mean'].iloc[0]:.3f} (α = 0) xuống "
           f"{ev['mean'].iloc[-1]:.3f} (α = {ev.index[-1]}). Vì đặc trưng tấn công lệch benign nhiều bậc độ lớn, kẻ tấn công "
           "phải \"bắt chước\" benign rất sát mới né được – đồng nghĩa phải giảm cường độ tấn công (một thắng lợi một phần "
           "của phòng thủ). Nhiễu Gaussian lên benign test: FPR " +
           ", ".join(f"σ={s:g}: {v:.4f}" for s, v in nz["mean"].items()) + ". Nhiễu nhỏ (σ = 0.1 độ lệch chuẩn) "
           "gần như không ảnh hưởng, nhưng nhiễu lớn làm cảnh báo giả tăng vọt: bộ phát hiện giả định đặc trưng được "
           "trích chính xác; nếu đặc trưng ở edge bị sai lệch (lỗi đồng hồ, mất gói) thì cần hiệu chỉnh lại ngưỡng.")
    R.figure(X.F / "fig_evasion.png", "TPR theo mức né tránh α", 9)
    pois = [e for e in ("E9_poison_1", "E9_poison_5") if e in X.summ.index]
    if pois and "E9_robust" in X.summ.index:
        R.table(pd.DataFrame({"Cấu hình": ["V1 sạch (E9)"] + [X.summ.loc[e, "config"] for e in pois],
                              "TPR": [X.s("E9_robust", "tpr")[0]] + [X.s(e, "tpr")[0] for e in pois],
                              "FPR": [X.s("E9_robust", "fpr")[0]] + [X.s(e, "fpr")[0] for e in pois],
                              "macro-F1": [X.s("E9_robust", "macro_f1")[0]] + [X.s(e, "macro_f1")[0] for e in pois]}),
                "Đầu độc dữ liệu huấn luyện (3 seed)", font=10)
        R.para("Đầu độc làm AE học tái tạo luôn mẫu tấn công và ngưỡng trên DSopt không đổi tương ứng – minh họa giả định "
               "\"dữ liệu benign ban đầu sạch\" của Meidan là điểm yếu cần bảo vệ (thu thập baseline ngay sau lắp đặt, cách ly).")

    R.h2("7.5 Chi phí tính toán và triển khai")
    rt = X.runs.groupby("exp")[["train_time_s", "epochs"]].mean()
    rows = [[X.summ.loc[e, "config"], rt.loc[e, "train_time_s"], rt.loc[e, "epochs"]] for e in
            ["E1_baseline", "E4_light", "E3_iforest", "E2_global"] if e in rt.index]
    R.table(pd.DataFrame(rows, columns=["Cấu hình", "Huấn luyện TB (s)", "Epoch TB"]),
            "Chi phí huấn luyện (2 luồng CPU / process)", font=10,
            fmt={"Huấn luyện TB (s)": lambda v: f"{v:.1f}", "Epoch TB": lambda v: "–" if pd.isna(v) else f"{v:.0f}"})
    R.bullets([
        f"Toàn bộ ma trận ({len(X.runs)} kết quả theo thiết bị × seed) mất vài giờ CPU trên laptop; huấn luyện một model per-device chỉ vài chục giây – "
        "khả thi để huấn luyện lại định kỳ tại gateway hoặc trên server rồi đẩy gói triển khai xuống.",
        "Suy luận V1 int8: vài µs/mẫu trên một lõi E-core, < 20 KB model, vài MB RAM – không phải nút thắt; nút thắt thực tế "
        "là trích 115 đặc trưng cho mỗi gói tin (ngoài phạm vi đề tài).",
        "Chi phí vận hành chính là **chọn ngưỡng/cửa sổ cho từng thiết bị** và theo dõi trôi phân phối benign.",
    ])


def ch8_conclusion(R: Report, X: Results):
    R.h1("Chương 8. Bảng ánh xạ, giới hạn và kết luận")
    R.h2("8.1 Bảng ánh xạ kết quả với paper")
    b = X.summ.loc["E1_baseline"]
    q = X.quant[(X.quant.exp == "E4_light") & (X.quant["mode"] == "int8") & (X.quant.calib == "recal")].iloc[0]
    R.table(pd.DataFrame([
        ["TPR (mức cửa sổ)", "100% mọi thiết bị", f"{b.tpr_mean:.4f} ± {b.tpr_std:.4f}", f"{q.tpr_mean:.4f}",
         "Không tái lập được (tcp/udp)"],
        ["FPR trung bình", "0.007 ± 0.01", f"{b.fpr_mean:.4f} ± {b.fpr_std:.4f}", f"{q.fpr_mean:.4f}", "Tương đương/thấp hơn"],
        ["ws*", "20–82", f"TB {b.ws_mean:.0f}", f"TB {q.ws_mean:.0f}", "Dài hơn (purge, dedup)"],
        ["Kích thước model", "172 kB (Keras)", "147.7 KB (TFLite fp32)", f"{q.size_bytes_mean / 1024:.1f} KB (int8)", "Giảm ~10×"],
        ["Baseline IF – FPR", "0.027 ± 0.041", f"{X.s('E3_iforest', 'fpr')[0]:.4f}" if "E3_iforest" in X.summ.index else "–",
         "–", "Tham khảo"],
        ["Thời gian phát hiện", "174 ± 212 ms", "theo số mẫu (không có timestamp)", "–", "Không so trực tiếp được"],
    ], columns=["Chỉ số", "Meidan 2018", "DT043 B0", "DT043 V1 int8+hiệu chỉnh", "Nhận xét"]),
        "Ánh xạ với Meidan 2018", font=9, col_widths_cm=[3.0, 3.0, 3.6, 3.4, 3.0])
    h20 = X.harm[X.harm.period == 20].set_index("policy")
    R.table(pd.DataFrame([
        ["Xếp hạng chiến lược (HARM rút gọn)", "Kết hợp shuffle + diversity tốt nhất",
         f"Kết hợp {h20.loc['combined', 'asp_mean']:.3f} < shuffle {h20.loc['shuffle', 'asp_mean']:.3f} < diversity "
         f"{h20.loc['diversity', 'asp_mean']:.3f} < không MTD {h20.loc['none', 'asp_mean']:.3f}", "Khớp xu hướng"],
        ["Rủi ro mức VM / đường (E11)", "R_V4 12.47, R_V5 12.58, R_V7 8.67, R_V8 5.62; đường 43.15 / 43.31",
         "Khớp ±0.01 mức VM; −0.8% mức đường", "Tái lập được"],
        ["Tổng toàn mạng (E11)", "R_s 167.38, R_d 163.73, R_r 260.84", "173.6 / 142.3 / 217.6",
         "Không tái lập số tuyệt đối"],
        ["Kết luận định tính (E11)", "S+D tốt nhất; D < R", "6/7 với topology Hình 3; 3/7 với Definition 2",
         "Khớp với Hình 3"],
        ["Bộ kích hoạt MTD", "Không mô hình hóa detector", "AE V1 thật làm trigger event-based", "Mở rộng của DT043"],
    ], columns=["Khía cạnh", "Paper chính (Masud 2025)", "DT043", "Nhận xét"]), "Ánh xạ với paper chính", font=9,
        col_widths_cm=[3.0, 4.2, 5.8, 3.0])
    R.h2("8.2 Giới hạn và mối đe dọa với tính hợp lệ")
    R.bullets([
        "**Dữ liệu:** N-BaIoT thu trong lab năm 2018, 9 thiết bị, 2 botnet; không có timestamp nên độ trễ đo bằng số mẫu.",
        "**Không tái lập được TPR 100%** của Meidan; nguyên nhân chỉ được khoanh vùng (ngưỡng + đặc tính tcp/udp), chưa tách riêng "
        "từng khác biệt quy trình.",
        "**Edge giả lập:** không có Raspberry Pi; energy là proxy; không đo pipeline trích đặc trưng.",
        "**Track B:** mô hình HARM rút gọn với tham số giả định; chỉ tái lập xu hướng; chưa đối chiếu toàn văn paper chính "
        "cho một số chi tiết (đánh dấu trong phiếu tái lập).",
        "**Thống kê:** n = 9 thiết bị cho Wilcoxon là nhỏ; V2, E6, E9 chỉ 3 seed.",
        "**Hậu kiểm ngưỡng** (7.1) được đề xuất sau khi xem test nên chỉ mang tính giải thích.",
    ])
    R.h2("8.3 Kết luận")
    c = X.crit
    n_pass = int(c["pass"].sum())
    R.para(f"Đề tài đã xây dựng đầy đủ khung thực nghiệm tái lập được (mã nguồn, cấu hình, seed, manifest dữ liệu, log và "
           f"artifact của mọi lần chạy) và hệ thống demo 4 tầng AI/BE/DB/FE. Trên {len(c)} tiêu chí chốt trước, {n_pass} đạt. "
           "Kết quả chính: (1) AE per-device phát hiện gần như tuyệt đối 8/10 loại tấn công với FPR rất thấp, nhưng bỏ sót "
           "BASHLITE tcp/udp ở một số thiết bị do các flood giả mạo nguồn trông giống benign và quy tắc ngưỡng mean+std nhạy "
           "với đuôi phân phối; (2) model nhẹ V1 với ~22% tham số và lượng tử hóa int8 cho file < 20 KB, suy luận vài µs/mẫu "
           "trên một lõi E-core – khả thi cho edge; (3) hiệu chỉnh ngưỡng sau lượng tử hóa giảm FPR và độ trễ nhưng không "
           "tăng macro-F1; (4) kết quả dao động đáng kể theo seed, khẳng định yêu cầu nhiều lần chạy; (5) mô phỏng MTD tái lập "
           "được xu hướng \"kết hợp tốt hơn đơn lẻ\" của paper chính và cho thấy MTD lai dùng cảnh báo AE rút ngắn thời gian "
           "lộ diện, với thành phần time-based bù cho các tấn công detector bỏ sót.")
    R.para("Hướng phát triển: chọn ngưỡng/cửa sổ có kiểm định trên dữ liệu mới; đặc trưng hoặc quy tắc riêng cho flood giả "
           "mạo nguồn; chạy trên Raspberry Pi thật với đo điện; mở rộng mô hình MTD với chi phí gián đoạn dịch vụ.")
    R.h2("8.4 Tài liệu tham khảo")
    R.numbered([
        "M. T. Masud, M. Keshk, N. Moustafa, B. Turnbull, W. Susilo, \"Vulnerability defence using hybrid moving target "
        "defence in Internet of Things systems,\" Computers & Security, vol. 153, 104380, 2025. doi:10.1016/j.cose.2025.104380.",
        "Y. Meidan, M. Bohadana, Y. Mathov, Y. Mirsky, D. Breitenbacher, A. Shabtai, Y. Elovici, \"N-BaIoT – Network-based "
        "detection of IoT botnet attacks using deep autoencoders,\" IEEE Pervasive Computing, 17(3), 2018. arXiv:1805.03409.",
        "Y. Meidan et al., \"detection_of_IoT_botnet_attacks_N_BaIoT,\" UCI Machine Learning Repository, 2018. "
        "doi:10.24432/C5RC8J. CC BY 4.0.",
        "Y. Mirsky, T. Doitshman, Y. Elovici, A. Shabtai, \"Kitsune: An ensemble of autoencoders for online network intrusion "
        "detection,\" NDSS, 2018.",
        "TensorFlow Lite – Post-training quantization, tài liệu chính thức TensorFlow.",
    ])


def appendix(R: Report, root):
    R.h1("Phụ lục")
    R.h2("A. Hướng dẫn tái lập")
    R.code("""
py -3.11 -m venv .venv
.venv\\Scripts\\python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File run_all.ps1
.venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000
# mở http://127.0.0.1:8000/  (thêm ?replay=Danmini_Doorbell:mirai/syn để tự phát lại)
""")
    R.h2("B. Kiểm thử")
    R.para("ai/tests: 30 test (unit: schema, chia + purge, không trùng hash giữa các tập, scaler chỉ thấy DStrn, ngưỡng, "
           "majority vote không vượt ranh giới segment, metric; integration: end-to-end trên dữ liệu tổng hợp, Keras ↔ "
           "TFLite, cùng seed cùng kết quả, Isolation Forest; negative: file rỗng, thiếu/thừa/sai thứ tự cột, NaN/±inf, chuỗi, "
           "dòng bị cắt, cửa sổ sai, manifest bị sửa, sai số chiều, int8 thiếu representative data). backend/tests: 12 test "
           "(API, cảnh báo, MTD, kiểm tra đầu vào, path traversal, lô quá lớn, gói model bị sửa, repository).")
    R.h2("C. Cấu trúc kết quả")
    R.code("""
results/raw/<exp>/<thiết bị>/seed=<s>/   config.yaml, metrics.json, train_log.csv
results/raw/runs_index.csv              nhật ký mọi lần chạy (kể cả lỗi)
results/raw/E8_edge/bench.csv           edge benchmark
results/tables/*.csv, results/figures/*.png
artifacts/models/<exp>/<thiết bị>/      model.keras, scaler.json, *.tflite (seed 42)
artifacts/deploy/<thiết bị>/            model.tflite, scaler.json, meta.json (AI → BE)
""")
