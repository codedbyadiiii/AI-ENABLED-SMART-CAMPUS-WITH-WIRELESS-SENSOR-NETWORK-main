"""
preprocessing.py
Shared preprocessing used by both historical training
and live ESP32 inference.
"""
import pandas as pd
import numpy as np

FEATURE_COLS = [
    'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos',
    'hour', 'dayofweek', 'is_weekend', 'month',
    'lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12', 'lag_144', 'lag_1008',
    'roll_mean_6', 'roll_mean_12', 'roll_std_6', 'roll_mean_144',
    'lights', 'lights_lag1',
    'T1', 'T2', 'T6', 'T_out', 'RH_1', 'RH_out', 'Windspeed', 'Tdewpoint'
]


def build_features_for_inference(
    current_reading: dict,
    recent_history: list  # list of recent total_power_w readings (oldest→newest)
) -> dict:
    """
    Build a feature row for a single live inference call.
    Args:
        current_reading : dict matching the ESP32 payload schema
        recent_history  : list of past total_power_w readings from DB
    Returns:
        dict of features matching FEATURE_COLS order
    """
    ts = pd.Timestamp(current_reading['timestamp'])

    def safe_lag(history, n):
        return float(history[-n]) if len(history) >= n else np.nan

    features = {
        'hour'      : ts.hour,
        'dayofweek' : ts.dayofweek,
        'is_weekend': int(ts.dayofweek >= 5),
        'month'     : ts.month,
        'hour_sin'  : np.sin(2 * np.pi * ts.hour / 24),
        'hour_cos'  : np.cos(2 * np.pi * ts.hour / 24),
        'dow_sin'   : np.sin(2 * np.pi * ts.dayofweek / 7),
        'dow_cos'   : np.cos(2 * np.pi * ts.dayofweek / 7),
        'lag_1'     : safe_lag(recent_history, 1),
        'lag_2'     : safe_lag(recent_history, 2),
        'lag_3'     : safe_lag(recent_history, 3),
        'lag_6'     : safe_lag(recent_history, 6),
        'lag_12'    : safe_lag(recent_history, 12),
        'lag_144'   : safe_lag(recent_history, 144),
        'lag_1008'  : safe_lag(recent_history, 1008),
        'roll_mean_6'  : float(np.mean(recent_history[-6:]))   if len(recent_history) >= 6   else np.nan,
        'roll_mean_12' : float(np.mean(recent_history[-12:]))  if len(recent_history) >= 12  else np.nan,
        'roll_std_6'   : float(np.std(recent_history[-6:]))    if len(recent_history) >= 6   else np.nan,
        'roll_mean_144': float(np.mean(recent_history[-144:])) if len(recent_history) >= 144 else np.nan,
        'lights'     : current_reading.get('light_power_w', 0.0),
        'lights_lag1': safe_lag(recent_history, 1),
        'T1'         : current_reading.get('temperature', 22.0),
        'T2'         : current_reading.get('temperature', 22.0),
        'T6'         : current_reading.get('temperature', 22.0),
        'T_out'      : current_reading.get('temperature', 22.0),
        'RH_1'       : 50.0,
        'RH_out'     : 60.0,
        'Windspeed'  : 0.0,
        'Tdewpoint'  : 10.0,
    }
    return features
