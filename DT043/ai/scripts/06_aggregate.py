"""Tổng hợp kết quả thô → bảng (CSV), kiểm định thống kê, đánh giá tiêu chí, hình.

Chạy:  python scripts/06_aggregate.py
Đầu ra: results/tables/*.csv, results/figures/*.png
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
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "results" / "raw"
TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"

LABEL = {"E1_baseline": "B0 (Meidan AE)", "E2_global": "B1 global", "E2_shared_pdnorm": "B1 chung+pdnorm",
         "E3_iforest": "B2 IsolationForest", "E4_light": "V1 AE nhẹ", "E6_leak": "E6 rò rỉ (đối chứng)",
         "E9_robust": "V1 (E9 robust)", "E9_poison_1": "V1 poison 1%", "E9_poison_5": "V1 poison 5%"}
for w in ("L5", "L3", "L1", "L01", "L001"):
    LABEL[f"E4_tiny_{w}"] = f"V2 cửa sổ {w}"
SHORT = {"Danmini_Doorbell": "Danmini", "Ecobee_Thermostat": "Ecobee", "Ennio_Doorbell": "Ennio",
         "Philips_B120N10_Baby_Monitor": "Philips", "Provision_PT_737E_Security_Camera": "PT737E",
         "Provision_PT_838_Security_Camera": "PT838", "Samsung_SNH_1011_N_Webcam": "Samsung",
         "SimpleHome_XCS7_1002_WHT_Security_Camera": "SH1002", "SimpleHome_XCS7_1003_WHT_Security_Camera": "SH1003"}
# Meidan 2018, Bảng 3 (tr*, ws*) – để ánh xạ
MEIDAN = {"Danmini_Doorbell": (0.042, 82), "Ennio_Doorbell": (0.011, 22), "Ecobee_Thermostat": (0.011, 20),
          "Philips_B120N10_Baby_Monitor": (0.030, 65), "Provision_PT_737E_Security_Camera": (0.035, 32),
          "Provision_PT_838_Security_Camera": (0.038, 43), "SimpleHome_XCS7_1002_WHT_Security_Camera": (0.056, 23),
          "SimpleHome_XCS7_1003_WHT_Security_Camera": (0.004, 25), "Samsung_SNH_1011_N_Webcam": (0.074, 32)}
KEYS = ["macro_f1", "tpr", "fpr", "f1_attack", "f1_balanced", "mcc", "balanced_acc", "accuracy"]


def load_runs() -> tuple[pd.DataFrame, list[dict]]:
    rows, raw = [], []
    for f in sorted(RAW.glob("*/*/seed=*/metrics.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        r = m["result"]
        row = {"exp": m["exp"], "device": m["device"], "seed": m["seed"], "thr": r["thr"], "ws": r["ws"],
               "roc_auc": r.get("roc_auc"), "pr_auc": r.get("pr_auc"),
               "delay_samples": r["window"].get("detect_delay_samples_mean"),
               "undetected_attacks": r["window"].get("undetected_attacks"),
               "params": m["model"].get("params"), "macs": m["model"].get("macs"),
               "train_time_s": m["train"].get("train_time_s"), "epochs": m["train"].get("epochs_run"),
               "n_train": m["data"]["n_train"]}
        row.update({k: r["window"][k] for k in KEYS})
        row.update({f"inst_{k}": r["instance"][k] for k in ("tpr", "fpr", "macro_f1")})
        rows.append(row)
        raw.append(m)
    return pd.DataFrame(rows), raw


def ci95(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return float("nan")
    return float(stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x)))


def summary_by_config(df: pd.DataFrame) -> pd.DataFrame:
    """Mỗi seed: trung bình 9 thiết bị → mean ± std ± CI95 qua các seed."""
    out = []
    for exp, g in df.groupby("exp"):
        per_seed = g.groupby("seed")[KEYS + ["roc_auc", "pr_auc"]].mean()
        row = {"config": LABEL.get(exp, exp), "exp": exp, "n_seeds": len(per_seed), "n_runs": len(g),
               "params": g["params"].iloc[0]}
        for k in ["macro_f1", "tpr", "fpr", "f1_balanced", "mcc", "roc_auc", "pr_auc", "accuracy"]:
            row[f"{k}_mean"] = per_seed[k].mean()
            row[f"{k}_std"] = per_seed[k].std(ddof=1)
            row[f"{k}_ci95"] = ci95(per_seed[k])
        row["ws_mean"] = g["ws"].mean()
        row["train_time_s_mean"] = g["train_time_s"].mean()
        out.append(row)
    return pd.DataFrame(out).sort_values("exp")


def device_means(df: pd.DataFrame, exp: str, key: str = "macro_f1") -> pd.Series:
    return df[df.exp == exp].groupby("device")[key].mean()


def wilcoxon(a: pd.Series, b: pd.Series, alternative: str) -> dict:
    j = a.index.intersection(b.index)
    d = (a[j] - b[j]).to_numpy()
    if len(j) < 2 or np.allclose(d, 0):
        return {"n": len(j), "mean_diff": float(d.mean()) if len(d) else np.nan, "p": 1.0, "wins": int((d > 0).sum())}
    res = stats.wilcoxon(a[j], b[j], alternative=alternative, zero_method="zsplit")
    return {"n": len(j), "mean_diff": float(d.mean()), "median_diff": float(np.median(d)), "p": float(res.pvalue),
            "wins": int((d > 1e-12).sum()), "ties": int((np.abs(d) <= 1e-12).sum())}


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    adj, running = np.empty(len(p)), 0.0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def quant_table(raw: list[dict]) -> pd.DataFrame:
    rows = []
    for m in raw:
        for mode, q in (m["result"].get("quantized") or {}).items():
            for cal in ("keep", "recal"):
                rows.append({"exp": m["exp"], "device": m["device"], "seed": m["seed"], "mode": mode, "calib": cal,
                             "size_bytes": q["size_bytes"], "ws": q[cal]["ws"],
                             **{k: q[cal][k] for k in ("macro_f1", "tpr", "fpr", "f1_balanced")},
                             "roc_auc": q.get("roc_auc")})
    return pd.DataFrame(rows)


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    df, raw = load_runs()
    df.to_csv(TAB / "runs_long.csv", index=False)
    print(f"{len(df)} lần chạy, {df.exp.nunique()} cấu hình")

    summ = summary_by_config(df)
    summ.to_csv(TAB / "summary_by_config.csv", index=False)
    short = summ[["config", "n_seeds", "n_runs", "params", "macro_f1_mean", "macro_f1_ci95", "tpr_mean", "fpr_mean",
                  "f1_balanced_mean", "mcc_mean", "roc_auc_mean", "ws_mean"]]
    print(short.round(4).to_string(index=False))

    # ---------------------------------------------------------------- theo thiết bị (B0 vs Meidan)
    if "E1_baseline" in set(df.exp):
        e1 = df[df.exp == "E1_baseline"].groupby("device").agg(
            tpr_mean=("tpr", "mean"), fpr_mean=("fpr", "mean"), fpr_std=("fpr", "std"),
            macro_f1_mean=("macro_f1", "mean"), macro_f1_std=("macro_f1", "std"), thr_mean=("thr", "mean"),
            ws_mean=("ws", "mean"), ws_min=("ws", "min"), ws_max=("ws", "max"), roc_auc=("roc_auc", "mean"),
            delay=("delay_samples", "mean"), n_train=("n_train", "first"), train_s=("train_time_s", "mean"))
        e1["meidan_thr"] = [MEIDAN[d][0] for d in e1.index]
        e1["meidan_ws"] = [MEIDAN[d][1] for d in e1.index]
        e1.to_csv(TAB / "per_device_B0_vs_meidan.csv")

    # ---------------------------------------------------------------- per-device macro-F1 nhiều cấu hình
    piv = df.pivot_table(index="device", columns="exp", values="macro_f1", aggfunc="mean")
    piv.to_csv(TAB / "per_device_macro_f1.csv")
    df.pivot_table(index="device", columns="exp", values="macro_f1", aggfunc="std").to_csv(
        TAB / "per_device_macro_f1_std_over_seeds.csv")

    # ---------------------------------------------------------------- recall theo loại tấn công
    pa = []
    for m in raw:
        for seg, v in m["result"]["window"].get("recall_per_attack", {}).items():
            pa.append({"exp": m["exp"], "device": m["device"], "seed": m["seed"], "attack": seg, "recall": v})
    pa = pd.DataFrame(pa)
    if len(pa):
        pa.pivot_table(index="attack", columns="exp", values="recall", aggfunc="mean").to_csv(
            TAB / "recall_per_attack.csv")
        pa[pa.exp == "E1_baseline"].pivot_table(index="device", columns="attack", values="recall",
                                                aggfunc="mean").to_csv(TAB / "recall_device_attack_B0.csv")
        grp = pa.assign(group=np.where(pa.attack.isin(["gafgyt/tcp", "gafgyt/udp"]), "tcp_udp", "8_loai_con_lai"))
        (grp.groupby(["exp", "group"])["recall"].agg(["mean", "std"]).unstack("group")
         .round(4).to_csv(TAB / "recall_groups.csv"))

    # ---------------------------------------------------------------- lượng tử hóa
    qt = quant_table(raw)
    if len(qt):
        qt.to_csv(TAB / "quant_long.csv", index=False)
        qs = (qt.groupby(["exp", "mode", "calib", "seed"])[["macro_f1", "tpr", "fpr", "f1_balanced", "size_bytes", "ws"]]
              .mean().groupby(["exp", "mode", "calib"]).agg(["mean", "std"]))
        qs.columns = [f"{a}_{b}" for a, b in qs.columns]
        qs.reset_index().to_csv(TAB / "quantization_summary.csv", index=False)

    # ---------------------------------------------------------------- ablation ngưỡng / cửa sổ
    ab = []
    for m in raw:
        for g in m["result"].get("ablation_grid", []) or []:
            ab.append({"exp": m["exp"], "device": m["device"], "seed": m["seed"], **g})
    ab = pd.DataFrame(ab)
    if len(ab):
        abs_ = (ab.groupby(["exp", "rule", "ws_kind", "seed"])[["tpr", "fpr", "macro_f1", "f1_balanced", "ws"]].mean()
                .groupby(["exp", "rule", "ws_kind"]).agg(["mean", "std"]))
        abs_.columns = [f"{a}_{b}" for a, b in abs_.columns]
        abs_.reset_index().to_csv(TAB / "ablation_threshold_window.csv", index=False)

    # ---------------------------------------------------------------- robustness
    ev, nz = [], []
    for m in raw:
        rb = m["result"].get("robustness") or {}
        ev += [{"device": m["device"], "seed": m["seed"], **e} for e in rb.get("evasion", [])]
        nz += [{"device": m["device"], "seed": m["seed"], **e} for e in rb.get("noise", [])]
    if ev:
        pd.DataFrame(ev).groupby("alpha")["tpr"].agg(["mean", "std", "min"]).to_csv(TAB / "robust_evasion.csv")
    if nz:
        pd.DataFrame(nz).groupby("sigma")["fpr"].agg(["mean", "std", "max"]).to_csv(TAB / "robust_noise.csv")

    # ---------------------------------------------------------------- kiểm định thống kê
    tests = []
    pairs = [("E1_baseline", "E2_global", "greater", "RQ2: per-device > global"),
             ("E1_baseline", "E2_shared_pdnorm", "greater", "RQ2b: model riêng > model chung (cùng pdnorm)"),
             ("E2_shared_pdnorm", "E2_global", "greater", "RQ2c: pdnorm > global norm (cùng model chung)"),
             ("E4_light", "E1_baseline", "two-sided", "RQ3: V1 vs B0"),
             ("E1_baseline", "E3_iforest", "greater", "B0 > IsolationForest"),
             ("E1_baseline", "E6_leak", "two-sided", "Rò rỉ: chia đúng vs chia sai")]
    for a, b, alt, name in pairs:
        if {a, b} <= set(df.exp):
            for key in ("macro_f1", "fpr"):
                tests.append({"test": name, "metric": key, "a": a, "b": b, "alternative": alt,
                              **wilcoxon(device_means(df, a, key), device_means(df, b, key), alt)})
    if len(qt):  # int8 hiệu chỉnh vs fp32 (cùng model), int8 hiệu chỉnh vs giữ ngưỡng
        for exp in ("E1_baseline", "E4_light"):
            q = qt[qt.exp == exp]
            if not len(q):
                continue
            f32 = q[(q["mode"] == "fp32") & (q.calib == "keep")].groupby("device")["macro_f1"].mean()
            i8r = q[(q["mode"] == "int8") & (q.calib == "recal")].groupby("device")["macro_f1"].mean()
            i8k = q[(q["mode"] == "int8") & (q.calib == "keep")].groupby("device")["macro_f1"].mean()
            tests.append({"test": f"RQ4: int8+recal vs fp32 ({exp})", "metric": "macro_f1", "a": "int8_recal",
                          "b": "fp32", "alternative": "two-sided", **wilcoxon(i8r, f32, "two-sided")})
            tests.append({"test": f"RQ4b: int8 recal > int8 giữ ngưỡng ({exp})", "metric": "macro_f1",
                          "a": "int8_recal", "b": "int8_keep", "alternative": "greater", **wilcoxon(i8r, i8k, "greater")})
    tdf = pd.DataFrame(tests)
    if len(tdf):
        tdf["p_holm"] = holm(tdf["p"].tolist())
        tdf.to_csv(TAB / "stat_tests.csv", index=False)
        print(tdf[["test", "metric", "n", "mean_diff", "wins", "p", "p_holm"]].round(4).to_string(index=False))

    # ---------------------------------------------------------------- tiêu chí đã chốt trước
    crit = []
    s = summ.set_index("exp")
    if "E1_baseline" in s.index:
        crit.append({"RQ": "RQ1", "criterion": "TPR ≥ 0.99 và FPR ≤ 0.02 (B0)",
                     "value": f"TPR={s.loc['E1_baseline', 'tpr_mean']:.4f}, FPR={s.loc['E1_baseline', 'fpr_mean']:.4f}",
                     "pass": bool(s.loc["E1_baseline", "tpr_mean"] >= 0.99 and s.loc["E1_baseline", "fpr_mean"] <= 0.02)})
    if len(tdf) and "RQ2: per-device > global" in set(tdf.test):
        r = tdf[(tdf.test == "RQ2: per-device > global") & (tdf.metric == "macro_f1")].iloc[0]
        crit.append({"RQ": "RQ2", "criterion": "B0 > B1 ở ≥7/9 thiết bị và p < 0.05",
                     "value": f"thắng {r['wins']}/9, p={r['p']:.4f}", "pass": bool(r["wins"] >= 7 and r["p"] < 0.05)})
    if {"E1_baseline", "E4_light"} <= set(s.index):
        d = s.loc["E1_baseline", "macro_f1_mean"] - s.loc["E4_light", "macro_f1_mean"]
        ratio = s.loc["E4_light", "params"] / s.loc["E1_baseline", "params"]
        crit.append({"RQ": "RQ3", "criterion": "V1 ≤ 25% tham số và Δmacro-F1 ≤ 0.01",
                     "value": f"tham số {ratio:.1%}, Δ={d:+.4f}", "pass": bool(ratio <= 0.25 and d <= 0.01)})
    if len(qt) and "E4_light" in set(qt.exp):
        q = qt[qt.exp == "E4_light"]
        f32 = q[(q["mode"] == "fp32") & (q.calib == "keep")]
        i8 = q[(q["mode"] == "int8") & (q.calib == "recal")]
        d = f32.macro_f1.mean() - i8.macro_f1.mean()
        size = i8.size_bytes.mean() / f32.size_bytes.mean()
        crit.append({"RQ": "RQ4", "criterion": "int8+recal: Δmacro-F1 ≤ 0.005 và kích thước ≤ 30% fp32 (V1)",
                     "value": f"Δ={d:+.4f}, kích thước {size:.1%}", "pass": bool(d <= 0.005 and size <= 0.30)})
    bench = RAW / "E8_edge" / "bench.csv"
    if bench.exists():
        b = pd.read_csv(bench)
        v = b[(b.model == "V1") & (b["mode"] == "int8") & (b.profile == "P1_edge")]
        if len(v):
            v = v.iloc[0]
            crit.append({"RQ": "RQ5", "criterion": "P1: p95 ≤ 1 ms, model ≤ 50 KB, RSS tăng ≤ 50 MB (V1 int8)",
                         "value": f"p95={v.p95_us:.1f} µs, {v.size_kb:.1f} KB, ΔRSS={v.rss_delta_mb:.1f} MB",
                         "pass": bool(v.p95_us <= 1000 and v.size_kb <= 50 and v.rss_delta_mb <= 50)})
    pd.DataFrame(crit).to_csv(TAB / "criteria_check.csv", index=False)
    print(pd.DataFrame(crit).to_string(index=False))

    figures(df, qt, ab, pa, ev)


def figures(df, qt, ab, pa, ev) -> None:
    plt.rcParams.update({"figure.dpi": 130, "font.size": 9})
    # 1) macro-F1 theo thiết bị cho các cấu hình chính
    exps = [e for e in ["E1_baseline", "E2_global", "E2_shared_pdnorm", "E3_iforest", "E4_light"] if e in set(df.exp)]
    if exps:
        g = df[df.exp.isin(exps)].groupby(["device", "exp"])["macro_f1"].agg(["mean", "std"]).reset_index()
        devs = sorted(df.device.unique())
        fig, ax = plt.subplots(figsize=(9, 3.6))
        w = 0.8 / len(exps)
        for i, e in enumerate(exps):
            s = g[g.exp == e].set_index("device").reindex(devs)
            ax.bar(np.arange(len(devs)) + i * w, s["mean"], w, yerr=s["std"], label=LABEL[e], capsize=2)
        ax.set_xticks(np.arange(len(devs)) + w * (len(exps) - 1) / 2, [SHORT.get(d, d) for d in devs], rotation=20)
        ax.set_ylabel("macro-F1 (mức cửa sổ)")
        ax.set_ylim(0, 1.05)
        ax.legend(ncol=3, fontsize=8, loc="lower right")
        ax.set_title("macro-F1 theo thiết bị (mean ± std qua 5 seed)")
        fig.tight_layout()
        fig.savefig(FIG / "fig_macro_f1_per_device.png")
        plt.close(fig)
    # 2) trade-off kích thước – chất lượng khi lượng tử hóa
    if len(qt):
        g = qt[qt.calib == "recal"].groupby(["exp", "mode"]).agg(size=("size_bytes", "mean"), f1=("macro_f1", "mean"),
                                                                 f1s=("macro_f1", "std")).reset_index()
        gk = qt[qt.calib == "keep"].groupby(["exp", "mode"]).agg(f1=("macro_f1", "mean")).reset_index()
        fig, ax = plt.subplots(figsize=(7, 4.4))
        for exp, mk in (("E1_baseline", "o"), ("E4_light", "s"), ("E4_tiny_L01", "^")):
            s = g[g.exp == exp]
            if len(s):
                ax.errorbar(s["size"] / 1024, s.f1, yerr=s.f1s, fmt=mk, label=f"{LABEL[exp]} (hiệu chỉnh ngưỡng)", capsize=2)
                for _, r in s.iterrows():
                    ax.annotate(r["mode"], (r["size"] / 1024, r.f1), fontsize=7, xytext=(4, 3), textcoords="offset points")
                k = gk[gk.exp == exp].merge(s[["mode", "size"]], on="mode")
                ax.scatter(k["size"] / 1024, k.f1, marker=mk, facecolors="none", edgecolors="gray", label=f"{LABEL[exp]} (giữ ngưỡng fp32)")
        ax.set_xscale("log")
        ax.set_xlabel("Kích thước file TFLite (KB, log)")
        ax.set_ylabel("macro-F1 trung bình")
        ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, frameon=False)
        ax.set_title("Lượng tử hóa: kích thước vs chất lượng")
        fig.tight_layout()
        fig.savefig(FIG / "fig_quantization_tradeoff.png")
        plt.close(fig)
    # 3) ablation ngưỡng
    if len(ab):
        a = ab[ab.exp == "E1_baseline"].groupby(["rule", "ws_kind"])[["macro_f1", "fpr", "tpr"]].mean().reset_index()
        fig, axes = plt.subplots(1, 2, figsize=(8, 3))
        for k, ax in zip(("macro_f1", "fpr"), axes):
            p = a.pivot(index="rule", columns="ws_kind", values=k)[["1", "ws*", "2ws*"]]
            p.plot.bar(ax=ax, rot=0)
            ax.set_title(f"B0: {k} theo quy tắc ngưỡng × cửa sổ")
            ax.legend(title="cửa sổ", fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG / "fig_ablation_threshold.png")
        plt.close(fig)
    # 4) recall theo loại tấn công
    if len(pa):
        p = pa[pa.exp.isin(["E1_baseline", "E4_light", "E3_iforest"])].pivot_table(
            index="attack", columns="exp", values="recall", aggfunc="mean")
        fig, ax = plt.subplots(figsize=(8, 3.2))
        p.rename(columns=LABEL).plot.bar(ax=ax, rot=30)
        ax.set_ylabel("Recall mức cửa sổ")
        ax.set_title("Recall theo loại tấn công (trung bình thiết bị × seed)")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(FIG / "fig_recall_per_attack.png")
        plt.close(fig)
    # 5) độ ổn định qua seed
    if "E1_baseline" in set(df.exp):
        fig, ax = plt.subplots(figsize=(8, 3))
        e = df[df.exp.isin(["E1_baseline", "E4_light"])]
        devs = sorted(e.device.unique())
        for i, exp in enumerate(["E1_baseline", "E4_light"]):
            data = [e[(e.exp == exp) & (e.device == d)]["macro_f1"].to_numpy() for d in devs]
            ax.boxplot(data, positions=np.arange(len(devs)) * 2.5 + i, widths=0.8, patch_artist=True,
                       boxprops={"facecolor": ["#9ec5fe", "#ffd59e"][i]})
        ax.set_xticks(np.arange(len(devs)) * 2.5 + 0.5, [SHORT[d] for d in devs], rotation=20)
        ax.set_ylabel("macro-F1")
        ax.set_title("Độ ổn định qua 5 seed (xanh: B0, cam: V1)")
        fig.tight_layout()
        fig.savefig(FIG / "fig_seed_stability.png")
        plt.close(fig)
    # 6) né tránh
    if ev:
        e = pd.DataFrame(ev).groupby("alpha")["tpr"].agg(["mean", "std"])
        fig, ax = plt.subplots(figsize=(4.5, 3))
        ax.errorbar(e.index, e["mean"], yerr=e["std"], marker="o", capsize=2)
        ax.set_xlabel("α (mức kéo mẫu tấn công về tâm benign)")
        ax.set_ylabel("TPR")
        ax.set_title("Né tránh kiểu mimicry (V1)")
        fig.tight_layout()
        fig.savefig(FIG / "fig_evasion.png")
        plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
