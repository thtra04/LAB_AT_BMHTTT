"""PHÂN TÍCH KHÁM PHÁ HẬU KIỂM (post-hoc) – KHÔNG nằm trong tiêu chí đã chốt trước.

Câu hỏi: lỗi bỏ sót gafgyt/tcp, gafgyt/udp có phải do quy tắc ngưỡng mean+std không? Nếu chọn ngưỡng thấp hơn
(percentile q của MSE trên DSopt) rồi để majority vote khử cảnh báo giả (ws* = cửa sổ nhỏ nhất cho FPR = 0 trên
DSopt, giới hạn 5000), thì TPR/FPR/độ trễ thay đổi thế nào?
Ngưỡng và cửa sổ vẫn CHỈ được chọn trên DSopt; nhưng việc đặt câu hỏi này xuất phát từ việc đã xem kết quả test,
nên kết quả chỉ dùng để giải thích, không dùng để tuyên bố cải tiến.

Chạy:  python scripts/09_posthoc_threshold.py   (dùng điểm MSE đã lưu của seed 42)
Đầu ra: results/tables/posthoc_threshold.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.metrics import evaluate_segments  # noqa: E402
from nbaiot.threshold import find_ws  # noqa: E402

RULES = [("mean+std (gốc)", None), ("p50", 50), ("p75", 75), ("p90", 90), ("p95", 95), ("p99", 99)]


def main() -> None:
    rows = []
    for exp in ("E1_baseline", "E4_light"):
        for f in sorted((ROOT / "results" / "scores" / exp).glob("*/seed42.npz")):
            z = np.load(f)
            opt = z["opt"].astype(np.float64)
            test = {k.replace("__", "/"): z[k] for k in z.files if k != "opt"}
            for name, q in RULES:
                thr = opt.mean() + opt.std(ddof=1) if q is None else float(np.percentile(opt, q))
                ws, opt_fpr = find_ws(opt > thr, max_ws=5000)
                r = evaluate_segments(test, thr, ws)
                pa = r["recall_per_attack"]
                rows.append({"exp": exp, "device": f.parent.name, "rule": name, "thr": thr, "ws": ws,
                             "opt_fpr": opt_fpr, "tpr": r["tpr"], "fpr": r["fpr"], "macro_f1": r["macro_f1"],
                             "f1_balanced": r["f1_balanced"],
                             "recall_tcp_udp": np.mean([pa[k] for k in ("gafgyt/tcp", "gafgyt/udp")]),
                             "delay_samples": r["detect_delay_samples_mean"]})
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "tables"
    df.to_csv(out / "posthoc_threshold_by_device.csv", index=False)
    s = df.groupby(["exp", "rule"], sort=False)[["tpr", "fpr", "macro_f1", "f1_balanced", "recall_tcp_udp", "ws",
                                                 "delay_samples"]].mean().reset_index()
    s.to_csv(out / "posthoc_threshold.csv", index=False)
    print(s.round(4).to_string(index=False))
    error_figure()


def error_figure(device: str = "Ennio_Doorbell") -> None:
    """Histogram MSE (thang log) của benign và một số tấn công + các ngưỡng – minh họa lỗi bỏ sót tcp/udp."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    z = np.load(ROOT / "results" / "scores" / "E1_baseline" / device / "seed42.npz")
    opt = z["opt"].astype(np.float64)
    bins = np.logspace(-4, 7, 120)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for k, lab in (("opt", "benign DSopt"), ("benign", "benign test"), ("gafgyt__tcp", "gafgyt/tcp"),
                   ("gafgyt__udp", "gafgyt/udp"), ("gafgyt__scan", "gafgyt/scan"), ("gafgyt__combo", "gafgyt/combo")):
        v = np.clip(z[k], 1e-4, 1e7)
        ax.hist(v, bins=bins, histtype="step", weights=np.full(len(v), 1 / len(v)), label=lab, linewidth=1.2)
    for name, v, ls in (("mean+std", opt.mean() + opt.std(ddof=1), "-"), ("p99", np.percentile(opt, 99), "--"),
                        ("p75", np.percentile(opt, 75), ":")):
        ax.axvline(v, color="k", linestyle=ls, linewidth=1)
        ax.text(v, ax.get_ylim()[1] * 0.9, f" {name}", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("MSE tái tạo (log)")
    ax.set_ylabel("tỷ lệ mẫu trong bin")
    ax.set_title(f"B0 – {device} (seed 42): tcp/udp nằm dưới ngưỡng mean+std")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "figures" / "fig_error_mse_hist.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
