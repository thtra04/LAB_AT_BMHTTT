-- DT043 – CSDL vận hành của hệ thống phát hiện botnet IoT (SQLite)
-- Tầng DB chỉ lưu metadata + kết quả suy luận; KHÔNG lưu dữ liệu thô N-BaIoT.
PRAGMA foreign_keys = ON;

-- Thiết bị IoT được giám sát (9 thiết bị của N-BaIoT)
CREATE TABLE IF NOT EXISTS devices (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    device_type   TEXT NOT NULL,
    has_mirai     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Model đã triển khai cho từng thiết bị (gói do tầng AI xuất ra: artifacts/deploy/<device>/)
CREATE TABLE IF NOT EXISTS models (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id     INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    variant       TEXT NOT NULL,            -- B0 | V1 | V2
    quant_mode    TEXT NOT NULL,            -- fp32 | fp16 | dyn | int8
    input_dim     INTEGER NOT NULL,
    params        INTEGER,
    size_bytes    INTEGER NOT NULL,
    threshold     REAL NOT NULL,            -- tr* (đã hiệu chỉnh cho model lượng tử)
    window_size   INTEGER NOT NULL,         -- ws*
    sha256        TEXT NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_models_device ON models(device_id, is_active);

-- Mỗi lô dữ liệu gửi tới API phát hiện (detect hoặc replay)
CREATE TABLE IF NOT EXISTS detection_batches (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id       INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    model_id        INTEGER NOT NULL REFERENCES models(id),
    source          TEXT NOT NULL,          -- api | replay:<segment>
    n_samples       INTEGER NOT NULL,
    n_flagged       INTEGER NOT NULL,       -- số mẫu có MSE > tr*
    n_alarm_windows INTEGER NOT NULL,       -- số cửa sổ majority vote dương
    max_mse         REAL NOT NULL,
    mean_mse        REAL NOT NULL,
    infer_us_per_sample REAL NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_batches_device ON detection_batches(device_id, created_at);

-- Cảnh báo sinh ra khi có cửa sổ majority vote dương
CREATE TABLE IF NOT EXISTS alerts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id     INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    batch_id      INTEGER NOT NULL REFERENCES detection_batches(id) ON DELETE CASCADE,
    severity      TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    first_sample  INTEGER NOT NULL,         -- vị trí mẫu đầu tiên làm cửa sổ dương
    alarm_ratio   REAL NOT NULL,            -- tỷ lệ cửa sổ dương trong lô
    status        TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'acknowledged')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_alerts_status ON alerts(status, created_at);

-- Hành động MTD (mô phỏng): time-based hoặc event-based (kích hoạt bởi cảnh báo AE)
CREATE TABLE IF NOT EXISTS mtd_actions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id     INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    alert_id      INTEGER REFERENCES alerts(id) ON DELETE SET NULL,
    technique     TEXT NOT NULL CHECK (technique IN ('shuffle', 'diversity')),
    trigger_kind  TEXT NOT NULL CHECK (trigger_kind IN ('time', 'event')),
    detail        TEXT NOT NULL,            -- vd. "IP 10.0.0.12 -> 10.0.0.47" (mô phỏng)
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Kết quả thực nghiệm tổng hợp (tầng AI ghi vào để dashboard hiển thị)
CREATE TABLE IF NOT EXISTS experiment_results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    exp           TEXT NOT NULL,
    variant       TEXT NOT NULL,
    device        TEXT NOT NULL,
    n_seeds       INTEGER NOT NULL,
    macro_f1_mean REAL, macro_f1_std REAL,
    tpr_mean      REAL, fpr_mean REAL,
    UNIQUE (exp, variant, device)
);
