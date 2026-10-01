/**
 * Centralized API Service for SecureGrid Member 3 Frontend
 * Supports live backend endpoints (VITE_API_URL) with seamless fallback to realistic demo data.
 */

const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:5000/api';

// --- MOCK DATA ENGINE ---
let isLiveApiAvailable = false;

// Initial Grid Devices Dataset based on Member 2 Smart Grid telemetry attributes
let mockDevices = [
  {
    id: 'meter_demo_01',
    name: 'Hackathon Demo Meter',
    type: 'Smart Meter',
    location: 'Demo Zone',
    status: 'Healthy',
    trustScore: 100,
    powerKw: 5.56,
    baselinePowerKw: 5.50,
    voltageV: 220.5,
    currentA: 25.22,
    frequencyHz: 60.0,
    anomalyType: 'Normal',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'ALLOW',
    lastSeen: 'Just now',
    ipAddress: '192.168.1.100',
    firmware: 'v1.0.0',
    explanation: 'System operating normally.',
    trustHistory: [
      { time: '12:00', score: 100 },
      { time: '12:15', score: 100 },
      { time: '12:30', score: 100 },
      { time: '12:45', score: 100 }
    ]
  },
  {
    id: 'SUB-TX-101',
    name: 'Substation Transformer 101',
    type: 'Substation Transformer',
    location: 'North Substation Alpha',
    status: 'Healthy',
    trustScore: 96,
    powerKw: 420.5,
    baselinePowerKw: 415.0,
    voltageV: 13800.2,
    currentA: 30.5,
    frequencyHz: 60.01,
    anomalyType: 'Normal',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'ALLOW',
    lastSeen: '10s ago',
    ipAddress: '192.168.10.15',
    firmware: 'v3.4.12-sec',
    explanation: 'System operating within normal parameters. Power, voltage, and network handshakes validated.',
    trustHistory: [
      { time: '12:00', score: 98 },
      { time: '12:15', score: 97 },
      { time: '12:30', score: 96 },
      { time: '12:45', score: 96 }
    ]
  },
  {
    id: 'SM-MET-402',
    name: 'Industrial Meter 402',
    type: 'Smart Meter',
    location: 'Heavy Industrial Zone 4',
    status: 'Threat',
    trustScore: 34,
    powerKw: 185.2,
    baselinePowerKw: 82.0,
    voltageV: 472.1,
    currentA: 392.2,
    frequencyHz: 59.82,
    anomalyType: 'Combined',
    anomalies: { energy: true, network: true, ddos: false, auth: true, combined: true },
    recommendation: 'RESTRICT',
    lastSeen: '2s ago',
    ipAddress: '192.168.40.102',
    firmware: 'v2.1.0-legacy',
    explanation: 'Combined Anomaly Detected: Power draw (+125.8% above EWMA baseline) accompanied by 18 rapid auth failures and unauthorized Modbus register rewrite attempt.',
    trustHistory: [
      { time: '12:00', score: 88 },
      { time: '12:15', score: 72 },
      { time: '12:30', score: 45 },
      { time: '12:45', score: 34 }
    ]
  },
  {
    id: 'INV-PV-809',
    name: 'Solar Farm Inverter B8',
    type: 'Solar Inverter',
    location: 'West Solar Array B',
    status: 'Warning',
    trustScore: 68,
    powerKw: 64.0,
    baselinePowerKw: 95.0,
    voltageV: 610.5,
    currentA: 104.8,
    frequencyHz: 59.95,
    anomalyType: 'Energy',
    anomalies: { energy: true, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'MONITOR',
    lastSeen: '5s ago',
    ipAddress: '192.168.80.209',
    firmware: 'v4.0.1',
    explanation: 'Energy Anomaly: Sudden generation drop (-32.6% vs expected solar irradiance model). Possible localized shading or firmware throttling.',
    trustHistory: [
      { time: '12:00', score: 95 },
      { time: '12:15', score: 92 },
      { time: '12:30', score: 75 },
      { time: '12:45', score: 68 }
    ]
  },
  {
    id: 'PMU-GRID-01',
    name: 'Transmission Node PMU 01',
    type: 'Phasor Measurement Unit',
    location: 'Main Grid Tie-In',
    status: 'Healthy',
    trustScore: 99,
    powerKw: 1250.0,
    baselinePowerKw: 1245.0,
    voltageV: 230050.0,
    currentA: 5.43,
    frequencyHz: 60.00,
    anomalyType: 'Normal',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'ALLOW',
    lastSeen: '1s ago',
    ipAddress: '10.0.1.5',
    firmware: 'v5.1.0-hsm',
    explanation: 'All synchrophasor measurements locked and verified. IEEE C37.118 protocol compliance verified.',
    trustHistory: [
      { time: '12:00', score: 99 },
      { time: '12:15', score: 99 },
      { time: '12:30', score: 99 },
      { time: '12:45', score: 99 }
    ]
  },
  {
    id: 'SM-MET-405',
    name: 'Commercial Park Meter 405',
    type: 'Smart Meter',
    location: 'Tech Park Sector C',
    status: 'Quarantined',
    trustScore: 12,
    powerKw: 0.0,
    baselinePowerKw: 145.0,
    voltageV: 0.0,
    currentA: 0.0,
    frequencyHz: 0.0,
    anomalyType: 'DDoS',
    anomalies: { energy: false, network: true, ddos: true, auth: true, combined: true },
    recommendation: 'QUARANTINE',
    lastSeen: '14s ago',
    ipAddress: '192.168.40.105',
    firmware: 'v2.0.8',
    explanation: 'Quarantined: High-volume SYN flood DDoS targeting grid gateway originating from MAC address. Automated relay lockout engaged by security policy.',
    trustHistory: [
      { time: '12:00', score: 85 },
      { time: '12:15', score: 50 },
      { time: '12:30', score: 20 },
      { time: '12:45', score: 12 }
    ]
  },
  {
    id: 'SUB-TX-104',
    name: 'Substation Transformer 104',
    type: 'Substation Transformer',
    location: 'East Substation Delta',
    status: 'Healthy',
    trustScore: 92,
    powerKw: 380.0,
    baselinePowerKw: 375.0,
    voltageV: 13795.0,
    currentA: 27.5,
    frequencyHz: 60.02,
    anomalyType: 'Normal',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'ALLOW',
    lastSeen: '8s ago',
    ipAddress: '192.168.10.18',
    firmware: 'v3.4.12-sec',
    explanation: 'Thermal and electrical parameters normal. Dynamic line rating within safe operational margins.',
    trustHistory: [
      { time: '12:00', score: 94 },
      { time: '12:15', score: 93 },
      { time: '12:30', score: 92 },
      { time: '12:45', score: 92 }
    ]
  },
  {
    id: 'INV-BAT-201',
    name: 'BESS Battery Inverter 201',
    type: 'Storage Inverter',
    location: 'Grid Battery Station 2',
    status: 'Warning',
    trustScore: 71,
    powerKw: 210.0,
    baselinePowerKw: 200.0,
    voltageV: 480.0,
    currentA: 437.5,
    frequencyHz: 60.05,
    anomalyType: 'Authentication',
    anomalies: { energy: false, network: false, ddos: false, auth: true, combined: false },
    recommendation: 'MONITOR',
    lastSeen: '4s ago',
    ipAddress: '192.168.70.12',
    firmware: 'v1.9.4',
    explanation: 'Authentication Anomaly: 4 consecutive SSH login attempts using expired Certificate Authority key from management VLAN.',
    trustHistory: [
      { time: '12:00', score: 95 },
      { time: '12:15', score: 90 },
      { time: '12:30', score: 78 },
      { time: '12:45', score: 71 }
    ]
  },
  {
    id: 'PMU-GRID-02',
    name: 'Transmission Node PMU 02',
    type: 'Phasor Measurement Unit',
    location: 'South Node Tie-In',
    status: 'Healthy',
    trustScore: 97,
    powerKw: 1180.0,
    baselinePowerKw: 1185.0,
    voltageV: 229980.0,
    currentA: 5.13,
    frequencyHz: 59.99,
    anomalyType: 'Normal',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    recommendation: 'ALLOW',
    lastSeen: '3s ago',
    ipAddress: '10.0.1.6',
    firmware: 'v5.1.0-hsm',
    explanation: 'Phasor data clean. Phase angle difference within stability bounds (2.4 deg).',
    trustHistory: [
      { time: '12:00', score: 98 },
      { time: '12:15', score: 97 },
      { time: '12:30', score: 97 },
      { time: '12:45', score: 97 }
    ]
  }
];

// Initial Threat Events Dataset
let mockThreatEvents = [
  {
    id: 'EVT-9041',
    timestamp: '2026-09-30 18:41:02',
    deviceId: 'SM-MET-405',
    anomalyType: 'DDOS',
    severity: 'CRITICAL',
    trustScore: 12,
    recommendation: 'QUARANTINE',
    status: 'ACTIVE',
    details: 'SYN Flood attack detected (14,200 pps). Network anomaly filter triggered.'
  },
  {
    id: 'EVT-9038',
    timestamp: '2026-09-30 18:38:45',
    deviceId: 'SM-MET-402',
    anomalyType: 'COMBINED',
    severity: 'HIGH',
    trustScore: 34,
    recommendation: 'RESTRICT',
    status: 'INVESTIGATING',
    details: 'Unusual power draw spike combined with credential brute force attempt.'
  },
  {
    id: 'EVT-9025',
    timestamp: '2026-09-30 18:25:10',
    deviceId: 'INV-BAT-201',
    anomalyType: 'AUTHENTICATION',
    severity: 'MEDIUM',
    trustScore: 71,
    recommendation: 'MONITOR',
    status: 'INVESTIGATING',
    details: 'Expired CA key handshake failure on Port 22.'
  },
  {
    id: 'EVT-9012',
    timestamp: '2026-09-30 18:12:30',
    deviceId: 'INV-PV-809',
    anomalyType: 'ENERGY',
    severity: 'LOW',
    trustScore: 68,
    recommendation: 'MONITOR',
    status: 'ACKNOWLEDGED',
    details: 'Power output variance exceeds 30% baseline deviation threshold.'
  }
];

// Helper to generate dynamic energy time-series telemetry data based on selected window
export function generateEnergyTelemetry(timeRangeMinutes = 60) {
  const pointsCount = timeRangeMinutes <= 15 ? 15 : timeRangeMinutes <= 60 ? 20 : 30;
  const now = new Date();
  const data = [];

  for (let i = pointsCount - 1; i >= 0; i--) {
    const time = new Date(now.getTime() - i * (timeRangeMinutes * 60 * 1000) / pointsCount);
    const timeStr = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Base sinus load curve + minor noise
    const baseVal = 2450 + Math.sin(i / 3) * 350;
    const noise = (Math.random() - 0.5) * 40;
    const actualPower = Math.round((baseVal + noise) * 10) / 10;
    const expectedBaseline = Math.round(baseVal * 10) / 10;

    // Introduce anomaly marker at specific point
    const isAnomalyPoint = i === 4 || i === 5;
    const anomalousPower = isAnomalyPoint ? actualPower + 520 : actualPower;

    const voltage = Math.round((13800 + (Math.random() - 0.5) * 80) * 10) / 10;
    const current = Math.round((anomalousPower * 1000 / (Math.sqrt(3) * 13800)) * 10) / 10;

    data.push({
      timestamp: timeStr,
      powerKw: anomalousPower,
      baselineKw: expectedBaseline,
      voltageV: voltage,
      currentA: current,
      frequencyHz: Math.round((60 + (Math.random() - 0.5) * 0.08) * 100) / 100,
      isAnomaly: isAnomalyPoint
    });
  }

  return data;
}

// Helper for EWMA Load Prediction (15-min horizon)
export function generateEWMAPredictionData() {
  const now = new Date();
  const points = [];
  
  // Past 10 points (actual vs EWMA)
  for (let i = 9; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 3 * 60 * 1000);
    const timeStr = t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const actual = 2500 + Math.sin(i * 0.4) * 200 + (Math.random() - 0.5) * 30;
    const ewma = 2500 + Math.sin((i + 0.3) * 0.4) * 190;
    points.push({
      time: timeStr,
      actual: Math.round(actual),
      ewmaPredicted: Math.round(ewma),
      isForecast: false
    });
  }

  // Future 5 points (EWMA forecast horizon)
  for (let i = 1; i <= 5; i++) {
    const t = new Date(now.getTime() + i * 3 * 60 * 1000);
    const timeStr = t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const ewmaForecast = 2500 + Math.sin((i - 0.5) * 0.4) * 210;
    points.push({
      time: timeStr + ' (fcst)',
      actual: null,
      ewmaPredicted: Math.round(ewmaForecast),
      isForecast: true
    });
  }

  return points;
}

