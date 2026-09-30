# SecureGrid — Member 3 Frontend

A professional Smart Grid Cybersecurity Operations Center (SOC) dashboard built with React, Vite, and Recharts.

## Core Security Pipeline Visualized

```
Telemetry → Anomaly Detection (Energy / Network / Auth) → Combined Analysis → Dynamic Trust Score → Security Event → Recommendation (ALLOW / MONITOR / RESTRICT / QUARANTINE)
```

## Features

- **SOC Security Header**: Real-time connection indicator (Live API vs Demo Data mode), system status, last refresh timestamp, and manual refresh controls.
- **KPI Summary Metrics**: Interactive filterable KPI cards (Total Devices, Healthy, Active Threats, Under Monitoring, Quarantined, Avg Trust Score).
- **Device Security Overview (`DeviceTable.jsx`)**: Search, filter by status/recommendation/anomaly, sortable table with status badges and quick action modal trigger.
- **Dynamic Trust Score Gauge (`TrustScore.jsx`)**: 0–100 Trust Score visualization with decision recommendations (ALLOW, MONITOR, RESTRICT, QUARANTINE) and trend history.
- **Time-Series Energy Telemetry (`EnergyChart.jsx`)**: Active load (kW), baseline expectations, voltage, current, and selectable time windows (15 min, 1h, 6h, 24h).
- **EWMA Load Prediction (`PredictionChart.jsx`)**: 15-minute load forecasting comparing actual load against EWMA baseline forecast.
- **Threat Stream Panel (`ThreatPanel.jsx`)**: Live security event feed with severity filters and threat details.
- **Anomaly Breakdown (`AnomalyBreakdown.jsx`)**: Distribution chart across Energy, Network, DDoS, Authentication, and Combined anomalies.
- **Device Detail Inspector (`DeviceDetail.jsx`)**: Deep-dive operational view showing telemetry, anomaly breakdowns, security events, trust score history, and exact diagnostic reasons why a device is flagged.

## Getting Started

### Installation

```bash
cd securegrid/member3_frontend
npm install
```

### Running Locally

```bash
npm run dev
```

The application will launch locally at `http://localhost:3000`.

### Backend API Configuration

By default, the dashboard operates in **DEMO DATA** mode if no backend server is detected. To point to a live backend (Member 1 / Member 2 API):

Set the environment variable in `.env` or run with:
```bash
VITE_API_URL=http://localhost:5000/api npm run dev
```
