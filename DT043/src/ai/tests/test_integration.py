"""Integration test: pipeline end-to-end trên dữ liệu tổng hợp nhỏ + Keras ↔ TFLite."""
import json

import numpy as np
import pytest

from nbaiot.config import load_config
from nbaiot.pipeline import load_split, run_one
from nbaiot.split import overlap_count

pytest.importorskip("tensorflow")


def _cfg(tmp_path, **over):
    base = {
        "paths": {"processed": str(tmp_path / "processed"), "results": str(tmp_path / "res"),
                  "scores": str(tmp_path / "scores"), "models": str(tmp_path / "models")},
        "devices": ["Fake_Device"],
        "split": {"purge_gap": 20},
        "train": {"max_epochs": 15, "patience": 3},
        "threshold": {"max_ws": 200},
        "threads": 1,
    }
    base.update(over)
    return load_config(overrides=base)


def test_no_leakage_between_splits(tiny_processed, tmp_path):
    import pandas as pd

    cfg = _cfg(tmp_path)
    dd = load_split(cfg, "Fake_Device", seed=0)
    tr = pd.DataFrame(dd.train)
    for seg, x in dd.test.items():
        assert overlap_count(pd.DataFrame(x), tr) == 0, seg
    # scaler chỉ dùng thống kê DStrn → trung bình train ≈ 0
    assert abs(dd.train.mean()) < 1e-3


def test_end_to_end_with_quantization(tiny_processed, tmp_path):
    cfg = _cfg(tmp_path, model={"kind": "ae", "hidden": [32, 8]}, quantize=["fp32", "int8"])
    out = run_one(cfg, "itest", "Fake_Device", seed=42)
    r = out["result"]
    assert r["window"]["tpr"] > 0.9 and r["window"]["fpr"] < 0.1
    # TFLite fp32 phải cho quyết định gần như trùng Keras
    assert abs(r["quantized"]["fp32"]["keep"]["tpr"] - r["window"]["tpr"]) < 1e-3
    assert r["quantized"]["int8"]["size_bytes"] < r["quantized"]["fp32"]["size_bytes"]
    saved = json.loads((tmp_path / "res" / "itest" / "Fake_Device" / "seed=42" / "metrics.json").read_text("utf-8"))
    assert saved["seed"] == 42 and "ablation_grid" in saved["result"]
    assert (tmp_path / "models" / "itest" / "Fake_Device" / "int8.tflite").exists()


def test_same_seed_same_result(tiny_processed, tmp_path):
    cfg = _cfg(tmp_path, model={"kind": "ae", "hidden": [16, 4]})
    a = run_one(cfg, "det", "Fake_Device", seed=7)["result"]
    b = run_one(cfg, "det", "Fake_Device", seed=7)["result"]
    assert a["thr"] == pytest.approx(b["thr"], rel=1e-6) and a["ws"] == b["ws"]


def test_iforest_baseline_runs(tiny_processed, tmp_path):
    cfg = _cfg(tmp_path, model={"kind": "iforest"})
    r = run_one(cfg, "if", "Fake_Device", seed=1)["result"]
    assert 0 <= r["window"]["macro_f1"] <= 1 and np.isfinite(r["roc_auc"])