// --- CENTRAL API EXPORTS ---

export async function checkApiHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET', signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      isLiveApiAvailable = true;
      return { isLive: true, mode: 'LIVE API' };
    }
  } catch (err) {
    isLiveApiAvailable = false;
  }
  return { isLive: false, mode: 'DEMO DATA' };
}

export async function getDashboardSummary() {
  if (isLiveApiAvailable) {
    try {
      const devices = await getDevices();
      const total = devices.length;
      const healthy = devices.filter(d => d.status === 'Healthy').length;
      const warning = devices.filter(d => d.status === 'Warning').length;
      const threat = devices.filter(d => d.status === 'Threat').length;
      const quarantined = devices.filter(d => d.status === 'Quarantined').length;
      const avgTrustScore = total ? Math.round(devices.reduce((sum, d) => sum + d.trustScore, 0) / total) : 100;

      return {
        totalDevices: total,
        healthyDevices: healthy,
        monitoringDevices: warning,
        activeThreats: threat,
        quarantinedDevices: quarantined,
        avgTrustScore,
        lastUpdated: new Date().toLocaleTimeString(),
        isLiveApi: true
      };
    } catch (e) {
      console.warn('Falling back to mock dataset for summary:', e);
    }
  }

  // Compute live from mock dataset
  const total = mockDevices.length;
  const healthy = mockDevices.filter(d => d.status === 'Healthy').length;
  const warning = mockDevices.filter(d => d.status === 'Warning').length;
  const threat = mockDevices.filter(d => d.status === 'Threat').length;
  const quarantined = mockDevices.filter(d => d.status === 'Quarantined').length;
  const avgTrustScore = Math.round(mockDevices.reduce((sum, d) => sum + d.trustScore, 0) / total);

  return {
    totalDevices: total,
    healthyDevices: healthy,
    monitoringDevices: warning,
    activeThreats: threat,
    quarantinedDevices: quarantined,
    avgTrustScore,
    lastUpdated: new Date().toLocaleTimeString(),
    isLiveApi: false
  };
}

