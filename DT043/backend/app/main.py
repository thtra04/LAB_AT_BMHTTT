"""Backend FastAPI – DT043.

Chạy (từ thư mục DT043):  .venv\\Scripts\\python -m uvicorn backend.app.main:app --port 8000
Mở dashboard:            http://127.0.0.1:8000/
Tài liệu API (Swagger):  http://127.0.0.1:8000/docs
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import settings as S
from .detector import DetectorRegistry
from .mtd import HybridMTD
from .schemas import DetectRequest, DetectResponse, ReplayResponse

sys.path.insert(0, str(S.PROJECT))
from db.repository import Repository  # noqa: E402

STATE: dict = {}


def init_state(deploy_dir=S.DEPLOY_DIR, db_path=S.DB_PATH) -> None:
    repo = Repository(db_path)
    reg = DetectorRegistry(deploy_dir, S.TFLITE_THREADS)
    for name, det in reg.detectors.items():
        m = det.meta
        repo.register_model(name, m["variant"], m["quant_mode"], det.dim, m.get("params", 0), det.size_bytes,
                            det.threshold, det.window_size, det.sha256)
    STATE.update(repo=repo, registry=reg, mtd=HybridMTD(repo, S.MTD_TIME_PERIOD_S))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if "repo" not in STATE:
        init_state()
    yield


app = FastAPI(title="DT043 – IoT botnet detection API", version="1.0", lifespan=lifespan)


def _severity(ratio: float) -> str:
    return "high" if ratio >= 0.5 else "medium" if ratio >= 0.1 else "low"


def _process(device: str, x: np.ndarray, source: str) -> tuple[dict, object]:
    try:
        det = STATE["registry"].get(device)
    except KeyError:
        raise HTTPException(404, f"Không có model cho thiết bị '{device}'") from None
    try:
        res = det.detect(x)
    except ValueError as e:
        raise HTTPException(422, str(e)) from None
    repo = STATE["repo"]
    dev_id = repo.device_id(device)
    model_id = repo.active_model_id(dev_id)
    n_alarm = int(res.window_alarms.sum())
    batch_id = repo.add_batch(dev_id, model_id, source, len(x), int(res.flags.sum()), n_alarm,
                              float(res.mse.max()), float(res.mse.mean()), res.infer_us_per_sample)
    alert_id, mtd_ids = None, []
    if n_alarm > 0:
        ratio = n_alarm / max(len(res.window_alarms), 1)
        alert_id = repo.add_alert(dev_id, batch_id, _severity(ratio), res.first_alarm, ratio)
        mtd_ids = STATE["mtd"].on_alert(device, dev_id, alert_id)
    summary = {"device": device, "batch_id": batch_id, "n_samples": len(x), "n_flagged": int(res.flags.sum()),
               "n_windows": int(len(res.window_alarms)), "n_alarm_windows": n_alarm,
               "threshold": det.threshold, "window_size": det.window_size,
               "infer_us_per_sample": res.infer_us_per_sample, "alert_id": alert_id, "mtd_action_ids": mtd_ids}
    return summary, res


# --------------------------------------------------------------------------- API
@app.get("/api/health")
def health():
    reg = STATE["registry"]
    return {"status": "ok", "models_loaded": len(reg.detectors), "bundle_errors": reg.errors}


@app.get("/api/devices")
def devices():
    return STATE["repo"].list_devices()


@app.post("/api/detect", response_model=DetectResponse)
def detect(req: DetectRequest):
    x = np.asarray(req.features, dtype=np.float64)
    if x.ndim != 2:
        raise HTTPException(422, "features phải là ma trận 2 chiều")
    summary, res = _process(req.device, x, "api")
    return {**summary, "mse": res.mse.tolist(), "flags": res.flags.tolist()}


@app.post("/api/replay/{device}", response_model=ReplayResponse)
def replay(device: str, segment: str = Query("benign", pattern=r"^(benign|gafgyt/\w+|mirai/\w+)$"),
           n: int = Query(2000, ge=10, le=S.MAX_SAMPLES_PER_REQUEST), offset: int = Query(0, ge=0)):
    """Phát lại dữ liệu N-BaIoT công khai (offline) qua bộ phát hiện. Benign chỉ lấy phần TEST (1/3 cuối)."""
    path = S.PROCESSED_DIR / device / (segment.replace("/", "__") + ".parquet")
    if not path.exists():
        raise HTTPException(404, f"Không có dữ liệu {device}/{segment}")
    try:
        cols = STATE["registry"].get(device).meta["feature_columns"]
    except KeyError:
        raise HTTPException(404, f"Không có model cho thiết bị '{device}'") from None
    df = pd.read_parquet(path, columns=cols)
    if segment == "benign":
        df = df.iloc[int(round(len(df) * 2 / 3)) + 500:]
    if offset >= len(df):
        raise HTTPException(422, f"offset vượt quá {len(df)} dòng")
    x = df.iloc[offset:offset + n].to_numpy(np.float64)
    summary, res = _process(device, x, f"replay:{segment}")
    step = max(1, len(res.mse) // 1500)  # giảm số điểm gửi cho FE
    return {**summary, "segment": segment, "offset": offset, "step": step,
            "mse": res.mse[::step].tolist(), "alarms": res.window_alarms[::step].astype(int).tolist()}


@app.get("/api/alerts")
def alerts(status: str | None = Query(None, pattern="^(open|acknowledged)$"), limit: int = Query(100, le=1000)):
    return STATE["repo"].list_alerts(status, limit)


@app.post("/api/alerts/{alert_id}/ack")
def ack(alert_id: int):
    if not STATE["repo"].ack_alert(alert_id):
        raise HTTPException(404, "Không có cảnh báo đang mở với id này")
    return {"ok": True}


@app.get("/api/batches")
def batches(limit: int = Query(50, le=500)):
    return STATE["repo"].list_batches(limit)


@app.get("/api/mtd/actions")
def mtd_actions(limit: int = Query(100, le=1000)):
    return STATE["repo"].list_mtd_actions(limit)


@app.post("/api/mtd/tick")
def mtd_tick():
    repo = STATE["repo"]
    devs = {d["name"]: d["id"] for d in repo.list_devices()}
    return {"created": STATE["mtd"].tick(devs)}


@app.get("/api/experiments")
def experiments():
    f = S.TABLES_DIR / "summary_by_config.csv"
    if f.exists():
        cols = {"config": "Cấu hình", "n_seeds": "Seed", "params": "Tham số", "macro_f1_mean": "macro-F1",
                "macro_f1_ci95": "±KTC95", "tpr_mean": "TPR", "fpr_mean": "FPR", "f1_balanced_mean": "F1 cân bằng",
                "ws_mean": "ws* TB"}
        df = pd.read_csv(f)[list(cols)].rename(columns=cols).round(4)
        return df.replace({np.nan: None}).to_dict(orient="records")
    return STATE["repo"].list_experiments()


@app.get("/")
def index():
    return FileResponse(S.FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=S.FRONTEND_DIR), name="static")
