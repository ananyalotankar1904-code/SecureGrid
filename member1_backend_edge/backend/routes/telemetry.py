from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from member1_backend_edge.backend.models.telemetry import (
    TelemetryPayload,
    TelemetryResponse,
    TelemetryListResponse,
)
from member1_backend_edge.backend.services.db_service import db_service
from member1_backend_edge.backend.services.ml_service import ml_service
from shared.config.constants import (
    DEVICE_STATUS_QUARANTINED,
    VOLTAGE_NOMINAL_V,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
)

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@router.post("", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED, summary="Ingest smart meter telemetry")
def ingest_telemetry(payload: TelemetryPayload):
    # 1. Check if device exists and if it is quarantined
    device = db_service.get_device(payload.device_id)
    if device and device.get("status") == DEVICE_STATUS_QUARANTINED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Device '{payload.device_id}' is currently QUARANTINED. Telemetry ingestion is rejected at the perimeter.",
        )

    # 2. Check for physical domain anomalies (e.g. extreme voltage surge or power/current contradiction)
    if payload.voltage > 260.0:
        db_service.save_security_event({
            "device_id": payload.device_id,
            "event_type": "VOLTAGE_SURGE_DETECTED",
            "severity": SEVERITY_HIGH,
            "description": f"Abnormal line voltage of {payload.voltage}V observed (Nominal: {VOLTAGE_NOMINAL_V}V).",
            "details": {
                "voltage": payload.voltage,
                "power_kw": payload.power_kw,
                "current": payload.current,
            },
            "mitigated": False,
        })

    if payload.failed_auth_attempts > 5:
        db_service.save_security_event({
            "device_id": payload.device_id,
            "event_type": "AUTH_FAILURE_FLOOD",
            "severity": SEVERITY_HIGH,
            "description": f"Consecutive failed authentication threshold exceeded: {payload.failed_auth_attempts} attempts.",
            "details": {"failed_auth_attempts": payload.failed_auth_attempts},
            "mitigated": False,
        })

    # 3. Persist telemetry record
    saved = db_service.save_telemetry(payload.model_dump())

    # 4. Optional ML analysis evaluation (if Member 2 module is loaded)
    ml_service.evaluate_telemetry(payload.model_dump())

    return TelemetryResponse(
        status="accepted",
        device_id=saved["device_id"],
        timestamp=saved["timestamp"],
        telemetry_id=saved["id"],
    )

@router.get("", response_model=TelemetryListResponse, summary="Query recent telemetry records across all meters")
def get_all_telemetry(
    limit: int = Query(50, ge=1, le=200, description="Max telemetry records"),
    offset: int = Query(0, ge=0, description="Offset"),
):
    items, total = db_service.get_telemetry(limit=limit, offset=offset)
    return TelemetryListResponse(total=total, items=items)

@router.get("/{device_id}", response_model=TelemetryListResponse, summary="Query telemetry time-series for a specific meter")
def get_device_telemetry(
    device_id: str,
    limit: int = Query(50, ge=1, le=200, description="Max telemetry records"),
    offset: int = Query(0, ge=0, description="Offset"),
):
    items, total = db_service.get_telemetry(device_id=device_id, limit=limit, offset=offset)
    return TelemetryListResponse(total=total, items=items)
