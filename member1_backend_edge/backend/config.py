import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Ensure root .env is always loaded regardless of process working directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

def reload_environment():
    """Reloads environment variables from root .env."""
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=True)

class Settings:
    """Application settings loaded from environment variables with safe defaults."""

    @property
    def ENVIRONMENT(self) -> str:
        return os.getenv("ENVIRONMENT", "development")

    @property
    def API_HOST(self) -> str:
        return os.getenv("API_HOST", "0.0.0.0")

    @property
    def API_PORT(self) -> int:
        return int(os.getenv("API_PORT", "8000"))

    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        )
        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
        if not origins or self.ENVIRONMENT == "development":
            for default_origin in ["http://localhost:3000", "http://localhost:5173"]:
                if default_origin not in origins:
                    origins.append(default_origin)
        return origins

    # Security Keys
    @property
    def ADMIN_API_KEY(self) -> str:
        return os.getenv("ADMIN_API_KEY", "securegrid-admin-dev-secret-key-32chars")

    @property
    def DEVICE_SHARED_SECRET(self) -> str:
        return os.getenv("DEVICE_SHARED_SECRET", "securegrid-meter-shared-secret-auth-key")

    # Supabase Credentials
    @property
    def SUPABASE_URL(self) -> str:
        return os.getenv("SUPABASE_URL", "").strip()

    @property
    def SUPABASE_KEY(self) -> str:
        return os.getenv("SUPABASE_KEY", "").strip()

    # MQTT Broker Configuration
    @property
    def MQTT_BROKER_HOST(self) -> str:
        return os.getenv("MQTT_BROKER_HOST", "localhost")

    @property
    def MQTT_BROKER_PORT(self) -> int:
        return int(os.getenv("MQTT_BROKER_PORT", "1883"))

    @property
    def MQTT_TOPIC(self) -> str:
        return os.getenv("MQTT_TOPIC", "securegrid/telemetry/#")

    @property
    def MQTT_CLIENT_ID(self) -> str:
        return os.getenv("MQTT_CLIENT_ID", "securegrid-edge-gateway")

    @property
    def MQTT_USERNAME(self) -> str:
        return os.getenv("MQTT_USERNAME", "")

    @property
    def MQTT_PASSWORD(self) -> str:
        return os.getenv("MQTT_PASSWORD", "")

    @property
    def MQTT_USE_TLS(self) -> bool:
        return os.getenv("MQTT_USE_TLS", "false").lower() in ("true", "1", "yes")

    # Rate Limiting
    @property
    def RATE_LIMIT_MAX_PER_MINUTE(self) -> int:
        return int(os.getenv("RATE_LIMIT_MAX_PER_MINUTE", "60"))

    @property
    def RATE_LIMIT_BURST_CAPACITY(self) -> int:
        return int(os.getenv("RATE_LIMIT_BURST_CAPACITY", "10"))

    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase credentials are provided and non-placeholder."""
        url = self.SUPABASE_URL
        key = self.SUPABASE_KEY
        return bool(
            url and 
            key and 
            not url.startswith("https://your-project-id") and 
            not key.startswith("your-supabase")
        )

settings = Settings()
