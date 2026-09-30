import json
import unittest
from member2_iot_ml.simulator.telemetry_generator import generate_telemetry
from member2_iot_ml.integration.frontend_adapter import process_for_frontend

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.device_id = "test_meter"

    def test_normal_telemetry(self):
        tel = generate_telemetry(self.device_id, "normal", seed=10)
        res = process_for_frontend(tel)
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertEqual(data["security"]["trust_status"], "TRUSTED")
        self.assertEqual(data["security"]["recommended_action"], "ALLOW")
        self.assertEqual(len(data["security"]["anomalies"]), 0)
        self.assertIn("predicted_load_kw", data["prediction"])

    def test_energy_anomaly(self):
        tel = generate_telemetry(self.device_id, "energy_anomaly", seed=11)
        res = process_for_frontend(tel)
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertEqual(data["security"]["trust_status"], "SUSPICIOUS")
        self.assertEqual(data["security"]["recommended_action"], "MONITOR")
        self.assertIn("ENERGY_ANOMALY", data["security"]["anomalies"])

    def test_network_anomaly(self):
        tel = generate_telemetry(self.device_id, "network_anomaly", seed=12)
        res = process_for_frontend(tel)
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertEqual(data["security"]["trust_status"], "SUSPICIOUS")
        self.assertEqual(data["security"]["recommended_action"], "MONITOR")
        self.assertIn("NETWORK_ANOMALY", data["security"]["anomalies"])

    def test_full_compromise(self):
        tel = generate_telemetry(self.device_id, "compromised", seed=13)
        res = process_for_frontend(tel)
        self.assertTrue(res["success"])
        data = res["data"]
        self.assertEqual(data["security"]["trust_status"], "HIGH_RISK")
        self.assertEqual(data["security"]["recommended_action"], "QUARANTINE")
        self.assertIn("ENERGY_ANOMALY", data["security"]["anomalies"])
        self.assertIn("NETWORK_ANOMALY", data["security"]["anomalies"])
        self.assertIn("AUTH_ANOMALY", data["security"]["anomalies"])

    def test_malformed_telemetry(self):
        tel = {"device_id": self.device_id, "power_kw": "not_a_number"}
        res = process_for_frontend(tel)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "Invalid telemetry")
        self.assertTrue(len(res["details"]) > 0)

if __name__ == "__main__":
    unittest.main()
