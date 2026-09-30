import React, { useState, useEffect } from 'react';
import { generateEWMAPredictionData } from '../services/api';
import { TrendingUp, Clock } from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  ReferenceLine 
} from 'recharts';

export function PredictionChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    setData(generateEWMAPredictionData());
  }, []);

  return (
    <div className="panel col-4">
      <div className="panel-header">
        <div className="panel-title">
          <TrendingUp size={15} style={{ color: 'var(--color-cyan)' }} />
          <span>EWMA Load Prediction</span>
        </div>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>15-Min Horizon</span>
      </div>

      <div className="panel-body">
        <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 12, lineHeight: 1.4 }}>
          15-Minute EWMA (Exponentially Weighted Moving Average) Grid Load Forecast vs Real Telemetry
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} tickLine={false} />
              <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} domain={['auto', 'auto']} />
              <Tooltip 
                contentStyle={{ 
                  background: 'var(--bg-dark)', 
                  border: '1px solid var(--border-subtle)', 
                  fontSize: 11 
                }} 
              />
              <Legend wrapperStyle={{ fontSize: 11, paddingTop: 4 }} />
              
              <Line 
                type="monotone" 
                dataKey="actual" 
                name="Actual Load (kW)"
                stroke="#38bdf8" 
                strokeWidth={2} 
                dot={{ r: 3 }}
                connectNulls={false}
              />
              <Line 
                type="monotone" 
                dataKey="ewmaPredicted" 
                name="EWMA Forecast (kW)"
                stroke="#f59e0b" 
                strokeWidth={2} 
                strokeDasharray="4 4"
                dot={{ r: 3, fill: '#f59e0b' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ 
          marginTop: 10, 
          padding: '6px 10px', 
          background: 'var(--bg-dark)', 
          borderRadius: 3, 
          border: '1px solid var(--border-subtle)',
          fontSize: 11,
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: 6
        }}>
          <Clock size={13} style={{ color: 'var(--color-cyan)' }} />
          <span>Forecast Horizon: Next 15 Minutes (EWMA Alpha = 0.35)</span>
        </div>
      </div>
    </div>
  );
}
