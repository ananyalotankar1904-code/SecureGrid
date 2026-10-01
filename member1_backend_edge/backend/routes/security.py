from typing import Optional
from fastapi import APIRouter, Query, status
from member1_backend_edge.backend.models.security import (
    SecurityEventCreate,
    SecurityEventResponse,
    SecurityEventListResponse,
)
from member1_backend_edge.backend.services.db_service import db_service

router = APIRouter(prefix="/security", tags=["Security Events & Threat Response"])

@router.get("/events", response_model=SecurityEventListResponse, summary="Query grid security events and alerts")
def list_security_events(
    severity: Optional[str] = Query(None, description="Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    items, total = db_service.get_security_events(severity=severity, limit=limit, offset=offset)
    return SecurityEventListResponse(total=total, items=items)

@router.get("/events/{device_id}", response_model=SecurityEventListResponse, summary="Query security events for a specific meter")
def get_device_security_events(
    device_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    items, total = db_service.get_security_events(device_id=device_id, severity=severity, limit=limit, offset=offset)
    return SecurityEventListResponse(total=total, items=items)

@router.post("/events", response_model=SecurityEventResponse, status_code=status.HTTP_201_CREATED, summary="Log a security event or anomaly")
def log_security_event(payload: SecurityEventCreate):
    saved = db_service.save_security_event(payload.model_dump())
    return saved
