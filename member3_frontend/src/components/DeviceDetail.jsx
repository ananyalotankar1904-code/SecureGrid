import React from 'react';
import { StatusBadge, AnomalyBadge } from './StatusBadge';
import { X, ShieldAlert, Activity, Lock, CheckCircle2, AlertOctagon } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function DeviceDetail({ device, onClose, onUpdateRecommendation }) {
  if (!device) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Activity size={18} style={{ color: 'var(--color-cyan)' }} />
            <div>
              <h3 style={{ fontSize: 16, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                {device.id} — {device.name}
              </h3>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                {device.type} | IP: {device.ipAddress} | Location: {device.location}
              </div>
            </div>
          </div>
          <button 
            onClick={onClose}
            style={{ 
              background: 'none', 
              border: 'none', 
              color: 'var(--text-muted)', 
              cursor: 'pointer',
              padding: 4
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Key Metric Grid */}
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">OPERATIONAL STATUS</span>
              <StatusBadge type="status" value={device.status} />
            </div>
            <div className="detail-item">
              <span className="detail-label">DYNAMIC TRUST SCORE</span>
              <span className="detail-val" style={{ 
                color: device.trustScore >= 80 ? 'var(--color-allow)' : device.trustScore >= 50 ? 'var(--color-monitor)' : 'var(--color-restrict)' 
              }}>
                {device.trustScore} / 100
              </span>
            </div>
            <div className="detail-item">
              <span className="detail-label">RECOMMENDATION</span>
              <StatusBadge type="recommendation" value={device.recommendation} />
            </div>
            <div className="detail-item">
              <span className="detail-label">ACTIVE POWER LOAD</span>
              <span className="detail-val">{device.powerKw} kW</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">LINE VOLTAGE</span>
              <span className="detail-val">{device.voltageV} V</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">CURRENT</span>
              <span className="detail-val">{device.currentA} A</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">FREQUENCY</span>
              <span className="detail-val">{device.frequencyHz} Hz</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">LAST TELEMETRY</span>
              <span className="detail-val">{device.lastSeen}</span>
            </div>
          </div>

          {/* Diagnostic Root-Cause Box */}
          <div>
            <h4 style={{ fontSize: 12, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
              <ShieldAlert size={14} style={{ color: 'var(--color-restrict)' }} />
              DIAGNOSTIC ANALYSIS & ANOMALY EXPLANATION
            </h4>
            <div className="explanation-box" style={{ 
              borderColor: device.recommendation === 'QUARANTINE' ? '#991b1b' : device.recommendation === 'RESTRICT' ? '#ef4444' : '#23314d',
              background: device.recommendation === 'QUARANTINE' ? 'rgba(153,27,27,0.2)' : 'var(--bg-dark)'
            }}>
              {device.explanation}
            </div>
          </div>

          {/* Security Vector Breakdown */}
          <div>
            <h4 style={{ fontSize: 12, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 8 }}>
              ANOMALY VECTOR STATUS
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8 }}>
              <div style={{ background: 'var(--bg-dark)', padding: '8px 10px', borderRadius: 4, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>ENERGY ANOMALY</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: device.anomalies.energy ? 'var(--color-restrict)' : 'var(--color-allow)' }}>
                  {device.anomalies.energy ? 'DETECTED' : 'CLEAR'}
                </div>
              </div>

              <div style={{ background: 'var(--bg-dark)', padding: '8px 10px', borderRadius: 4, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>NETWORK ANOMALY</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: device.anomalies.network ? 'var(--color-restrict)' : 'var(--color-allow)' }}>
                  {device.anomalies.network ? 'DETECTED' : 'CLEAR'}
                </div>
              </div>

              <div style={{ background: 'var(--bg-dark)', padding: '8px 10px', borderRadius: 4, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>AUTHENTICATION</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: device.anomalies.auth ? 'var(--color-restrict)' : 'var(--color-allow)' }}>
                  {device.anomalies.auth ? 'DETECTED' : 'CLEAR'}
                </div>
              </div>

              <div style={{ background: 'var(--bg-dark)', padding: '8px 10px', borderRadius: 4, border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>COMBINED VECTOR</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: device.anomalies.combined ? 'var(--color-quarantine)' : 'var(--color-allow)' }}>
                  {device.anomalies.combined ? 'CRITICAL' : 'CLEAR'}
                </div>
              </div>
            </div>
          </div>

          {/* Trust History Chart */}
          <div>
            <h4 style={{ fontSize: 12, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 6 }}>
              HISTORICAL TRUST SCORE TRAJECTORY
            </h4>
            <div style={{ height: 120, width: '100%', background: 'var(--bg-dark)', padding: 8, borderRadius: 4, border: '1px solid var(--border-subtle)' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={device.trustHistory || []}>
                  <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                  <YAxis domain={[0, 100]} stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                  <Tooltip contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-subtle)', fontSize: 11 }} />
                  <Line type="monotone" dataKey="score" stroke="var(--color-cyan)" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SOC Operator Mitigation Action Controls */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: 14, marginTop: 4 }}>
            <h4 style={{ fontSize: 12, textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: 8 }}>
              SOC OPERATOR ENFORCEMENT OVERRIDE
            </h4>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <button 
                className="btn-refresh" 
                style={{ borderColor: 'var(--border-allow)', color: 'var(--color-allow)' }}
                onClick={() => onUpdateRecommendation(device.id, 'ALLOW')}
              >
                <CheckCircle2 size={13} />
                <span>OVERRIDE: ALLOW</span>
              </button>

              <button 
                className="btn-refresh" 
                style={{ borderColor: 'var(--border-monitor)', color: 'var(--color-monitor)' }}
                onClick={() => onUpdateRecommendation(device.id, 'MONITOR')}
              >
                <Activity size={13} />
                <span>OVERRIDE: MONITOR</span>
              </button>

              <button 
                className="btn-refresh" 
                style={{ borderColor: 'var(--border-restrict)', color: 'var(--color-restrict)' }}
                onClick={() => onUpdateRecommendation(device.id, 'RESTRICT')}
              >
                <AlertOctagon size={13} />
                <span>OVERRIDE: RESTRICT</span>
              </button>

              <button 
                className="btn-refresh" 
                style={{ borderColor: 'var(--border-quarantine)', color: '#fda4af', background: 'var(--bg-quarantine)' }}
                onClick={() => onUpdateRecommendation(device.id, 'QUARANTINE')}
              >
                <Lock size={13} />
                <span>OVERRIDE: QUARANTINE</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
