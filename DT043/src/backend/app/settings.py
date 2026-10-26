"""Cấu hình backend (có thể ghi đè bằng biến môi trường DT043_*)."""
from __future__ import annotations

import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
DEPLOY_DIR = Path(os.environ.get("DT043_DEPLOY_DIR", PROJECT / "artifacts" / "deploy"))
PROCESSED_DIR = Path(os.environ.get("DT043_PROCESSED_DIR", PROJECT / "data" / "processed"))
DB_PATH = Path(os.environ.get("DT043_DB", PROJECT / "db" / "dt043.sqlite3"))
FRONTEND_DIR = PROJECT / "frontend"
TABLES_DIR = PROJECT / "results" / "tables"

MAX_SAMPLES_PER_REQUEST = 20_000      # chống gửi lô quá lớn
MTD_TIME_PERIOD_S = 60                # chu kỳ MTD time-based (mô phỏng)
TFLITE_THREADS = 1                    # suy luận như trên edge: 1 luồng
