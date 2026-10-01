from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status
from member1_backend_edge.backend.models.prediction import (
    PredictionCreate,
    PredictionResponse,
    PredictionListResponse,
)
from member1_backend_edge.backend.services.db_service import db_service
from member1_backend_edge.backend.services.ml_service import ml_service

router = APIRouter(prefix="/predictions", tags=["ML Predictions & Trust Scores"])

@router.get("", response_model=PredictionListResponse, summary="Query trust scores and load forecasts")
def list_predictions(
    trust_status: Optional[str] = Query(None, description="Filter by trust_status (TRUSTED, ELEVATED_RISK, COMPROMISED)"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    items, total = db_service.get_predictions(trust_status=trust_status, limit=limit, offset=offset)
    return PredictionListResponse(total=total, items=items)

@router.get("/status", summary="Check Member 2 ML integration status")
def get_ml_status():
    """Returns whether Member 2's ML module has been discovered and imported."""
    return ml_service.get_integration_status()

@router.get("/{device_id}", response_model=PredictionResponse, summary="Get latest trust score and prediction for a meter")
def get_device_prediction(device_id: str):
    items, total = db_service.get_predictions(device_id=device_id, limit=1)
    if not items:
        # If no explicit prediction exists yet, construct a default baseline
        device = db_service.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device '{device_id}' not found.",
            )
        baseline = {
            "id": f"prd-base-{device_id}",
            "device_id": device_id,
            "trust_score": 100.0 if device.get("status") == "ACTIVE" else 40.0,
            "trust_status": "TRUSTED" if device.get("status") == "ACTIVE" else "COMPROMISED",
            "anomaly_detected": device.get("status") != "ACTIVE",
            "anomaly_type": None,
            "predicted_load_kw": 3.0,
            "confidence_score": 0.95,
            "reasons": ["Default baseline evaluation", f"Status: {device.get('status')}"],
        }
        saved = db_service.save_prediction(baseline)
        return saved
    return items[0]

@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED, summary="Submit ML inference results or trust score")
def submit_prediction(payload: PredictionCreate):
    saved = db_service.save_prediction(payload.model_dump())
    
    # If the ML module reported high-risk or compromised status, flag a security event
    if saved.get("trust_score", 100) < 50.0 or saved.get("anomaly_detected"):
        db_service.save_security_event({
            "device_id": saved["device_id"],
            "event_type": "ML_ANOMALY_ALERT",
            "severity": "HIGH",
            "description": f"Trust score degraded to {saved['trust_score']:.1f} ({saved['trust_status']}). Reasons: {', '.join(saved.get('reasons', []))}",
            "details": {
                "trust_score": saved["trust_score"],
                "trust_status": saved["trust_status"],
                "anomaly_type": saved.get("anomaly_type"),
                "reasons": saved.get("reasons"),
            },
            "mitigated": False,
        })

    return saved
