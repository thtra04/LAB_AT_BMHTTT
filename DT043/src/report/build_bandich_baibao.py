"""Sinh file Word bản dịch tiếng Việt bài báo chính (Masud et al. 2025) từ bản Markdown.

Chạy tại DT043/src:  .venv\\Scripts\\python report/build_bandich_baibao.py
Đầu vào: ../tailieu/docs/ban_dich_bai_bao_chinh.md (+ hình trong report/paper_figs/, cắt bằng extract_paper_figs.py)
Đầu ra: ../tailieu/docs/BanDich_BaiBao_DT043_1150080120_HoangThanhTra.docx
Markdown được hỗ trợ: tiêu đề #…#####, đoạn văn (**đậm**), danh sách "- ", bảng "|", ảnh ![](…), dòng chú thích
*Bảng/Hình/Thuật toán …*, ghi chú *[…]*, khối ``` (thuật toán, công thức).
"""
import re
import sys
from pathlib import Path

import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from docx_helpers import Report  # noqa: E402

DOCS = HERE.parent.parent / "tailieu" / "docs"
SRC = DOCS / "ban_dich_bai_bao_chinh.md"
OUT = DOCS / "BanDich_BaiBao_DT043_1150080120_HoangThanhTra.docx"
ITALIC = re.compile(r"(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)")  # *nghiêng* → bỏ dấu, Report chỉ hiểu **đậm**
NARROW = ("masud_fig5", "masud_fig8")                            # hình dọc, đặt hẹp hơn


def plain(text: str) -> str:
    return ITALIC.sub(lambda m: m.group(1), text.replace("`", ""))


def italic_line(R: Report, text: str, center: bool, size: float):
    p = R.doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(size)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY


def flush_table(R: Report, rows: list[str]):
    cells = [[plain(c.strip()) for c in r.strip().strip("|").split("|")] for r in rows]
    body = [c for c in cells[1:] if not all(set(x) <= set("-: ") for x in c)]
    df = pd.DataFrame(body, columns=cells[0])
    R.table(df, font=8 if len(df.columns) > 6 else 10)


def main() -> None:
    R = Report()
    lines = SRC.read_text(encoding="utf-8").splitlines()
    i, first_h1 = 0, True
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```"):
            j = i + 1
            while not lines[j].strip().startswith("```"):
                j += 1
            R.code("\n".join(lines[i + 1:j]))
            R.doc.add_paragraph()
            i = j + 1
            continue
        if s.startswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            flush_table(R, lines[i:j])
            i = j
            continue
        if s.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(plain(lines[i].strip()[2:]))
                i += 1
            R.bullets(items)
            continue
        m = re.match(r"!\[.*?\]\((.+?)\)", s)
        if m:
            path = (DOCS / m.group(1)).resolve()
            R.doc.add_picture(str(path), width=Cm(9.0 if path.stem in NARROW else 15.5))
            R.doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif re.match(r"^\*(Bảng|Hình|Thuật toán) \d+\..*\*$", s):
            italic_line(R, s.strip("*"), center=True, size=11)
        elif s.startswith("*[") and s.endswith("]*"):
            italic_line(R, s.strip("*"), center=False, size=11)
        elif s.startswith("##### "):
            R.para(s[6:], bold=True, justify=False)
        elif s.startswith("#### "):
            R.h3(s[5:])
        elif s.startswith("### "):
            R.h2(s[4:])
        elif s.startswith("## "):
            R.h1(s[3:])
        elif s.startswith("# "):
            if not first_h1:
                R.page_break()
            R.para(s[2:], bold=True, size=16 if first_h1 else 15, align="center")
            first_h1 = False
        elif s:
            R.para(plain(s))
        i += 1
    R.save(OUT)
    print(f"Đã ghi {OUT}")


if __name__ == "__main__":
    main()
