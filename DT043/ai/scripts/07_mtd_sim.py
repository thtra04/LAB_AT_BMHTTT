"""E10 – Track B: (1) tái lập có chọn lọc so sánh MTD shuffle / diversity / kết hợp trên mô hình HARM rút gọn;
(2) biến thể MTD lai kích hoạt bởi cảnh báo AE (V1, seed 42) trên luồng dữ liệu test thật.

Chạy:  python scripts/07_mtd_sim.py
Đầu ra: results/tables/mtd_harm_static.csv, mtd_harm_policies.csv, mtd_hybrid_policy.csv, results/figures/fig_mtd_*.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.config import load_config  # noqa: E402
from nbaiot.mtd.harm import iot_network, simulate, static_metrics  # noqa: E402
from nbaiot.mtd.policy_sim import episode_alarm_positions, evaluate_policy  # noqa: E402

TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"
SEEDS = [42, 1337, 2024, 7, 123]


def part1(devices: list[str]) -> None:
    net = iot_network(devices)
    pd.DataFrame([static_metrics(net)]).to_csv(TAB / "mtd_harm_static.csv", index=False)
    rows = []
    for period in (5, 10, 20):
        for pol in ("none", "shuffle", "diversity", "combined"):
            for s in SEEDS:
                rows.append({"period": period, "seed": s, **simulate(net, pol, period=period, seed=s)})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "mtd_harm_policies_runs.csv", index=False)
    summ = df.groupby(["period", "policy"])[["asp", "attack_cost_mean", "time_to_compromise_mean", "mtd_moves_per_run"]] \
        .agg(["mean", "std"])
    summ.columns = [f"{a}_{b}" for a, b in summ.columns]
    summ = summ.reset_index()
    summ.to_csv(TAB / "mtd_harm_policies.csv", index=False)
    print(summ[["period", "policy", "asp_mean", "asp_std", "attack_cost_mean_mean", "mtd_moves_per_run_mean"]]
          .round(3).to_string(index=False))
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    for pol in ("none", "shuffle", "diversity", "combined"):
        s = summ[summ.policy == pol]
        ax.errorbar(s.period, s.asp_mean, yerr=s.asp_std, marker="o", capsize=2, label=pol)
    ax.set_xlabel("Chu kỳ MTD (bước thời gian)")
    ax.set_ylabel("ASP (ngân sách 20 bước)")
    ax.set_title("HARM rút gọn: hiệu quả các kỹ thuật MTD")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig_mtd_harm.png", dpi=130)
    plt.close(fig)


def part2(devices: list[str], exp: str = "E4_light", seed: int = 42) -> None:
    rows = []
    rng = np.random.default_rng(0)
    for dev in devices:
        f = ROOT / "results" / "scores" / exp / dev / f"seed{seed}.npz"
        mfile = ROOT / "results" / "raw" / exp / dev / f"seed={seed}" / "metrics.json"
        if not f.exists() or not mfile.exists():
            print("bỏ qua (chưa có điểm):", dev)
            continue
        r = json.loads(mfile.read_text(encoding="utf-8"))["result"]
        z = np.load(f)
        scores = {k.replace("__", "/"): z[k] for k in z.files if k != "opt"}
        lengths = {k: len(v) for k, v in scores.items()}
        alarms = episode_alarm_positions(scores, r["thr"], r["ws"])
        for period in (100, 500, 2000, 10000):
            for pol in ("time", "hybrid"):
                rows.append({"device": dev, **evaluate_policy(alarms, lengths, pol, period, cooldown=period, rng=rng)})
        rows.append({"device": dev, **evaluate_policy(alarms, lengths, "event", 0, cooldown=500, rng=rng, n_phase=1)})
    if not rows:
        return
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "mtd_hybrid_policy_by_device.csv", index=False)
    summ = df.groupby(["policy", "period"])[["exposure_mean", "exposure_p95", "moves_per_10k",
                                              "wasted_moves_per_10k_benign"]].mean().reset_index()
    summ.to_csv(TAB / "mtd_hybrid_policy.csv", index=False)
    print(summ.round(2).to_string(index=False))
    fig, ax = plt.subplots(figsize=(5.5, 3.4))
    for pol, mk in (("time", "o"), ("hybrid", "s"), ("event", "^")):
        s = summ[summ.policy == pol]
        ax.plot(s.moves_per_10k, s.exposure_mean, marker=mk, label=pol)
        for _, rr in s.iterrows():
            if pol != "event":
                ax.annotate(f"T={int(rr.period)}", (rr.moves_per_10k, rr.exposure_mean), fontsize=7,
                            xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Số lần move / 10.000 mẫu (chi phí)")
    ax.set_ylabel("Thời gian lộ diện TB (mẫu)")
    ax.set_title("MTD lai kích hoạt bởi AE (V1): an ninh vs chi phí")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig_mtd_hybrid_tradeoff.png", dpi=130)
    plt.close(fig)


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    devices = load_config()["devices"]
    part1(devices)
    part2(devices)


if __name__ == "__main__":
    main()
