"""Chia benign thành DStrn / DSopt / DStst theo thời gian (có purge gap) và chặn rò rỉ."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .data import row_hashes


@dataclass
class SplitIdx:
    train: np.ndarray
    opt: np.ndarray
    test: np.ndarray


def chronological_split(n: int, fractions=(1 / 3, 1 / 3, 1 / 3), purge_gap: int = 0) -> SplitIdx:
    """Chia theo thứ tự dòng; bỏ `purge_gap` dòng ở đầu tập opt và tập test."""
    if n <= 0:
        raise ValueError("n phải > 0")
    f = np.asarray(fractions, dtype=float)
    if f.shape != (3,) or np.any(f <= 0) or not np.isclose(f.sum(), 1.0, atol=1e-5):
        raise ValueError("fractions phải gồm 3 số dương có tổng = 1")
    b1 = int(round(n * f[0]))
    b2 = int(round(n * (f[0] + f[1])))
    train = np.arange(0, b1)
    opt = np.arange(min(b1 + purge_gap, b2), b2)
    test = np.arange(min(b2 + purge_gap, n), n)
    if min(len(train), len(opt), len(test)) == 0:
        raise ValueError(f"purge_gap={purge_gap} quá lớn so với n={n}")
    return SplitIdx(train, opt, test)


def random_split(n: int, fractions=(1 / 3, 1 / 3, 1 / 3), seed: int = 0) -> SplitIdx:
    """Chia ngẫu nhiên – CHỈ dùng cho thí nghiệm minh họa rò rỉ (E6)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    b1 = int(round(n * fractions[0]))
    b2 = int(round(n * (fractions[0] + fractions[1])))
    return SplitIdx(np.sort(perm[:b1]), np.sort(perm[b1:b2]), np.sort(perm[b2:]))


def drop_overlap(df: pd.DataFrame, reference_hashes: np.ndarray) -> tuple[pd.DataFrame, int]:
    """Bỏ khỏi `df` các dòng trùng hash với tập tham chiếu (train/opt). Giữ thứ tự."""
    if len(df) == 0:
        return df, 0
    mask = np.isin(row_hashes(df), reference_hashes)
    return df.loc[~mask].reset_index(drop=True), int(mask.sum())


def overlap_count(a: pd.DataFrame, b: pd.DataFrame) -> int:
    """Số dòng của `a` trùng hash với `b` (dùng trong test chống rò rỉ)."""
    return int(np.isin(row_hashes(a), row_hashes(b)).sum())