export async function getDevices() {
  if (isLiveApiAvailable) {
    try {
      const [devRes, predRes, telRes] = await Promise.all([
        fetch(`${API_BASE_URL}/devices?limit=100`),
        fetch(`${API_BASE_URL}/predictions?limit=100`),
        fetch(`${API_BASE_URL}/telemetry?limit=100`)
      ]);
      if (devRes.ok && predRes.ok && telRes.ok) {
        const [devData, predData, telData] = await Promise.all([devRes.json(), predRes.json(), telRes.json()]);
        
        const devices = devData.items || [];
        const predictions = predData.items || [];
        const telemetries = telData.items || [];
        
        return devices.map(d => {
          const pred = predictions.find(p => p.device_id === d.device_id) || {};
          const tel = telemetries.find(t => t.device_id === d.device_id) || {};
          
          return {
            id: d.device_id,
            name: d.device_name,
            type: d.device_type,
            location: d.location,
            status: d.status === 'ACTIVE' ? (pred.trust_status === 'COMPROMISED' ? 'Threat' : pred.trust_status === 'ELEVATED_RISK' ? 'Warning' : 'Healthy') : (d.status === 'QUARANTINED' ? 'Quarantined' : 'Healthy'),
            trustScore: pred.trust_score !== undefined ? Math.round(pred.trust_score) : 100,
            powerKw: tel.power_kw || 0,
            baselinePowerKw: pred.predicted_load_kw || 0,
            voltageV: tel.voltage || 220,
            currentA: tel.current || 0,
            frequencyHz: 60,
            anomalyType: pred.anomaly_type || 'Normal',
            anomalies: {
              energy: (pred.reasons || []).includes('ENERGY_ANOMALY'),
              network: (pred.reasons || []).includes('NETWORK_ANOMALY'),
              ddos: (pred.reasons || []).includes('NETWORK_ANOMALY'),
              auth: (pred.reasons || []).includes('AUTH_ANOMALY'),
              combined: (pred.reasons || []).length > 1
            },
            recommendation: d.status === 'QUARANTINED' ? 'QUARANTINE' : (pred.trust_status === 'COMPROMISED' ? 'RESTRICT' : pred.trust_status === 'ELEVATED_RISK' ? 'MONITOR' : 'ALLOW'),
            lastSeen: new Date(d.updated_at || tel.timestamp || Date.now()).toLocaleTimeString(),
            ipAddress: d.ip_address || '0.0.0.0',
            firmware: d.firmware_version || 'v1.0',
            explanation: (pred.reasons || []).join(', ') || 'System operating normally.',
            trustHistory: []
          };
        });
      }
    } catch (e) {
      console.warn('Falling back to mock dataset for devices:', e);
    }
  }
  return mockDevices;
}

