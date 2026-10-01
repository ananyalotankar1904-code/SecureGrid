from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Query, status
from member1_backend_edge.backend.models.device import (
    DeviceCreate,
    DeviceResponse,
    DeviceListResponse,
    DeviceStatusUpdate,
)
from member1_backend_edge.backend.services.db_service import db_service
from member1_backend_edge.backend.services.security_service import security_service

router = APIRouter(prefix="/devices", tags=["Devices"])

@router.get("", response_model=DeviceListResponse, summary="List all registered smart meters")
def list_devices(
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, SUSPICIOUS, QUARANTINED, OFFLINE)"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Record pagination offset"),
):
    items, total = db_service.get_devices(status=status, limit=limit, offset=offset)
    return DeviceListResponse(total=total, items=items)

@router.post("/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Register a new smart meter")
def register_device(payload: DeviceCreate):
    existing = db_service.get_device(payload.device_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with ID '{payload.device_id}' is already registered.",
        )
    created = db_service.register_device(payload.model_dump())
    return created

@router.get("/{device_id}", response_model=DeviceResponse, summary="Get details for a specific smart meter")
def get_device(device_id: str):
    device = db_service.get_device(device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' was not found in registry.",
        )
    return device

@router.post("/{device_id}/status", summary="Update device containment status (Quarantine / Reactivate)")
def update_device_status(
    device_id: str,
    payload: DeviceStatusUpdate,
    x_admin_key: Optional[str] = Header(None, description="Administrative authorization API key"),
):
    """
    Administrative endpoint for threat mitigation.
    Applies logical containment or reactivation and registers an auditable security event.
    """
    result = security_service.execute_containment_action(
        device_id=device_id,
        new_status=payload.status,
        reason=payload.reason,
        admin_key=x_admin_key,
    )
    return result
