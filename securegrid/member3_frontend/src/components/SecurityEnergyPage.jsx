import React, { useState } from 'react';
import { ThreatPanel } from './ThreatPanel';
import { AnomalyBreakdown } from './AnomalyBreakdown';
import { EnergyChart } from './EnergyChart';
import { PredictionChart } from './PredictionChart';
import { ShieldAlert, Zap } from 'lucide-react';

export function SecurityEnergyPage({ 
  devices, 
  threatEvents, 
  selectedDevice, 
  onSelectDeviceById 
}) {
  const [activeTab, setActiveTab] = useState('security'); // 'security' | 'energy'

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header" style={{ marginBottom: 20 }}>
        <h1 className="page-title">SECURITY & ENERGY ANALYTICS</h1>
        <p className="page-subtitle">Detailed threat breakdown, active security incident logs, real-time load telemetry, and EWMA load forecasts.</p>
      </div>

      {/* 2 Large Internal Tabs */}
      <div className="internal-tab-bar">
        <button 
          className={`internal-tab-btn ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <ShieldAlert size={18} />
          <span>SECURITY THREATS & ANOMALIES</span>
        </button>

        <button 
          className={`internal-tab-btn ${activeTab === 'energy' ? 'active' : ''}`}
          onClick={() => setActiveTab('energy')}
        >
          <Zap size={18} />
          <span>ENERGY & PREDICTION</span>
        </button>
      </div>

      {/* Tab 1: SECURITY */}
      {activeTab === 'security' && (
        <div className="tab-content-grid">
          {/* Anomaly Breakdown & Threat Event Stream */}
          <AnomalyBreakdown devices={devices} />
          <ThreatPanel events={threatEvents} onSelectDeviceById={onSelectDeviceById} />
        </div>
      )}

      {/* Tab 2: ENERGY & PREDICTION */}
      {activeTab === 'energy' && (
        <div className="tab-content-grid">
          {/* Time Series Energy Chart & EWMA Forecast */}
          <EnergyChart selectedDevice={selectedDevice} />
          <PredictionChart />
        </div>
      )}
    </div>
  );
}
