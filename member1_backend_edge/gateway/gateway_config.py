import os
from dotenv import load_dotenv

load_dotenv()

class GatewayConfig:
    """Edge Gateway configuration with environment variable overrides and safe defaults."""

    # MQTT Broker Settings
    BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    TOPIC: str = os.getenv("MQTT_TOPIC", "securegrid/telemetry/#")
    CLIENT_ID: str = os.getenv("MQTT_CLIENT_ID", "securegrid-edge-gateway")
    USERNAME: str = os.getenv("MQTT_USERNAME", "")
    PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    USE_TLS: bool = os.getenv("MQTT_USE_TLS", "false").lower() in ("true", "1", "yes")
    CA_CERT: str = os.getenv("MQTT_CA_CERT", "")

    # Device Authentication Strategy: 'token', 'hmac', or 'dev_permissive'
    AUTH_STRATEGY: str = os.getenv("GATEWAY_AUTH_STRATEGY", "token")
    REQUIRE_AUTH: bool = os.getenv("GATEWAY_REQUIRE_AUTH", "true").lower() in ("true", "1", "yes")
    SHARED_SECRET: str = os.getenv("DEVICE_SHARED_SECRET", "securegrid-meter-shared-secret-auth-key")

    # Rate Limiting (Token Bucket per Device ID)
    RATE_LIMIT_MAX_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_MAX_PER_MINUTE", "60"))
    RATE_LIMIT_BURST_CAPACITY: int = int(os.getenv("RATE_LIMIT_BURST_CAPACITY", "10"))

    # Backend Forwarding URL
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    FORWARD_TIMEOUT_SECONDS: float = float(os.getenv("FORWARD_TIMEOUT_SECONDS", "3.0"))

    @property
    def transport_security_description(self) -> str:
        """Accurate description of connection security."""
        if self.USE_TLS:
            return f"TLS Encrypted (Port {self.BROKER_PORT})"
        return f"Plaintext MQTT (No TLS - Development / Local Demo Only)"

gateway_config = GatewayConfig()
