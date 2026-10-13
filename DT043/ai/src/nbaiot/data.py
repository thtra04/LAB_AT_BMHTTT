"""Đọc, kiểm tra schema và nạp dữ liệu N-BaIoT theo từng thiết bị."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

N_FEATURES = 115
WINDOWS = ["L5", "L3", "L1", "L0.1", "L0.01"]
STREAMS = ["MI_dir", "H", "HH", "HH_jit", "HpHp"]
ATTACK_FILES = {
    "gafgyt": ["combo", "junk", "scan", "tcp", "udp"],
    "mirai": ["ack", "scan", "syn", "udp", "udpplain"],
}


class SchemaError(ValueError):
    """Dữ liệu không đúng schema N-BaIoT."""


def expected_columns() -> list[str]:
    """115 tên cột theo đúng thứ tự trong N-BaIoT."""
    stats3 = ["weight", "mean", "variance"]
    stats7 = ["weight", "mean", "std", "magnitude", "radius", "covariance", "pcc"]
    cols = []
    for stream, stats in [("MI_dir", stats3), ("H", stats3), ("HH", stats7),
                          ("HH_jit", ["weight", "mean", "variance"]), ("HpHp", stats7)]:
        for w in WINDOWS:
            cols += [f"{stream}_{w}_{s}" for s in stats]
    return cols


COLUMNS = expected_columns()
assert len(COLUMNS) == N_FEATURES


def window_columns(window: str) -> list[str]:
    """23 cột của một cửa sổ thời gian (vd. 'L1'); 'all' trả về cả 115 cột."""
    if window == "all":
        return list(COLUMNS)
    if window not in WINDOWS:
        raise ValueError(f"Cửa sổ không hợp lệ: {window}")
    return [c for c in COLUMNS if f"_{window}_" in c]


def validate_frame(df: pd.DataFrame, source: str = "") -> pd.DataFrame:
    """Kiểm tra schema: đúng 115 cột, đúng tên/thứ tự, kiểu số, không NaN/inf, không rỗng."""
    if df.shape[0] == 0:
        raise SchemaError(f"{source}: file rỗng")
    if list(df.columns) != COLUMNS:
        missing = set(COLUMNS) - set(df.columns)
        extra = set(df.columns) - set(COLUMNS)
        raise SchemaError(f"{source}: sai cột (thiếu {len(missing)}, thừa {len(extra)}, "
                          f"hoặc sai thứ tự)")
    non_numeric = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise SchemaError(f"{source}: cột không phải số: {non_numeric[:3]}")
    values = df.to_numpy()
    if not np.isfinite(values).all():
        raise SchemaError(f"{source}: có NaN hoặc ±inf")
    return df


def read_csv(path: Path) -> pd.DataFrame:
    """Đọc 1 file CSV N-BaIoT (float64) và kiểm tra schema."""
    try:
        df = pd.read_csv(path, dtype=np.float64)
    except ValueError as e:  # chuỗi không chuyển được sang số
        raise SchemaError(f"{path}: {e}") from e
    return validate_frame(df, str(path))


def raw_segments(raw_dir: Path, device: str) -> dict[str, Path]:
    """Danh sách file CSV của 1 thiết bị: {'benign': ..., 'gafgyt/combo': ..., 'mirai/ack': ...}."""
    base = Path(raw_dir) / device
    segs = {"benign": base / "benign_traffic.csv"}
    for botnet, attacks in ATTACK_FILES.items():
        for a in attacks:
            p = base / f"{botnet}_attacks" / f"{a}.csv"
            if p.exists():
                segs[f"{botnet}/{a}"] = p
    if not segs["benign"].exists():
        raise FileNotFoundError(segs["benign"])
    return segs


def processed_path(processed_dir: Path, device: str, segment: str) -> Path:
    return Path(processed_dir) / device / (segment.replace("/", "__") + ".parquet")


def load_device(processed_dir: Path, device: str, columns: list[str] | None = None) -> dict[str, pd.DataFrame]:
    """Nạp mọi segment đã xử lý (parquet float32, đã khử trùng lặp) của 1 thiết bị."""
    folder = Path(processed_dir) / device
    if not folder.exists():
        raise FileNotFoundError(f"Chưa chạy scripts/03_prepare.py cho {device}")
    out = {}
    for p in sorted(folder.glob("*.parquet")):
        seg = p.stem.replace("__", "/")
        out[seg] = pd.read_parquet(p, columns=columns)
    if "benign" not in out:
        raise FileNotFoundError(f"{device}: thiếu benign")
    return out


def row_hashes(df: pd.DataFrame) -> np.ndarray:
    """Hash từng dòng (dùng để phát hiện trùng lặp giữa các tập)."""
    return pd.util.hash_pandas_object(df, index=False).to_numpy()
