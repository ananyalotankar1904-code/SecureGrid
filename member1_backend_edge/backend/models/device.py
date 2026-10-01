from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from shared.config.constants import ALL_DEVICE_STATUSES, DEVICE_STATUS_ACTIVE

class DeviceBase(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=64, description="Unique identifier of the smart meter")
    device_name: str = Field(..., min_length=1, max_length=100, description="Friendly label for the meter")
    device_type: str = Field(default="residential_meter", description="Operational classification of device")
    location: Optional[str] = Field(default="Sector 1", max_length=200, description="Grid sector or physical location")
    ip_address: Optional[str] = Field(default=None, description="IP network address")
    mac_address: Optional[str] = Field(default=None, description="Hardware MAC address")
    firmware_version: Optional[str] = Field(default=None, description="Firmware version string")

class DeviceCreate(DeviceBase):
    status: str = Field(default=DEVICE_STATUS_ACTIVE, description="Initial device status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper = v.upper()
        if upper not in ALL_DEVICE_STATUSES:
            raise ValueError(f"Status must be one of {ALL_DEVICE_STATUSES}, got: {v}")
        return upper

class DeviceStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status (ACTIVE, SUSPICIOUS, QUARANTINED, OFFLINE)")
    reason: Optional[str] = Field(default=None, description="Reason for status change / containment")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper = v.upper()
        if upper not in ALL_DEVICE_STATUSES:
            raise ValueError(f"Status must be one of {ALL_DEVICE_STATUSES}, got: {v}")
        return upper

class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    status: str
    created_at: datetime
    updated_at: datetime

class DeviceListResponse(BaseModel):
    total: int
    items: List[DeviceResponse]
