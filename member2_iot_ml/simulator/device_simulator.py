import json
import time
import paho.mqtt.client as mqtt
from .config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD, MQTT_TOPIC, SIMULATION_INTERVAL
from .telemetry_generator import generate_telemetry

def get_mqtt_client(client_id):
    try:
        # Handle paho-mqtt 2.x requirement for CallbackAPIVersion
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=client_id)
    except AttributeError:
        # Fallback for paho-mqtt 1.x
        client = mqtt.Client(client_id=client_id)
        
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    return client

class DeviceSimulator:
    def __init__(self, device_ids: list):
        self.device_ids = device_ids
        self.modes = {dev_id: "normal" for dev_id in device_ids}
        self.client = get_mqtt_client("sim_group_client")
        self.mqtt_connected = False

    def connect_mqtt(self):
        try:
            self.client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
            self.mqtt_connected = True
            print(f"Connected to MQTT Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}. Running in local testing mode without MQTT.")
            self.mqtt_connected = False

    def set_mode(self, device_id: str, mode: str):
        valid_modes = ["normal", "energy_anomaly", "network_anomaly", "auth_attack", "compromised"]
        if mode in valid_modes and device_id in self.modes:
            self.modes[device_id] = mode
            print(f"[{device_id}] Switched to mode: {mode}")
        else:
            print(f"Invalid mode or device_id. Valid modes: {valid_modes}")

    def generate_all_telemetry(self):
        results = []
        for dev_id in self.device_ids:
            mode = self.modes[dev_id]
            telemetry = generate_telemetry(dev_id, mode)
            results.append(telemetry)
        return results

    def run(self, max_iterations=None):
        self.connect_mqtt()
        if self.mqtt_connected:
            self.client.loop_start()
        
        try:
            print(f"Starting simulation for {len(self.device_ids)} devices...")
            iterations = 0
            while True:
                if max_iterations is not None and iterations >= max_iterations:
                    break
                    
                all_telemetry = self.generate_all_telemetry()
                for telemetry in all_telemetry:
                    payload = json.dumps(telemetry)
                    if self.mqtt_connected:
                        self.client.publish(MQTT_TOPIC, payload)
                    print(f"Published/Generated: {payload}")
                
                iterations += 1
                if max_iterations is None or iterations < max_iterations:
                    time.sleep(SIMULATION_INTERVAL)
        except KeyboardInterrupt:
            print("Stopping simulation...")
        finally:
            if self.mqtt_connected:
                self.client.loop_stop()
                self.client.disconnect()
            
def simulate_devices(device_ids, max_iterations=None):
    sim = DeviceSimulator(device_ids)
    sim.run(max_iterations)

if __name__ == "__main__":
    from .config import DEFAULT_DEVICE_ID
    simulate_devices([DEFAULT_DEVICE_ID, "meter_02", "meter_03"])
