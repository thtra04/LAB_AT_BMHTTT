"""Ngưỡng tr* và cửa sổ majority vote ws* (Meidan 2018, phương trình 1–2)."""
from __future__ import annotations

import numpy as np

RULES = ("mean_std", "mean_3std", "p99", "p99_9")


def threshold(scores: np.ndarray, rule: str = "mean_std") -> float:
    s = np.asarray(scores, dtype=np.float64)
    if s.size == 0:
        raise ValueError("Không có điểm để tính ngưỡng")
    if rule == "mean_std":
        return float(s.mean() + s.std(ddof=1))
    if rule == "mean_3std":
        return float(s.mean() + 3 * s.std(ddof=1))
    if rule == "p99":
        return float(np.percentile(s, 99))
    if rule == "p99_9":
        return float(np.percentile(s, 99.9))
    raise ValueError(f"Quy tắc ngưỡng không hợp lệ: {rule}")


def window_votes(flags: np.ndarray, ws: int) -> np.ndarray:
    """Majority vote trượt (bước 1) trong MỘT segment: cửa sổ dương nếu số mẫu dương > ws/2.

    Segment ngắn hơn ws → một quyết định duy nhất trên toàn segment.
    """
    f = np.asarray(flags, dtype=np.int64)
    if ws < 1:
        raise ValueError("ws phải ≥ 1")
    if f.size == 0:
        return np.zeros(0, dtype=bool)
    if f.size < ws:
        return np.array([f.sum() > f.size / 2])
    c = np.concatenate([[0], np.cumsum(f)])
    sums = c[ws:] - c[:-ws]
    return sums > ws / 2


def find_ws(opt_flags, max_ws: int = 1000) -> tuple[int, float]:
    """ws* = cửa sổ nhỏ nhất cho FPR = 0 trên DSopt; nếu không có, lấy ws có FPR nhỏ nhất.

    `opt_flags` là 1 mảng, hoặc danh sách mảng (nhiều segment – vote không vượt ranh giới).
    """
    segs = opt_flags if isinstance(opt_flags, (list, tuple)) else [opt_flags]
    best_ws, best_fpr = 1, 1.0
    for ws in range(1, max_ws + 1):
        v = np.concatenate([window_votes(f, ws) for f in segs])
        fpr = float(v.mean()) if v.size else 0.0
        if fpr == 0.0:
            return ws, 0.0
        if fpr < best_fpr:
            best_ws, best_fpr = ws, fpr
    return best_ws, best_fpr


def first_detection(flags: np.ndarray, ws: int) -> int | None:
    """Số mẫu cần quan sát từ đầu segment tấn công đến khi có cửa sổ dương đầu tiên."""
    v = window_votes(flags, ws)
    idx = np.flatnonzero(v)
    if idx.size == 0:
        return None
    return int(idx[0]) + min(ws, len(flags))
