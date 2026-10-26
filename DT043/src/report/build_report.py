"""Sinh báo cáo DT043 (.docx) từ kết quả trong results/.

Chạy:  python report/build_report.py
Đầu ra: ../tailieu/bao_cao/BaoCao_DT043_1150080120_HoangThanhTra.docx
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from chapters_results import Results, appendix, ch6_results, ch7_analysis, ch8_conclusion  # noqa: E402
from chapters_static import ch1_intro, ch2_background, ch3_data, ch4_method, ch5_setup, cover  # noqa: E402
from docx_helpers import Report  # noqa: E402

OUT = ROOT.parent / "tailieu" / "bao_cao" / "BaoCao_DT043_1150080120_HoangThanhTra.docx"


def main() -> None:
    R = Report()
    X = Results(ROOT)
    cover(R, ROOT)
    ch1_intro(R)
    ch2_background(R, ROOT)
    ch3_data(R, ROOT)
    ch4_method(R, ROOT)
    ch5_setup(R, ROOT)
    ch6_results(R, X)
    ch7_analysis(R, X)
    ch8_conclusion(R, X)
    appendix(R, ROOT)
    R.save(OUT)
    print(f"Đã lưu {OUT} – {R.n_tab} bảng, {R.n_fig} hình")


if __name__ == "__main__":
    main()
