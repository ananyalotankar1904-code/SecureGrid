import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from member1_backend_edge.backend.config import settings

logger = logging.getLogger("securegrid.db")

class DatabaseService:
    """
    Persistence service supporting Supabase PostgreSQL with transparent in-memory fallback.
    Ensures backend and tests run smoothly even without live cloud credentials.
    """

    def __init__(self):
        self._supabase_client = None
        self._is_live = False
        self._memory_devices: Dict[str, Dict[str, Any]] = {}
        self._memory_telemetry: List[Dict[str, Any]] = []
        self._memory_security_events: List[Dict[str, Any]] = []
        self._memory_predictions: List[Dict[str, Any]] = []
        self._connection_error: Optional[str] = None
        
        self._initialize_client()
        if not self._is_live:
            self._preload_seed_data()

    def _initialize_client(self):
        """Attempts to initialize the Supabase client and verifies live connectivity with a test query."""
        if not settings.is_supabase_configured:
            logger.info("Supabase not configured or in dev placeholder mode. Using in-memory persistence.")
            self._supabase_client = None
            self._is_live = False
            self._connection_error = "SUPABASE_URL and SUPABASE_KEY are not configured in root .env"
            return

        try:
            from supabase import create_client
            client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
            # Execute a lightweight query to verify live network connectivity and table existence
            client.table("devices").select("device_id").limit(1).execute()
            self._supabase_client = client
            self._is_live = True
            self._connection_error = None
            logger.info("Supabase PostgreSQL client connected and live persistence verified successfully.")
        except Exception as e:
            self._supabase_client = None
            self._is_live = False
            err_str = str(e)
            
            # Parse error for clear, actionable diagnostics
            if "devices" in err_str.lower() and ("relation" in err_str.lower() or "not exist" in err_str.lower() or "pgrst205" in err_str.lower()):
                self._connection_error = (
                    "Connected to Supabase, but required table 'devices' was not found. "
                    "Run member1_backend_edge/database/schema.sql in the Supabase SQL Editor."
                )
            elif "401" in err_str or "unauthorized" in err_str.lower() or "invalid api key" in err_str.lower() or "jwt" in err_str.lower():
                self._connection_error = "Supabase authentication rejected: Invalid or expired SUPABASE_KEY."
            elif "getaddrinfo" in err_str or "connecterror" in err_str.lower():
                self._connection_error = f"Network connection failed for SUPABASE_URL: {settings.SUPABASE_URL}"
            else:
                self._connection_error = f"Supabase connection test failed: {err_str[:200]}"
            
            logger.warning(f"Supabase connection notice: {self._connection_error}. Operating in local memory fallback.")

    def _preload_seed_data(self):
        """Preloads standard mock smart meters into memory for local development."""
        now = datetime.now(timezone.utc).isoformat()
        initial_devices = [
            {
                "device_id": "MTR-NYC-001",
                "device_name": "Residential Feeder 1A",
                "device_type": "residential_meter",
                "location": "Sector 4 Substation",
                "status": "ACTIVE",
                "ip_address": "192.168.1.101",
                "mac_address": "00:1B:44:11:3A:B7",
                "firmware_version": "v1.4.2",
                "created_at": now,
                "updated_at": now,
            },
            {
                "device_id": "MTR-NYC-002",
                "device_name": "Residential Feeder 1B",
                "device_type": "residential_meter",
                "location": "Sector 4 Substation",
                "status": "ACTIVE",
                "ip_address": "192.168.1.102",
                "mac_address": "00:1B:44:11:3A:B8",
                "firmware_version": "v1.4.2",
                "created_at": now,
                "updated_at": now,
            },
            {
                "device_id": "MTR-NYC-003",
                "device_name": "Commercial Plaza Hub",
                "device_type": "commercial_meter",
                "location": "Sector 2 Industrial",
                "status": "ACTIVE",
                "ip_address": "192.168.1.103",
                "mac_address": "00:1B:44:11:3A:C1",
                "firmware_version": "v1.4.2",
                "created_at": now,
                "updated_at": now,
            },
        ]
        for dev in initial_devices:
            self._memory_devices[dev["device_id"]] = dev

    def get_health_status(self) -> Dict[str, Any]:
        """Returns database connectivity and operational status."""
        # Attempt reconnect if credentials were added to .env after startup
        if not self._is_live and settings.is_supabase_configured:
            self._initialize_client()

        health = {
            "status": "connected" if self._is_live else "local_memory_mode",
            "provider": "supabase_postgresql" if self._is_live else "in_memory_repository",
            "live_persistence_verified": self._is_live,
            "mock_mode": not self._is_live,
        }
        if self._is_live:
            health["supabase_url"] = settings.SUPABASE_URL
        else:
            health["diagnostics"] = {
                "supabase_configured": settings.is_supabase_configured,
                "reason": self._connection_error or "In-memory mock repository active",
            }
        return health

    # =========================================================================
    # Device Management
    # =========================================================================

    def get_devices(
        self, status: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        if self._is_live:
            try:
                query = self._supabase_client.table("devices").select("*", count="exact")
                if status:
                    query = query.eq("status", status.upper())
                query = query.range(offset, offset + limit - 1)
                res = query.execute()
                return res.data or [], res.count or len(res.data or [])
            except Exception as e:
                logger.error(f"Supabase get_devices error: {e}")

        # In-memory fallback
        all_devs = list(self._memory_devices.values())
        if status:
            all_devs = [d for d in all_devs if d.get("status") == status.upper()]
        total = len(all_devs)
        paginated = all_devs[offset : offset + limit]
        return paginated, total

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        if self._is_live:
            try:
                res = self._supabase_client.table("devices").select("*").eq("device_id", device_id).execute()
                if res.data:
                    return res.data[0]
                return None
            except Exception as e:
                logger.error(f"Supabase get_device error: {e}")

        return self._memory_devices.get(device_id)

    def register_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        dev_id = device_data["device_id"]
        
        record = {
            **device_data,
            "status": device_data.get("status", "ACTIVE").upper(),
            "created_at": device_data.get("created_at") or now,
            "updated_at": now,
        }

        if self._is_live:
            try:
                res = self._supabase_client.table("devices").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase register_device error: {e}")
                raise e

        # In-memory store
        self._memory_devices[dev_id] = record
        return record

    def update_device_status(self, device_id: str, new_status: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        upper_status = new_status.upper()

        if self._is_live:
            try:
                res = (
                    self._supabase_client.table("devices")
                    .update({"status": upper_status, "updated_at": now})
                    .eq("device_id", device_id)
                    .execute()
                )
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase update_device_status error: {e}")

        # In-memory store
        if device_id in self._memory_devices:
            self._memory_devices[device_id]["status"] = upper_status
            self._memory_devices[device_id]["updated_at"] = now
            return self._memory_devices[device_id]
        return None

    # =========================================================================
    # Telemetry Operations
    # =========================================================================

    def save_telemetry(self, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        record = {
            "id": telemetry_data.get("id") or str(uuid.uuid4()),
            "device_id": telemetry_data["device_id"],
            "timestamp": telemetry_data["timestamp"] if isinstance(telemetry_data["timestamp"], str) else telemetry_data["timestamp"].isoformat(),
            "power_kw": float(telemetry_data["power_kw"]),
            "voltage": float(telemetry_data["voltage"]),
            "current": float(telemetry_data["current"]),
            "request_rate": float(telemetry_data.get("request_rate", 1.0)),
            "failed_auth_attempts": int(telemetry_data.get("failed_auth_attempts", 0)),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if self._is_live:
            try:
                res = self._supabase_client.table("telemetry").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase save_telemetry error: {e}")

        # In-memory store
        self._memory_telemetry.append(record)
        return record

    def get_telemetry(
        self, device_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        if self._is_live:
            try:
                query = self._supabase_client.table("telemetry").select("*", count="exact")
                if device_id:
                    query = query.eq("device_id", device_id)
                query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
                res = query.execute()
                return res.data or [], res.count or len(res.data or [])
            except Exception as e:
                logger.error(f"Supabase get_telemetry error: {e}")

        filtered = self._memory_telemetry
        if device_id:
            filtered = [t for t in self._memory_telemetry if t.get("device_id") == device_id]
        
        # Sort newest first
        sorted_records = sorted(filtered, key=lambda x: str(x.get("timestamp")), reverse=True)
        total = len(sorted_records)
        paginated = sorted_records[offset : offset + limit]
        return paginated, total

    # =========================================================================
    # Security Events
    # =========================================================================

    def save_security_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        raw_id = event_data.get("id")
        try:
            if raw_id:
                event_id = str(uuid.UUID(str(raw_id)))
            else:
                event_id = str(uuid.uuid4())
        except (ValueError, AttributeError):
            event_id = str(uuid.uuid4())

        record = {
            "id": event_id,
            "device_id": event_data["device_id"],
            "event_type": event_data["event_type"],
            "severity": event_data.get("severity", "MEDIUM").upper(),
            "description": event_data["description"],
            "details": event_data.get("details", {}),
            "mitigated": event_data.get("mitigated", False),
            "timestamp": event_data.get("timestamp") or now,
            "created_at": now,
        }

        if self._is_live:
            try:
                res = self._supabase_client.table("security_events").insert(record).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase save_security_event error: {e}")

        self._memory_security_events.append(record)
        return record

    def get_security_events(
        self,
        device_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        if self._is_live:
            try:
                query = self._supabase_client.table("security_events").select("*", count="exact")
                if device_id:
                    query = query.eq("device_id", device_id)
                if severity:
                    query = query.eq("severity", severity.upper())
                query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
                res = query.execute()
                return res.data or [], res.count or len(res.data or [])
            except Exception as e:
                logger.error(f"Supabase get_security_events error: {e}")

        filtered = self._memory_security_events
        if device_id:
            filtered = [e for e in filtered if e.get("device_id") == device_id]
        if severity:
            filtered = [e for e in filtered if e.get("severity") == severity.upper()]

        sorted_records = sorted(filtered, key=lambda x: str(x.get("timestamp")), reverse=True)
        total = len(sorted_records)
        paginated = sorted_records[offset : offset + limit]
        return paginated, total

    # =========================================================================
    # Predictions & Trust Scores
    # =========================================================================

    def save_prediction(self, pred_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Saves a prediction record.
        - Trust score information is persisted to the 'trust_scores' table.
        - Load forecast data is persisted to the 'load_predictions' table when
          both 'predicted_load_kw' and 'confidence_score' are provided.
        - Appends to in-memory store and returns the normalized record.
        """
        # 1. Normalize timestamp to ISO 8601 string
        ts_val = pred_data.get("timestamp")
        if isinstance(ts_val, datetime):
            if ts_val.tzinfo is None:
                ts_val = ts_val.replace(tzinfo=timezone.utc)
            ts_str = ts_val.isoformat()
        elif isinstance(ts_val, str) and ts_val.strip():
            ts_str = ts_val.strip()
        else:
            ts_str = datetime.now(timezone.utc).isoformat()

        # 2. Build normalized prediction record
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": pred_data.get("id") or f"prd-{uuid.uuid4().hex[:8]}",
            "device_id": str(pred_data["device_id"]),
            "timestamp": ts_str,
            "trust_score": float(pred_data["trust_score"]),
            "trust_status": str(pred_data["trust_status"]).upper(),
            "anomaly_detected": bool(pred_data.get("anomaly_detected", False)),
            "anomaly_type": pred_data.get("anomaly_type"),
            "predicted_load_kw": float(pred_data["predicted_load_kw"]) if pred_data.get("predicted_load_kw") is not None else None,
            "confidence_score": float(pred_data["confidence_score"]) if pred_data.get("confidence_score") is not None else None,
            "reasons": list(pred_data.get("reasons", [])),
            "created_at": now,
        }

        # 3. Live Supabase persistence with isolated try/except blocks
        if self._is_live and self._supabase_client:
            # Table 1: trust_scores (exact columns from schema.sql)
            try:
                trust_payload = {
                    "device_id": record["device_id"],
                    "timestamp": record["timestamp"],
                    "trust_score": record["trust_score"],
                    "trust_status": record["trust_status"],
                    "anomaly_detected": record["anomaly_detected"],
                    "anomaly_type": record["anomaly_type"],
                    "reasons": record["reasons"],
                }
                res_trust = self._supabase_client.table("trust_scores").insert(trust_payload).execute()
                if res_trust.data and len(res_trust.data) > 0 and "id" in res_trust.data[0]:
                    record["id"] = str(res_trust.data[0]["id"])
                logger.info(f"Supabase trust_score inserted successfully for device '{record['device_id']}'.")
            except Exception as e:
                logger.error(f"Failed to insert trust_score into Supabase: {e}", exc_info=True)

            # Table 2: load_predictions (exact columns from schema.sql)
            # Only inserted when both predicted_load_kw and confidence_score are provided
            if record.get("predicted_load_kw") is not None and record.get("confidence_score") is not None:
                try:
                    load_payload = {
                        "device_id": record["device_id"],
                        "timestamp": record["timestamp"],
                        "predicted_load_kw": record["predicted_load_kw"],
                        "confidence_score": record["confidence_score"],
                    }
                    res_load = self._supabase_client.table("load_predictions").insert(load_payload).execute()
                    logger.info(f"Supabase load_prediction inserted successfully for device '{record['device_id']}'.")
                except Exception as e:
                    logger.error(f"Failed to insert load_prediction into Supabase: {e}", exc_info=True)

        # 4. In-memory append for test & fallback continuity
        self._memory_predictions.append(record)
        return record

    def get_predictions(
        self,
        device_id: Optional[str] = None,
        trust_status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieves prediction history.
        When live mode is enabled, queries Supabase 'trust_scores' joined with 'load_predictions'.
        Falls back to in-memory store if offline or query encounters an error.
        """
        if self._is_live and self._supabase_client:
            try:
                # Query trust_scores as the primary evaluation history
                query = self._supabase_client.table("trust_scores").select("*", count="exact")
                if device_id:
                    query = query.eq("device_id", device_id)
                if trust_status:
                    query = query.eq("trust_status", trust_status.upper())
                query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
                res_trust = query.execute()
                trust_rows = res_trust.data or []
                total = res_trust.count if res_trust.count is not None else len(trust_rows)

                if trust_rows:
                    dev_ids = list({row["device_id"] for row in trust_rows if "device_id" in row})
                    load_res = (
                        self._supabase_client.table("load_predictions")
                        .select("*")
                        .in_("device_id", dev_ids)
                        .order("timestamp", desc=True)
                        .execute()
                    )
                    load_rows = load_res.data or []

                    # Build mapping for quick lookup: (device_id, timestamp) and device_id fallback
                    load_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
                    dev_latest_load: Dict[str, Dict[str, Any]] = {}
                    for lr in load_rows:
                        did = lr.get("device_id")
                        ts = str(lr.get("timestamp"))
                        if (did, ts) not in load_map:
                            load_map[(did, ts)] = lr
                        if did not in dev_latest_load:
                            dev_latest_load[did] = lr

                    results = []
                    for tr in trust_rows:
                        did = tr.get("device_id")
                        ts = str(tr.get("timestamp"))
                        matched_load = load_map.get((did, ts)) or dev_latest_load.get(did)
                        
                        item = {
                            "id": str(tr.get("id")),
                            "device_id": did,
                            "timestamp": tr.get("timestamp"),
                            "trust_score": float(tr.get("trust_score", 100.0)),
                            "trust_status": tr.get("trust_status", "TRUSTED"),
                            "anomaly_detected": bool(tr.get("anomaly_detected", False)),
                            "anomaly_type": tr.get("anomaly_type"),
                            "predicted_load_kw": float(matched_load["predicted_load_kw"]) if matched_load and matched_load.get("predicted_load_kw") is not None else None,
                            "confidence_score": float(matched_load["confidence_score"]) if matched_load and matched_load.get("confidence_score") is not None else None,
                            "reasons": tr.get("reasons") or [],
                        }
                        results.append(item)
                    return results, total

                # If no trust_scores rows exist yet, check load_predictions (only if no trust_status filter applied)
                if not trust_status:
                    l_query = self._supabase_client.table("load_predictions").select("*", count="exact")
                    if device_id:
                        l_query = l_query.eq("device_id", device_id)
                    l_query = l_query.order("timestamp", desc=True).range(offset, offset + limit - 1)
                    res_load = l_query.execute()
                    load_rows = res_load.data or []
                    if load_rows:
                        results = []
                        for lr in load_rows:
                            results.append({
                                "id": str(lr.get("id")),
                                "device_id": lr.get("device_id"),
                                "timestamp": lr.get("timestamp"),
                                "trust_score": 100.0,
                                "trust_status": "TRUSTED",
                                "anomaly_detected": False,
                                "anomaly_type": None,
                                "predicted_load_kw": float(lr["predicted_load_kw"]) if lr.get("predicted_load_kw") is not None else None,
                                "confidence_score": float(lr["confidence_score"]) if lr.get("confidence_score") is not None else None,
                                "reasons": [],
                            })
                        return results, res_load.count if res_load.count is not None else len(results)

                return [], 0
            except Exception as e:
                logger.error(f"Supabase get_predictions error: {e}", exc_info=True)

        # In-memory fallback
        filtered = self._memory_predictions
        if device_id:
            filtered = [p for p in filtered if p.get("device_id") == device_id]
        if trust_status:
            filtered = [p for p in filtered if p.get("trust_status") == trust_status.upper()]

        sorted_records = sorted(filtered, key=lambda x: str(x.get("timestamp")), reverse=True)
        total = len(sorted_records)
        paginated = sorted_records[offset : offset + limit]
        return paginated, total


# Global singleton instance
db_service = DatabaseService()
