# SecureGrid - Member 2: IoT Simulator & ML Engines

This folder contains the work for Member 2 in the SecureGrid hackathon project. It handles device simulation, anomaly detection, dynamic trust scoring, and basic load prediction.

## 1. What Member 2 Owns
- **IoT Simulator**: Generates realistic and abnormal smart meter telemetry.
- **Attack Simulation**: Triggers network and energy attacks to demonstrate dynamic response.
- **Anomaly Detection**: Evaluates incoming telemetry against thresholds to detect abnormal patterns.
- **Trust Engine**: Calculates a continuous 0-100 trust score to determine device trustworthiness. DOES NOT execute quarantine.
- **Load Prediction**: Provides an Exponentially Weighted Moving Average (EWMA) forecast for the React dashboard.

*(Member 2 does NOT own the API backend, authentication, database, edge gateway, or frontend dashboard).*

## 2. Folder Structure
- `simulator/` - Telemetry generation and MQTT publishing
- `attacks/` - Scripts to toggle attack modes (DDoS, compromised)
- `anomaly_detection/` - Core logic for energy & network anomalies
- `trust_engine/` - Logic for dynamic trust score assessment and security events
- `prediction/` - EWMA ML model for load forecasting

## 3. Telemetry Schema
All components consume and produce data based on this canonical structure:

```json
{
  "device_id": "meter_01",
  "timestamp": "2026-09-30T14:00:00",
  "power_kw": 5.2,
  "voltage": 230.0,
  "current": 22.6,
  "request_rate": 5,
  "failed_auth_attempts": 0
}
```

## 4. Normal Behavior
- **Power**: ~3–7 kW
- **Voltage**: ~220–240 V
- **Request Rate**: ~2–8 requests/sec
- **Failed Auth**: 0

## 5. Attack Scenarios
Using the attack simulator, we can switch devices to:
- **ENERGY ANOMALY**: High power consumption (15-30 kW).
- **NETWORK ANOMALY**: High request rate (500-1000 requests/sec).
- **AUTH ATTACK**: Elevated failed authentication attempts (5-20).
- **COMPROMISED**: All of the above combined.

## 6. Anomaly Detection Methodology
The anomaly engine combines:
- Energy thresholds (power_kw > 10.0 kW).
- Network thresholds (request_rate > 50, failed_auth > 3).
It outputs a severity of LOW, MEDIUM, or HIGH, mapping specific reasons.

## 7. Trust-Score Methodology
Calculates a 0-100 score weighing:
- 40% Network behavior
- 30% Energy behavior
- 20% Security behavior
- 10% Historical baseline
Statuses:
- **85-100**: TRUSTED
- **50-84**: SUSPICIOUS
- **0-49**: HIGH_RISK

## 8. Security Events
Generates an actionable JSON event recommending an action (ALLOW, MONITOR, RESTRICT, QUARANTINE) based on trust score and anomalies. **Only the Backend executes the quarantine.**

## 9. Prediction Methodology
Uses an EWMA (Exponentially Weighted Moving Average) model that keeps historical state to predict the electrical load 15 minutes into the future with low computational cost and no GPU requirements.

## 10. How to Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `paho-mqtt`, `python-dotenv`, `numpy`)*

## 11. How to Run Locally (Simulator)
Update your `.env` or configuration in `simulator/config.py`. You do NOT need a running MQTT broker; it will default to a local printing simulation if connection fails.
```bash
python -m simulator.device_simulator
```

## 12. How to Run Tests
```bash
python test_end_to_end.py
```

## 13. Integration Interfaces
Member 1 (FastAPI Backend) can import the evaluation functions directly in their API route:

```python
from member2_iot_ml.anomaly_detection.anomaly_engine import analyze_telemetry
from member2_iot_ml.trust_engine.trust_score import calculate_trust_score
from member2_iot_ml.trust_engine.security_event import generate_security_event

anomaly_result = analyze_telemetry(telemetry)
trust_result = calculate_trust_score(anomaly_result)
security_event = generate_security_event(telemetry, anomaly_result, trust_result)

if security_event["recommended_action"] == "QUARANTINE":
    execute_quarantine(device_id)
```

## 14. How Member 3 Consumes Outputs
Member 3 (React Dashboard) expects JSON. The `predict_load(telemetry)` function from `member2_iot_ml.prediction.load_prediction` returns a structured dict suitable for `json.dumps()`:
```json
{
  "timestamp": "2026-09-30T14:15:00",
  "predicted_load_kw": 5.8,
  "confidence": 0.85
}
```
