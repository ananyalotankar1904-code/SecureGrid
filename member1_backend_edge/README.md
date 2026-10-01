# Member 1: Backend + Raspberry Pi + Edge Gateway Module

## 📋 Responsibilities
As **Member 1 Lead**, this module implements the telemetry ingestion and persistence pipeline:
1. **Edge Gateway** (`gateway/`):
   - Ingests raw smart meter readings via MQTT (or fallback HTTP).
   - Validates physical electrical boundaries and JSON schema.
   - Authenticates smart meters (token / HMAC) with fail-closed security.
   - Enforces token bucket rate limiting to prevent denial-of-service floods.
2. **FastAPI Backend** (`backend/`):
   - Exposes REST endpoints for devices, telemetry, security events, and ML predictions.
   - Health diagnostics distinguishing application availability from external connectivity.
   - CORS middleware configured for Member 3's React dashboard.
   - Administrative threat mitigation (quarantine and reactivation).
3. **Database Layer** (`database/`):
   - Supabase PostgreSQL schema (`database/schema.sql`) and seeder (`database/seed.py`).
   - Clean persistence service layer (`db_service.py`) supporting both live Supabase and transparent in-memory fallback for local development without credentials.
4. **Teammate Integration Points**:
   - Ingestion contract with **Member 2** ML module (`services/ml_service.py`).
   - Clean, validated REST APIs for **Member 3** frontend dashboard.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` in the repository root and adjust as necessary:

```bash
# Backend REST API
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Admin Key for Threat Containment (Quarantine)
ADMIN_API_KEY=securegrid-admin-dev-secret-key-32chars
DEVICE_SHARED_SECRET=securegrid-meter-shared-secret-auth-key

# Supabase PostgreSQL (Leave placeholder for in-memory dev mode)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-key

# MQTT Broker (Raspberry Pi or Laptop)
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_TOPIC=securegrid/telemetry/#
MQTT_CLIENT_ID=securegrid-edge-gateway
MQTT_USE_TLS=false
```

---

## 🚀 Running the Services

### 1. Run the FastAPI REST Backend
From the repository root:
```bash
python -m uvicorn member1_backend_edge.backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Root info: `http://localhost:8000/`

### 2. Run the MQTT Edge Gateway
```bash
python -m member1_backend_edge.gateway.mqtt_subscriber
```
The gateway will:
- Connect to the configured MQTT broker (or report fallback status if offline).
- Subscribe to `securegrid/telemetry/#`.
- Validate each incoming message through Auth -> Rate Limiting -> Schema Range Checks.
- Forward approved packets to `POST /telemetry` on the backend.

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 🗄️ Supabase PostgreSQL Setup

1. Log in to [Supabase](https://supabase.com) and create a new project.
2. In the Supabase Dashboard, navigate to **SQL Editor** -> **New query**.
3. Open `member1_backend_edge/database/schema.sql`, copy all contents, paste into the SQL editor, and click **Run**.
4. Retrieve your **Project URL** and **anon/service_role key** from **Project Settings** -> **API**.
5. Set `SUPABASE_URL` and `SUPABASE_KEY` in your `.env` file.
6. Seed initial devices:
   ```bash
   python -m member1_backend_edge.database.seed
   ```
*Note: If Supabase credentials are not configured or the network is offline, the backend automatically operates in in-memory mode, ensuring hackathon demos and unit tests never block.*

---

## 🍓 Raspberry Pi Deployment & Laptop Fallback

### On a Physical Raspberry Pi:
1. Ensure Python 3.10+ and Mosquitto are installed:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip mosquitto mosquitto-clients
   sudo systemctl enable mosquitto && sudo systemctl start mosquitto
   ```
2. Clone repo onto Pi, install dependencies (`pip install -r requirements.txt`).
3. Set `.env` with `MQTT_BROKER_HOST=localhost` and `BACKEND_API_URL=http://<backend-ip>:8000`.
4. Run `python -m member1_backend_edge.gateway.mqtt_subscriber`.

### Laptop Fallback (Demo Mode):
If a physical Raspberry Pi is not present or Wi-Fi restricts broker traffic:
1. Run local Mosquitto using Docker:
   ```bash
   docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto:2.0
   ```
2. Or use direct REST ingestion fallback: simulate telemetry by directly posting JSON from `shared/sample_data/normal_telemetry.json` to `http://localhost:8000/telemetry`.

---

## ⚠️ Known Limitations
- **In-Memory Rate Limiting**: The gateway's token-bucket rate limiter resides in local process memory. In a distributed multi-node edge deployment, rate-limiting tokens should be synchronized via a shared store (e.g. Redis).
- **Logical vs. Physical Quarantine**: `POST /devices/{device_id}/status` enforces logical quarantine at the gateway perimeter and database level. In this prototype, physical breaker trips are simulated and logged to avoid damage to physical test hardware.
