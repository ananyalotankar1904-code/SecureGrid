-- ==============================================================================
-- SecureGrid Supabase PostgreSQL Schema
-- Tables: devices, telemetry, trust_scores, security_events, load_predictions
-- Run this script in the Supabase SQL Editor (Dashboard -> SQL Editor -> New Query)
-- ==============================================================================

-- 1. Enable UUID extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Devices Table: Registry of smart meters and grid edge assets
CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(64) PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL DEFAULT 'residential_meter',
    location VARCHAR(200) DEFAULT 'Sector 1',
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPICIOUS', 'QUARANTINED', 'OFFLINE')),
    ip_address VARCHAR(45),
    mac_address VARCHAR(20),
    firmware_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);

-- 3. Telemetry Table: High-frequency electrical metrics from smart meters
CREATE TABLE IF NOT EXISTS telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(64) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    power_kw NUMERIC(8, 3) NOT NULL CHECK (power_kw >= 0.0),
    voltage NUMERIC(6, 2) NOT NULL CHECK (voltage > 0.0),
    current NUMERIC(6, 2) NOT NULL CHECK (current >= 0.0),
    request_rate NUMERIC(5, 2) NOT NULL DEFAULT 1.0 CHECK (request_rate >= 0.0),
    failed_auth_attempts INT NOT NULL DEFAULT 0 CHECK (failed_auth_attempts >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_telemetry_device_time ON telemetry(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp DESC);

-- 4. Trust Scores Table: Historical & current device trust calculations
CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(64) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    trust_score NUMERIC(5, 2) NOT NULL CHECK (trust_score >= 0.0 AND trust_score <= 100.0),
    trust_status VARCHAR(20) NOT NULL CHECK (trust_status IN ('TRUSTED', 'ELEVATED_RISK', 'COMPROMISED')),
    anomaly_detected BOOLEAN NOT NULL DEFAULT FALSE,
    anomaly_type VARCHAR(100),
    reasons JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trust_scores_device ON trust_scores(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trust_scores_status ON trust_scores(trust_status);

-- 5. Security Events Table: Policy violations, attacks, and operator containment
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(64) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    mitigated BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_security_events_device ON security_events(device_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp DESC);

-- 6. Load Predictions Table: Short-term electrical demand forecasts
CREATE TABLE IF NOT EXISTS load_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(64) NOT NULL REFERENCES devices(device_id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    predicted_load_kw NUMERIC(8, 3) NOT NULL CHECK (predicted_load_kw >= 0.0),
    confidence_score NUMERIC(4, 3) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_load_predictions_device ON load_predictions(device_id, timestamp DESC);
