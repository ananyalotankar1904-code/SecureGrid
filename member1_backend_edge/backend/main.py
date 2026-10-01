import logging
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from member1_backend_edge.backend.config import settings
from member1_backend_edge.backend.services.db_service import db_service
from member1_backend_edge.backend.services.ml_service import ml_service
from member1_backend_edge.backend.routes import (
    devices_router,
    telemetry_router,
    security_router,
    predictions_router,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("securegrid.main")

# Initialize FastAPI application
app = FastAPI(
    title="SecureGrid Edge Backend & Telemetry Ingestion API",
    description=(
        "Trust-aware cybersecurity prototype backend for smart electrical grids. "
        "Provides edge telemetry ingestion, device authentication, rate-limiting enforcement, "
        "PostgreSQL persistence, and threat containment controls."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS) for Member 3 Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(devices_router)
app.include_router(telemetry_router)
app.include_router(security_router)
app.include_router(predictions_router)

# Custom Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Provide clean, structured error responses for schema validation failures."""
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        errors.append({
            "field": field,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    logger.warning(f"Payload validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Incoming payload failed schema or range constraints.",
            "details": errors,
        },
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch unhandled errors and return a standardized JSON response."""
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request.",
        },
    )

# Root Endpoint
@app.get("/", tags=["System"])
def root_info():
    """Returns basic API info, version, and navigation links."""
    return {
        "service": "SecureGrid Edge Backend",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoints": {
            "health": "/health",
            "devices": "/devices",
            "telemetry": "/telemetry",
            "security_events": "/security/events",
            "predictions": "/predictions",
        },
    }

# Health Check Endpoint
@app.get("/health", tags=["System"])
def health_check():
    """
    Evaluates backend health and diagnoses connectivity to persistence and edge brokers.
    Distinguishes application availability from external service connectivity.
    """
    db_health = db_service.get_health_status()
    ml_health = ml_service.get_integration_status()

    # Application is always 'healthy' if it can serve REST requests; component statuses report degraded or mock mode
    overall_status = "healthy"
    
    return {
        "status": overall_status,
        "service": "SecureGrid Backend",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
        "components": {
            "database": db_health,
            "mqtt_gateway": {
                "broker": f"{settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}",
                "topic": settings.MQTT_TOPIC,
                "tls_enabled": settings.MQTT_USE_TLS,
                "configured": True,
            },
            "ml_anomaly_detection": ml_health,
        },
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("member1_backend_edge.backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
