def detect_energy_anomaly(power_kw: float, expected_kw: float = 5.0, threshold_kw: float = 10.0) -> dict:
    """
    Energy anomaly detection. Evaluates current power against expected and threshold logic.
    Returns a structured dictionary with detection results and reason.
    """
    is_anomaly = power_kw > threshold_kw
    
    score = 0
    reason = None
    
    if is_anomaly:
        deviation = power_kw - threshold_kw
        score = min(100, int(50 + (deviation * 5)))
        reason = "power consumption significantly above expected range"
    else:
        # Score is proportional to expected but doesn't reach anomaly thresholds
        score = max(0, min(40, int((power_kw / expected_kw) * 10)))
        
    return {
        "is_anomaly": is_anomaly,
        "score": score,
        "reason": reason
    }
