import React, { useState, useEffect } from 'react';
import { getAnomalyBreakdown } from '../services/api';
import { PieChart as PieIcon } from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';

export function AnomalyBreakdown({ devices }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    getAnomalyBreakdown().then(res => setData(res));
  }, [devices]);

  return (
    <div className="panel col-6">
      <div className="panel-header">
        <div className="panel-title">
          <PieIcon size={15} style={{ color: 'var(--color-cyan)' }} />
          <span>Anomaly Type Breakdown</span>
        </div>
        <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Dataset Aggregation</span>
      </div>

      <div className="panel-body">
        <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 12 }}>
          Distribution of detected threats across energy, network, DDoS, authentication, and combined vector models.
        </div>

        <div style={{ height: 260, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20, top: 10, bottom: 10 }}>
              <XAxis type="number" stroke="var(--text-muted)" fontSize={11} allowDecimals={false} />
              <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" fontSize={11} tickLine={false} width={100} />
              <Tooltip 
                contentStyle={{ 
                  background: 'var(--bg-dark)', 
                  border: '1px solid var(--border-subtle)', 
                  fontSize: 11 
                }} 
              />
              <Bar dataKey="count" name="Detected Devices / Incidents" radius={[0, 4, 4, 0]}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