export async function getThreatEvents() {
  if (isLiveApiAvailable) {
    try {
      const res = await fetch(`${API_BASE_URL}/security/events?limit=50`);
      if (res.ok) {
        const data = await res.json();
        return (data.items || []).map(e => ({
          id: e.id,
          timestamp: new Date(e.timestamp).toLocaleString(),
          deviceId: e.device_id,
          anomalyType: e.event_type.replace('ML_ANOMALY_ALERT', 'COMBINED').replace('_DETECTED', ''),
          severity: e.severity,
          trustScore: e.details?.trust_score || 0,
          recommendation: e.severity === 'CRITICAL' ? 'QUARANTINE' : e.severity === 'HIGH' ? 'RESTRICT' : 'MONITOR',
          status: e.mitigated ? 'RESOLVED' : 'ACTIVE',
          details: e.description
        }));
      }
    } catch (e) {
      console.warn('Falling back to mock dataset for threat events:', e);
    }
  }
  return mockThreatEvents;
}

export async function getAnomalyBreakdown() {
  // Aggregate anomaly types from current dataset
  const breakdown = {
    Energy: 0,
    Network: 0,
    DDoS: 0,
    Authentication: 0,
    Combined: 0
  };

  mockDevices.forEach(d => {
    if (d.anomalies.energy) breakdown.Energy++;
    if (d.anomalies.network && !d.anomalies.ddos) breakdown.Network++;
    if (d.anomalies.ddos) breakdown.DDoS++;
    if (d.anomalies.auth) breakdown.Authentication++;
    if (d.anomalies.combined) breakdown.Combined++;
  });

  return [
    { name: 'Energy', count: breakdown.Energy, color: '#f59e0b' },
    { name: 'Network', count: breakdown.Network, color: '#38bdf8' },
    { name: 'DDoS', count: breakdown.DDoS, color: '#991b1b' },
    { name: 'Authentication', count: breakdown.Authentication, color: '#a855f7' },
    { name: 'Combined', count: breakdown.Combined, color: '#ef4444' }
  ];
}

