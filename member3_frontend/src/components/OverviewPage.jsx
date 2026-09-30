import React from 'react';
import { KpiCard } from './KpiCard';
import { StatusBadge } from './StatusBadge';
import { 
  Cpu, 
  ShieldCheck, 
  AlertTriangle, 
  Activity, 
  Lock, 
  Gauge, 
  ArrowRight, 
  ShieldAlert, 
  Server, 
  Layers 
} from 'lucide-react';

export function OverviewPage({ 
  summary, 
  devices, 
  threatEvents, 
  onNavigate, 
  onSelectDevice 
}) {
  const healthyCount = devices.filter(d => d.status === 'Healthy').length;
  const warningCount = devices.filter(d => d.status === 'Warning').length;
  const threatCount = devices.filter(d => d.status === 'Threat').length;
  const quarantineCount = devices.filter(d => d.status === 'Quarantined').length;
  const totalCount = devices.length || 1;

  // Devices needing attention (Threat, Quarantined, Warning)
  const attentionDevices = devices.filter(d => d.status !== 'Healthy');
  // Latest 4-5 security events
  const recentEvents = threatEvents.slice(0, 5);

  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">SYSTEM OVERVIEW</h1>
          <p className="page-subtitle">Real-time status and operational health of the SecureGrid smart-grid infrastructure.</p>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="kpi-row-spacious">
        <KpiCard 
          title="Total Devices"
          value={summary ? summary.totalDevices : devices.length}
          subtext="Grid Infrastructure"
          icon={Cpu}
          color="var(--color-cyan)"
          onClick={() => onNavigate('devices')}
        />
        <KpiCard 
          title="Healthy Devices"
          value={healthyCount}
          subtext="ALLOW State (Normal)"
          icon={ShieldCheck}
          color="var(--color-allow)"
          onClick={() => onNavigate('devices')}
        />
        <KpiCard 
          title="Active Threats"
          value={threatCount}
          subtext="RESTRICT State"
          icon={AlertTriangle}
          color="var(--color-restrict)"
          onClick={() => onNavigate('devices')}
        />
        <KpiCard 
          title="Under Monitoring"
          value={warningCount}
          subtext="MONITOR State"
          icon={Activity}
          color="var(--color-monitor)"
          onClick={() => onNavigate('devices')}
        />
        <KpiCard 
          title="Quarantined"
          value={quarantineCount}
          subtext="QUARANTINE State"
          icon={Lock}
          color="var(--color-quarantine)"
          onClick={() => onNavigate('devices')}
        />
        <KpiCard 
          title="Avg Trust Score"
          value={summary ? summary.avgTrustScore : 78}
          subtext="Overall Grid Health"
          icon={Gauge}
          color={summary && summary.avgTrustScore >= 80 ? 'var(--color-allow)' : 'var(--color-monitor)'}
        />
      </div>

      {/* Main Content Sections */}
      <div className="overview-layout">
        {/* Left Column: Security Overview Summary & Active Attention */}
        <div className="overview-main-col">
          {/* Section 1: Security Overview */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <Layers size={16} style={{ color: 'var(--color-cyan)' }} />
                <span>Security State Distribution</span>
              </div>
            </div>
            <div className="panel-body">
              <div className="security-summary-grid">
                <div className="status-summary-card status-card-healthy">
                  <div className="status-summary-header">
                    <span className="status-summary-label">HEALTHY (ALLOW)</span>
                    <span className="status-summary-count">{healthyCount}</span>
                  </div>
                  <div className="status-progress-bg">
                    <div className="status-progress-bar bg-allow" style={{ width: `${(healthyCount / totalCount) * 100}%` }}></div>
                  </div>
                  <div className="status-summary-sub">Operating within normal parameters</div>
                </div>

                <div className="status-summary-card status-card-warning">
                  <div className="status-summary-header">
                    <span className="status-summary-label">MONITORING (MONITOR)</span>
                    <span className="status-summary-count">{warningCount}</span>
                  </div>
                  <div className="status-progress-bg">
                    <div className="status-progress-bar bg-monitor" style={{ width: `${(warningCount / totalCount) * 100}%` }}></div>
                  </div>
                  <div className="status-summary-sub">Minor anomaly or auth warning</div>
                </div>

                <div className="status-summary-card status-card-threat">
                  <div className="status-summary-header">
                    <span className="status-summary-label">RESTRICTED (RESTRICT)</span>
                    <span className="status-summary-count">{threatCount}</span>
                  </div>
                  <div className="status-progress-bg">
                    <div className="status-progress-bar bg-restrict" style={{ width: `${(threatCount / totalCount) * 100}%` }}></div>
                  </div>
                  <div className="status-summary-sub">Combined anomaly threat detected</div>
                </div>

                <div className="status-summary-card status-card-quarantine">
                  <div className="status-summary-header">
                    <span className="status-summary-label">QUARANTINED (QUARANTINE)</span>
                    <span className="status-summary-count">{quarantineCount}</span>
                  </div>
                  <div className="status-progress-bg">
                    <div className="status-progress-bar bg-quarantine" style={{ width: `${(quarantineCount / totalCount) * 100}%` }}></div>
                  </div>
                  <div className="status-summary-sub">Isolated by automated security policy</div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Active Attention Devices */}
          <div className="panel" style={{ marginTop: 20 }}>
            <div className="panel-header">
              <div className="panel-title">
                <AlertTriangle size={16} style={{ color: 'var(--color-restrict)' }} />
                <span>Active Attention Required</span>
                <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'none', marginLeft: 8 }}>
                  ({attentionDevices.length} flagged devices)
                </span>
              </div>
              <button className="text-nav-btn" onClick={() => onNavigate('devices')}>
                View All Devices &rarr;
              </button>
            </div>
            <div className="panel-body">
              {attentionDevices.length === 0 ? (
                <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>
                  All smart grid devices are currently operating normally in Healthy state.
                </div>
              ) : (
                <div className="attention-cards-grid">
                  {attentionDevices.map(d => (
                    <div 
                      key={d.id} 
                      className="attention-card"
                      onClick={() => onSelectDevice(d)}
                    >
                      <div className="attention-card-header">
                        <span className="font-mono" style={{ fontWeight: 700, color: 'var(--color-cyan)', fontSize: 14 }}>
                          {d.id}
                        </span>
                        <StatusBadge type="recommendation" value={d.recommendation} />
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--text-primary)', fontWeight: 600, margin: '4px 0' }}>
                        {d.name}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                        {d.type} | Trust Score: <strong style={{ color: 'var(--color-restrict)' }}>{d.trustScore}/100</strong>
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, lineClamp: 2 }}>
                        {d.explanation}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Recent Security Events & Page Navigation */}
        <div className="overview-side-col">
          {/* Recent Security Events */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <ShieldAlert size={16} style={{ color: 'var(--color-restrict)' }} />
                <span>Recent Security Events</span>
              </div>
            </div>
            <div className="panel-body">
              <div className="recent-events-list">
                {recentEvents.map(evt => (
                  <div key={evt.id} className={`recent-event-item severity-${evt.severity}`}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 4 }}>
                      <span className="font-mono" style={{ color: 'var(--color-cyan)', fontWeight: 600 }}>{evt.id}</span>
                      <span style={{ color: 'var(--text-muted)' }}>{evt.timestamp}</span>
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 4 }}>
                      {evt.details}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="font-mono" style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                        Device: {evt.deviceId}
                      </span>
                      <StatusBadge type="recommendation" value={evt.recommendation} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Navigation Action Card */}
          <div className="panel nav-callout-panel" style={{ marginTop: 20 }}>
            <div className="panel-header">
              <div className="panel-title">Quick Dashboard Navigation</div>
            </div>
            <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <button 
                className="btn-large-nav btn-nav-primary"
                onClick={() => onNavigate('devices')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <Server size={20} />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontWeight: 700 }}>VIEW DEVICES</div>
                    <div style={{ fontSize: 11, opacity: 0.8, textTransform: 'none' }}>Search & inspect all smart grid devices</div>
                  </div>
                </div>
                <ArrowRight size={18} />
              </button>

              <button 
                className="btn-large-nav btn-nav-secondary"
                onClick={() => onNavigate('security_energy')}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <ShieldAlert size={20} />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontWeight: 700 }}>VIEW SECURITY & ENERGY</div>
                    <div style={{ fontSize: 11, opacity: 0.8, textTransform: 'none' }}>Inspect threats, load curves & EWMA forecasts</div>
                  </div>
                </div>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
