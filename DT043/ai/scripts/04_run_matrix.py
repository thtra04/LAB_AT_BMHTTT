"""Chạy ma trận thí nghiệm (song song theo thiết bị × seed), bỏ qua lần chạy đã có kết quả.

Mỗi lần chạy là một subprocess Python riêng (giải phóng RAM chắc chắn, lỗi/OOM của một lần chạy không làm
sập cả ma trận); --workers subprocess chạy đồng thời.

Ví dụ:
  python scripts/04_run_matrix.py E1_baseline E4_light --workers 6
  python scripts/04_run_matrix.py E1_baseline --devices Danmini_Doorbell --seeds 42   # smoke test
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import subprocess
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))
TMP = ROOT / ".tmp"


def _setup_env() -> None:
    TMP.mkdir(exist_ok=True)
    for k in ("TMP", "TEMP", "TMPDIR"):
        os.environ[k] = str(TMP)
    tempfile.tempdir = str(TMP)
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _task(exp: str, device: str | None, seed: int, overrides: dict) -> dict:
    _setup_env()
    import warnings

    warnings.filterwarnings("ignore")
    from nbaiot.config import load_config
    from nbaiot.pipeline import run_one, run_shared

    cfg = load_config(exp, overrides)
    t0 = time.time()
    try:
        if cfg.get("shared_model"):
            out = run_shared(cfg, exp, seed)
            r = out[0]["result"]["window"]
        else:
            r = run_one(cfg, exp, device, seed)["result"]["window"]
        return {"exp": exp, "device": device or "ALL", "seed": seed, "status": "ok",
                "wall_s": round(time.time() - t0, 1), "tpr": r["tpr"], "fpr": r["fpr"], "macro_f1": r["macro_f1"]}
    except Exception as e:  # noqa: BLE001 – ghi lỗi, không dừng cả ma trận
        return {"exp": exp, "device": device or "ALL", "seed": seed, "status": f"error: {e!r}",
                "trace": traceback.format_exc(), "wall_s": round(time.time() - t0, 1)}


def main() -> None:
    _setup_env()
    from nbaiot.config import load_config

    ap = argparse.ArgumentParser()
    ap.add_argument("experiments", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--devices", nargs="*")
    ap.add_argument("--seeds", nargs="*", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--one", nargs=3, metavar=("EXP", "DEVICE", "SEED"), help="(nội bộ) chạy đúng 1 lần chạy")
    args = ap.parse_args()
    if args.one:
        exp, dev, seed = args.one
        r = _task(exp, None if dev == "ALL" else dev, int(seed), {})
        print("RESULT" + json.dumps(r, default=float))
        return

    tasks = []
    for exp in args.experiments:
        cfg = load_config(exp)
        devices = args.devices or cfg["devices"]
        seeds = args.seeds or cfg["seeds"]
        res_dir = ROOT / cfg["paths"]["results"] / exp
        for s in seeds:
            if cfg.get("shared_model"):
                done = all((res_dir / d / f"seed={s}" / "metrics.json").exists() for d in cfg["devices"])
                if args.force or not done:
                    tasks.append((exp, None, s))
                continue
            for d in devices:
                if args.force or not (res_dir / d / f"seed={s}" / "metrics.json").exists():
                    tasks.append((exp, d, s))
    print(f"{len(tasks)} lần chạy cần thực hiện", flush=True)

    index = ROOT / "results" / "raw" / "runs_index.csv"
    index.parent.mkdir(parents=True, exist_ok=True)
    fields = ["time", "exp", "device", "seed", "status", "wall_s", "tpr", "fpr", "macro_f1"]
    new = not index.exists()
    def launch(e: str, d: str | None, s: int) -> dict:
        t0 = time.time()
        out = subprocess.run([sys.executable, __file__, "--one", e, d or "ALL", str(s)], capture_output=True,
                             text=True, encoding="utf-8", errors="replace", env=os.environ.copy())
        line = [ln for ln in out.stdout.splitlines() if ln.startswith("RESULT")]
        if line:
            return json.loads(line[0][6:])
        return {"exp": e, "device": d or "ALL", "seed": s, "status": f"error: subprocess exit {out.returncode}",
                "trace": out.stderr[-2000:], "wall_s": round(time.time() - t0, 1)}

    with open(index, "a", newline="", encoding="utf-8") as fidx, ThreadPoolExecutor(max_workers=args.workers) as pool:
        w = csv.DictWriter(fidx, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        futs = [pool.submit(launch, e, d, s) for e, d, s in tasks]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            r["time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            w.writerow(r)
            fidx.flush()
            msg = (f"[{i}/{len(tasks)}] {r['exp']} {r['device']} seed={r['seed']} {r['status']} "
                   f"{r['wall_s']}s")
            if r["status"] == "ok":
                msg += f" TPR={r['tpr']:.4f} FPR={r['fpr']:.4f} macroF1={r['macro_f1']:.4f}"
            else:
                msg += "\n" + r.get("trace", "")
            print(msg, flush=True)


if __name__ == "__main__":
    main()
