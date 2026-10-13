"""Nạp cấu hình YAML: configs/base.yaml + ghi đè từ configs/exp/<tên>.yaml."""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CONFIG_DIR = ROOT / "ai" / "configs"


def deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_config(exp: str | Path | None = None, overrides: dict | None = None) -> dict:
    with open(CONFIG_DIR / "base.yaml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if exp:
        p = Path(exp)
        if not p.exists():
            p = CONFIG_DIR / "exp" / f"{exp}.yaml"
        with open(p, encoding="utf-8") as f:
            cfg = deep_merge(cfg, yaml.safe_load(f))
    return deep_merge(cfg, overrides or {})
