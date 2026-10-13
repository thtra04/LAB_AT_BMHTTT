"""Tải N-BaIoT từ UCI, ghi thông tin tải, giải nén zip + rar và tạo manifest SHA-256.

Chạy:  python scripts/01_download.py [--unrar "D:/Program Files/UnRAR.exe"]
Đầu ra: data/raw/..., data/DOWNLOAD_INFO.json, data/MANIFEST.sha256
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://archive.ics.uci.edu/static/public/442/detection+of+iot+botnet+attacks+n+baiot.zip"
DATA = ROOT / "data"
RAW = DATA / "raw"
ZIP_PATH = DATA / "download" / "n_baiot.zip"


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        total = 0
        while True:
            block = r.read(1 << 20)
            if not block:
                break
            f.write(block)
            total += len(block)
            if total % (100 << 20) < (1 << 20):
                print(f"  ... {total / 2**20:.0f} MB", flush=True)
    tmp.replace(dest)


def find_unrar(cli: str | None) -> str:
    candidates = [cli, shutil.which("unrar"), r"D:\Program Files\UnRAR.exe",
                  r"C:\Program Files\WinRAR\UnRAR.exe", shutil.which("7z"),
                  r"C:\Program Files\7-Zip\7z.exe"]
    for c in candidates:
        if c and Path(c).exists():
            return c
    sys.exit("Không tìm thấy UnRAR/7z. Truyền --unrar <đường dẫn>.")


def extract_rar(tool: str, rar: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    if Path(tool).name.lower().startswith("7z"):
        cmd = [tool, "x", "-y", f"-o{out}", str(rar)]
    else:
        cmd = [tool, "x", "-o+", "-y", str(rar), str(out) + "\\"]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--unrar", default=None)
    ap.add_argument("--skip-download", action="store_true")
    args = ap.parse_args()

    if not args.skip_download or not ZIP_PATH.exists():
        print(f"Tải {URL}")
        download(URL, ZIP_PATH)
    info = {
        "dataset": "detection_of_IoT_botnet_attacks_N_BaIoT",
        "source_page": "https://archive.ics.uci.edu/dataset/442/detection+of+iot+botnet+attacks+n+baiot",
        "url": URL,
        "doi": "10.24432/C5RC8J",
        "license": "CC BY 4.0",
        "uci_donated": "2018-03-18",
        "citation": "Meidan Y. et al. (2018) N-BaIoT: Network-based Detection of IoT Botnet Attacks "
                    "Using Deep Autoencoders. IEEE Pervasive Computing 17(3):12-22.",
        "downloaded_at_utc": dt.datetime.fromtimestamp(ZIP_PATH.stat().st_mtime, dt.timezone.utc).isoformat(),
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256(ZIP_PATH),
    }
    print("SHA-256 zip:", info["zip_sha256"])

    print("Giải nén zip ...")
    RAW.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extractall(RAW)

    tool = find_unrar(args.unrar)
    for rar in sorted(RAW.rglob("*.rar")):
        print("Giải nén", rar.relative_to(RAW))
        extract_rar(tool, rar, rar.parent / rar.stem)
    info["extractor"] = Path(tool).name

    lines = []
    for p in sorted(RAW.rglob("*")):
        if p.is_file():
            lines.append(f"{sha256(p)}  {p.relative_to(DATA).as_posix()}")
    (DATA / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    info["n_files"] = len(lines)
    (DATA / "DOWNLOAD_INFO.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Xong: {len(lines)} file trong manifest.")


if __name__ == "__main__":
    main()