// Allows updating quarantine/recommendation state manually from UI
export async function updateDeviceRecommendation(deviceId, newRecommendation) {
  const dev = mockDevices.find(d => d.id === deviceId);
  if (dev) {
    dev.recommendation = newRecommendation;
    if (newRecommendation === 'QUARANTINE') {
      dev.status = 'Quarantined';
      dev.trustScore = Math.min(dev.trustScore, 10);
      dev.explanation = `Manual Operator Override: Device isolated and quarantined by SOC operator.`;
    } else if (newRecommendation === 'ALLOW') {
      dev.status = 'Healthy';
      dev.trustScore = Math.max(dev.trustScore, 90);
      dev.explanation = `Manual Operator Override: Device cleared and marked healthy by SOC operator.`;
    } else if (newRecommendation === 'MONITOR') {
      dev.status = 'Warning';
      dev.trustScore = 70;
    } else if (newRecommendation === 'RESTRICT') {
      dev.status = 'Threat';
      dev.trustScore = 40;
    }
  }
  return dev;
}

// Trigger simulated tick update for dynamic telemetry testing
export function simulateTelemetryTick() {
  // Randomly oscillate a non-quarantined device's power slightly
  mockDevices.forEach(d => {
    if (d.status !== 'Quarantined' && d.id !== 'meter_demo_01') {
      const delta = (Math.random() - 0.5) * 4.0;
      d.powerKw = Math.max(0, Math.round((d.powerKw + delta) * 10) / 10);
      d.lastSeen = 'Just now';
    }
  });
  return [...mockDevices];
}

