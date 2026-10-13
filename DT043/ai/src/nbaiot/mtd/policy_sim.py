"""MTD lai kích hoạt bởi cảnh báo AE: so sánh time-based / event-based / hybrid trên luồng quyết định THẬT.

Luồng mỗi thiết bị = [benign test] + các đoạn tấn công (mỗi file tấn công = 1 "đợt tấn công" bắt đầu ở mẫu 0).
"""
from __future__ import annotations

import numpy as np

from ..threshold import window_votes


def episode_alarm_positions(scores: dict[str, np.ndarray], thr: float, ws: int) -> dict[str, np.ndarray]:
    """Vị trí (theo mẫu, tính từ đầu segment) của các cửa sổ cảnh báo – đã cộng ws−1 để là mẫu cuối cửa sổ."""
    out = {}
    for seg, s in scores.items():
        v = window_votes(np.asarray(s) > thr, ws)
        off = min(ws, len(s)) - 1
        out[seg] = np.flatnonzero(v) + off
    return out


def evaluate_policy(alarms: dict[str, np.ndarray], lengths: dict[str, int], policy: str, period: int,
                    cooldown: int, rng: np.random.Generator, n_phase: int = 50) -> dict:
    """Trả về: thời gian lộ diện trung bình (mẫu), số move / 10k mẫu, tỷ lệ move vô ích (trong benign)."""
    exposures, moves_total, wasted, total_len = [], 0, 0, sum(lengths.values())
    for _ in range(n_phase):  # pha ngẫu nhiên của đồng hồ time-based
        phase = int(rng.integers(0, period)) if period else 0
        t0 = 0
        for seg, n in lengths.items():
            times = set()
            if policy in ("time", "hybrid"):
                first = (period - (t0 + phase) % period) % period
                times |= set(range(first, n, period))
            if policy in ("event", "hybrid"):
                last = -10**9
                for a in alarms[seg]:
                    if a - last >= cooldown:
                        times.add(int(a))
                        last = a
            moves = sorted(times)
            moves_total += len(moves)
            if seg == "benign":
                wasted += sum(1 for m in moves if policy != "time" and m in set(alarms[seg].tolist()))
            else:
                exposures.append(moves[0] if moves else n)
            t0 += n
    return {"policy": policy, "period": period,
            "exposure_mean": float(np.mean(exposures)), "exposure_p95": float(np.percentile(exposures, 95)),
            "moves_per_10k": moves_total / n_phase / total_len * 1e4,
            "wasted_moves_per_10k_benign": wasted / n_phase / max(lengths.get("benign", 1), 1) * 1e4}
