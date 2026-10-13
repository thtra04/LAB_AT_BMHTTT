"""AI → BE: xuất gói triển khai cho từng thiết bị (model TFLite + scaler + ngưỡng đã hiệu chỉnh).

Mặc định: V1 (E4_light) full-int8, ngưỡng/cửa sổ hiệu chỉnh lại trên DSopt bằng chính model int8, seed 42.
Chạy:  python scripts/08_export_deploy.py [--exp E4_light --mode int8]
Đầu ra: artifacts/deploy/<device>/{model.tflite, scaler.json, meta.json}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.config import load_config  # noqa: E402
from nbaiot.data import window_columns  # noqa: E402

VARIANT = {"E1_baseline": "B0", "E4_light": "V1", "E4_tiny_L01": "V2"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="E4_light")
    ap.add_argument("--mode", default="int8")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    cfg = load_config(args.exp)
    out_root = ROOT / "artifacts" / "deploy"
    for dev in cfg["devices"]:
        src = ROOT / "artifacts" / "models" / args.exp / dev
        m = json.loads((ROOT / "results" / "raw" / args.exp / dev / f"seed={args.seed}" / "metrics.json")
                       .read_text(encoding="utf-8"))
        q = m["result"]["quantized"][args.mode]["recal"]
        out = out_root / dev
        out.mkdir(parents=True, exist_ok=True)
        blob = (src / f"{args.mode}.tflite").read_bytes()
        (out / "model.tflite").write_bytes(blob)
        shutil.copy(src / "scaler.json", out / "scaler.json")
        meta = {
            "device": dev, "variant": VARIANT.get(args.exp, args.exp), "exp": args.exp, "seed": args.seed,
            "quant_mode": args.mode, "input_dim": m["model"]["dims"][0], "params": m["model"]["params"],
            "feature_columns": window_columns(cfg["features"]["window"]),
            "threshold": q["thr"], "window_size": q["ws"], "size_bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "test_metrics": {k: q[k] for k in ("tpr", "fpr", "macro_f1", "f1_balanced")},
        }
        (out / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{dev:45s} thr={q['thr']:.4g} ws={q['ws']} size={len(blob)} B")


if __name__ == "__main__":
    main()
