"""Sinh DT043/DT043_walkthrough.ipynb rồi chạy toàn bộ bằng nbclient (kernel = .venv).

Chạy tại thư mục DT043:  .venv\Scripts\python report/build_notebook.py DT043_walkthrough.ipynb --execute
Cần thêm: .venv\Scripts\python -m pip install ipykernel nbformat nbclient
"""
import sys
from pathlib import Path

import nbformat as nbf

OUT = Path(sys.argv[1])
cells = []


def md(s):
    cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))


def code(s):
    cells.append(nbf.v4.new_code_cell(s.strip("\n")))


md("""
# DT043 – Phát hiện botnet IoT bằng autoencoder nhẹ (notebook trình bày)

**Hoàng Thanh Trà · MSSV 1150080120 · 11CNPM2**

Notebook này đi lại toàn bộ quy trình của đề tài **bằng đúng mã nguồn trong `ai/src/nbaiot`** (không viết lại thuật toán):

1. Môi trường và dataset (chứng minh đúng bộ N-BaIoT được giao)
2. Chất lượng dữ liệu và EDA
3. Chia dữ liệu chống rò rỉ
4. Huấn luyện thử V1 (AE nhẹ) cho một thiết bị, chọn ngưỡng `tr*` và cửa sổ `ws*`
5. Lượng tử hóa int8 + hiệu chỉnh ngưỡng
6. Edge benchmark rút gọn
7. Kết quả chính thức của ma trận 468 lần chạy, kiểm định, đối chiếu tiêu chí
8. MTD
9. Demo API backend

**Cách chạy:** mở bằng VS Code/Jupyter, chọn kernel `DT043/.venv` (Python 3.11), chạy lần lượt từ trên xuống.
Phần 4–6 chạy thật trên dữ liệu (≈ 1–3 phút); phần 7 đọc kết quả đã lưu trong `results/` của ma trận thí nghiệm đầy đủ (chạy lại mất ~4–5 giờ bằng `ai/scripts/04_run_matrix.py`).
""")

code(r"""
import json, os, sys, time, importlib.util
from pathlib import Path

ROOT = Path.cwd()
while not (ROOT / "ai" / "src" / "nbaiot").exists():
    ROOT = ROOT.parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "ai" / "src"))
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
import pandas as pd
from IPython.display import Image, display, Markdown
pd.set_option("display.max_columns", 30, "display.width", 160)
print("Thư mục dự án:", ROOT)
""")

md("## 1. Môi trường và dataset")
code(r"""
env = json.loads((ROOT / "results/env_info.json").read_text(encoding="utf-8"))
pd.Series({k: env[k] for k in env if not isinstance(env[k], (dict, list))}).to_frame("giá trị")
""")
md("""
### 1.1 Chứng minh dùng đúng bộ N-BaIoT trong đề
Thông tin tải (nguồn, DOI, giấy phép, ngày tải, SHA-256 file zip) được ghi lúc tải bằng `ai/scripts/01_download.py`.
""")
code(r"""
info = json.loads((ROOT / "data/DOWNLOAD_INFO.json").read_text(encoding="utf-8"))
pd.Series({k: info[k] for k in ["source_page", "url", "doi", "license", "downloaded_at_utc", "zip_bytes", "zip_sha256", "n_files"]}).to_frame("giá trị")
""")
md("Kiểm tra lại SHA-256 của cả 107 file CSV so với `data/MANIFEST.sha256` (dùng chính hàm của `ai/scripts/02_verify_manifest.py`, ≈ 1 phút):")
code(r"""
spec = importlib.util.spec_from_file_location("verify_manifest", ROOT / "ai/scripts/02_verify_manifest.py")
vm = importlib.util.module_from_spec(spec); spec.loader.exec_module(vm)
t0 = time.time()
bad = vm.verify(ROOT / "data")
n_files = sum(1 for l in (ROOT / "data/MANIFEST.sha256").read_text(encoding="utf-8").splitlines() if l.strip())
print(f"{n_files} file trong manifest – sai/thiếu: {len(bad)} – {time.time() - t0:.0f} s")
print("Manifest OK – mọi file khớp SHA-256." if not bad else bad[:5])
""")

