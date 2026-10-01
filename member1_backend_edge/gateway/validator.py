import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from shared.config.constants import (
    VOLTAGE_MIN_V,
    VOLTAGE_MAX_V,
    POWER_MIN_KW,
    POWER_MAX_KW,
    CURRENT_MIN_A,
    CURRENT_MAX_A,
    REQUEST_RATE_MAX_HZ,
)

logger = logging.getLogger("securegrid.gateway.validator")

class TelemetryValidator:
    """
    Validates incoming raw telemetry payloads against physical grid boundaries,
    type constraints, and formatting requirements before ingestion.
    """

    REQUIRED_FIELDS = [
        "device_id",
        "timestamp",
        "power_kw",
        "voltage",
        "current",
        "request_rate",
        "failed_auth_attempts",
    ]

    def validate_payload(self, raw_data: Any) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validates raw dictionary or deserialized JSON payload.
        Returns:
            (is_valid: bool, error_message: Optional[str], cleaned_dict: Optional[dict])
        """
        if not isinstance(raw_data, dict):
            return False, "Payload must be a JSON object", None

        # 1. Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in raw_data:
                return False, f"Missing required telemetry field: '{field}'", None

        device_id = str(raw_data.get("device_id", "")).strip()
        if not device_id or len(device_id) < 3 or len(device_id) > 64:
            return False, f"Invalid device_id '{device_id}' (length must be 3-64 chars)", None

        # 2. Check and parse timestamp
        ts_val = raw_data.get("timestamp")
        parsed_dt = None
        if isinstance(ts_val, datetime):
            parsed_dt = ts_val
        elif isinstance(ts_val, str):
            try:
                # Handle ISO 8601 string
                ts_str = ts_val.replace("Z", "+00:00")
                parsed_dt = datetime.fromisoformat(ts_str)
            except ValueError:
                return False, f"Timestamp '{ts_val}' is not valid ISO-8601 format", None
        else:
            return False, "Timestamp must be an ISO-8601 string or datetime object", None

        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)

        # Check timestamp drift (reject timestamps > 24h into the future)
        now = datetime.now(timezone.utc)
        drift_seconds = abs((now - parsed_dt).total_seconds())
        if drift_seconds > 86400:
            return False, f"Timestamp drift is excessive ({drift_seconds:.0f}s from current UTC)", None

        # 3. Validate numerical values and physical limits
        try:
            power_kw = float(raw_data["power_kw"])
            voltage = float(raw_data["voltage"])
            current = float(raw_data["current"])
            request_rate = float(raw_data["request_rate"])
            failed_auth_attempts = int(raw_data["failed_auth_attempts"])
        except (ValueError, TypeError) as e:
            return False, f"Numerical conversion error: {e}", None

        # Voltage physical boundaries
        if voltage <= 0.0:
            return False, f"Voltage must be strictly positive (> 0.0V), got: {voltage}V", None
        if voltage < VOLTAGE_MIN_V or voltage > 2000.0:
            return False, f"Voltage {voltage}V is outside plausible grid boundary [{VOLTAGE_MIN_V}V, 2000.0V]", None

        # Power boundaries
        if power_kw < POWER_MIN_KW or power_kw > 2000.0:
            return False, f"Power {power_kw}kW is outside physical limits [{POWER_MIN_KW}kW, 2000.0kW]", None

        # Current boundaries
        if current < CURRENT_MIN_A or current > 1000.0:
            return False, f"Current {current}A is outside physical limits [{CURRENT_MIN_A}A, 1000.0A]", None

        # Rate boundary
        if request_rate < 0.0 or request_rate > 2000.0:
            return False, f"Request rate {request_rate}Hz is outside valid bounds [0.0, 2000.0]", None

        # Failed auth attempts
        if failed_auth_attempts < 0:
            return False, f"failed_auth_attempts must be non-negative, got: {failed_auth_attempts}", None

        cleaned = {
            "device_id": device_id,
            "timestamp": parsed_dt.isoformat(),
            "power_kw": round(power_kw, 3),
            "voltage": round(voltage, 2),
            "current": round(current, 2),
            "request_rate": round(request_rate, 2),
            "failed_auth_attempts": failed_auth_attempts,
            "auth_token": raw_data.get("auth_token"),
        }

        return True, None, cleaned

validator = TelemetryValidator()
