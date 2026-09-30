import React from 'react';

export function KpiCard({ title, value, subtext, icon: Icon, color, isActive, onClick }) {
  return (
    <div 
      className={`kpi-card ${isActive ? 'active-filter' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
    >
      <div className="kpi-title">
        <span>{title}</span>
        {Icon && <Icon size={16} style={{ color: color || 'var(--text-muted)' }} />}
      </div>
      <div className="kpi-value" style={{ color: color || 'var(--text-primary)' }}>
        {value}
      </div>
      {subtext && <div className="kpi-subtext">{subtext}</div>}
    </div>
  );
}
