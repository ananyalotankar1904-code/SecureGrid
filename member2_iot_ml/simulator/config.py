import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "smartgrid/telemetry")

SIMULATION_INTERVAL = float(os.getenv("SIMULATION_INTERVAL", 1.0))
DEFAULT_DEVICE_ID = os.getenv("DEFAULT_DEVICE_ID", "meter_07")
