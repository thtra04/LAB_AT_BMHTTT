"""Thêm E12 vào báo cáo Word HIỆN CÓ bằng cách sửa tại chỗ, không chạy lại build_report.py.

Lý do: file .docx đã được sửa tay sau lần sinh gần nhất (bỏ phụ lục, đổi mục tài liệu tham khảo, rút vài đoạn),
nên sinh lại từ chapters_*.py sẽ làm mất các chỉnh sửa đó.

Chạy:  python report/patch_report_e12.py <docx nguồn> <docx đích> [tỷ lệ thu hình]
Sau đó: powershell -File report/finalize_word.ps1 <docx đích>
"""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import docx
import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parent.parent
TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"


def replace(p: Paragraph, old: str, new: str) -> None:
    """Thay chuỗi trong đoạn gồm nhiều run, giữ định dạng của run đầu tiên chứa chuỗi."""
    start = p.text.find(old)
    if start < 0:
        raise ValueError(f"Không thấy: {old[:60]}")
    end, pos, placed = start + len(old), 0, False
    for r in p.runs:
        a, b = pos, pos + len(r.text)
        pos = b
        if b <= start or a >= end:
            continue
        keep_l = r.text[: max(0, start - a)]
        keep_r = r.text[max(0, end - a):]
        r.text = keep_l + ("" if placed else new) + keep_r
        placed = True


def find_p(d, startswith: str) -> Paragraph:
    for p in d.paragraphs:
        if p.text.strip().startswith(startswith):
            return p
    raise ValueError(startswith)


def find_t(d, first_cell: str, n_cols: int) -> Table:
    for t in d.tables:
        if t.cell(0, 0).text.strip() == first_cell and len(t.columns) == n_cols:
            return t
    raise ValueError(first_cell)


def set_cell(cell, text: str) -> None:
    p = cell.paragraphs[0]
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""


def add_row_after(t: Table, ref: int, values: list[str]) -> None:
    tr = copy.deepcopy(t.rows[ref]._tr)
    t.rows[ref]._tr.addnext(tr)
    for c, v in zip(t.rows[ref + 1].cells, values):
        set_cell(c, v)


def para(d, anchor, text: str, style=None, size=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY) -> Paragraph:
    p = d.add_paragraph(style=style)
    for i, part in enumerate(text.split("**")):
        if part:
            r = p.add_run(part)
            r.bold = i % 2 == 1
            if size:
                r.font.size = Pt(size)
    p.alignment = align
    anchor.addprevious(p._p)
    return p


def caption_like(d, anchor, sample: Paragraph, text: str) -> Paragraph:
    el = copy.deepcopy(sample._p)
    anchor.addprevious(el)
    p = Paragraph(el, sample._parent)
    runs = p.runs
    runs[0].text = text
    for r in runs[1:]:
        r.text = ""
    return p


def table(d, anchor, header: list[str], rows: list[list[str]], widths: list[float], font=9) -> None:
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = 1
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    for j, h in enumerate(header):
        c = t.rows[0].cells[j]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold, r.font.size = True, Pt(font)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"), shd.set(qn("w:color"), "auto"), shd.set(qn("w:fill"), "D9E2F3")
        c._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = ""
            cells[j].paragraphs[0].add_run(v).font.size = Pt(font)
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)
    anchor.addprevious(t._tbl)
    para(d, anchor, "", size=4)


