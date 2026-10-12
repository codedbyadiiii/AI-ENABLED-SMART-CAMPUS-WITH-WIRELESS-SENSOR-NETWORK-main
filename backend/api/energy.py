"""
energy.py
GET /api/current    — latest sensor reading
GET /api/history    — historical readings (hourly/daily aggregated)
"""
from fastapi import APIRouter, Query
from database.db import get_connection
from typing import Optional

router = APIRouter()


@router.get("/current")
def get_current():
    """Return the most recent sensor reading from DB."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if row is None:
        return {"message": "No data yet. Waiting for ESP32 readings."}
    return dict(row)


@router.get("/history")
def get_history(
    resolution: str  = Query("hourly", enum=["raw", "hourly", "daily"]),
    limit      : int = Query(144, ge=1, le=2016)
):
    """
    Return historical energy data.
    resolution=raw      → last `limit` raw 10-min readings
    resolution=hourly   → hourly averages
    resolution=daily    → daily totals in kWh
    """
    conn = get_connection()

    if resolution == "raw":
        rows = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    elif resolution == "hourly":
        rows = conn.execute("""
            SELECT strftime('%Y-%m-%d %H:00:00', timestamp) AS hour,
                   AVG(total_power_w)  AS avg_power_w,
                   SUM(energy_kwh)     AS total_kwh,
                   AVG(temperature)    AS avg_temp,
                   COUNT(*)            AS readings
            FROM sensor_readings
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]

    else:  # daily
        rows = conn.execute("""
            SELECT strftime('%Y-%m-%d', timestamp) AS day,
                   SUM(energy_kwh)    AS total_kwh,
                   AVG(total_power_w) AS avg_power_w,
                   MAX(total_power_w) AS peak_power_w
            FROM sensor_readings
            GROUP BY day
            ORDER BY day DESC
            LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in reversed(rows)]
