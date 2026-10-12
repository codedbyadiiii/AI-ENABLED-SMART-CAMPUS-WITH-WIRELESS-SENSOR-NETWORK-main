"""
anomaly.py
GET /api/anomalies — list detected anomalies
"""
from fastapi import APIRouter, Query
from database.db import get_connection

router = APIRouter()


@router.get("/anomalies")
def get_anomalies(
    limit     : int  = Query(50,    ge=1, le=500),
    confirmed : bool = Query(False, description="Filter confirmed anomalies only")
):
    """
    Return recent anomaly events from DB.
    confirmed=True filters only human-confirmed anomalies.
    """
    conn = get_connection()
    if confirmed:
        rows = conn.execute(
            "SELECT * FROM anomalies WHERE is_confirmed=1 "
            "ORDER BY detected_at DESC LIMIT ?", (limit,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM anomalies ORDER BY detected_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
