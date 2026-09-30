import json
import os
from member2_iot_ml.simulator.telemetry_generator import generate_telemetry
from member2_iot_ml.integration.frontend_adapter import process_for_frontend

def save_fixture(name, data):
    dir_path = os.path.join(os.path.dirname(__file__), "demo_data")
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{name}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def generate_demos():
    print("=== GENERATING DEMO DATA FOR MEMBER 3 ===")
    
    scenarios = [
        ("NORMAL", "normal", 42, "normal_device"),
        ("ENERGY ANOMALY ONLY", "energy_anomaly", 44, "energy_anomaly"),
        ("NETWORK/DDOS ANOMALY ONLY", "network_anomaly", 45, "ddos_anomaly"),
        ("FULL COMPROMISE", "compromised", 43, "compromised_device")
    ]
    
    device_id = "meter_demo_01"
    
    for title, mode, seed, filename in scenarios:
        print(f"\n--- {title} ---")
        tel = generate_telemetry(device_id, mode, seed=seed)
        result = process_for_frontend(tel)
        print(json.dumps(result, indent=2))
        save_fixture(filename, result)
        print(f"-> Saved to member2_iot_ml/integration/demo_data/{filename}.json")

if __name__ == "__main__":
    generate_demos()
