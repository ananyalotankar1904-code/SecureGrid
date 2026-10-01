from .anomaly_detection.anomaly_engine import analyze_telemetry as m2_analyze
from .trust_engine.trust_score import calculate_trust_score
from .prediction.load_prediction import predict_load

def analyze_telemetry(telemetry: dict) -> dict:
    """
    """
    import datetime
    
    # Member 2's engine expects timestamp as a string
    if isinstance(telemetry.get("timestamp"), datetime.datetime):
        telemetry["timestamp"] = telemetry["timestamp"].isoformat()
        
    anomaly = m2_analyze(telemetry)
    trust = calculate_trust_score(anomaly)
    prediction = predict_load(telemetry)
    
    # Map trust status to backend expected schema: TRUSTED, ELEVATED_RISK, COMPROMISED
    m2_status = trust.get("trust_status", "TRUSTED")
    if m2_status == "HIGH_RISK":
        trust_status = "COMPROMISED"
    elif m2_status == "SUSPICIOUS":
        trust_status = "ELEVATED_RISK"
    else:
        trust_status = "TRUSTED"
        
    anomaly_detected = anomaly.get("anomaly_score", 0) > 0
    reasons = anomaly.get("reasons", [])
    if anomaly.get("energy_anomaly") and "ENERGY_ANOMALY" not in reasons: reasons.append("ENERGY_ANOMALY")
    if anomaly.get("network_anomaly") and "NETWORK_ANOMALY" not in reasons: reasons.append("NETWORK_ANOMALY")
    if anomaly.get("failed_auth_anomaly") and "AUTH_ANOMALY" not in reasons: reasons.append("AUTH_ANOMALY")

    return {
        "device_id": telemetry["device_id"],
        "timestamp": telemetry.get("timestamp"),
        "trust_score": float(trust.get("trust_score", 100.0)),
        "trust_status": trust_status,
        "anomaly_detected": anomaly_detected,
        "anomaly_type": ", ".join(reasons) if reasons else None,
        "predicted_load_kw": float(prediction.get("predicted_load_kw", 0.0)) if prediction.get("predicted_load_kw") is not None else None,
        "confidence_score": float(prediction.get("confidence", 0.95)),
        "reasons": reasons
    }
