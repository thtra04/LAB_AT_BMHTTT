"""Chuyển Keras → TFLite (fp32 / fp16 / dynamic-range int8 / full-integer int8) và suy luận theo lô."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np

MODES = ("fp32", "fp16", "dyn", "int8")


def to_tflite(model, mode: str, rep_data: np.ndarray | None = None, n_rep: int = 500,
              seed: int = 0) -> bytes:
    """Xuất qua SavedModel (đóng băng trọng số) rồi chuyển sang TFLite."""
    import tensorflow as tf

    if mode not in MODES:
        raise ValueError(f"mode không hợp lệ: {mode}")
    tmp = Path(tempfile.mkdtemp(prefix="sm_"))
    try:
        model.export(str(tmp / "sm"), verbose=False)
        conv = tf.lite.TFLiteConverter.from_saved_model(str(tmp / "sm"))
        if mode != "fp32":
            conv.optimizations = [tf.lite.Optimize.DEFAULT]
        if mode == "fp16":
            conv.target_spec.supported_types = [tf.float16]
        if mode == "int8":
            if rep_data is None or len(rep_data) == 0:
                raise ValueError("int8 cần representative dataset (lấy từ DStrn)")
            rng = np.random.default_rng(seed)
            idx = rng.choice(len(rep_data), size=min(n_rep, len(rep_data)), replace=False)
            rep = rep_data[np.sort(idx)].astype(np.float32)
            conv.representative_dataset = lambda: ([rep[i:i + 1]] for i in range(len(rep)))
            conv.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            conv.inference_input_type = tf.int8
            conv.inference_output_type = tf.int8
        return conv.convert()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class TFLiteRunner:
    """Chạy model TFLite theo lô, tự lượng tử hóa/giải lượng tử hóa đầu vào/ra int8."""

    def __init__(self, model_content: bytes, num_threads: int = 1, batch: int = 4096):
        import tensorflow as tf

        self.batch = batch
        self.it = tf.lite.Interpreter(model_content=model_content, num_threads=num_threads)
        d = self.it.get_input_details()[0]
        self.it.resize_tensor_input(d["index"], [batch, d["shape"][1]])
        self.it.allocate_tensors()
        self.inp = self.it.get_input_details()[0]
        self.out = self.it.get_output_details()[0]
        self.dim = int(self.inp["shape"][1])

    def _q(self, x: np.ndarray) -> np.ndarray:
        if self.inp["dtype"] == np.int8:
            s, z = self.inp["quantization"]
            return np.clip(np.round(x / s + z), -128, 127).astype(np.int8)
        return x.astype(np.float32)

    def _dq(self, y: np.ndarray) -> np.ndarray:
        if self.out["dtype"] == np.int8:
            s, z = self.out["quantization"]
            return (y.astype(np.float32) - z) * s
        return y

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=np.float32)
        if x.ndim != 2 or x.shape[1] != self.dim:
            raise ValueError(f"Đầu vào phải có shape (n, {self.dim})")
        out = np.empty_like(x)
        for i in range(0, len(x), self.batch):
            chunk = x[i:i + self.batch]
            n = len(chunk)
            if n < self.batch:
                chunk = np.vstack([chunk, np.zeros((self.batch - n, self.dim), np.float32)])
            self.it.set_tensor(self.inp["index"], self._q(chunk))
            self.it.invoke()
            out[i:i + n] = self._dq(self.it.get_tensor(self.out["index"]))[:n]
        return out

    def mse(self, x: np.ndarray) -> np.ndarray:
        """MSE tái tạo so với đầu vào float GỐC (không phải bản đã lượng tử hóa)."""
        return np.mean((self.predict(x).astype(np.float64) - x) ** 2, axis=1)  # float64: tránh tràn số
