import random
from datetime import datetime

def generate_telemetry(device_id: str, mode: str = "normal", seed=None) -> dict:
    """
    Generates telemetry based on the specified mode.
    Modes: normal, energy_anomaly, network_anomaly, auth_attack, compromised
    """
    if seed is not None:
        random.seed(seed)
        
    timestamp = datetime.utcnow().isoformat()
    
    # Defaults for normal mode
    power_kw = round(random.uniform(3.0, 7.0), 2)
    voltage = round(random.uniform(220.0, 240.0), 1)
    current = round((power_kw * 1000) / voltage, 2)
    request_rate = random.randint(2, 8)
    failed_auth_attempts = 0
    
    if mode == "energy_anomaly":
        # Abnormally high power consumption
        power_kw = round(random.uniform(15.0, 30.0), 2)
        current = round((power_kw * 1000) / voltage, 2)
        
    elif mode == "network_anomaly":
        # DDoS-like request rate
        request_rate = random.randint(500, 1000)
        
    elif mode == "auth_attack":
        # Failed auth attempts
        failed_auth_attempts = random.randint(5, 20)
        
    elif mode == "compromised":
        power_kw = round(random.uniform(25.0, 40.0), 2)
        current = round((power_kw * 1000) / voltage, 2)
        request_rate = random.randint(500, 1000)
        failed_auth_attempts = random.randint(10, 25)
        
    return {
        "device_id": device_id,
        "timestamp": timestamp,
        "power_kw": power_kw,
        "voltage": voltage,
        "current": current,
        "request_rate": request_rate,
        "failed_auth_attempts": failed_auth_attempts
    }