md("## 2. Chất lượng dữ liệu và EDA")
code(r"""
fs = pd.read_csv(ROOT / "results/data_quality/file_stats.csv")
ds = pd.read_csv(ROOT / "results/data_quality/device_summary.csv")
print(f"Tổng số dòng gốc : {fs.rows_raw.sum():,}  (UCI công bố 7,062,606)")
print(f"Trùng lặp chính xác: {fs.exact_duplicates.sum():,} ({fs.exact_duplicates.sum() / fs.rows_raw.sum():.1%})")
print(f"Sau khử trùng    : {fs.rows_dedup.sum():,}")
print(f"NaN / Inf        : {fs.nan.sum()} / {fs.inf.sum()}")
print(f"Tỷ lệ tấn công : benign = {ds.rows_dedup_attack.sum() / ds.rows_dedup_benign.sum():.1f} : 1  → không dùng Accuracy")
ds
""")
code(r"""
display(fs.sort_values("dup_ratio", ascending=False).head(6)[["device", "segment", "rows_raw", "exact_duplicates", "dup_ratio", "rows_dedup"]])
display(Image(filename=str(ROOT / "results/figures/eda_class_counts.png"), width=850))
display(Image(filename=str(ROOT / "results/figures/eda_pca_danmini.png"), width=650))
""")

md("""
## 3. Chia dữ liệu chống rò rỉ
Benign của từng thiết bị được chia **theo thứ tự thời gian** 1/3 DStrn – 1/3 DSopt – 1/3 test, bỏ **500 dòng đệm** ở mỗi ranh giới,
scaler chỉ fit trên DStrn và loại khỏi test các dòng trùng hash với DStrn/DSopt. Cấu hình lấy từ `ai/configs/base.yaml` + `exp/E4_light.yaml` (V1).
""")
code(r"""
from nbaiot.config import load_config
from nbaiot.split import chronological_split
from nbaiot.pipeline import load_split, make_and_train, decide, full_eval
from nbaiot.seed import set_seed

DEVICE, SEED = "Ennio_Doorbell", 42   # thiết bị có lỗi chính (flood tcp/udp); đổi tên để thử thiết bị khác
cfg = load_config("E4_light")
print("split:", cfg["split"]); print("model:", cfg["model"]); print("threshold:", cfg["threshold"])

idx = chronological_split(1000, cfg["split"]["fractions"], purge_gap=50)   # ví dụ nhỏ để thấy vùng đệm
print("Ví dụ 1000 dòng, đệm 50 → train", idx.train[[0, -1]], "opt", idx.opt[[0, -1]], "test", idx.test[[0, -1]])
""")
code(r"""
t0 = time.time()
set_seed(SEED, cfg.get("threads"))
dd = load_split(cfg, DEVICE, SEED)
print(f"Nạp + chia + chuẩn hóa: {time.time() - t0:.1f} s")
print({k: dd.info[k] for k in ("n_benign", "n_train", "n_opt", "n_test_benign_before")})
print("Dòng trùng bị loại khỏi test:", dd.info["overlap_removed"])
pd.Series(dd.info["n_test"], name="số dòng test").to_frame().T
""")

