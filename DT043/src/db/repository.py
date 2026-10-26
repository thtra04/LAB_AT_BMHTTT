"""Tầng DB: khởi tạo SQLite và các hàm truy cập dữ liệu (repository) cho backend."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
DEFAULT_DB = Path(__file__).with_name("dt043.sqlite3")

DEVICE_TYPES = {
    "Danmini_Doorbell": "Doorbell",
    "Ecobee_Thermostat": "Thermostat",
    "Ennio_Doorbell": "Doorbell",
    "Philips_B120N10_Baby_Monitor": "Baby monitor",
    "Provision_PT_737E_Security_Camera": "Security camera",
    "Provision_PT_838_Security_Camera": "Security camera",
    "Samsung_SNH_1011_N_Webcam": "Webcam",
    "SimpleHome_XCS7_1002_WHT_Security_Camera": "Security camera",
    "SimpleHome_XCS7_1003_WHT_Security_Camera": "Security camera",
}
NO_MIRAI = {"Ennio_Doorbell", "Samsung_SNH_1011_N_Webcam"}


class Repository:
    def __init__(self, path: str | Path = DEFAULT_DB):
        self.path = str(path)
        with self.conn() as c:
            c.executescript(SCHEMA.read_text(encoding="utf-8"))

    @contextmanager
    def conn(self):
        c = sqlite3.connect(self.path)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys = ON")
        try:
            yield c
            c.commit()
        finally:
            c.close()

    # ------------------------------------------------------------------ devices & models
    def upsert_device(self, name: str) -> int:
        with self.conn() as c:
            c.execute("INSERT OR IGNORE INTO devices(name, device_type, has_mirai) VALUES (?,?,?)",
                      (name, DEVICE_TYPES.get(name, "Unknown"), int(name not in NO_MIRAI)))
            return c.execute("SELECT id FROM devices WHERE name=?", (name,)).fetchone()["id"]

    def register_model(self, device: str, variant: str, quant_mode: str, input_dim: int, params: int,
                       size_bytes: int, threshold: float, window_size: int, sha256: str) -> int:
        dev_id = self.upsert_device(device)
        with self.conn() as c:
            row = c.execute("SELECT id FROM models WHERE device_id=? AND sha256=? AND is_active=1",
                            (dev_id, sha256)).fetchone()
            if row:
                return row["id"]
            c.execute("UPDATE models SET is_active=0 WHERE device_id=?", (dev_id,))
            cur = c.execute(
                "INSERT INTO models(device_id, variant, quant_mode, input_dim, params, size_bytes, threshold,"
                " window_size, sha256) VALUES (?,?,?,?,?,?,?,?,?)",
                (dev_id, variant, quant_mode, input_dim, params, size_bytes, threshold, window_size, sha256))
            return cur.lastrowid

    def list_devices(self) -> list[dict]:
        with self.conn() as c:
            rows = c.execute(
                "SELECT d.id, d.name, d.device_type, d.has_mirai, m.id AS model_id, m.variant, m.quant_mode,"
                " m.size_bytes, m.threshold, m.window_size, m.params,"
                " (SELECT COUNT(*) FROM alerts a WHERE a.device_id=d.id AND a.status='open') AS open_alerts"
                " FROM devices d LEFT JOIN models m ON m.device_id=d.id AND m.is_active=1 ORDER BY d.name"
            ).fetchall()
        return [dict(r) for r in rows]

    def device_id(self, name: str) -> int | None:
        with self.conn() as c:
            r = c.execute("SELECT id FROM devices WHERE name=?", (name,)).fetchone()
        return r["id"] if r else None

    def active_model_id(self, device_id: int) -> int | None:
        with self.conn() as c:
            r = c.execute("SELECT id FROM models WHERE device_id=? AND is_active=1", (device_id,)).fetchone()
        return r["id"] if r else None

    # ------------------------------------------------------------------ detection
    def add_batch(self, device_id: int, model_id: int, source: str, n_samples: int, n_flagged: int,
                  n_alarm_windows: int, max_mse: float, mean_mse: float, infer_us: float) -> int:
        with self.conn() as c:
            return c.execute(
                "INSERT INTO detection_batches(device_id, model_id, source, n_samples, n_flagged,"
                " n_alarm_windows, max_mse, mean_mse, infer_us_per_sample) VALUES (?,?,?,?,?,?,?,?,?)",
                (device_id, model_id, source, n_samples, n_flagged, n_alarm_windows, max_mse, mean_mse,
                 infer_us)).lastrowid

    def add_alert(self, device_id: int, batch_id: int, severity: str, first_sample: int, ratio: float) -> int:
        with self.conn() as c:
            return c.execute("INSERT INTO alerts(device_id, batch_id, severity, first_sample, alarm_ratio)"
                             " VALUES (?,?,?,?,?)", (device_id, batch_id, severity, first_sample, ratio)).lastrowid

    def list_alerts(self, status: str | None = None, limit: int = 100) -> list[dict]:
        q = ("SELECT a.*, d.name AS device, b.source FROM alerts a JOIN devices d ON d.id=a.device_id"
             " JOIN detection_batches b ON b.id=a.batch_id")
        args: tuple = ()
        if status:
            q += " WHERE a.status=?"
            args = (status,)
        q += " ORDER BY a.id DESC LIMIT ?"
        with self.conn() as c:
            return [dict(r) for r in c.execute(q, args + (limit,)).fetchall()]

    def ack_alert(self, alert_id: int) -> bool:
        with self.conn() as c:
            return c.execute("UPDATE alerts SET status='acknowledged' WHERE id=? AND status='open'",
                             (alert_id,)).rowcount == 1

    def list_batches(self, limit: int = 50) -> list[dict]:
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT b.*, d.name AS device FROM detection_batches b JOIN devices d ON d.id=b.device_id"
                " ORDER BY b.id DESC LIMIT ?", (limit,)).fetchall()]

    # ------------------------------------------------------------------ MTD
    def add_mtd_action(self, device_id: int, technique: str, trigger: str, detail: str,
                       alert_id: int | None = None) -> int:
        with self.conn() as c:
            return c.execute("INSERT INTO mtd_actions(device_id, alert_id, technique, trigger_kind, detail)"
                             " VALUES (?,?,?,?,?)", (device_id, alert_id, technique, trigger, detail)).lastrowid

    def list_mtd_actions(self, limit: int = 100) -> list[dict]:
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT m.*, d.name AS device FROM mtd_actions m JOIN devices d ON d.id=m.device_id"
                " ORDER BY m.id DESC LIMIT ?", (limit,)).fetchall()]

    # ------------------------------------------------------------------ experiments
    def upsert_experiment(self, exp: str, variant: str, device: str, n_seeds: int, f1_mean: float,
                          f1_std: float, tpr: float, fpr: float) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO experiment_results(exp, variant, device, n_seeds, macro_f1_mean,"
                      " macro_f1_std, tpr_mean, fpr_mean) VALUES (?,?,?,?,?,?,?,?)"
                      " ON CONFLICT(exp, variant, device) DO UPDATE SET n_seeds=excluded.n_seeds,"
                      " macro_f1_mean=excluded.macro_f1_mean, macro_f1_std=excluded.macro_f1_std,"
                      " tpr_mean=excluded.tpr_mean, fpr_mean=excluded.fpr_mean",
                      (exp, variant, device, n_seeds, f1_mean, f1_std, tpr, fpr))

    def list_experiments(self) -> list[dict]:
        with self.conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT * FROM experiment_results ORDER BY exp, device").fetchall()]
