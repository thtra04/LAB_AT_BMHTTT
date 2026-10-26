"""Chuẩn hóa z-score (fit chỉ trên DStrn). Dùng theo từng thiết bị hoặc chung (global)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


class ZScaler:
    def __init__(self, eps: float = 1e-8):
        self.eps = eps
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None
        self.device: str | None = None

    def fit(self, x: np.ndarray, device: str | None = None) -> "ZScaler":
        x = np.asarray(x, dtype=np.float64)
        if x.ndim != 2 or len(x) < 2:
            raise ValueError("Cần ma trận 2 chiều có ≥ 2 dòng để fit scaler")
        self.mean_ = x.mean(axis=0)
        std = x.std(axis=0)
        self.std_ = np.where(std < self.eps, 1.0, std)  # cột hằng → giữ nguyên độ lệch
        self.device = device
        return self

    def transform(self, x: np.ndarray, device: str | None = None) -> np.ndarray:
        if self.mean_ is None:
            raise RuntimeError("Scaler chưa được fit")
        if device is not None and self.device is not None and device != self.device:
            raise ValueError(f"Scaler của {self.device} không dùng được cho {device}")
        x = np.asarray(x, dtype=np.float64)
        if x.shape[1] != self.mean_.shape[0]:
            raise ValueError(f"Sai số đặc trưng: {x.shape[1]} ≠ {self.mean_.shape[0]}")
        return ((x - self.mean_) / self.std_).astype(np.float32)

    def save(self, path: Path) -> None:
        Path(path).write_text(json.dumps({"device": self.device, "mean": self.mean_.tolist(),
                                          "std": self.std_.tolist()}), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ZScaler":
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        s = cls()
        s.mean_, s.std_, s.device = np.array(d["mean"]), np.array(d["std"]), d["device"]
        return s