md("## 4. Huấn luyện V1 (AE nhẹ 115-32-8) và chọn ngưỡng")
code(r"""
from nbaiot.models import layer_dims, count_params
dims_v1, dims_b0 = layer_dims(115, cfg["model"]["hidden"]), layer_dims(115, "meidan")
print("V1:", dims_v1, f"– {count_params(dims_v1):,} tham số")
print("B0 (Meidan):", dims_b0, f"– {count_params(dims_b0):,} tham số  → V1 = {count_params(dims_v1) / count_params(dims_b0):.1%}")

t0 = time.time()
scorer, model, tinfo = make_and_train(cfg, dd.train, dd.opt, SEED)
print(f"Huấn luyện: {time.time() - t0:.1f} s, {tinfo['epochs_run']} epoch (tốt nhất: {tinfo['best_epoch']})")
""")
code(r"""
opt_s = scorer(dd.opt)
test_s = {k: scorer(v) for k, v in dd.test.items()}
thr, ws, opt_fpr = decide(cfg, opt_s)
print(f"tr* = mean + std của MSE trên DSopt = {thr:.4f}  |  ws* = {ws} (FPR trên DSopt = {opt_fpr})")
res = full_eval({**cfg, "ablation_grid": False}, opt_s, test_s, thr, ws)
w = res["window"]
print(f"Mức cửa sổ – macro-F1 {w['macro_f1']:.4f} | TPR {w['tpr']:.4f} | FPR {w['fpr']:.5f} | ROC-AUC {res['roc_auc']:.4f}")
for k in ("gafgyt/tcp", "gafgyt/udp"):
    if k in test_s:
        print(f"{k}: {np.mean(test_s[k] > thr):.2%} mẫu vượt ngưỡng, MSE trung vị {np.median(test_s[k]):.3f} so với tr* {thr:.3f}")
pd.Series(w["recall_per_attack"], name="recall").round(4).to_frame()
""")
code(r"""
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(9, 3.5))
bins = np.logspace(-4, 7, 120)
ax.hist(test_s["benign"], bins=bins, alpha=.6, label="benign (test)", density=True)
for k in ("gafgyt/scan", "gafgyt/tcp", "gafgyt/udp"):
    if k in test_s: ax.hist(test_s[k], bins=bins, alpha=.5, label=k, density=True)
ax.axvline(thr, color="r", ls="--", label="tr*")
ax.set_xscale("log"); ax.set_xlabel("MSE tái tạo (log)"); ax.legend(); ax.set_title(f"{DEVICE} – V1, seed {SEED}")
plt.show()
""")
md("""
Nhận xét: với Ennio, gafgyt combo/junk/scan nằm hẳn trên ngưỡng, còn **gafgyt/tcp và gafgyt/udp** (flood giả mạo nguồn) gần như toàn bộ nằm dưới ngưỡng nên recall ≈ 0 – đây là lỗi chính được phân tích trong báo cáo (Ennio không có dữ liệu Mirai).
Đây là kết quả **1 thiết bị × 1 seed**; ở thiết bị khác (ví dụ Danmini) tcp/udp lại được bắt, nên kết luận phải dựa trên trung bình 9 thiết bị × 5 seed ở phần 7.
""")

md("## 5. Lượng tử hóa int8 + hiệu chỉnh ngưỡng")
code(r"""
from nbaiot.quantize import to_tflite, TFLiteRunner
from nbaiot.metrics import evaluate_segments

blob32 = to_tflite(model, "fp32")
blob8 = to_tflite(model, "int8", rep_data=dd.train, seed=SEED)
r8 = TFLiteRunner(blob8, num_threads=1)
test8 = {k: r8.mse(v) for k, v in dd.test.items()}
keep = evaluate_segments(test8, thr, ws)
thr8, ws8, _ = decide(cfg, r8.mse(dd.opt))
recal = evaluate_segments(test8, thr8, ws8)
pd.DataFrame({
    "fp32": {"KB": len(blob32) / 1024, "tr*": thr, "ws*": ws, "macro_f1": w["macro_f1"], "TPR": w["tpr"], "FPR": w["fpr"]},
    "int8 giữ ngưỡng fp32": {"KB": len(blob8) / 1024, "tr*": thr, "ws*": ws, "macro_f1": keep["macro_f1"], "TPR": keep["tpr"], "FPR": keep["fpr"]},
    "int8 hiệu chỉnh trên DSopt": {"KB": len(blob8) / 1024, "tr*": thr8, "ws*": ws8, "macro_f1": recal["macro_f1"], "TPR": recal["tpr"], "FPR": recal["fpr"]},
}).T.round(5)
""")

