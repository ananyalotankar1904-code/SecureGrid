from datetime import datetime

def generate_security_event(telemetry: dict, anomaly_result: dict, trust_result: dict) -> dict:
    """
    Generates a security event based on the analysis and trust evaluation.
    Member 1 will use this to determine automated actions like quarantine.
    """
    if "error" in anomaly_result or "error" in trust_result:
        return {"error": "Cannot generate event due to previous errors."}
        
    anomalies = []
    if anomaly_result.get("energy_anomaly"):
        anomalies.append("ENERGY_ANOMALY")
    if anomaly_result.get("network_anomaly"):
        anomalies.append("NETWORK_ANOMALY")
    if anomaly_result.get("failed_auth_anomaly"):
        anomalies.append("AUTH_ANOMALY")
    
    event_type = "NORMAL_OPERATION"
    if anomalies:
        if trust_result.get("trust_status") == "HIGH_RISK":
            event_type = "DEVICE_COMPROMISED"
        else:
            event_type = "SUSPICIOUS_BEHAVIOR"
            
    recommended_action = "ALLOW"
    if trust_result.get("trust_status") == "HIGH_RISK":
        recommended_action = "QUARANTINE"
    elif trust_result.get("trust_status") == "SUSPICIOUS":
        recommended_action = "RESTRICT" if "AUTH_ANOMALY" in anomalies else "MONITOR"
        
    return {
        "device_id": telemetry.get("device_id"),
        "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
        "event_type": event_type,
        "severity": anomaly_result.get("severity", "LOW"),
        "trust_score": trust_result.get("trust_score", 100),
        "anomalies": anomalies,
        "recommended_action": recommended_action
    }
