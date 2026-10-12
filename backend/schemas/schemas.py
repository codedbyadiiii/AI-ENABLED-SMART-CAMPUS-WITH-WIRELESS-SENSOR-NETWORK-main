"""
schemas.py
Pydantic models for request validation and response serialisation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorPayload(BaseModel):
    """
    Expected JSON body from ESP32 via POST /api/sensor-data.
    Fields match the classroom sensor layout.
    """
    timestamp         : datetime
    light_power_w     : Optional[float] = Field(None, ge=0, description="Light circuit power (W)")
    fan_power_w       : Optional[float] = Field(None, ge=0, description="Fan circuit power (W)")
    projector_power_w : Optional[float] = Field(None, ge=0, description="Projector power (W)")
    total_power_w     : Optional[float] = Field(None, ge=0, description="Total measured power (W)")
    energy_kwh        : Optional[float] = Field(None, ge=0, description="Interval energy (kWh)")
    occupancy         : Optional[int]   = Field(None, ge=0, description="Number of occupants")
    temperature       : Optional[float] = Field(None, description="Indoor temperature (°C)")
    light_intensity   : Optional[float] = Field(None, ge=0, description="Lux reading")


class PredictionResponse(BaseModel):
    current_energy_wh           : float
    predicted_next_interval_wh  : float
    predicted_next_hour_kwh     : float
    anomaly_detected            : bool
    anomaly_type                : Optional[str]
    severity_sigma              : Optional[float]
    model_used                  : str


class AnomalyRecord(BaseModel):
    id              : int
    detected_at     : datetime
    actual_power_w  : Optional[float]
    residual_w      : Optional[float]
    severity_sigma  : Optional[float]
    anomaly_type    : Optional[str]
    likely_appliance: Optional[str]
    is_confirmed    : int
