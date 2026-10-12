"""
sensor.py
POST /api/sensor-data  — ingest a reading from ESP32 and return prediction.
"""
from fastapi import APIRouter, HTTPException  # type: ignore[import-not-found]
from schemas.schemas import SensorPayload, PredictionResponse
from database.db import get_connection
import sys, os
import importlib.util

sys.path.append(os.path.join(os.path.dirname(__file__), '../../ml'))

router = APIRouter()


def _load_predict_next_interval():
    """Load the ML prediction function from the project ml directory."""
    predict_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../ml/predict.py')
    )
    spec = importlib.util.spec_from_file_location('ml_predict', predict_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load prediction module from {predict_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.predict_next_interval


def _fetch_recent_history(conn, n: int = 1008) -> list:
    """Pull the last n total_power_w readings from DB (oldest first)."""
    rows = conn.execute(
        "SELECT total_power_w FROM sensor_readings "
        "ORDER BY timestamp DESC LIMIT ?", (n,)
    ).fetchall()
    return [r['total_power_w'] for r in reversed(rows) if r['total_power_w'] is not None]


@router.post("/sensor-data", response_model=PredictionResponse)
def ingest_sensor_data(payload: SensorPayload):
    """
    Receive a sensor reading from ESP32.
    1. Persist to DB.
    2. Fetch recent history for feature engineering.
    3. Run prediction + anomaly detection.
    4. Persist anomaly if detected.
    5. Return structured prediction response.
    """
    conn = get_connection()
    try:
        # 1. Insert raw reading
        conn.execute("""
            INSERT INTO sensor_readings
            (timestamp, light_power_w, fan_power_w, projector_power_w,
            total_power_w, energy_kwh, occupancy, temperature, light_intensity)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            payload.timestamp.isoformat(),
            payload.light_power_w, payload.fan_power_w, payload.projector_power_w,
            payload.total_power_w, payload.energy_kwh, payload.occupancy,
            payload.temperature, payload.light_intensity,
        ))
        conn.commit()

        # 2. Fetch history
        history = _fetch_recent_history(conn)

        # 3. Predict
        from predict import predict_next_interval # type: ignore
        result = predict_next_interval(payload.dict(), history)

        # 4. Persist anomaly
        if result['anomaly_detected']:
            conn.execute("""
                INSERT INTO anomalies
                (detected_at, actual_power_w, residual_w, severity_sigma,
                anomaly_type, likely_appliance)
                VALUES (?,?,?,?,?,?)
            """, (
                payload.timestamp.isoformat(),
                payload.total_power_w,
                (payload.total_power_w or 0) - result['current_energy_wh'],
                result['severity_sigma'],
                result['anomaly_type'],
                'unknown'  # replaced by appliance-level analysis when available
            ))
            conn.commit()

        return PredictionResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
