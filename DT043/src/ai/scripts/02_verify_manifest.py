"""Kiểm tra dữ liệu trong data/ khớp data/MANIFEST.sha256 (exit 1 nếu sai/thiếu).

Chạy:  python scripts/02_verify_manifest.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify(data_dir: Path) -> list[str]:
    """Trả về danh sách file sai checksum hoặc bị thiếu."""
    bad = []
    for line in (Path(data_dir) / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        p = Path(data_dir) / rel
        if not p.exists() or sha256(p) != digest:
            bad.append(rel)
    return bad


if __name__ == "__main__":
    bad = verify(ROOT / "data")
    if bad:
        print(f"LỖI: {len(bad)} file sai/thiếu, ví dụ: {bad[:5]}")
        sys.exit(1)
    print("Manifest OK – mọi file khớp SHA-256.")
