import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from member1_backend_edge.backend.config import settings
from member1_backend_edge.backend.services.db_service import db_service
from shared.config.constants import ALL_DEVICE_STATUSES, SEVERITY_HIGH, SEVERITY_CRITICAL

logger = logging.getLogger("securegrid.security")

class SecurityService:
    """Handles threat responses, containment actions, and administrative security authorizations."""

    def verify_admin_key(self, provided_key: Optional[str]) -> bool:
        """Verifies provided admin key against configured secret."""
        if not provided_key or provided_key.strip() != settings.ADMIN_API_KEY:
            return False
        return True

    def execute_containment_action(
        self, device_id: str, new_status: str, reason: Optional[str], admin_key: Optional[str]
    ) -> Dict[str, Any]:
        """
        Executes an authorized status transition (e.g., QUARANTINED, ACTIVE) on a target smart meter.
        Applies logical quarantine at the application and edge layer, and records an auditable event.
        """
        if not self.verify_admin_key(admin_key):
            logger.warning(f"Unauthorized containment attempt on device {device_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing X-Admin-Key header for sensitive threat response action.",
            )

        upper_status = new_status.upper()
        if upper_status not in ALL_DEVICE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid device status: {new_status}. Allowed: {ALL_DEVICE_STATUSES}",
            )

        device = db_service.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found in grid inventory.",
            )

        old_status = device.get("status", "UNKNOWN")
        updated_device = db_service.update_device_status(device_id, upper_status)

        # Record auditable security event
        severity = SEVERITY_CRITICAL if upper_status == "QUARANTINED" else SEVERITY_HIGH
        event_record = db_service.save_security_event({
            "device_id": device_id,
            "event_type": f"ADMIN_STATUS_{upper_status}",
            "severity": severity,
            "description": f"Logical device state changed from {old_status} to {upper_status}. Reason: {reason or 'No reason provided'}",
            "details": {
                "previous_status": old_status,
                "target_status": upper_status,
                "reason": reason,
                "action_type": "logical_containment",
            },
            "mitigated": True,
        })

        logger.info(f"Containment action executed: {device_id} set to {upper_status}")

        return {
            "success": True,
            "device_id": device_id,
            "previous_status": old_status,
            "new_status": upper_status,
            "event_id": event_record["id"],
            "message": f"Device {device_id} status updated to {upper_status}. Note: This represents logical quarantine in SecureGrid; physical grid contactor disconnect is disabled in prototype mode.",
        }

security_service = SecurityService()
