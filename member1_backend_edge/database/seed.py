"""
Database seeder for SecureGrid.
Inserts default smart meters, baseline trust scores, and normal telemetry records.
Supports seeding directly into Supabase (if credentials configured) or standard logging.
"""

import sys
import os
from datetime import datetime, timezone

# Add project root to sys.path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from member1_backend_edge.backend.config import settings
from member1_backend_edge.backend.services.db_service import db_service

SAMPLE_DEVICES = [
    {
        "device_id": "MTR-NYC-001",
        "device_name": "Residential Feeder 1A",
        "device_type": "residential_meter",
        "location": "Sector 4 Substation",
        "status": "ACTIVE",
        "ip_address": "192.168.1.101",
        "mac_address": "00:1B:44:11:3A:B7",
        "firmware_version": "v1.4.2",
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
    },
]

def seed_database():
    """Seed devices and baseline data into database."""
    print("Seeding SecureGrid database...")
    print(f"Supabase configured: {settings.is_supabase_configured}")

    for dev in SAMPLE_DEVICES:
        try:
            existing = db_service.get_device(dev["device_id"])
            if not existing:
                res = db_service.register_device(dev)
                print(f"  + Registered meter: {dev['device_id']} ({dev['device_name']})")
            else:
                print(f"  - Device {dev['device_id']} already registered.")
        except Exception as e:
            print(f"  x Failed to seed {dev['device_id']}: {e}")

    # Seed baseline trust score
    now = datetime.now(timezone.utc)
    for dev in SAMPLE_DEVICES:
        pred_data = {
            "device_id": dev["device_id"],
            "timestamp": now.isoformat(),
            "trust_score": 98.0,
            "trust_status": "TRUSTED",
            "anomaly_detected": False,
            "anomaly_type": None,
            "predicted_load_kw": 3.5,
            "confidence_score": 0.99,
            "reasons": ["Device in normal operational baseline", "0 failed auth attempts"],
        }
        db_service.save_prediction(pred_data)

    print("Seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
