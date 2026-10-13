"""Ghi cấu hình phần cứng/phần mềm vào results/env_info.json (đưa vào báo cáo)."""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[2]


def cpu_name() -> str:
    if platform.system() == "Windows":
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command",
                                  "(Get-CimInstance Win32_Processor).Name"],
                                 capture_output=True, text=True, timeout=30).stdout.strip()
            return out or platform.processor()
        except Exception:  # noqa: BLE001
            pass
    return platform.processor()


def main() -> None:
    pkgs = ["tensorflow", "keras", "numpy", "pandas", "pyarrow", "scikit-learn", "scipy", "psutil",
            "PyYAML", "matplotlib", "networkx", "pytest"]
    try:
        git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:  # noqa: BLE001
        git = "unknown"
    info = {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "machine": platform.machine(),
        "cpu": cpu_name(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cpus": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / 2**30, 1),
        "python": sys.version.split()[0],
        "packages": {p: version(p) for p in pkgs},
        "git_commit": git,
    }
    out = ROOT / "results" / "env_info.json"
    out.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
