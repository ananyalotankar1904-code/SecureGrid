from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=64, description="Smart meter unique identifier")
    timestamp: datetime = Field(..., description="Timezone-aware timestamp of measurement")
    power_kw: float = Field(..., ge=0.0, le=2000.0, description="Active power consumption in kW (non-negative)")
    voltage: float = Field(..., gt=0.0, le=2000.0, description="RMS AC line voltage (strictly positive)")
    current: float = Field(..., ge=0.0, le=1000.0, description="RMS AC line current in amperes (non-negative)")
    request_rate: float = Field(..., ge=0.0, le=2000.0, description="Transmission rate in Hz")
    failed_auth_attempts: int = Field(..., ge=0, description="Failed authentication attempts in current window")
    auth_token: Optional[str] = Field(default=None, description="Optional authentication credential or HMAC signature")

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            # Assume UTC if not explicitly provided
            return v.replace(tzinfo=timezone.utc)
        return v

class TelemetryResponse(BaseModel):
    status: str = "accepted"
    device_id: str
    timestamp: datetime
    telemetry_id: str

class TelemetryListResponse(BaseModel):
    total: int
    items: List[TelemetryPayload]
