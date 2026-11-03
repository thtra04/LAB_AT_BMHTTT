"""Cắt hình/bảng từ PDF của hai bài báo để đưa vào slide phân tích bài báo.

Chạy:  python report/extract_paper_figs.py
Đầu vào: ../tailieu/docs/báo/*.pdf · Đầu ra: report/paper_figs/*.png (220 dpi)
"""
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
PAPERS = HERE.parent.parent / "tailieu" / "docs" / "báo"
OUT = HERE / "paper_figs"
MASUD = PAPERS / "Vulnerability defence using hybrid moving target defence in Internet of.pdf"
MEIDAN = PAPERS / "N-BaIoT Network-based detection of IoT botnet attacks using deep autoencoders.pdf"

# (file PDF, trang, vùng cắt theo điểm PDF, tên ảnh)
CROPS = [
    (MASUD, 5, (54, 52, 272, 218), "masud_fig1"),                 # Fig. 1 – 4 host, 8 VM (bản dịch)
    (MASUD, 6, (93, 345, 502, 529), "masud_fig2"),                # Fig. 2 – khung vận hành MTD (bản dịch)
    (MASUD, 11, (92, 50, 504, 276), "masud_fig4"),                # Fig. 4 – di trú VM (bản dịch)
    (MASUD, 12, (61, 52, 266, 516), "masud_fig5"),                # Fig. 5 – IPV, PSV (bản dịch)
    (MASUD, 15, (75, 164, 252, 387), "masud_fig8"),               # Fig. 8 – đám mây lớn (bản dịch)
    (MASUD, 16, (70, 53, 526, 255), "masud_fig9"),                # Fig. 9 – chỉ số theo thời gian (bản dịch)
    (MASUD, 8, (316, 52, 548, 226), "masud_fig3_tharm"),          # Fig. 3 – tầng trên/dưới của THARM
    (MASUD, 14, (70, 52, 525, 337), "masud_fig6_metrics"),        # Fig. 6 – AR, AC, RoC sau MTD
    (MASUD, 14, (52, 368, 275, 520), "masud_fig7_asp"),          # Fig. 7 – ASP từng đường trước/sau diversity
    (MEIDAN, 6, (44, 40, 568, 234), "meidan_fig2_results"),       # Fig. 2 (a, b) – độ chính xác, thời gian phát hiện
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for pdf, page, clip, name in CROPS:
        with pymupdf.open(pdf) as doc:
            pix = doc[page - 1].get_pixmap(dpi=220, clip=pymupdf.Rect(*clip))
        pix.save(OUT / f"{name}.png")
        print(f"{name}.png  {pix.width}x{pix.height}")


if __name__ == "__main__":
    main()
