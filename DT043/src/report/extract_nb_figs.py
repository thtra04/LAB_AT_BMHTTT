"""Lấy hình (output PNG) từ notebook DT043_walkthrough.ipynb để đặt vào slide "Các bước làm bài" (bộ 4'30).

Chạy tại DT043/src:  python report/extract_nb_figs.py
Đầu ra: report/nb_figs/*.png. Hình đánh số theo thứ tự xuất hiện trong notebook (đã chạy, có output);
nếu chạy lại notebook làm đổi số hình thì script báo lỗi để sửa bảng PICK.
"""
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NB = HERE.parent / "DT043_walkthrough.ipynb"
OUT = HERE / "nb_figs"
N_IMAGES = 14
PICK = {  # thứ tự hình trong notebook → tên file (mục notebook)
    1: "eda_dedup_counts.png",      # mục 2: số mẫu sau khử trùng lặp theo thiết bị
    2: "eda_pca_danmini.png",       # mục 2: PCA benign/tấn công – Danmini
    3: "v1_mse_hist_ennio.png",     # mục 4: MSE tái tạo của V1 trên Ennio và ngưỡng tr*
    4: "recall_per_attack.png",     # mục 7: recall theo loại tấn công
    5: "seed_stability.png",        # mục 7: độ ổn định qua 5 seed
    6: "quant_tradeoff.png",        # mục 7: lượng tử hóa – kích thước vs chất lượng
    8: "mtd_hybrid.png",            # mục 8: MTD lai – an ninh vs chi phí
    10: "masud_fig6_rerun.png",     # mục 9.2: chạy lại Hình 6 (Masud 2025)
}


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    imgs = [o["data"]["image/png"] for c in nb["cells"] for o in c.get("outputs", []) if "image/png" in o.get("data", {})]
    if len(imgs) != N_IMAGES:
        raise SystemExit(f"notebook có {len(imgs)} hình, mong đợi {N_IMAGES} – kiểm tra lại bảng PICK")
    OUT.mkdir(exist_ok=True)
    for k, name in PICK.items():
        (OUT / name).write_bytes(base64.b64decode(imgs[k - 1]))
        print("đã ghi", OUT / name)


if __name__ == "__main__":
    main()
