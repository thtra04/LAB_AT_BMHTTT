"""Vẽ lại các biểu đồ của hai bài báo theo ĐÚNG dạng biểu đồ gốc, bằng kết quả chạy lại của đề tài.

- Masud et al. (2025) Hình 6: AR, AC, RoC của toàn mạng khi áp S, D, R, S+D, S+D+R lên từng VM (V5, V4, V7, V2, V1, V3, V6).
- Masud et al. (2025) Hình 7: ASP từng đường tấn công trước / sau diversity (V5).
- Meidan et al. (2018) Hình 2 (a, b): TPR/FPR theo thuật toán (boxplot 9 thiết bị) và độ trễ phát hiện theo thiết bị.

Giả định phải tự đặt vì bài báo không nêu (ghi lại trong bảng đầu ra):
- Shuffle VM bất kỳ: di trú sang host đích (V2 → host 3 như Hình 4a, các VM khác → host 4 như ví dụ V5 ở mục 4.2);
  quy tắc cạnh tổng quát hóa từ ví dụ V5 (xem tharm.shuffle). Topology: Hình 3 (thêm V6 → V4).
- Meidan Hình 2b đo giây trên lưu lượng thật; N-BaIoT không có timestamp nên dùng độ trễ theo số mẫu.

Chạy:  python ai/scripts/11_paper_figures.py
Đầu ra: results/tables/paper_fig6_masud.csv, paper_fig6_masud_vs_paper.csv, paper_fig7_masud.csv, paper_fig2_meidan.csv
        results/figures/fig_paper_masud_fig6.png, fig_paper_masud_fig7.png, fig_paper_meidan_fig2.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.mtd import tharm as T  # noqa: E402

TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"
FIG6_ORDER = ["V5", "V4", "V7", "V2", "V1", "V3", "V6"]          # trục x của Hình 6 trong bài báo
SHUFFLE_DST = {"V2": "H3"}                                        # Hình 4a; còn lại → H4 (ví dụ V5, mục 4.2)
# AR đọc bằng mắt từ Hình 6(a) của bài báo (sai số đọc ≈ ±5) – bài báo không in bảng số cho hình này
PAPER_FIG6_AR = {"s": [167, 171, 184, 188, 203, 203, 209], "d": [203, 222, 232, 203, 221, 205, 210],
                 "r": [261, 263, 258, 252, 266, 263, 265], "s+d": [165, 179, 193, 182, 205, 194, 205],
                 "s+d+r": [173, 196, 211, 195, 222, 206, 218]}
# kiểu đường / ký hiệu giống Hình 6 của bài báo
STYLE = {"s": ("o", "#3b6fc4"), "d": ("x", "#e08a3c"), "r": ("^", "#3a9d5d"), "s+d": ("*", "#d64545"),
         "s+d+r": ("v", "#7b1f8a")}


def mtd_states(base: T.Tharm, vm: str) -> dict[str, T.Tharm]:
    s = T.shuffle(base, vm, SHUFFLE_DST.get(vm, "H4"))
    sd = T.diversity(s, vm)
    return {"s": s, "d": T.diversity(base, vm), "r": T.redundancy(base, vm), "s+d": sd, "s+d+r": T.redundancy(sd, vm)}


def masud_fig6() -> pd.DataFrame:
    rows = []
    for fig3 in (True, False):
        base = T.build(with_fig3_edge=fig3)
        for vm in FIG6_ORDER:
            for name, st in mtd_states(base, vm).items():
                m = st.network_metrics()
                rows.append({"topology": "Hình 3 (+V6→V4)" if fig3 else "Definition 2", "VM": vm, "MTD": name,
                             "shuffle tới": SHUFFLE_DST.get(vm, "H4"), "n_paths": m["n_paths"], "AR": m["R"],
                             "AC": m["AC"], "RoC": m["RoC"]})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "paper_fig6_masud.csv", index=False)

    d = df[df.topology == "Hình 3 (+V6→V4)"]
    cmp = d[["VM", "MTD", "AR"]].rename(columns={"AR": "AR_tái_lập"})
    cmp["AR_bài_báo(đọc từ hình)"] = [PAPER_FIG6_AR[m][FIG6_ORDER.index(v)] for v, m in zip(cmp.VM, cmp.MTD)]
    cmp["lệch %"] = 100 * (cmp["AR_tái_lập"] - cmp["AR_bài_báo(đọc từ hình)"]) / cmp["AR_bài_báo(đọc từ hình)"]
    cmp.to_csv(TAB / "paper_fig6_masud_vs_paper.csv", index=False)
    print("== Hình 6: số VM lệch ≤ 5% so với bài báo, theo MTD\n",
          cmp.assign(ok=cmp["lệch %"].abs() <= 5).groupby("MTD").ok.sum().to_string())
    fig = plt.figure(figsize=(13, 8.2))
    pos = {"AR": [0.05, 0.55, 0.42, 0.40], "AC": [0.55, 0.55, 0.42, 0.40], "RoC": [0.30, 0.06, 0.42, 0.40]}
    for k, lab in (("AR", "a)"), ("AC", "b)"), ("RoC", "c)")):
        ax = fig.add_axes(pos[k])
        for name, (mk, col) in STYLE.items():
            y = d[d.MTD == name].set_index("VM").loc[FIG6_ORDER, k]
            ax.plot(FIG6_ORDER, y, linestyle="--", marker=mk, color=col, markersize=8 if mk != "*" else 11,
                    label=f"{k}{name.replace('s+d+r', 's+d+r')}", linewidth=1)
        ax.set_xlabel("VM", fontweight="bold")
        ax.set_ylabel(k, fontweight="bold")
        ax.set_ylim(bottom=0)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=8, loc="lower left")
        ax.text(0.02, 0.92, lab, transform=ax.transAxes, fontsize=13)
    fig.suptitle("Chạy lại Hình 6 (Masud et al. 2025): AR, AC, RoC của mạng khi áp MTD lên từng VM", fontsize=12)
    fig.savefig(FIG / "fig_paper_masud_fig6.png", dpi=150)
    plt.close(fig)
    return df


def masud_fig7() -> pd.DataFrame:
    base = T.build(with_fig3_edge=True)
    after = T.diversity(base, "V5")
    rows = []
    for i, p in enumerate(base.paths(), 1):
        rows.append({"đường": f"Path {i}", "chuỗi": "-".join(p), "ASP trước diversity": base.path_metrics(p)["ASP"],
                     "ASP sau diversity": after.path_metrics(p)["ASP"]})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "paper_fig7_masud.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(df))
    ax.bar(x - 0.18, df["ASP trước diversity"], 0.36, color="#1f5f7a", label="Before Diversity")
    ax.bar(x + 0.18, df["ASP sau diversity"], 0.36, color="#ed7d31", label="After Diversity")
    ax.set_xticks(x, df["đường"])
    ax.set_title("Attack Successful Probability (ASP)", fontweight="bold")
    ax.grid(True, axis="y", alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False)
    for i, r in df.iterrows():
        ax.text(i, -0.1, r["chuỗi"].replace("A-", "A→").replace("-", "→"), ha="center", fontsize=7,
                transform=ax.get_xaxis_transform(), color="#555")
    fig.suptitle("Chạy lại Hình 7 (Masud et al. 2025): ASP từng đường trước / sau diversity V5", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "fig_paper_masud_fig7.png", dpi=150)
    plt.close(fig)
    return df


def meidan_fig2() -> pd.DataFrame:
    runs = pd.read_csv(TAB / "runs_long.csv")
    algos = {"E1_baseline": "Autoencoder", "E3_iforest": "IsolationForest", "E4_light": "AE nhẹ (V1)"}
    runs = runs[runs.exp.isin(algos)]
    dev = runs.groupby(["exp", "device"], as_index=False)[["tpr", "fpr", "delay_samples"]].mean()
    dev["thuật toán"] = dev.exp.map(algos)
    devices = sorted(dev.device.unique())
    dev["Device ID"] = dev.device.map({d: i + 1 for i, d in enumerate(devices)})
    dev.to_csv(TAB / "paper_fig2_meidan.csv", index=False)

    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.8))
    names = list(algos.values())
    for i, n in enumerate(names):
        g = dev[dev["thuật toán"] == n]
        for off, col, k in ((-0.18, "#a6d8a0", "fpr"), (0.18, "#cdbde3", "tpr")):
            a.boxplot(g[k], positions=[i + off], widths=0.32, patch_artist=True,
                      boxprops={"facecolor": col}, medianprops={"color": "black"})
    a.set_xticks(range(len(names)), names)
    a.set_xlabel("Algorithm", fontweight="bold")
    a.set_ylim(-0.03, 1.05)
    a.legend([plt.Rectangle((0, 0), 1, 1, fc="#a6d8a0"), plt.Rectangle((0, 0), 1, 1, fc="#cdbde3")], ["FPR", "TPR"],
             loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2, frameon=False)
    a.grid(True, alpha=0.3)
    a.set_title("(a) Độ chính xác phát hiện (9 thiết bị)", y=-0.22)
    colors = {"Autoencoder": "#f8766d", "IsolationForest": "#7cae00", "AE nhẹ (V1)": "#00bfc4"}
    for n in names:
        g = dev[dev["thuật toán"] == n].sort_values("Device ID")
        b.plot(g["Device ID"], g["delay_samples"], marker="o", linewidth=3, markersize=8, color=colors[n], label=n)
    b.set_xticks(range(1, len(devices) + 1))
    b.set_xlabel("Device ID", fontweight="bold")
    b.set_ylabel("Độ trễ phát hiện TB (số mẫu)", fontweight="bold")
    b.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=3, frameon=False)
    b.grid(True, alpha=0.3)
    b.set_title("(b) Độ trễ phát hiện theo thiết bị (đo bằng số mẫu)", y=-0.22)
    fig.tight_layout()
    fig.savefig(FIG / "fig_paper_meidan_fig2.png", dpi=150)
    plt.close(fig)
    return dev


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    f6, f7, f2 = masud_fig6(), masud_fig7(), meidan_fig2()
    print("== Hình 6 (Hình 3 topology)\n", f6[f6.topology.str.startswith("Hình")].pivot_table(
        index="VM", columns="MTD", values="AR").loc[FIG6_ORDER].round(2).to_string())
    print("== Hình 7\n", f7.round(4).to_string(index=False))
    print("== Hình 2 Meidan\n", f2.groupby("thuật toán")[["tpr", "fpr", "delay_samples"]].median().round(4).to_string())


if __name__ == "__main__":
    main()
