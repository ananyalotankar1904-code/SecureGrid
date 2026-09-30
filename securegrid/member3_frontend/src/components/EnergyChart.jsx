import React, { useState, useEffect } from 'react';
import { generateEnergyTelemetry } from '../services/api';
import { Zap, Clock, AlertTriangle } from 'lucide-react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend,
  ReferenceDot
} from 'recharts';

export function EnergyChart({ selectedDevice }) {
  const [timeRange, setTimeRange] = useState(60); // minutes
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Generate energy time-series telemetry based on range
    const data = generateEnergyTelemetry(timeRange);
    
    // Scale slightly if an individual device is selected
    if (selectedDevice) {
      const scale = selectedDevice.powerKw / (data[data.length - 1]?.powerKw || 2450);
      const adjusted = data.map(pt => ({
        ...pt,
        powerKw: Math.round(pt.powerKw * scale * 10) / 10,
        baselineKw: Math.round(pt.baselineKw * scale * 10) / 10
      }));
      setChartData(adjusted);
    } else {
      setChartData(data);
    }
  }, [timeRange, selectedDevice]);

  const latestPoint = chartData[chartData.length - 1] || {};

  return (
    <div className="panel col-8">
      <div className="panel-header">
        <div className="panel-title">
          <Zap size={15} style={{ color: 'var(--color-monitor)' }} />
          <span>Energy Telemetry & Anomaly Analysis</span>
          {selectedDevice && (
            <span style={{ fontSize: 11, color: 'var(--color-cyan)', marginLeft: 8, textTransform: 'none' }}>
              [{selectedDevice.id}]
            </span>
          )}
        </div>

        {/* Time range selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div className="time-btn-group">
            <button 
              className={`time-btn ${timeRange === 15 ? 'active' : ''}`}
              onClick={() => setTimeRange(15)}
            >
              15 min
            </button>
            <button 
              className={`time-btn ${timeRange === 60 ? 'active' : ''}`}
              onClick={() => setTimeRange(60)}
            >
              1 hour
            </button>
            <button 
              className={`time-btn ${timeRange === 360 ? 'active' : ''}`}
              onClick={() => setTimeRange(360)}
            >
              6 hours
            </button>
            <button 
              className={`time-btn ${timeRange === 1440 ? 'active' : ''}`}
              onClick={() => setTimeRange(1440)}
            >
              24 hours
            </button>
          </div>
        </div>
      </div>

      <div className="panel-body">
        {/* Telemetry Summary Bar */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', 
          gap: 12, 
          marginBottom: 16,
          background: 'var(--bg-dark)',
          padding: '10px 14px',
          borderRadius: 4,
          border: '1px solid var(--border-subtle)'
        }}>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>CURRENT POWER</div>
            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-cyan)' }}>
              {latestPoint.powerKw || 0} kW
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>EXPECTED BASELINE</div>
            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
              {latestPoint.baselineKw || 0} kW
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>VOLTAGE (V)</div>
            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {latestPoint.voltageV || 0} V
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>FREQUENCY</div>
            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--color-allow)' }}>
              {latestPoint.frequencyHz || 60.0} Hz
            </div>
          </div>
        </div>

        {/* Time Series Chart */}
        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData}>
              <XAxis dataKey="timestamp" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
              <Tooltip 
                contentStyle={{ 
                  background: 'var(--bg-dark)', 
                  border: '1px solid var(--border-subtle)', 
                  fontSize: 12 
                }} 
              />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
              
              <Area 
                type="monotone" 
                dataKey="powerKw" 
                name="Actual Power Load (kW)"
                fill="rgba(56, 189, 248, 0.15)" 
                stroke="#38bdf8" 
                strokeWidth={2} 
              />
              <Line 
                type="monotone" 
                dataKey="baselineKw" 
                name="Expected Baseline Load (kW)"
                stroke="#94a3b8" 
                strokeDasharray="4 4" 
                strokeWidth={1.5} 
                dot={false}
              />
              {chartData.map((entry, index) => 
                entry.isAnomaly ? (
                  <ReferenceDot 
                    key={index} 
                    x={entry.timestamp} 
                    y={entry.powerKw} 
                    r={6} 
                    fill="#ef4444" 
                    stroke="#ffffff" 
                    strokeWidth={2}
                  />
                ) : null
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
