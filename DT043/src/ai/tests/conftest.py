import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.data import COLUMNS  # noqa: E402


def synthetic_frame(n: int, shift: float = 0.0, seed: int = 0) -> pd.DataFrame:
    """Dữ liệu tổng hợp đúng schema N-BaIoT: benign quanh 0, attack bị dịch `shift`."""
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, (n, 8))
    mix = rng.normal(0, 1, (8, len(COLUMNS)))
    x = base @ mix * 0.3 + shift + rng.normal(0, 0.05, (n, len(COLUMNS)))
    return pd.DataFrame(x, columns=COLUMNS)


@pytest.fixture
def tiny_processed(tmp_path):
    """Thư mục processed giả cho 1 thiết bị: benign + 2 loại tấn công."""
    dev = tmp_path / "processed" / "Fake_Device"
    dev.mkdir(parents=True)
    synthetic_frame(3000, 0.0, 1).astype(np.float32).to_parquet(dev / "benign.parquet", index=False)
    synthetic_frame(600, 4.0, 2).astype(np.float32).to_parquet(dev / "mirai__ack.parquet", index=False)
    synthetic_frame(600, 2.5, 3).astype(np.float32).to_parquet(dev / "gafgyt__scan.parquet", index=False)
    return tmp_path
