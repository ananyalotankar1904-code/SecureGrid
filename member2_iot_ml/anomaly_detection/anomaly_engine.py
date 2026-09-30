from .energy_anomaly import detect_energy_anomaly
from .network_anomaly import detect_network_anomaly

def validate_telemetry(telemetry: dict) -> list:
    """Validates the structure of the incoming telemetry."""
    errors = []
    required_fields = ["device_id", "timestamp", "power_kw", "voltage", "current", "request_rate", "failed_auth_attempts"]
    for field in required_fields:
        if field not in telemetry:
            errors.append(f"Missing required field: {field}")
            
    if "power_kw" in telemetry:
        if not isinstance(telemetry["power_kw"], (int, float)):
            errors.append("power_kw must be a number")
        elif telemetry["power_kw"] < 0:
            errors.append("power_kw cannot be negative")
            
    if "request_rate" in telemetry:
        if not isinstance(telemetry["request_rate"], (int, float)):
            errors.append("request_rate must be a number")
        
    return errors

def analyze_telemetry(telemetry: dict) -> dict:
    """
    Consumes telemetry JSON, analyzes it, and returns a structured anomaly result.
    Combines both energy and network detection.
    """
    errors = validate_telemetry(telemetry)
    if errors:
        return {"error": "Invalid telemetry", "details": errors}

    energy_res = detect_energy_anomaly(telemetry["power_kw"])
    net_res = detect_network_anomaly(telemetry["request_rate"], telemetry["failed_auth_attempts"])
    
    reasons = []
    if energy_res["reason"]:
        reasons.append(energy_res["reason"])
    reasons.extend(net_res["reasons"])
    
    energy_anomaly = energy_res["is_anomaly"]
    network_anomaly = telemetry["request_rate"] > 50
    failed_auth_anomaly = telemetry["failed_auth_attempts"] > 3
    
    # Calculate a simple representative anomaly score
    score = 0
    if energy_anomaly:
        score += 40
    if network_anomaly:
        score += 40
    if failed_auth_anomaly:
        score += 20
        
    # Severity classification
    severity = "LOW"
    if score > 75:
        severity = "HIGH"
    elif score > 30:
        severity = "MEDIUM"
        
    return {
        "device_id": telemetry.get("device_id"),
        "energy_anomaly": energy_anomaly,
        "network_anomaly": network_anomaly,
        "failed_auth_anomaly": failed_auth_anomaly,
        "anomaly_score": score,
        "severity": severity,
        "reasons": reasons
    }