md("""
### 5.1 Đối chiếu với lần chạy chính thức và gói đã triển khai (cùng seed 42)
Nếu quy trình tái lập được, ngưỡng/cửa sổ và metric chạy lại trong notebook phải trùng (hoặc rất sát) với `results/raw/E4_light/<thiết bị>/seed=42/metrics.json`
và `artifacts/deploy/<thiết bị>/meta.json` (gói backend đang dùng).
""")
code(r"""
off_run = json.loads((ROOT / f"results/raw/E4_light/{DEVICE}/seed=42/metrics.json").read_text(encoding="utf-8"))["result"]
meta = json.loads((ROOT / f"artifacts/deploy/{DEVICE}/meta.json").read_text(encoding="utf-8"))
pd.DataFrame({
    "notebook (chạy lại)": {"tr* fp32": thr, "ws* fp32": ws, "macro_f1 fp32": w["macro_f1"], "TPR fp32": w["tpr"], "FPR fp32": w["fpr"],
                             "tr* int8": thr8, "ws* int8": ws8, "KB int8": len(blob8) / 1024},
    "lần chạy chính thức": {"tr* fp32": off_run["thr"], "ws* fp32": off_run["ws"], "macro_f1 fp32": off_run["window"]["macro_f1"],
                            "TPR fp32": off_run["window"]["tpr"], "FPR fp32": off_run["window"]["fpr"]},
    "gói triển khai": {"tr* int8": meta["threshold"], "ws* int8": meta["window_size"], "KB int8": meta["size_bytes"] / 1024},
}).round(4)
""")
md("""
## 6. Edge benchmark rút gọn
Bản đầy đủ (`ai/scripts/05_bench_edge.py`) ghim 1 luồng vào một lõi E-core, 10.000 lần × 5 lượt trong process riêng.
Ở đây chạy rút gọn 3.000 lần × 3 lượt, batch 1, 1 luồng, không ghim lõi, nên số đo chỉ để minh họa. Energy proxy (CPU-time × 55 W / 14 lõi) cần nhiều lần gọi vì đồng hồ CPU của Windows chỉ chính xác ~15,6 ms, nên chỉ lấy từ bảng chính thức bên dưới.
""")
code(r"""
from nbaiot.bench import bench_tflite
x = dd.test["benign"][:5000].astype(np.float32)
rows = {}
for name, blob in (("V1 fp32", blob32), ("V1 int8", blob8)):
    b = bench_tflite(blob, x, threads=1, batch=1, n_iter=3000, warmup=200, repeats=3)
    rows[name] = {"KB": len(blob) / 1024, "p50_us": b["p50_us"], "p95_us": b["p95_us"], "mẫu/s": b["throughput_samples_s"],
                  "RAM tăng (MB)": b["rss_delta_mb"]}
pd.DataFrame(rows).T.round(2)
""")
code(r"""
deck = json.loads((ROOT / "report/deck_data.json").read_text(encoding="utf-8"))
off = pd.DataFrame(deck["edge"]).T[["size_kb", "p50_us", "p95_us", "throughput_samples_s", "rss_delta_mb", "energy_proxy_uJ"]]
display(Markdown("**Kết quả chính thức** (ghim E-core, P1 = 1 luồng batch 1; P0 = 20 luồng):"))
off.loc[[i for i in off.index if i.startswith("V1") or i.startswith("B0_fp32")]].astype(float).round(2)
""")

