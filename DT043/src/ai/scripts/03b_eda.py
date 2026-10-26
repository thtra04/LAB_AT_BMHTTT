"""EDA – khám phá dữ liệu TRƯỚC khi huấn luyện (chỉ dùng benign + mẫu nhỏ attack).

Chạy:  python scripts/03b_eda.py
Đầu ra: results/figures/eda_*.png, results/tables/eda_*.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))
from nbaiot.config import load_config  # noqa: E402
from nbaiot.data import load_device  # noqa: E402

FIG, TAB = ROOT / "results" / "figures", ROOT / "results" / "tables"
SHORT = lambda d: d.split("_")[0] + ("_" + d.split("_")[1] if d.startswith(("Provision", "SimpleHome")) else "")  # noqa: E731


def main() -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"figure.dpi": 130, "font.size": 8})
    cfg = load_config()
    proc = ROOT / cfg["paths"]["processed"]
    stats = pd.read_csv(ROOT / "results" / "data_quality" / "file_stats.csv")

    # 1) số mẫu theo thiết bị/botnet (thang log) → mất cân bằng
    c = stats.assign(group=stats.segment.str.split("/").str[0]).pivot_table(
        index="device", columns="group", values="rows_dedup", aggfunc="sum").fillna(0)
    c.index = [SHORT(d) for d in c.index]
    ax = c[["benign", "gafgyt", "mirai"]].plot.bar(figsize=(7, 3), logy=True, rot=20)
    ax.set_ylabel("số dòng (log)")
    ax.set_title("Số mẫu sau khử trùng lặp theo thiết bị")
    plt.tight_layout()
    plt.savefig(FIG / "eda_class_counts.png")
    plt.close()

    # 2) tự tương quan bậc 1 của đặc trưng benign: thứ tự gốc vs xáo trộn → lý do chia theo thời gian
    rows, feat_box = [], {}
    rng = np.random.default_rng(0)
    for dev in cfg["devices"]:
        b = load_device(proc, dev, columns=None)["benign"]
        x = b.to_numpy(np.float64)
        x = (x - x.mean(0)) / np.where(x.std(0) == 0, 1, x.std(0))
        lag1 = np.nanmean([np.corrcoef(x[:-1, j], x[1:, j])[0, 1] for j in range(x.shape[1]) if x[:, j].std() > 0])
        xs = x[rng.permutation(len(x))]
        lag1s = np.nanmean([np.corrcoef(xs[:-1, j], xs[1:, j])[0, 1] for j in range(x.shape[1]) if xs[:, j].std() > 0])
        rows.append({"device": dev, "n_benign": len(b), "lag1_autocorr_ordered": lag1, "lag1_autocorr_shuffled": lag1s})
        feat_box[SHORT(dev)] = b["HH_L0.1_mean"].to_numpy()
    ac = pd.DataFrame(rows)
    ac.to_csv(TAB / "eda_autocorrelation.csv", index=False)
    print(ac.round(3).to_string(index=False))

    # 3) phân phối 1 đặc trưng giữa các thiết bị → lý do chuẩn hóa theo từng thiết bị
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.boxplot(list(feat_box.values()), showfliers=False)
    ax.set_xticks(range(1, len(feat_box) + 1), list(feat_box.keys()), rotation=20)
    ax.set_ylabel("HH_L0.1_mean (byte)")
    ax.set_title("Cùng một đặc trưng khác hẳn giữa các thiết bị (benign)")
    plt.tight_layout()
    plt.savefig(FIG / "eda_feature_by_device.png")
    plt.close()

    # 4) gafgyt/tcp vs benign trên vài đặc trưng (giải thích lỗi FN)
    segs = load_device(proc, "Ennio_Doorbell")
    cols = ["H_L5_weight", "H_L5_mean", "H_L5_variance", "HH_L0.1_weight", "HpHp_L0.1_mean"]
    comp = pd.DataFrame({k: segs[k][cols].median() for k in ("benign", "gafgyt/tcp", "gafgyt/udp", "gafgyt/scan")})
    comp.to_csv(TAB / "eda_ennio_tcp_vs_benign_median.csv")
    print(comp.round(2))

    # 5) PCA 2D (fit trên benign) – Danmini
    segs = load_device(proc, "Danmini_Doorbell")
    sc = StandardScaler().fit(segs["benign"])
    pca = PCA(2, random_state=0).fit(sc.transform(segs["benign"]))
    fig, ax = plt.subplots(figsize=(5, 4))
    for name in ("benign", "gafgyt/tcp", "gafgyt/scan", "mirai/syn", "mirai/udp"):
        s = segs[name].sample(min(2000, len(segs[name])), random_state=0)
        z = pca.transform(np.clip(sc.transform(s), -50, 50))
        ax.scatter(z[:, 0], z[:, 1], s=3, alpha=0.5, label=name)
    ax.set_title("PCA (fit trên benign) – Danmini_Doorbell")
    ax.legend(markerscale=4, fontsize=7)
    plt.tight_layout()
    plt.savefig(FIG / "eda_pca_danmini.png")
    plt.close()


if __name__ == "__main__":
    main()
