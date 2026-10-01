from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from shared.config.constants import (
    TRUST_STATUS_TRUSTED,
    TRUST_STATUS_ELEVATED_RISK,
    TRUST_STATUS_COMPROMISED,
)

class PredictionCreate(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=64, description="Target smart meter identifier")
    timestamp: Optional[datetime] = Field(default=None, description="Timestamp of evaluation")
    trust_score: float = Field(..., ge=0.0, le=100.0, description="Calculated trust score (0 to 100)")
    trust_status: str = Field(..., description="TRUSTED, ELEVATED_RISK, or COMPROMISED")
    anomaly_detected: bool = Field(default=False, description="Flag indicating anomaly detected")
    anomaly_type: Optional[str] = Field(default=None, description="Category of anomaly if detected")
    predicted_load_kw: Optional[float] = Field(default=None, ge=0.0, description="Forecasted electrical load (kW)")
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence of model inference")
    reasons: List[str] = Field(default_factory=list, description="Explanations contributing to trust score")

    @field_validator("trust_status")
    @classmethod
    def validate_trust_status(cls, v: str) -> str:
        upper = v.upper()
        valid = [TRUST_STATUS_TRUSTED, TRUST_STATUS_ELEVATED_RISK, TRUST_STATUS_COMPROMISED]
        if upper not in valid:
            raise ValueError(f"trust_status must be one of {valid}, got: {v}")
        return upper

class PredictionResponse(PredictionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique prediction identifier")
    timestamp: datetime = Field(..., description="Timestamp of prediction")

class PredictionListResponse(BaseModel):
    total: int
    items: List[PredictionResponse]
