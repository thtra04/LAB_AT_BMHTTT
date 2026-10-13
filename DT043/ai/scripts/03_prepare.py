"""Kiểm tra chất lượng dữ liệu, khử trùng lặp trong từng file và lưu Parquet float32 theo thiết bị.

Chạy:  python scripts/03_prepare.py
Đầu ra: data/processed/<device>/<segment>.parquet
        results/data_quality/file_stats.csv, device_summary.csv, constant_columns.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.config import load_config  # noqa: E402
from nbaiot.data import processed_path, raw_segments, read_csv, row_hashes  # noqa: E402

OUT = ROOT / "results" / "data_quality"


def main() -> None:
    cfg = load_config()
    raw_dir = ROOT / cfg["paths"]["raw"]
    proc_dir = ROOT / cfg["paths"]["processed"]
    OUT.mkdir(parents=True, exist_ok=True)

    rows, const_rows = [], []
    for device in cfg["devices"]:
        for seg, path in raw_segments(raw_dir, device).items():
            df = read_csv(path)
            n_raw = len(df)
            dup_mask = df.duplicated(keep="first")
            df = df.loc[~dup_mask].reset_index(drop=True)
            std = df.std(ddof=0)
            const_cols = list(std.index[std == 0])
            out = processed_path(proc_dir, device, seg)
            out.parent.mkdir(parents=True, exist_ok=True)
            df32 = df.astype(np.float32)
            df32.to_parquet(out, index=False)
            n_dup32 = int(pd.Series(row_hashes(df32)).duplicated().sum())
            rows.append({
                "device": device, "segment": seg,
                "label": "benign" if seg == "benign" else "attack",
                "botnet": seg.split("/")[0] if seg != "benign" else "",
                "rows_raw": n_raw, "exact_duplicates": int(dup_mask.sum()),
                "dup_ratio": round(float(dup_mask.mean()), 6),
                "rows_dedup": len(df), "extra_dups_after_float32": n_dup32,
                "nan": 0, "inf": 0, "constant_cols": len(const_cols),
                "max_abs_value": float(np.abs(df.to_numpy()).max()),
            })
            const_rows += [{"device": device, "segment": seg, "column": c} for c in const_cols]
            print(f"{device:45s} {seg:16s} raw={n_raw:>8d} dup={int(dup_mask.sum()):>7d}", flush=True)

    stats = pd.DataFrame(rows)
    stats.to_csv(OUT / "file_stats.csv", index=False)
    pd.DataFrame(const_rows).to_csv(OUT / "constant_columns.csv", index=False)
    summ = stats.pivot_table(index="device", columns="label", values=["rows_raw", "rows_dedup"],
                             aggfunc="sum")
    summ.columns = [f"{a}_{b}" for a, b in summ.columns]
    summ["attack_to_benign_ratio"] = (summ["rows_dedup_attack"] / summ["rows_dedup_benign"]).round(2)
    summ.to_csv(OUT / "device_summary.csv")
    print(summ)
    print("Tổng dòng gốc:", int(stats.rows_raw.sum()), "– sau khử trùng:", int(stats.rows_dedup.sum()))


if __name__ == "__main__":
    main()
