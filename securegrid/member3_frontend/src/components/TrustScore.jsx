import React from 'react';
import { StatusBadge } from './StatusBadge';
import { ShieldCheck, TrendingDown, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

export function TrustScore({ device, systemAvgScore }) {
  const currentScore = device ? device.trustScore : systemAvgScore;
  const targetName = device ? `${device.id} (${device.name})` : 'SYSTEM AVERAGE';
  const recommendation = device ? device.recommendation : (systemAvgScore >= 80 ? 'ALLOW' : systemAvgScore >= 50 ? 'MONITOR' : 'RESTRICT');

  // Gauge calculations
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (currentScore / 100) * circumference;

  let gaugeColor = 'var(--color-allow)';
  if (currentScore < 40) gaugeColor = 'var(--color-quarantine)';
  else if (currentScore < 65) gaugeColor = 'var(--color-restrict)';
  else if (currentScore < 85) gaugeColor = 'var(--color-monitor)';

  const trustHistory = device && device.trustHistory ? device.trustHistory : [
    { time: '12:00', score: 92 },
    { time: '12:15', score: 88 },
    { time: '12:30', score: currentScore + 2 },
    { time: '12:45', score: currentScore }
  ];

  return (
    <div className="panel col-4">
      <div className="panel-header">
        <div className="panel-title">
          <ShieldCheck size={15} style={{ color: gaugeColor }} />
          <span>Dynamic Trust Score</span>
        </div>
      </div>

      <div className="panel-body" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 12, textAlign: 'center', letterSpacing: '0.04em' }}>
          TARGET: <strong style={{ color: 'var(--text-primary)', textTransform: 'uppercase' }}>{targetName}</strong>
        </div>

        {/* Circular Gauge */}
        <div className="trust-gauge-wrapper">
          <svg className="gauge-svg" viewBox="0 0 160 160">
            <circle
              className="gauge-bg"
              cx="80"
              cy="80"
              r={radius}
            />
            <circle
              className="gauge-fill"
              cx="80"
              cy="80"
              r={radius}
              stroke={gaugeColor}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 80 80)"
            />
            <text x="80" y="75" className="gauge-text-val">
              {currentScore}
            </text>
            <text x="80" y="105" className="gauge-text-lbl">
              TRUST SCORE
            </text>
          </svg>
        </div>

        {/* Recommendation Pill */}
        <div style={{ margin: '14px 0', textAlign: 'center' }}>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 6, letterSpacing: '0.04em' }}>
            DECISION RECOMMENDATION
          </div>
          <StatusBadge type="recommendation" value={recommendation} />
        </div>

        {/* Trend line */}
        <div style={{ width: '100%', marginTop: 12 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, display: 'flex', justifyContent: 'space-between' }}>
            <span>Recent Trust Score Trend</span>
            <span style={{ color: currentScore >= 80 ? 'var(--color-allow)' : 'var(--color-restrict)', display: 'flex', alignItems: 'center', gap: 2 }}>
              {currentScore >= 80 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              {currentScore}%
            </span>
          </div>
          <div style={{ height: 85, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trustHistory}>
                <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
                <YAxis domain={[0, 100]} hide />
                <Tooltip 
                  contentStyle={{ background: 'var(--bg-dark)', border: '1px solid var(--border-subtle)', fontSize: 11 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke={gaugeColor} 
                  strokeWidth={2} 
                  dot={{ r: 3, fill: gaugeColor }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
