"""
prediction.py
GET /api/prediction — on-demand prediction using latest DB data
"""
from fastapi import APIRouter, HTTPException
from database.db import get_connection
from schemas.schemas import PredictionResponse
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../ml'))

router = APIRouter()


@router.get("/prediction", response_model=PredictionResponse)
def get_prediction():
    """
    Run an on-demand prediction using the latest available DB reading.
    Useful for dashboard polling without waiting for new ESP32 data.
    """
    conn = get_connection()
    try:
        latest = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()

        if latest is None:
            raise HTTPException(status_code=404, detail="No sensor data available yet.")

        history_rows = conn.execute(
            "SELECT total_power_w FROM sensor_readings "
            "ORDER BY timestamp DESC LIMIT 1008"
        ).fetchall()
        history = [r['total_power_w'] for r in reversed(history_rows)
                   if r['total_power_w'] is not None]

        from predict import predict_next_interval
        result = predict_next_interval(dict(latest), history)
        return PredictionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
