"""Gom số liệu cho slide thuyết trình từ results/ → report/deck_data.json (để Word và PPT dùng chung một nguồn số)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
T = ROOT / "results" / "tables"


def r4(x):
    return None if pd.isna(x) else round(float(x), 4)


def main() -> None:
    fs = pd.read_csv(ROOT / "results" / "data_quality" / "file_stats.csv")
    ds = pd.read_csv(ROOT / "results" / "data_quality" / "device_summary.csv")
    ac = pd.read_csv(T / "eda_autocorrelation.csv")
    summ = pd.read_csv(T / "summary_by_config.csv").set_index("exp")
    groups = pd.read_csv(T / "recall_groups.csv", header=[0, 1], index_col=0)
    q = pd.read_csv(T / "quantization_summary.csv")
    bench = pd.read_csv(ROOT / "results" / "raw" / "E8_edge" / "bench.csv")
    post = pd.read_csv(T / "posthoc_threshold.csv")
    crit = pd.read_csv(T / "criteria_check.csv")
    harm = pd.read_csv(T / "mtd_harm_policies.csv")
    hyb = pd.read_csv(T / "mtd_hybrid_policy.csv")
    runs = pd.read_csv(T / "runs_long.csv")
    tests = pd.read_csv(T / "stat_tests.csv")

    cfgs = {}
    for exp in summ.index:
        s = summ.loc[exp]
        cfgs[exp] = {"label": s.config, "macro_f1": r4(s.macro_f1_mean), "macro_f1_ci": r4(s.macro_f1_ci95),
                     "tpr": r4(s.tpr_mean), "fpr": r4(s.fpr_mean), "f1_bal": r4(s.f1_balanced_mean),
                     "ws": r4(s.ws_mean), "seeds": int(s.n_seeds)}
    rec = {exp: {"tcp_udp": r4(groups.loc[exp, ("mean", "tcp_udp")]),
                 "others": r4(groups.loc[exp, ("mean", "8_loai_con_lai")])} for exp in groups.index}

    def qrow(exp, mode, calib):
        r = q[(q.exp == exp) & (q["mode"] == mode) & (q.calib == calib)].iloc[0]
        return {"kb": round(r.size_bytes_mean / 1024, 1), "macro_f1": r4(r.macro_f1_mean), "tpr": r4(r.tpr_mean),
                "fpr": r4(r.fpr_mean), "ws": round(float(r.ws_mean))}

    quant = {f"{m}_{mode}_{c}": qrow(e, mode, c) for e, m in (("E1_baseline", "B0"), ("E4_light", "V1"))
             for mode in ("fp32", "fp16", "dyn", "int8") for c in ("keep", "recal")}

    def brow(model, mode, prof):
        r = bench[(bench.model == model) & (bench["mode"] == mode) & (bench.profile == prof)].iloc[0]
        return {k: r4(r[k]) for k in ("p50_us", "p95_us", "p99_us", "invoke_p50_us", "throughput_samples_s",
                                      "rss_delta_mb", "energy_proxy_uJ", "size_kb", "macs")}

    edge = {f"{m}_{mode}_{p}": brow(m, mode, p) for m in ("B0", "V1", "V2") for mode in ("fp32", "int8")
            for p in ("P1_edge", "P0_b1", "P0_b256") if len(bench[(bench.model == m) & (bench["mode"] == mode)])}

    sd = runs[runs.exp.isin(["E1_baseline", "E4_light"])].groupby(["exp", "device"])["tpr"].agg(["min", "max"])
    h20 = harm[harm.period == 20].set_index("policy")
    hy = hyb.set_index(["policy", "period"])
    p2 = tests[(tests.test == "RQ2: per-device > global") & (tests.metric == "macro_f1")]

    data = {
        "data": {"rows_raw": int(fs.rows_raw.sum()), "rows_dedup": int(fs.rows_dedup.sum()),
                 "dups": int(fs.exact_duplicates.sum()), "ratio_min": round(float(ds.attack_to_benign_ratio.min()), 1),
                 "ratio_max": round(float(ds.attack_to_benign_ratio.max()), 1),
                 "ac_min": round(float(ac.lag1_autocorr_ordered.min()), 2),
                 "ac_max": round(float(ac.lag1_autocorr_ordered.max()), 2)},
        "configs": cfgs, "recall_groups": rec, "quant": quant, "edge": edge,
        "posthoc": post.round(4).to_dict(orient="records"),
        "unstable_pairs": int(((sd["max"] - sd["min"]) > 0.05).sum()),
        "rq2": {"wins": int(p2.wins.iloc[0]), "p": r4(p2.p.iloc[0])} if len(p2) else None,
        "harm20": {p: r4(h20.loc[p, "asp_mean"]) for p in h20.index},
        "hybrid": {"event_exposure": r4(hy.loc[("event", 0), "exposure_mean"]),
                   "event_moves": r4(hy.loc[("event", 0), "moves_per_10k"]),
                   "series": hyb.round(2).to_dict(orient="records")},
        "criteria": crit.to_dict(orient="records"),
        "n_runs": int(len(runs)),
    }
    (HERE / "deck_data.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print("Đã ghi report/deck_data.json")


if __name__ == "__main__":
    main()
