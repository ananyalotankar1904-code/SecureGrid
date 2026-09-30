import React, { useState, useMemo } from 'react';
import { StatusBadge } from './StatusBadge';
import { ShieldAlert, AlertTriangle } from 'lucide-react';

export function ThreatPanel({ events, onSelectDeviceById }) {
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [anomalyTypeFilter, setAnomalyTypeFilter] = useState('ALL');

  const filteredEvents = useMemo(() => {
    return events.filter(evt => {
      const matchSev = severityFilter === 'ALL' || evt.severity.toUpperCase() === severityFilter.toUpperCase();
      const matchType = anomalyTypeFilter === 'ALL' || evt.anomalyType.toUpperCase() === anomalyTypeFilter.toUpperCase();
      return matchSev && matchType;
    });
  }, [events, severityFilter, anomalyTypeFilter]);

  return (
    <div className="panel col-6">
      <div className="panel-header">
        <div className="panel-title">
          <ShieldAlert size={15} style={{ color: 'var(--color-restrict)' }} />
          <span>Security Event Log Stream</span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'none', marginLeft: 6 }}>
            ({filteredEvents.length} events)
          </span>
        </div>
      </div>

      <div className="panel-body">
        {/* Filters */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
          <select 
            className="filter-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="ALL">Severity: All</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <select 
            className="filter-select"
            value={anomalyTypeFilter}
            onChange={(e) => setAnomalyTypeFilter(e.target.value)}
          >
            <option value="ALL">Anomaly: All</option>
            <option value="ENERGY">Energy</option>
            <option value="NETWORK">Network</option>
            <option value="DDOS">DDoS</option>
            <option value="AUTHENTICATION">Authentication</option>
            <option value="COMBINED">Combined</option>
          </select>
        </div>

        {/* Threat Stream List */}
        <div className="threat-list">
          {filteredEvents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)', fontSize: 12 }}>
              No security events match the active severity/anomaly filters.
            </div>
          ) : (
            filteredEvents.map(evt => (
              <div key={evt.id} className={`threat-item severity-${evt.severity}`}>
                <div className="threat-meta">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span className="font-mono" style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      {evt.id}
                    </span>
                    <button 
                      style={{ 
                        background: 'none', 
                        border: 'none', 
                        color: 'var(--color-cyan)', 
                        fontFamily: 'var(--font-mono)', 
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        padding: 0,
                        fontSize: 11
                      }}
                      onClick={() => onSelectDeviceById && onSelectDeviceById(evt.deviceId)}
                    >
                      {evt.deviceId}
                    </button>
                  </div>
                  <span style={{ color: 'var(--text-muted)' }}>{evt.timestamp}</span>
                </div>

                <div className="threat-desc">{evt.details}</div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 4 }}>
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    <span className="badge" style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>
                      {evt.anomalyType}
                    </span>
                    <span className="badge" style={{ 
                      background: evt.severity === 'CRITICAL' ? 'rgba(153,27,27,0.4)' : evt.severity === 'HIGH' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
                      color: evt.severity === 'CRITICAL' ? '#fca5a5' : evt.severity === 'HIGH' ? '#f87171' : '#fbbf24'
                    }}>
                      {evt.severity}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                      Trust Score: <strong style={{ color: 'var(--text-primary)' }}>{evt.trustScore}</strong>
                    </span>
                    <StatusBadge type="recommendation" value={evt.recommendation} />
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