const member2DemoScenarios = {
  NORMAL: {
    powerKw: 5.56, requestRate: 4, failedAuth: 0,
    trustScore: 100, status: 'Healthy', recommendation: 'ALLOW',
    anomalies: { energy: false, network: false, ddos: false, auth: false, combined: false },
    anomalyType: 'Normal', severity: 'LOW',
    explanation: 'System operating normally. No anomalies detected.',
  },
  ENERGY_ANOMALY: {
    powerKw: 16.75, requestRate: 8, failedAuth: 0,
    trustScore: 70, status: 'Warning', recommendation: 'MONITOR',
    anomalies: { energy: true, network: false, ddos: false, auth: false, combined: false },
    anomalyType: 'Energy', severity: 'MEDIUM',
    explanation: 'power consumption significantly above expected range',
  },
  DDOS: {
    powerKw: 4.09, requestRate: 655, failedAuth: 0,
    trustScore: 60, status: 'Warning', recommendation: 'MONITOR',
    anomalies: { energy: false, network: true, ddos: true, auth: false, combined: false },
    anomalyType: 'DDoS', severity: 'MEDIUM',
    explanation: 'abnormally high request rate',
  },
  COMPROMISE: {
    powerKw: 39.39, requestRate: 689, failedAuth: 13,
    trustScore: 10, status: 'Quarantined', recommendation: 'QUARANTINE',
    anomalies: { energy: true, network: true, ddos: true, auth: true, combined: true },
    anomalyType: 'Combined', severity: 'HIGH',
    explanation: 'power consumption significantly above expected range, abnormally high request rate, authentication failures detected',
  }
};

export async function setDemoScenario(scenarioName) {
  const scenario = member2DemoScenarios[scenarioName];
  if (!scenario) return;

  const dev = mockDevices.find(d => d.id === 'meter_demo_01');
  if (dev) {
    dev.powerKw = scenario.powerKw;
    dev.trustScore = scenario.trustScore;
    dev.status = scenario.status;
    dev.recommendation = scenario.recommendation;
    dev.anomalies = { ...scenario.anomalies };
    dev.anomalyType = scenario.anomalyType;
    dev.explanation = scenario.explanation;
    
    // Add to history
    dev.trustHistory.push({ time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), score: dev.trustScore });
    if(dev.trustHistory.length > 10) dev.trustHistory.shift();

    // Update threat events
    mockThreatEvents = mockThreatEvents.filter(e => e.deviceId !== 'meter_demo_01');
    if (scenarioName !== 'NORMAL') {
      mockThreatEvents.unshift({
        id: 'EVT-DEMO-' + Date.now(),
        timestamp: new Date().toLocaleString(),
        deviceId: 'meter_demo_01',
        anomalyType: scenario.anomalyType.toUpperCase(),
        severity: scenario.severity.toUpperCase(),
        trustScore: scenario.trustScore,
        recommendation: scenario.recommendation,
        status: 'ACTIVE',
        details: scenario.explanation
      });
    }
  }
}
