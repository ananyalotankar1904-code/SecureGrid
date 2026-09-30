import React from 'react';

export function StatusBadge({ type, value }) {
  if (!value) return null;

  const valUpper = value.toUpperCase();
  let badgeClass = 'badge-allow';

  if (valUpper === 'MONITOR' || valUpper === 'WARNING') {
    badgeClass = 'badge-monitor';
  } else if (valUpper === 'RESTRICT' || valUpper === 'THREAT') {
    badgeClass = 'badge-restrict';
  } else if (valUpper === 'QUARANTINE' || valUpper === 'QUARANTINED') {
    badgeClass = 'badge-quarantine';
  }

  return (
    <span className={`badge ${badgeClass}`}>
      {valUpper}
    </span>
  );
}

export function AnomalyBadge({ anomalyType }) {
  if (!anomalyType || anomalyType === 'Normal') {
    return <span className="badge badge-allow">Normal</span>;
  }

  let badgeClass = 'badge-monitor';
  if (anomalyType === 'Combined' || anomalyType === 'DDoS') {
    badgeClass = 'badge-quarantine';
  } else if (anomalyType === 'Energy' || anomalyType === 'Network' || anomalyType === 'Authentication') {
    badgeClass = 'badge-restrict';
  }

  return <span className={`badge ${badgeClass}`}>{anomalyType}</span>;
}
