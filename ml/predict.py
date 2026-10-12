"""
predict.py
Inference module — loads saved model and returns structured predictions.
Training code lives in train.py; this file is for inference ONLY.
"""
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
from preprocessing import FEATURE_COLS, build_features_for_inference

MODEL_PATH    = Path(__file__).parent / 'models' / 'xgboost_tuned.json'
THRESH_PATH   = Path(__file__).parent / 'models' / 'anomaly_thresholds.npy'

# Loaded once at startup, not on every API request
_model      = None
_thresholds = None


def _load_artifacts():
    global _model, _thresholds
    if _model is None:
        _model = xgb.XGBRegressor()
        _model.load_model(MODEL_PATH)
    if _thresholds is None:
        _thresholds = np.load(THRESH_PATH, allow_pickle=True).item()
    return _model, _thresholds


def predict_next_interval(current_reading: dict, recent_history: list) -> dict:
    """
    Predict energy consumption for the NEXT 10-minute interval.

    Args:
        current_reading : latest ESP32 payload dict
        recent_history  : list of total_power_w values from DB (oldest→newest)

    Returns:
        Structured prediction dict ready for API response / DB insert
    """
    model, thresholds = _load_artifacts()

    features = build_features_for_inference(current_reading, recent_history)
    row = pd.DataFrame([features])[FEATURE_COLS]
    row = row.fillna(row.mean())   # cold-start: fill missing lags with mean

    pred_wh = float(model.predict(row)[0])
    pred_wh = max(0.0, pred_wh)   # energy cannot be negative

    # Anomaly detection on current reading
    actual_wh      = current_reading.get('total_power_w', None)
    anomaly_status = None
    severity_sigma = None

    if actual_wh is not None and len(recent_history) >= 1:
        expected_wh = float(recent_history[-1])   # last known reading as baseline
        residual    = actual_wh - expected_wh
        sigma       = (residual - thresholds['mean']) / thresholds['std']
        severity_sigma = round(abs(float(sigma)), 2)

        if residual > thresholds['upper']:
            anomaly_status = 'over_consumption'
        elif residual < thresholds['lower']:
            anomaly_status = 'under_consumption'

    return {
        'current_energy_wh'          : round(float(actual_wh or 0), 2),
        'predicted_next_interval_wh' : round(pred_wh, 2),
        'predicted_next_hour_kwh'    : round(pred_wh * 6 / 1000, 4),
        'anomaly_detected'           : anomaly_status is not None,
        'anomaly_type'               : anomaly_status,
        'severity_sigma'             : severity_sigma,
        'model_used'                 : 'XGBoost (tuned, v1.0)',
    }
