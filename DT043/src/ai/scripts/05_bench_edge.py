"""E8 – Edge benchmark: mỗi (model × kiểu lượng tử × profile) chạy trong process RIÊNG để đo RAM sạch.

Profile:
  P0 – PC đầy đủ (tất cả luồng), batch 1 và batch 256
  P1 – edge giả lập: 1 luồng, ghim vào 1 E-core, batch 1
Chạy:  python scripts/05_bench_edge.py [--device Danmini_Doorbell] [--quick]
Đầu ra: results/raw/E8_edge/bench.csv
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

# Giả định cho energy proxy: Intel i7-13650HX "Processor Base Power" 55 W / 14 lõi ≈ 3.93 W mỗi lõi.
# Đây là PROXY (cận trên thô), không phải đo điện thực tế.
CORE_POWER_W = 55.0 / 14

MODELS = [  # (exp, nhãn model)
    ("E1_baseline", "B0"),
    ("E4_light", "V1"),
    ("E4_tiny_L01", "V2"),
]


def child(args) -> None:
    import numpy as np
    import psutil

    from nbaiot.bench import bench_tflite, efficiency_cores

    if args.affinity is not None:
        psutil.Process().cpu_affinity([args.affinity])
    blob = Path(args.model).read_bytes()
    dim = int(args.dim)
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, (4096, dim)).astype(np.float32)  # đã chuẩn hóa z-score → ~N(0,1)
    r = bench_tflite(blob, x, threads=args.threads, batch=args.batch, n_iter=args.n_iter,
                     repeats=args.repeats)
    r["affinity"] = args.affinity
    r["e_cores"] = efficiency_cores()
    print("RESULT" + json.dumps(r))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="Danmini_Doorbell")
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--child", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--dim")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--affinity", type=int)
    ap.add_argument("--n-iter", type=int, default=10000)
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args()
    if args.child:
        child(args)
        return

    from nbaiot.bench import efficiency_cores
    from nbaiot.models import count_macs, count_params

    ecores = efficiency_cores()
    pin = ecores[-1] if ecores else None
    n_all = os.cpu_count()
    profiles = [("P0_b1", n_all, 1, None), ("P0_b256", n_all, 256, None), ("P1_edge", 1, 1, pin)]
    n_iter, repeats = (1000, 2) if args.quick else (10000, 5)
    rows = []
    for exp, label in MODELS:
        mdir = ROOT / "artifacts" / "models" / exp / args.device
        mfile = ROOT / "results" / "raw" / exp / args.device / "seed=42" / "metrics.json"
        if not mfile.exists():
            print("bỏ qua – chưa có model:", exp)
            continue
        meta = json.loads(mfile.read_text(encoding="utf-8"))["model"]
        for tfl in sorted(mdir.glob("*.tflite")):
            mode = tfl.stem
            for prof, thr, batch, aff in profiles:
                it = n_iter if batch == 1 else max(200, n_iter // 20)
                cmd = [sys.executable, __file__, "--child", "--model", str(tfl), "--dim", str(meta["dims"][0]),
                       "--threads", str(thr), "--batch", str(batch), "--n-iter", str(it),
                       "--repeats", str(repeats)]
                if aff is not None:
                    cmd += ["--affinity", str(aff)]
                out = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ,
                                     "TF_CPP_MIN_LOG_LEVEL": "3", "PYTHONIOENCODING": "utf-8"})
                line = [ln for ln in out.stdout.splitlines() if ln.startswith("RESULT")]
                if not line:
                    print("LỖI", tfl, prof, out.stderr[-500:])
                    continue
                r = json.loads(line[0][6:])
                r.update({"model": label, "exp": exp, "mode": mode, "profile": prof,
                          "size_kb": tfl.stat().st_size / 1024, "params": count_params(meta["dims"]),
                          "macs": count_macs(meta["dims"]),
                          "energy_proxy_uJ": r["cpu_us_per_call"] * CORE_POWER_W / max(batch, 1)})
                r.pop("e_cores", None)
                rows.append(r)
                print(f"{label:3s} {mode:5s} {prof:8s} p50={r['p50_us']:.1f}us p95={r['p95_us']:.1f}us "
                      f"thr={r['throughput_samples_s']:.0f}/s rssΔ={r['rss_delta_mb']:.1f}MB "
                      f"E≈{r['energy_proxy_uJ']:.2f}uJ", flush=True)
    out_dir = ROOT / "results" / "raw" / "E8_edge"
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / ("bench_quick.csv" if args.quick else "bench.csv"), index=False)
    (out_dir / "bench_meta.json").write_text(json.dumps({
        "device_models": args.device, "e_cores": ecores, "pinned_cpu_P1": pin,
        "core_power_w_assumption": CORE_POWER_W, "note": "energy_proxy_uJ = CPU-time/mẫu × 55W/14 lõi"},
        indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
