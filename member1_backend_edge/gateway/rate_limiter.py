import time
import threading
import logging
from typing import Dict, Tuple, Any
from member1_backend_edge.gateway.gateway_config import gateway_config

logger = logging.getLogger("securegrid.gateway.ratelimit")

class TokenBucketRateLimiter:
    """
    In-memory Token Bucket rate limiter per device identifier.
    
    IMPORTANT ARCHITECTURAL LIMITATION:
    This rate limiter state is stored entirely in local process memory.
    It protects this specific edge gateway node against local DDoS floods and broadcast storms.
    It is NOT distributed across multiple gateway or backend replicas. For multi-node distributed
    deployments, a distributed cache like Redis or Valkey should be used.
    """

    def __init__(
        self,
        rate_per_minute: int = gateway_config.RATE_LIMIT_MAX_PER_MINUTE,
        burst_capacity: int = gateway_config.RATE_LIMIT_BURST_CAPACITY,
    ):
        self.rate_per_second = rate_per_minute / 60.0
        self.burst_capacity = float(burst_capacity)
        # Device buckets: { device_id: {"tokens": float, "last_updated": float} }
        self._buckets: Dict[str, Dict[str, float]] = {}
        self._lock = threading.Lock()

    def check_rate_limit(self, device_id: str, cost: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluates whether a message transmission from device_id is permitted.
        Returns:
            (allowed: bool, details: dict)
        """
        with self._lock:
            now = time.time()

            if device_id not in self._buckets:
                self._buckets[device_id] = {
                    "tokens": self.burst_capacity,
                    "last_updated": now,
                }

            bucket = self._buckets[device_id]
            elapsed = now - bucket["last_updated"]
            bucket["last_updated"] = now

            # Refill tokens based on elapsed time up to burst capacity
            bucket["tokens"] = min(
                self.burst_capacity,
                bucket["tokens"] + elapsed * self.rate_per_second
            )

            if bucket["tokens"] >= cost:
                bucket["tokens"] -= cost
                return True, {
                    "allowed": True,
                    "remaining_tokens": round(bucket["tokens"], 2),
                    "device_id": device_id,
                }
            else:
                logger.warning(
                    f"Rate limit exceeded for device '{device_id}'. "
                    f"Available tokens: {bucket['tokens']:.2f}, Cost required: {cost}"
                )
                return False, {
                    "allowed": False,
                    "remaining_tokens": round(bucket["tokens"], 2),
                    "device_id": device_id,
                    "retry_after_seconds": round((cost - bucket["tokens"]) / self.rate_per_second, 2),
                }

    def reset(self, device_id: Optional[str] = None):
        """Resets rate limit bucket for testing."""
        with self._lock:
            if device_id:
                self._buckets.pop(device_id, None)
            else:
                self._buckets.clear()

rate_limiter = TokenBucketRateLimiter()
