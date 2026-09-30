import traceback
from ..anomaly_detection.anomaly_engine import analyze_telemetry
from ..trust_engine.trust_score import calculate_trust_score
from ..trust_engine.security_event import generate_security_event
from ..prediction.load_prediction import predict_load

def process_for_frontend(telemetry: dict) -> dict:
    """
    Takes raw telemetry, runs it through the Member 2 intelligence layer,
    and returns a clean, frontend-friendly JSON response for Member 3.
    """
    try:
        if "error" in telemetry:
            return {
                "success": False,
                "error": "Invalid input telemetry",
                "details": [telemetry.get("error")]
            }

        anomaly = analyze_telemetry(telemetry)
        if "error" in anomaly:
            return {
                "success": False,
                "error": anomaly["error"],
                "details": anomaly.get("details", [])
            }

        trust = calculate_trust_score(anomaly)
        event = generate_security_event(telemetry, anomaly, trust)
        prediction = predict_load(telemetry)
        
        # Build frontend-friendly structure
        return {
            "success": True,
            "data": {
                "device_id": telemetry.get("device_id"),
                "timestamp": telemetry.get("timestamp"),
                "telemetry": {
                    "power_kw": telemetry.get("power_kw"),
                    "voltage": telemetry.get("voltage"),
                    "current": telemetry.get("current"),
                    "request_rate": telemetry.get("request_rate"),
                    "failed_auth_attempts": telemetry.get("failed_auth_attempts")
                },
                "security": {
                    "trust_score": trust.get("trust_score"),
                    "trust_status": trust.get("trust_status"),
                    "severity": event.get("severity"),
                    "anomalies": event.get("anomalies", []),
                    "event_type": event.get("event_type"),
                    "recommended_action": event.get("recommended_action")
                },
                "prediction": {
                    "predicted_load_kw": prediction.get("predicted_load_kw"),
                    "confidence": prediction.get("confidence")
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Internal processing error",
            "details": [str(e)]
        }