def main(src: str, dst: str, scale: float) -> None:
    d = docx.Document(src)

    # ---- 1. Sửa các câu đã lỗi thời
    replace(find_p(d, "Sau khi có toàn văn, mô hình 3-layer"), "14 test so khớp", "24 test so khớp")
    replace(find_p(d, "Rủi ro mức VM khớp tới"), "ASP của Bảng 4 không tái lập được vì Eq. 1 bản in có thể âm và paper không công bố mã nguồn.",
            "ASP của Bảng 4 không tái lập được vì paper không nêu đủ cách tính; Eq. 1 được xét lại ở mục 6.10.")
    replace(find_p(d, "Bảng 18."), "Tổng toàn mạng: không tái lập được số tuyệt đối",
            "Tổng toàn mạng theo cách tính của E11 (AC theo VM = Σ cost): không khớp; xem mục 6.10")
    replace(find_p(d, "Tổng toàn mạng của paper không suy ra"),
            "Tổng toàn mạng của paper không suy ra được từ dữ liệu công bố (danh sách cạnh sau shuffle bị cắt; AC theo VM ở mục 4.2 "
            "lớn gấp 5–8 lần tổng cost của Bảng 1–2), nên chỉ so xu hướng.",
            "Với cách tính của E11, tổng toàn mạng không khớp (danh sách cạnh sau shuffle bị cắt; AC theo VM ở mục 4.2 lớn gấp 5–8 "
            "lần tổng cost của Bảng 1–2), nên ở đây chỉ so xu hướng; mục 6.10 tìm được cách tính gần hơn cho AC và RoC.")
    replace(find_p(d, "Đường diversity khớp cả 7/7 VM"),
            "AC và RoC khác thang đo (AC của bài gấp 5–8 lần tổng cost Bảng 1–2, như mục 6.8).",
            "Tính chung Hình 6(a), 11/35 điểm lệch ≤ 5%. AR của S+D chỉ thấp nhất khi áp lên V5; ở 5 VM khác diversity thấp nhất, "
            "ở V4 shuffle thấp nhất, nên kết luận \"S+D tốt nhất\" chỉ tái lập được ở ví dụ V5. AC và RoC: xem mục 6.10.")
    replace(find_p(d, "Hình 7 không tái lập được"),
            "tức bài dùng một cách tính ASP đường không được công bố.",
            "nên hai bảng số này không tương thích. Eq. 1 nguyên văn đưa ASP đường về cùng thang đo (mục 6.10), nhưng bài không "
            "in chuỗi VM của 8 đường nên không so được từng cột.")
    replace(find_p(d, "Track B: mô hình HARM rút gọn"),
            "khớp mức VM và đường tấn công nhưng không khớp tổng toàn mạng vì Bảng 4 của paper không nêu đủ cách tính.",
            "khớp mức VM và đường tấn công. E12 đưa tổng AC, RoC về gần bài bằng công thức AC do đề tài suy ra (giả thuyết, không "
            "giải thích được V2); tổng R của diversity, redundancy, Hình 5(b), 6, 7, 9 vẫn chưa khớp.")
    replace(find_p(d, "Đề tài đã xây dựng đầy đủ khung"),
            "với thành phần time-based bù cho các tấn công detector bỏ sót.",
            "với thành phần time-based bù cho các tấn công detector bỏ sót; (6) tái lập paper chính khớp đầu vào, rủi ro mức VM và "
            "mức đường, tổng AC, RoC gần khớp qua công thức suy ra, nhưng không thể khớp toàn bộ vì paper thiếu công thức và "
            "có chỗ không nhất quán.")

    t9 = find_t(d, "ID", 4)
    add_row_after(t9, len(t9.rows) - 1, ["E12", "Tái hiện thêm tổng mạng, Hình 5–8 của paper chính", "Tất định; Hình 8: 4 cỡ × 5 seed", "paper chính"])

    t30 = find_t(d, "Khía cạnh", 4)
    idx = {r.cells[0].text.strip(): i for i, r in enumerate(t30.rows)}
    i = idx["Tổng toàn mạng (E11)"]
    add_row_after(t30, i, ["Tổng AC, RoC (E12)", "AC 666.2 / 624.73 / 878.3; RoC 1.01 / 1.04 / 1.46",
                           "AC 654.3 / 603.5 / 897.4; RoC 1.07 / 0.95 / 1.46", "Gần khớp (AC ≤ 3.4%, RoC ≤ 8.4%); công thức là giả thuyết"])
    idx = {r.cells[0].text.strip(): i for i, r in enumerate(t30.rows)}
    set_cell(t30.rows[idx["Hình 6 – AR theo VM (vẽ lại)"]].cells[2], "11/35 điểm lệch ≤ 5%: diversity 7/7; S, S+D chỉ khớp ở V5")
    set_cell(t30.rows[idx["Hình 7 – ASP theo đường (vẽ lại)"]].cells[2], "5 đường; OR độc lập 0.91–0.94; Eq. 1 nguyên văn 0.24–0.48")
    set_cell(t30.rows[idx["Hình 7 – ASP theo đường (vẽ lại)"]].cells[3], "Cùng thang đo; không so được từng đường")
    add_row_after(t30, idx["Hình 7 – ASP theo đường (vẽ lại)"],
                  ["Hình 5, 8, 9 (E12)", "IPV, PSV; mạng 400 VM; theo thời gian", "5(a) IPV ≈ m/n; 5(b) lệch; 8 chỉ so tỷ lệ; 9 không làm",
                   "Không tái lập đầy đủ"])

    # ---- 2. Mục mới 6.10 và đổi số mục sau đó
    # chỉ lấy tiêu đề thật: mục lục cũng có dòng bắt đầu bằng chuỗi này
    h_old = next(p for p in d.paragraphs if p.style.name == "Heading 2" and p.text.startswith("6.10 Bảng đối chiếu"))
    anchor = h_old._p
    cap_t, cap_f = find_p(d, "Bảng 20."), find_p(d, "Hình 12.")
    h = d.add_paragraph("6.10 E12 – Tái hiện thêm tổng toàn mạng và các hình còn lại của paper chính", style="Heading 2")
    anchor.addprevious(h._p)
    para(d, anchor, "E11 chưa giải thích được thang đo của AC và ASP. E12 thử lại với các công thức đơn giản và **không chỉnh số cho "
                    "khớp**. Tìm được **AC theo VM = Σ CVSS BS × attack cost**: khớp V5, V7, V8, nhưng V2 lệch −33,9%. Đây là **giả thuyết "
                    "của đề tài**, chọn sau khi dò trên 4 số bài in nên có thể khớp ngẫu nhiên. Bằng chứng hỗ trợ là tổng AC toàn mạng, "
                    "không dùng khi chọn công thức, cũng khớp trong khoảng ±3,4% (Definition 2, chỉ dùng Bảng 1–2). Mã nguồn: "
                    "ai/scripts/12_masud_full_repro.py; chi tiết: docs/tai_lap_E12_day_du.md.")
    n = pd.read_csv(TAB / "e12_network_totals.csv")
    n = n[(n.topology == "Definition 2") & (n["biến thể"] == "Σ BS×cost")]
    rows = []
    for m, lab in (("shuffle", "Shuffle"), ("diversity", "Diversity"), ("redundancy", "Redundancy")):
        g = n[n.MTD == m].set_index("chỉ số")
        fmt = lambda k, dp: f"{g.loc[k, 'E12']:.{dp}f} ({g.loc[k, 'lệch E12 %']:+.1f}%)".replace("-", "−")
        rows.append([lab, f"{g.loc['R', 'bài báo']:.2f}", fmt("R", 2), f"{g.loc['AC', 'bài báo']:.1f}", f"{g.loc['AC', 'E11 cũ']:.1f}", fmt("AC", 1),
                     f"{g.loc['RoC', 'bài báo']:.2f}", f"{g.loc['RoC', 'E11 cũ']:.2f}", fmt("RoC", 2)])
    caption_like(d, anchor, cap_t, "Bảng 21. Tổng toàn mạng trên Definition 2: paper, E11 và E12 (trong ngoặc: lệch so với paper)")
    table(d, anchor, ["MTD trên V5", "R paper", "R E12", "AC paper", "AC E11", "AC E12", "RoC paper", "RoC E11", "RoC E12"], rows,
          [1.9, 1.3, 2.1, 1.3, 1.2, 2.1, 1.2, 1.1, 2.0], font=8.5)
    para(d, anchor, "Số giá trị tổng mạng lệch ≤ 5% tăng từ 1/9 lên **5/9**; tổng R của diversity và redundancy vẫn lệch −13,1% và −16,6%. "
                    "Tìm vét cạn các tập 4 đường có đường ví dụ của bài không cho tập nào khớp đồng thời R_s và AC_s.")
    for b in ["**Hình 6:** AC, RoC nay cùng bậc với bài nhưng khác hình dạng: số điểm lệch ≤ 5% là AR 3, AC 9, RoC 7 trên 35 điểm mỗi chỉ số "
              "(Definition 2); AR 11, AC 2, RoC 3 (Hình 3). Giá trị của bài đọc bằng mắt từ hình.",
              "**Hình 7:** Eq. 1 nguyên văn (tích dịch vụ của V8 lấy bằng 0) cho ASP đường 0.24–0.48, cùng thang đo với bài (0.2–0.43), nhưng diversity "
              "V5 làm ASP tăng, ngược lời bình của bài.",
              "**Hình 5:** IPV ≈ m/n giống hình của bài, nhưng m = 8–10 lấy từ chính hình nên chỉ kiểm tra công thức; PSV ở 5(b) không khớp; 5(c) không làm "
              "vì bài không định nghĩa phép gộp.",
              "**Hình 8:** bài không mô tả mạng 400 VM nên chỉ so tỷ lệ với trước MTD. Riêng diversity không phụ thuộc giả định: AR 0.61 (bài 0.65), AC 1.63 (bài 1.38), "
              "RoA 0.37 (bài 0.48).",
              "**Hình 9:** không làm vì bài không có mô hình theo thời gian, và trục ASP 200–400 trái định nghĩa ASP ∈ [0, 1].",
              "**Điểm không nhất quán trong bài:** mục 4.3 ghi R_d = 163.73, Hình 6 vẽ khoảng 203; AR của diversity V5 khớp Hình 3 còn AC gần Definition 2; "
              "trong Definition 2, V6 là ngõ cụt nên MTD lên V6 không đổi chỉ số, nhưng Hình 6 vẫn vẽ giá trị khác nhau."]:
        para(d, anchor, b, style="List Bullet")
    d.add_picture(str(FIG / "fig_e12_masud_fig6.png"), width=Cm(14.5))
    pic = d.paragraphs[-1]
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    anchor.addprevious(pic._p)
    caption_like(d, anchor, cap_f, "Hình 13. Hình 6 của Masud et al. (2025): giá trị đọc từ hình của bài (trên) và E12 trên Definition 2 (dưới)")
    replace(h_old, "6.10 Bảng đối chiếu", "6.11 Bảng đối chiếu")

    # ---- 3. Đánh lại số bảng, hình phía sau mục mới
    after = False
    for p in d.paragraphs:
        if p._p is h_old._p:
            after = True
            continue
        if not after:
            continue
        m = re.match(r"(Bảng|Hình) (\d+)\.", p.text)
        if m:
            num = int(m[2]) + 1   # mục mới thêm 1 bảng và 1 hình
            replace(p, f"{m[1]} {m[2]}.", f"{m[1]} {num}.")

    # ---- 3b. Mục lục gọn trong 1 trang: chỉ lấy tiêu đề cấp 1–2, bớt khoảng cách dòng
    for el in d.element.body.iter(qn("w:instrText")):
        if "TOC" in (el.text or ""):
            el.text = el.text.replace('"1-3"', '"1-2"')
    for st in d.styles:
        if st.name.lower() in ("toc 1", "toc 2"):
            st.paragraph_format.space_after = Pt(1)
            st.paragraph_format.space_before = Pt(0)
            st.paragraph_format.line_spacing = 1.0
            st.font.size = Pt(12)

    # ---- 4. Để chương 2–8 và tài liệu tham khảo chạy liền, thu hình để giữ trong 30 trang
    for p in d.paragraphs:
        if 'w:type="page"' in p._p.xml and not p.text.strip():
            nxt = p._p.getnext()
            if nxt is not None and nxt.tag.endswith("}p") and not Paragraph(nxt, p._parent).text.startswith(("MỤC LỤC", "Chương 1.")):
                p._p.getparent().remove(p._p)
    for p in list(d.paragraphs):      # dòng trống ngay trước tiêu đề không cần thiết khi đã có khoảng cách của tiêu đề
        nxt = p._p.getnext()
        if (not p.text.strip() and "w:drawing" not in p._p.xml and "w:br" not in p._p.xml and nxt is not None and nxt.tag.endswith("}p")
                and Paragraph(nxt, p._parent).style.name.startswith("Heading")):
            p._p.getparent().remove(p._p)
    if scale != 1:
        for s in d.inline_shapes:
            s.width, s.height = int(s.width * scale), int(s.height * scale)
    d.save(dst)
    print("Đã lưu", dst)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0)
