"""
Adapter service for Member 2 ML & Trust Scoring module.
Provides an interface to invoke or ingest anomaly detection and trust calculations.
Maintains system resilience when Member 2's models are not yet imported.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("securegrid.ml_adapter")

class MLServiceAdapter:
    """Coordinates ML analysis and trust evaluation between Backend and Member 2's modules."""

    def __init__(self):
        self._ml_module = None
        self._integration_active = False
        self._check_member2_module()

    def _check_member2_module(self):
        """Attempts to dynamically load Member 2's ML module if implemented."""
        try:
            import member2_iot_ml # type: ignore
            self._ml_module = member2_iot_ml
            self._integration_active = True
            logger.info("Successfully connected to Member 2 ML module.")
        except ImportError:
            self._ml_module = None
            self._integration_active = False
            logger.info("Member 2 ML module not yet discovered. Operating in pending integration mode.")

    def get_integration_status(self) -> Dict[str, Any]:
        """Returns the current readiness and availability of Member 2's ML system."""
        return {
            "status": "connected" if self._integration_active else "pending_member2_module",
            "module": "member2_iot_ml",
            "connected": self._integration_active,
            "capabilities": [
                "energy_anomaly_detection",
                "network_flood_detection",
                "trust_score_engine",
                "load_forecasting",
            ] if self._integration_active else [],
        }

    def evaluate_telemetry(self, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Coordinates evaluation of fresh telemetry against ML models.
        If Member 2's engine is imported, invokes their pipeline.
        If not imported, gracefully returns None without fabricating false predictions.
        """
        if self._integration_active and hasattr(self._ml_module, "analyze_telemetry"):
            try:
                return self._ml_module.analyze_telemetry(telemetry)
            except Exception as e:
                logger.error(f"Error executing Member 2 analyze_telemetry: {e}")
                return None
        return None

ml_service = MLServiceAdapter()
