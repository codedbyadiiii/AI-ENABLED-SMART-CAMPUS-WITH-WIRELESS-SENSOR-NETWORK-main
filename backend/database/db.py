"""
db.py
SQLite database connection and table initialisation.
Replace SQLite with PostgreSQL for production by swapping the URL.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'data' / 'classroom_energy.db'


def get_connection():
    """Return a SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    schema = """
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp         DATETIME NOT NULL,
        light_power_w     REAL,
        fan_power_w       REAL,
        projector_power_w REAL,
        total_power_w     REAL,
        energy_kwh        REAL,
        occupancy         INTEGER,
        temperature       REAL,
        light_intensity   REAL,
        created_at        DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_sr_timestamp ON sensor_readings(timestamp);

    CREATE TABLE IF NOT EXISTS predictions (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        for_timestamp        DATETIME NOT NULL,
        predicted_power_w    REAL,
        predicted_energy_kwh REAL,
        prediction_horizon   TEXT DEFAULT '10min',
        model_version        TEXT,
        created_at           DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_pred_ts ON predictions(for_timestamp);

    CREATE TABLE IF NOT EXISTS anomalies (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_at         DATETIME NOT NULL,
        actual_power_w      REAL,
        expected_power_w    REAL,
        residual_w          REAL,
        severity_sigma      REAL,
        anomaly_type        TEXT,
        likely_appliance    TEXT,
        is_confirmed        INTEGER DEFAULT 0,
        notes               TEXT,
        created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_anom_ts ON anomalies(detected_at);
    """
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
