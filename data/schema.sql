
-- ─────────────────────────────────────────────────────────────
-- TABLE 1: raw sensor readings (from ESP32 via MQTT / HTTP POST)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sensor_readings (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         DATETIME NOT NULL,
    light_power_w     REAL,          -- watt reading from light circuit
    fan_power_w       REAL,          -- watt reading from fan circuit
    projector_power_w REAL,          -- watt reading from projector
    total_power_w     REAL,          -- sum or direct total clamp reading
    energy_kwh        REAL,          -- cumulative or interval energy
    occupancy         INTEGER,       -- number of students (0 if empty)
    temperature       REAL,          -- °C from DHT22 or similar
    light_intensity   REAL,          -- lux from BH1750 or similar
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sr_timestamp ON sensor_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sr_created   ON sensor_readings(created_at);

-- ─────────────────────────────────────────────────────────────
-- TABLE 2: model predictions
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS predictions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    for_timestamp        DATETIME NOT NULL,   -- the interval being predicted
    predicted_power_w    REAL,
    predicted_energy_kwh REAL,
    prediction_horizon   TEXT DEFAULT '10min',
    model_version        TEXT,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_pred_ts ON predictions(for_timestamp);

-- ─────────────────────────────────────────────────────────────
-- TABLE 3: anomaly events
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anomalies (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at         DATETIME NOT NULL,
    actual_power_w      REAL,
    expected_power_w    REAL,
    residual_w          REAL,
    severity_sigma      REAL,           -- how many σ from normal
    anomaly_type        TEXT,           -- 'over_consumption' | 'under_consumption'
    likely_appliance    TEXT,           -- 'lights' | 'fan' | 'projector' | 'unknown'
    is_confirmed        INTEGER DEFAULT 0,   -- 1 = human confirmed real event
    notes               TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anom_ts ON anomalies(detected_at);
