from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from shared.config.constants import ALL_SEVERITIES, SEVERITY_MEDIUM

class SecurityEventCreate(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=64, description="Meter identifier associated with event")
    event_type: str = Field(..., min_length=2, max_length=100, description="Classification of security event")
    severity: str = Field(default=SEVERITY_MEDIUM, description="Impact severity: LOW, MEDIUM, HIGH, CRITICAL")
    description: str = Field(..., min_length=5, description="Contextual explanation of detected threat")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Diagnostic telemetry or forensic facts")
    mitigated: bool = Field(default=False, description="Whether containment or remediation has been applied")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        upper = v.upper()
        if upper not in ALL_SEVERITIES:
            raise ValueError(f"Severity must be one of {ALL_SEVERITIES}, got: {v}")
        return upper

class SecurityEventResponse(SecurityEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique event identifier")
    timestamp: datetime = Field(..., description="Timestamp of event occurrence")

class SecurityEventListResponse(BaseModel):
    total: int
    items: List[SecurityEventResponse]