md("## 7. Kết quả chính thức của ma trận thí nghiệm (468 lần chạy)")
code(r"""
s = pd.read_csv(ROOT / "results/tables/summary_by_config.csv")
s[["config", "n_seeds", "n_runs", "params", "macro_f1_mean", "macro_f1_ci95", "tpr_mean", "fpr_mean", "f1_balanced_mean"]].round(4)
""")
code(r"""
display(pd.read_csv(ROOT / "results/tables/recall_groups.csv", header=[0, 1], index_col=0).round(4))
display(Image(filename=str(ROOT / "results/figures/fig_recall_per_attack.png"), width=850))
""")
code(r"""
st = pd.read_csv(ROOT / "results/tables/stat_tests.csv")
st[["test", "metric", "n", "mean_diff", "wins", "p", "p_holm"]].round(4)
""")
code(r"""
display(Image(filename=str(ROOT / "results/figures/fig_seed_stability.png"), width=800))
display(Image(filename=str(ROOT / "results/figures/fig_quantization_tradeoff.png"), width=800))
""")
md("### Đối chiếu tiêu chí đã chốt trước (không chỉnh sau khi có kết quả)")
code(r"""
pd.read_csv(ROOT / "results/tables/criteria_check.csv")
""")

md("## 8. Moving Target Defence (mô phỏng HARM rút gọn)")
code(r"""
display(pd.read_csv(ROOT / "results/tables/mtd_harm_policies.csv").round(4))
display(Image(filename=str(ROOT / "results/figures/fig_mtd_harm.png"), width=700))
display(Image(filename=str(ROOT / "results/figures/fig_mtd_hybrid_tradeoff.png"), width=700))
""")

md("""
## 9. Demo API backend (FastAPI + SQLite + gói triển khai V1 int8)
Dùng CSDL tạm để không ghi vào `db/dt043.sqlite3`. Dashboard đầy đủ: `.venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000` rồi mở http://127.0.0.1:8000/.
""")
code(r"""
import tempfile
os.environ["DT043_DB"] = str(Path(tempfile.mkdtemp()) / "nb_demo.sqlite3")
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient
from backend.app.main import app

with TestClient(app) as c:
    print(c.get("/api/health").json())
    rows = []
    for dev, seg in [("Danmini_Doorbell", "mirai/syn"), ("Ennio_Doorbell", "benign"), ("Ennio_Doorbell", "gafgyt/tcp")]:
        r = c.post(f"/api/replay/{dev}?segment={seg}&n=2000&offset=0").json()
        rows.append({"thiết bị": dev, "segment": seg, "mẫu": r["n_samples"], "vượt ngưỡng": r["n_flagged"],
                     "cửa sổ cảnh báo": f"{r['n_alarm_windows']}/{r['n_windows']}", "µs/mẫu": round(r["infer_us_per_sample"], 2),
                     "cảnh báo": r["alert_id"] is not None})
    display(pd.DataFrame(rows))
    display(pd.DataFrame(c.get("/api/mtd/actions").json()))
""")

md("""
## 10. Kết luận
- AE per-device bắt gần tuyệt đối 8/10 loại tấn công với FPR rất thấp (B0 0,0025); bỏ sót flood tcp/udp giả mạo nguồn của BASHLITE.
- V1 int8 ≈ 15 KB, vài µs/mẫu trên 1 lõi → khả thi cho edge (RQ5 đạt); RQ1–RQ4 không đạt và được giữ nguyên tiêu chí.
- Kết quả dao động theo seed → cần nhiều lần chạy và kiểm định; MTD kết hợp shuffle + diversity cho ASP thấp nhất, MTD lai dùng cảnh báo AE giảm thời gian lộ diện.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata={
    "kernelspec": {"name": "python3", "display_name": "Python 3 (DT043 .venv)", "language": "python"},
    "language_info": {"name": "python"}})
nbf.write(nb, OUT)
print("đã ghi", OUT)

if "--execute" in sys.argv:
    from nbclient import NotebookClient
    nb = nbf.read(OUT, as_version=4)
    NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(OUT.parent)}}).execute()
    nbf.write(nb, OUT)
    print("đã chạy xong và lưu output")
