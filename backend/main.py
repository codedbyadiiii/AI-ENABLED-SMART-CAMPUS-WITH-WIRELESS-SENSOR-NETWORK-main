"""
main.py
FastAPI application entry point for the Classroom Energy Monitoring system.
Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from api import sensor, energy, prediction, anomaly  # type: ignore[import-not-found]

app = FastAPI(
    title="Classroom Energy Monitoring API",
    description="AI-powered energy monitoring backend for ESP32 sensor data.",
    version="1.0.0",
)

# Allow dashboard frontend to connect (update origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sensor.router,     prefix="/api", tags=["Sensor Data"])
app.include_router(energy.router,     prefix="/api", tags=["Energy History"])
app.include_router(prediction.router, prefix="/api", tags=["Predictions"])
app.include_router(anomaly.router,    prefix="/api", tags=["Anomalies"])


@app.get("/")
def root():
    return {"status": "running", "message": "Classroom Energy Monitoring API v1.0"}
