"""Đo latency / bộ nhớ / CPU-time của model TFLite cho 1 mẫu (mô phỏng suy luận trên edge)."""
from __future__ import annotations

import ctypes
import platform
import time

import numpy as np
import psutil


def efficiency_cores() -> list[int]:
    """Danh sách logical CPU thuộc lõi tiết kiệm điện (E-core) trên Windows; [] nếu không xác định được."""
    if platform.system() != "Windows":
        return []
    from ctypes import wintypes

    k = ctypes.WinDLL("kernel32")
    need = wintypes.ULONG(0)
    k.GetSystemCpuSetInformation(None, 0, ctypes.byref(need), None, 0)
    buf = (ctypes.c_ubyte * need.value)()
    if not k.GetSystemCpuSetInformation(buf, need, ctypes.byref(need), None, 0):
        return []
    raw, off, info = bytes(buf), 0, []
    while off < need.value:
        size = int.from_bytes(raw[off:off + 4], "little")
        info.append((raw[off + 14], raw[off + 18]))  # (LogicalProcessorIndex, EfficiencyClass)
        off += size
    classes = {e for _, e in info}
    if len(classes) < 2:
        return []
    low = min(classes)
    return [lp for lp, e in info if e == low]


def rss_mb() -> float:
    return psutil.Process().memory_info().rss / 2**20


def bench_tflite(model_bytes: bytes, x: np.ndarray, threads: int, batch: int = 1,
                 n_iter: int = 10000, warmup: int = 200, repeats: int = 5) -> dict:
    """Đo latency từng lần invoke (gồm set_tensor + invoke + get_tensor) và CPU-time trung bình."""
    import tensorflow as tf

    proc = psutil.Process()
    rss0 = rss_mb()
    t0 = time.perf_counter()
    it = tf.lite.Interpreter(model_content=model_bytes, num_threads=threads)
    d = it.get_input_details()[0]
    it.resize_tensor_input(d["index"], [batch, d["shape"][1]])
    it.allocate_tensors()
    load_ms = (time.perf_counter() - t0) * 1e3
    inp, out = it.get_input_details()[0], it.get_output_details()[0]
    if inp["dtype"] == np.int8:
        s, z = inp["quantization"]
        xq = np.clip(np.round(x / s + z), -128, 127).astype(np.int8)
    else:
        xq = x.astype(np.float32)
    n = len(xq)
    rss_loaded = rss_mb()

    for i in range(warmup):
        j = (i * batch) % (n - batch)
        it.set_tensor(inp["index"], xq[j:j + batch])
        it.invoke()
        it.get_tensor(out["index"])
    reps = []
    peak = rss_loaded
    c0 = proc.cpu_times()
    for _ in range(repeats):
        lat = np.empty(n_iter)
        inv = np.empty(n_iter)
        for i in range(n_iter):
            j = (i * batch) % (n - batch)
            t = time.perf_counter_ns()
            it.set_tensor(inp["index"], xq[j:j + batch])
            t1 = time.perf_counter_ns()
            it.invoke()
            t2 = time.perf_counter_ns()
            it.get_tensor(out["index"])
            lat[i] = time.perf_counter_ns() - t
            inv[i] = t2 - t1
        peak = max(peak, rss_mb())
        reps.append({"p50_us": np.percentile(lat, 50) / 1e3, "p95_us": np.percentile(lat, 95) / 1e3,
                     "p99_us": np.percentile(lat, 99) / 1e3, "mean_us": lat.mean() / 1e3,
                     "invoke_p50_us": np.percentile(inv, 50) / 1e3})
    c1 = proc.cpu_times()
    # CPU-time cộng dồn mọi lượt (đồng hồ CPU của Windows chỉ có độ phân giải ~15.6 ms)
    cpu_us_per_call = ((c1.user - c0.user) + (c1.system - c0.system)) / (n_iter * repeats) * 1e6
    agg = {k: float(np.mean([r[k] for r in reps])) for k in reps[0]}
    agg.update({f"{k}_std": float(np.std([r[k] for r in reps])) for k in reps[0]})
    agg.update({"cpu_us_per_call": cpu_us_per_call, "batch": batch, "threads": threads, "n_iter": n_iter,
                "repeats": repeats,
                "throughput_samples_s": batch / (agg["mean_us"] / 1e6),
                "load_ms": load_ms, "rss_before_mb": rss0, "rss_loaded_mb": rss_loaded,
                "rss_peak_mb": peak, "rss_delta_mb": peak - rss0})
    return agg
