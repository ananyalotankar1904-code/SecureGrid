import json
import logging
import signal
import sys
import time
from typing import Optional, Dict, Any
import httpx
import paho.mqtt.client as mqtt

from member1_backend_edge.gateway.gateway_config import gateway_config
from member1_backend_edge.gateway.device_auth import device_auth
from member1_backend_edge.gateway.validator import validator
from member1_backend_edge.gateway.rate_limiter import rate_limiter

logger = logging.getLogger("securegrid.gateway.mqtt")

class EdgeMQTTGateway:
    """
    Raspberry Pi and Local Dev MQTT Gateway Subscriber.
    Ingests smart meter telemetry, authenticates devices, validates electrical ranges,
    enforces rate limits, and forwards valid measurements to the FastAPI backend.
    """

    def __init__(self, config=gateway_config, http_client: Optional[httpx.Client] = None):
        self.config = config
        self.http_client = http_client or httpx.Client(timeout=self.config.FORWARD_TIMEOUT_SECONDS)
        self.is_running = False
        self._client: Optional[mqtt.Client] = None

    def _setup_mqtt_client(self) -> mqtt.Client:
        # Paho MQTT v2 client instantiation
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.config.CLIENT_ID,
        )

        if self.config.USERNAME and self.config.PASSWORD:
            client.username_pw_set(self.config.USERNAME, self.config.PASSWORD)

        if self.config.USE_TLS:
            if self.config.CA_CERT:
                client.tls_set(ca_certs=self.config.CA_CERT)
            else:
                client.tls_set()
            logger.info("MQTT TLS enabled for secure edge communication.")
        else:
            logger.info("MQTT running without TLS encryption (suitable for local demo / lab).")

        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        return client

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.config.BROKER_HOST}:{self.config.BROKER_PORT}")
            client.subscribe(self.config.TOPIC)
            logger.info(f"Subscribed to topic: {self.config.TOPIC}")
        else:
            logger.error(f"MQTT connection failed with return code {rc}")

    def on_disconnect(self, client, userdata, flags, rc, properties=None):
        logger.warning(f"Disconnected from MQTT broker (rc: {rc}).")

    def process_message_payload(self, raw_payload: str) -> Dict[str, Any]:
        """
        Processes a raw JSON string through Auth -> Rate Limiting -> Range Validation.
        Returns a result dictionary containing status and action taken.
        """
        try:
            data = json.loads(raw_payload)
        except json.JSONDecodeError as e:
            logger.warning(f"Rejected payload: Invalid JSON ({e})")
            return {"status": "rejected", "reason": "invalid_json"}

        device_id = str(data.get("device_id", "UNKNOWN")).strip()
        auth_token = data.get("auth_token")
        timestamp = str(data.get("timestamp", ""))

        # 1. Device Authentication (Fail closed)
        is_auth, auth_err = device_auth.authenticate_device(device_id, auth_token, timestamp)
        if not is_auth:
            logger.warning(f"Dropped telemetry from '{device_id}': Auth failure ({auth_err})")
            self._notify_security_event(
                device_id=device_id,
                event_type="UNAUTHORIZED_TELEMETRY_ATTEMPT",
                severity="HIGH",
                description=f"Rejected telemetry with invalid or missing credential: {auth_err}",
            )
            return {"status": "rejected", "reason": "auth_failure", "error": auth_err}

        # 2. Rate Limiting Check
        allowed, rate_info = rate_limiter.check_rate_limit(device_id)
        if not allowed:
            logger.warning(f"Dropped telemetry from '{device_id}': Rate limit exceeded.")
            self._notify_security_event(
                device_id=device_id,
                event_type="RATE_LIMIT_FLOOD",
                severity="MEDIUM",
                description=f"Device transmission frequency exceeded limit. Cooldown: {rate_info.get('retry_after_seconds')}s",
            )
            return {"status": "rejected", "reason": "rate_limited", "info": rate_info}

        # 3. Electrical Range and Schema Validation
        is_valid, val_err, cleaned_data = validator.validate_payload(data)
        if not is_valid:
            logger.warning(f"Dropped telemetry from '{device_id}': Validation failure ({val_err})")
            self._notify_security_event(
                device_id=device_id,
                event_type="TELEMETRY_VALIDATION_ERROR",
                severity="MEDIUM",
                description=f"Payload failed physical/schema check: {val_err}",
            )
            return {"status": "rejected", "reason": "validation_failure", "error": val_err}

        # 4. Forward to FastAPI backend
        forward_ok = self.forward_to_backend(cleaned_data)
        return {"status": "accepted" if forward_ok else "forward_failed", "data": cleaned_data}

    def on_message(self, client, userdata, msg):
        """MQTT message reception callback."""
        payload_str = msg.payload.decode("utf-8", errors="replace")
        logger.debug(f"Received MQTT message on {msg.topic}: {payload_str}")
        self.process_message_payload(payload_str)

    def forward_to_backend(self, payload: Dict[str, Any]) -> bool:
        """Sends validated telemetry to the FastAPI backend REST endpoint."""
        url = f"{self.config.BACKEND_API_URL.rstrip('/')}/telemetry"
        try:
            res = self.http_client.post(url, json=payload)
            if res.status_code in (200, 201):
                logger.info(f"Forwarded telemetry for '{payload['device_id']}' to backend (HTTP {res.status_code})")
                return True
            elif res.status_code == 403:
                logger.warning(f"Backend rejected telemetry for '{payload['device_id']}': Device is QUARANTINED.")
                return False
            else:
                logger.warning(f"Backend responded with HTTP {res.status_code}: {res.text}")
                return False
        except httpx.RequestError as e:
            logger.error(f"Failed to reach FastAPI backend at {url}: {e}")
            return False

    def _notify_security_event(self, device_id: str, event_type: str, severity: str, description: str):
        """Optionally posts security event directly to backend."""
        url = f"{self.config.BACKEND_API_URL.rstrip('/')}/security/events"
        try:
            self.http_client.post(url, json={
                "device_id": device_id,
                "event_type": event_type,
                "severity": severity,
                "description": description,
                "details": {"source": "edge_gateway"},
                "mitigated": False,
            })
        except Exception:
            pass # Non-blocking diagnostic notification

    def start(self):
        """Starts the MQTT loop."""
        self._client = self._setup_mqtt_client()
        self.is_running = True
        logger.info(f"Starting Edge Gateway [{self.config.transport_security_description}]...")
        try:
            self._client.connect(self.config.BROKER_HOST, self.config.BROKER_PORT, 60)
            self._client.loop_start()
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker ({e}). Fallback to local HTTP ingestion.")

    def stop(self):
        """Gracefully disconnects and stops the MQTT loop."""
        logger.info("Stopping Edge Gateway subscriber...")
        self.is_running = False
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
        self.http_client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    gateway = EdgeMQTTGateway()
    gateway.start()

    def signal_handler(sig, frame):
        print("\nShutdown signal received.")
        gateway.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("SecureGrid Edge Gateway running. Press Ctrl+C to stop.")
    while gateway.is_running:
        time.sleep(1)
