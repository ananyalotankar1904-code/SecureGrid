from .model import simple_predict
from datetime import datetime, timedelta

def predict_load(telemetry: dict) -> dict:
    """
    Consumes current telemetry and returns a short-term load prediction.
    Outputs a structured response for Member 3's dashboard.
    """
    if "error" in telemetry:
        return {"error": "Invalid telemetry"}
        
    device_id = telemetry.get("device_id", "unknown")
    current_power = telemetry.get("power_kw", 0.0)
    timestamp_str = telemetry.get("timestamp", datetime.utcnow().isoformat())
    
    try:
        current_time = datetime.fromisoformat(timestamp_str)
    except ValueError:
        current_time = datetime.utcnow()
        
    # Predict for 15 minutes into the future
    future_time = current_time + timedelta(minutes=15)
    
    predicted_load = simple_predict(device_id, current_power)
    
    # Confidence decreases with variance, but for prototype we mock a reasonable baseline
    confidence = 0.85
    
    return {
        "timestamp": future_time.isoformat(),
        "predicted_load_kw": predicted_load,
        "confidence": confidence
    }
