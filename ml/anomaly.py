"""
anomaly.py
Appliance-level anomaly attribution.
Designed for real ESP32 data — not validated on UCI dataset.
Will produce meaningful results only when per-circuit sensor data arrives.
"""


def identify_anomalous_appliance(
    actual_light_w: float,
    actual_fan_w: float,
    actual_projector_w: float,
    expected_light_w: float,
    expected_fan_w: float,
    expected_projector_w: float,
) -> dict:
    """
    Compare actual vs expected per-appliance power readings.
    Returns the most likely culprit appliance for an anomaly.

    Args:
        actual_*   : current sensor reading (W) for each circuit
        expected_* : rolling mean from DB history for each circuit
    Returns:
        dict with per-appliance residuals and the most likely culprit
    """
    residuals = {
        'lights'   : actual_light_w     - expected_light_w,
        'fan'      : actual_fan_w       - expected_fan_w,
        'projector': actual_projector_w - expected_projector_w,
    }
    culprit = max(residuals, key=lambda k: abs(residuals[k]))

    return {
        'residuals'          : residuals,
        'likely_appliance'   : culprit,
        'culprit_residual_w' : round(residuals[culprit], 2),
        'explanation'        : (
            f"'{culprit}' shows the largest deviation from expected: "
            f"{residuals[culprit]:+.1f} W"
        )
    }
