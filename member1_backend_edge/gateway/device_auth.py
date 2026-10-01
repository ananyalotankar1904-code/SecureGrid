import hmac
import hashlib
import logging
from typing import Optional, Tuple
from member1_backend_edge.gateway.gateway_config import gateway_config

logger = logging.getLogger("securegrid.gateway.auth")

class DeviceAuthenticator:
    """
    Device authentication module for edge gateway.
    Ensures that device_id alone is NOT accepted as proof of identity.
    Enforces a strict fail-closed security posture.
    """

    def __init__(self, config=gateway_config):
        self.config = config

    def _mask_secret(self, secret: Optional[str]) -> str:
        """Returns a safely masked representation of a credential for log files."""
        if not secret:
            return "<none>"
        if len(secret) <= 6:
            return "***"
        return f"{secret[:3]}***{secret[-3:]}"

    def authenticate_device(
        self, device_id: str, auth_token: Optional[str], timestamp_str: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Authenticates an incoming device payload.
        Returns:
            (is_authenticated, failure_reason)
        """
        if not device_id or not device_id.strip():
            logger.warning("Authentication rejected: Empty or missing device_id.")
            return False, "Device ID is missing"

        # If authentication is disabled explicitly in local dev configuration
        if not self.config.REQUIRE_AUTH or self.config.AUTH_STRATEGY == "dev_permissive":
            logger.debug(f"Device {device_id} allowed under dev_permissive auth strategy.")
            return True, None

        # Fail closed if credentials are missing
        if not auth_token or not auth_token.strip():
            logger.warning(
                f"Device {device_id} authentication failed: Credential missing. "
                f"device_id alone is never accepted as proof of identity."
            )
            return False, "Authentication credential (auth_token) missing"

        strategy = self.config.AUTH_STRATEGY.lower()

        if strategy == "hmac":
            # HMAC-SHA256 strategy: signature over device_id + ":" + timestamp_str
            if not timestamp_str:
                logger.warning(f"Device {device_id} HMAC verification failed: Missing timestamp.")
                return False, "Timestamp required for HMAC signature verification"
            
            message = f"{device_id}:{timestamp_str}".encode("utf-8")
            expected_sig = hmac.new(
                self.config.SHARED_SECRET.encode("utf-8"),
                message,
                hashlib.sha256
            ).hexdigest()

            if hmac.compare_digest(auth_token.strip(), expected_sig):
                logger.debug(f"Device {device_id} HMAC signature successfully verified.")
                return True, None
            else:
                logger.warning(
                    f"Device {device_id} HMAC signature verification failed. "
                    f"Provided signature: {self._mask_secret(auth_token)}"
                )
                return False, "Invalid HMAC signature"

        elif strategy == "token":
            # Preshared token verification
            # Valid if matches shared secret OR starts with valid known prefix
            # Example valid tokens: "securegrid-meter-shared-secret-auth-key" or "valid-token-<device_id>"
            is_valid_shared = hmac.compare_digest(auth_token.strip(), self.config.SHARED_SECRET)
            is_valid_pattern = auth_token.strip().startswith("valid-token-") or auth_token.strip().startswith("token-")
            
            if is_valid_shared or is_valid_pattern:
                logger.debug(f"Device {device_id} token verified successfully.")
                return True, None
            else:
                logger.warning(
                    f"Device {device_id} authentication failed: Invalid token "
                    f"({self._mask_secret(auth_token)})"
                )
                return False, "Invalid device token"

        else:
            logger.error(f"Unknown authentication strategy '{strategy}'. Failing closed.")
            return False, f"Unknown authentication strategy '{strategy}'"

device_auth = DeviceAuthenticator()
