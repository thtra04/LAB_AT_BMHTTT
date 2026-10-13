"""Bộ phát hiện per-device ở backend: nạp gói triển khai (model.tflite + scaler.json + meta.json)."""
from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


class BundleError(RuntimeError):
    """Gói triển khai thiếu file hoặc bị sửa đổi."""


@dataclass
class DetectionResult:
    mse: np.ndarray
    flags: np.ndarray
    window_alarms: np.ndarray
    infer_us_per_sample: float

    @property
    def first_alarm(self) -> int | None:
        idx = np.flatnonzero(self.window_alarms)
        return int(idx[0]) if idx.size else None


def window_votes(flags: np.ndarray, ws: int) -> np.ndarray:
    """Majority vote trượt: cửa sổ dương nếu số mẫu dương > ws/2 (giống tầng AI)."""
    f = np.asarray(flags, dtype=np.int64)
    if f.size == 0:
        return np.zeros(0, dtype=bool)
    if f.size < ws:
        return np.array([f.sum() > f.size / 2])
    c = np.concatenate([[0], np.cumsum(f)])
    return (c[ws:] - c[:-ws]) > ws / 2


class DeviceDetector:
    def __init__(self, bundle_dir: Path, threads: int = 1):
        bundle_dir = Path(bundle_dir)
        for name in ("model.tflite", "scaler.json", "meta.json"):
            if not (bundle_dir / name).exists():
                raise BundleError(f"{bundle_dir.name}: thiếu {name}")
        self.meta = json.loads((bundle_dir / "meta.json").read_text(encoding="utf-8"))
        blob = (bundle_dir / "model.tflite").read_bytes()
        if hashlib.sha256(blob).hexdigest() != self.meta["sha256"]:
            raise BundleError(f"{bundle_dir.name}: SHA-256 model không khớp meta.json")
        sc = json.loads((bundle_dir / "scaler.json").read_text(encoding="utf-8"))
        if sc.get("device") not in (None, self.meta["device"]):
            raise BundleError("scaler không thuộc thiết bị này")
        self.mean = np.asarray(sc["mean"], dtype=np.float64)
        self.std = np.asarray(sc["std"], dtype=np.float64)
        self.device = self.meta["device"]
        self.dim = int(self.meta["input_dim"])
        self.threshold = float(self.meta["threshold"])
        self.window_size = int(self.meta["window_size"])
        self.sha256 = self.meta["sha256"]
        self.size_bytes = len(blob)

        import tensorflow as tf

        self._lock = threading.Lock()  # Interpreter TFLite không thread-safe
        self._it = tf.lite.Interpreter(model_content=blob, num_threads=threads)
        self._batch = 0
        self._inp = self._out = None

    def _ensure_batch(self, n: int) -> None:
        if n != self._batch:
            d = self._it.get_input_details()[0]
            self._it.resize_tensor_input(d["index"], [n, self.dim])
            self._it.allocate_tensors()
            self._inp, self._out = self._it.get_input_details()[0], self._it.get_output_details()[0]
            self._batch = n

    def _predict(self, z: np.ndarray, chunk: int = 2048) -> np.ndarray:
        out = np.empty_like(z)
        for i in range(0, len(z), chunk):
            part = z[i:i + chunk]
            self._ensure_batch(len(part))
            x = part
            if self._inp["dtype"] == np.int8:
                s, zp = self._inp["quantization"]
                x = np.clip(np.round(part / s + zp), -128, 127).astype(np.int8)
            self._it.set_tensor(self._inp["index"], x)
            self._it.invoke()
            y = self._it.get_tensor(self._out["index"])
            if self._out["dtype"] == np.int8:
                s, zp = self._out["quantization"]
                y = (y.astype(np.float32) - zp) * s
            out[i:i + len(part)] = y
        return out

    def detect(self, features: np.ndarray) -> DetectionResult:
        x = np.asarray(features, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != self.dim:
            raise ValueError(f"Cần ma trận (n, {self.dim}), nhận {x.shape}")
        if len(x) == 0:
            raise ValueError("Lô rỗng")
        if not np.isfinite(x).all():
            raise ValueError("Đặc trưng chứa NaN/inf")
        z = ((x - self.mean) / self.std).astype(np.float32)
        with self._lock:
            t0 = time.perf_counter()
            rec = self._predict(z)
            dt = time.perf_counter() - t0
        mse = np.mean((rec.astype(np.float64) - z) ** 2, axis=1)
        flags = mse > self.threshold
        return DetectionResult(mse, flags, window_votes(flags, self.window_size), dt / len(x) * 1e6)


class DetectorRegistry:
    """Nạp mọi gói trong artifacts/deploy/ khi backend khởi động."""

    def __init__(self, deploy_dir: Path, threads: int = 1):
        self.detectors: dict[str, DeviceDetector] = {}
        self.errors: dict[str, str] = {}
        if Path(deploy_dir).exists():
            for d in sorted(Path(deploy_dir).iterdir()):
                if d.is_dir():
                    try:
                        self.detectors[d.name] = DeviceDetector(d, threads)
                    except (BundleError, KeyError, ValueError) as e:
                        self.errors[d.name] = str(e)

    def get(self, device: str) -> DeviceDetector:
        if device not in self.detectors:
            raise KeyError(device)
        return self.detectors[device]
