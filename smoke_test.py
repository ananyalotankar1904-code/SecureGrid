import time
import requests
from member2_iot_ml.simulator.telemetry_generator import generate_telemetry

def test_integration():
    print("Testing Normal Telemetry...")
    normal = generate_telemetry("meter_demo_01", "normal")
    res = requests.post("http://localhost:8000/telemetry", json=normal)
    print("Response:", res.status_code, res.json())
    time.sleep(1)
    
    print("Testing DDoS Attack...")
    ddos = generate_telemetry("meter_demo_01", "network_anomaly")
    res = requests.post("http://localhost:8000/telemetry", json=ddos)
    print("Response:", res.status_code, res.json())

if __name__ == "__main__":
    test_integration()
