from member1_backend_edge.backend.routes.devices import router as devices_router
from member1_backend_edge.backend.routes.telemetry import router as telemetry_router
from member1_backend_edge.backend.routes.security import router as security_router
from member1_backend_edge.backend.routes.predictions import router as predictions_router

__all__ = [
    "devices_router",
    "telemetry_router",
    "security_router",
    "predictions_router",
]
