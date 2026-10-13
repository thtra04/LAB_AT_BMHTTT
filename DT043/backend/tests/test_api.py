"""Test tầng BE + DB: API phát hiện, replay, cảnh báo, MTD, kiểm tra đầu vào và gói model bị sửa."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "ai" / "src"))
pytest.importorskip("tensorflow")
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from nbaiot.data import COLUMNS  # noqa: E402

DEV = "Fake_Device"


def _make_bundle(root: Path) -> Path:
    """Gói triển khai nhỏ: AE 115-16-4-16-115 int8 huấn luyện trên dữ liệu ~N(0,1)."""
    import keras

    from nbaiot.models import build_autoencoder
    from nbaiot.quantize import to_tflite

    keras.utils.set_random_seed(0)
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, (3000, 115)).astype(np.float32)
    m = build_autoencoder(115, [16, 4])
    m.compile("adam", "mse")
    m.fit(x, x, epochs=3, batch_size=128, verbose=0)
    blob = to_tflite(m, "int8", rep_data=x)
    b = root / "deploy" / DEV
    b.mkdir(parents=True)
    (b / "model.tflite").write_bytes(blob)
    (b / "scaler.json").write_text(json.dumps({"device": DEV, "mean": [0.0] * 115, "std": [1.0] * 115}))
    mse = np.mean((m.predict(x, verbose=0) - x) ** 2, axis=1)
    (b / "meta.json").write_text(json.dumps({
        "device": DEV, "variant": "V-test", "quant_mode": "int8", "input_dim": 115, "params": 0,
        "feature_columns": COLUMNS, "threshold": float(mse.mean() + 3 * mse.std()), "window_size": 5,
        "size_bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}))
    proc = root / "processed" / DEV
    proc.mkdir(parents=True)
    pd.DataFrame(rng.normal(0, 1, (3000, 115)), columns=COLUMNS).astype(np.float32).to_parquet(proc / "benign.parquet")
    pd.DataFrame(rng.normal(30, 5, (500, 115)), columns=COLUMNS).astype(np.float32).to_parquet(proc / "mirai__syn.parquet")
    return b


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    root = tmp_path_factory.mktemp("be")
    _make_bundle(root)
    from backend.app import main, settings

    settings.PROCESSED_DIR = root / "processed"
    main.S.PROCESSED_DIR = root / "processed"
    main.STATE.clear()
    main.init_state(deploy_dir=root / "deploy", db_path=root / "test.sqlite3")
    with TestClient(main.app) as c:
        yield c


def test_health_and_devices(client):
    h = client.get("/api/health").json()
    assert h["models_loaded"] == 1 and h["bundle_errors"] == {}
    devs = client.get("/api/devices").json()
    assert devs[0]["name"] == DEV and devs[0]["quant_mode"] == "int8"


def test_benign_replay_no_alert(client):
    r = client.post(f"/api/replay/{DEV}", params={"segment": "benign", "n": 500})
    assert r.status_code == 200
    assert r.json()["alert_id"] is None


def test_attack_replay_creates_alert_and_mtd(client):
    r = client.post(f"/api/replay/{DEV}", params={"segment": "mirai/syn", "n": 300}).json()
    assert r["n_alarm_windows"] > 0 and r["alert_id"] is not None
    assert len(r["mtd_action_ids"]) == 2  # shuffle + diversity
    alerts = client.get("/api/alerts", params={"status": "open"}).json()
    assert any(a["id"] == r["alert_id"] for a in alerts)
    assert client.post(f"/api/alerts/{r['alert_id']}/ack").status_code == 200
    assert client.post(f"/api/alerts/{r['alert_id']}/ack").status_code == 404  # không xác nhận 2 lần
    kinds = {(m["technique"], m["trigger_kind"]) for m in client.get("/api/mtd/actions").json()}
    assert ("shuffle", "event") in kinds and ("diversity", "event") in kinds


def test_detect_endpoint(client):
    x = np.random.default_rng(1).normal(0, 1, (20, 115)).tolist()
    r = client.post("/api/detect", json={"device": DEV, "features": x})
    assert r.status_code == 200 and len(r.json()["mse"]) == 20


def test_time_based_mtd_tick(client):
    assert isinstance(client.post("/api/mtd/tick").json()["created"], list)


# ------------------------------------------------------------------ negative
def test_unknown_device_404(client):
    assert client.post("/api/detect", json={"device": "Nope", "features": [[0.0] * 115]}).status_code == 404
    assert client.post("/api/replay/Nope").status_code == 404


def test_wrong_dimension_422(client):
    assert client.post("/api/detect", json={"device": DEV, "features": [[0.0] * 23]}).status_code == 422


def test_ragged_rows_422(client):
    r = client.post("/api/detect", json={"device": DEV, "features": [[0.0] * 115, [0.0] * 114]})
    assert r.status_code == 422


def test_bad_segment_and_device_name_422(client):
    assert client.post(f"/api/replay/{DEV}", params={"segment": "../../etc"}).status_code == 422
    assert client.post("/api/detect", json={"device": "../x", "features": [[0.0] * 115]}).status_code == 422


def test_oversized_request_rejected(client):
    assert client.post(f"/api/replay/{DEV}", params={"n": 10**6}).status_code == 422


def test_tampered_bundle_rejected(tmp_path):
    from backend.app.detector import BundleError, DeviceDetector

    b = _make_bundle(tmp_path)
    blob = bytearray((b / "model.tflite").read_bytes())
    blob[-10] ^= 0xFF
    (b / "model.tflite").write_bytes(bytes(blob))
    with pytest.raises(BundleError):
        DeviceDetector(b)


def test_repository_alert_flow(tmp_path):
    from db.repository import Repository

    repo = Repository(tmp_path / "r.sqlite3")
    mid = repo.register_model("Danmini_Doorbell", "V1", "int8", 115, 8059, 15000, 0.5, 20, "abc")
    assert repo.register_model("Danmini_Doorbell", "V1", "int8", 115, 8059, 15000, 0.5, 20, "abc") == mid
    dev = repo.device_id("Danmini_Doorbell")
    bid = repo.add_batch(dev, mid, "api", 100, 10, 3, 9.0, 1.0, 2.5)
    aid = repo.add_alert(dev, bid, "low", 5, 0.03)
    assert repo.list_alerts("open")[0]["id"] == aid
    assert repo.list_devices()[0]["open_alerts"] == 1
