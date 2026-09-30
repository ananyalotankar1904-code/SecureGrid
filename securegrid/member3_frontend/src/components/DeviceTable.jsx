import React, { useState, useMemo } from 'react';
import { StatusBadge, AnomalyBadge } from './StatusBadge';
import { Search, Filter, ArrowUpDown } from 'lucide-react';

export function DeviceTable({ 
  devices, 
  selectedDeviceId, 
  onSelectDevice,
  statusFilter,
  setStatusFilter,
  recommendationFilter,
  setRecommendationFilter,
  isFullPage = false
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [anomalyFilter, setAnomalyFilter] = useState('ALL');
  const [sortField, setSortField] = useState('id');
  const [sortAsc, setSortAsc] = useState(true);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  const filteredDevices = useMemo(() => {
    return devices.filter(d => {
      // Search across ID, name, type, location, status, and recommendation
      const term = searchTerm.toLowerCase().trim();
      const matchSearch = !term || 
        d.id.toLowerCase().includes(term) ||
        d.name.toLowerCase().includes(term) ||
        d.type.toLowerCase().includes(term) ||
        d.status.toLowerCase().includes(term) ||
        d.recommendation.toLowerCase().includes(term) ||
        (d.location && d.location.toLowerCase().includes(term));

      // Status filter
      const matchStatus = statusFilter === 'ALL' || d.status.toUpperCase() === statusFilter.toUpperCase();

      // Recommendation filter
      const matchRec = recommendationFilter === 'ALL' || d.recommendation.toUpperCase() === recommendationFilter.toUpperCase();

      // Anomaly filter
      let matchAnomaly = true;
      if (anomalyFilter !== 'ALL') {
        if (anomalyFilter === 'Normal') matchAnomaly = d.anomalyType === 'Normal';
        else if (anomalyFilter === 'Energy') matchAnomaly = d.anomalies.energy;
        else if (anomalyFilter === 'Network') matchAnomaly = d.anomalies.network;
        else if (anomalyFilter === 'DDoS') matchAnomaly = d.anomalies.ddos;
        else if (anomalyFilter === 'Authentication') matchAnomaly = d.anomalies.auth;
        else if (anomalyFilter === 'Combined') matchAnomaly = d.anomalies.combined;
      }

      return matchSearch && matchStatus && matchRec && matchAnomaly;
    }).sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      if (typeof valA === 'string') {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }

      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [devices, searchTerm, statusFilter, recommendationFilter, anomalyFilter, sortField, sortAsc]);

  return (
    <div className={`panel ${isFullPage ? 'col-12' : 'col-8'}`}>
      <div className="panel-header">
        <div className="panel-title">
          <Filter size={15} style={{ color: 'var(--color-cyan)' }} />
          <span>Device Security Overview</span>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'none', marginLeft: 8 }}>
            ({filteredDevices.length} of {devices.length} devices)
          </span>
        </div>
      </div>

      <div className="panel-body">
        {/* Filter Controls Container */}
        <div className="filter-bar">
          {/* Prominent Centered Search Bar */}
          <div className="search-container-prominent">
            <div className="search-input-wrapper">
              <Search size={20} className="search-icon-prominent" />
              <input 
                type="text"
                className="search-input-prominent"
                placeholder="Search devices by ID, type, location or status..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Filters Row */}
          <div className="filter-dropdowns-row">
            <select 
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">Status: All</option>
              <option value="HEALTHY">Healthy</option>
              <option value="WARNING">Warning</option>
              <option value="THREAT">Threat</option>
              <option value="QUARANTINED">Quarantined</option>
            </select>

            <select 
              className="filter-select"
              value={recommendationFilter}
              onChange={(e) => setRecommendationFilter(e.target.value)}
            >
              <option value="ALL">Recommendation: All</option>
              <option value="ALLOW">ALLOW</option>
              <option value="MONITOR">MONITOR</option>
              <option value="RESTRICT">RESTRICT</option>
              <option value="QUARANTINE">QUARANTINE</option>
            </select>

            <select 
              className="filter-select"
              value={anomalyFilter}
              onChange={(e) => setAnomalyFilter(e.target.value)}
            >
              <option value="ALL">Anomaly: All</option>
              <option value="Normal">Normal</option>
              <option value="Energy">Energy</option>
              <option value="Network">Network</option>
              <option value="Authentication">Authentication</option>
              <option value="Combined">Combined</option>
            </select>
          </div>
        </div>

        {/* Table View */}
        <div className="table-responsive">
          <table className="device-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('id')}>
                  Device ID <ArrowUpDown size={11} />
                </th>
                <th onClick={() => handleSort('type')}>
                  Type <ArrowUpDown size={11} />
                </th>
                <th onClick={() => handleSort('status')}>
                  Status <ArrowUpDown size={11} />
                </th>
                <th onClick={() => handleSort('trustScore')}>
                  Trust Score <ArrowUpDown size={11} />
                </th>
                <th onClick={() => handleSort('powerKw')}>
                  Power (kW) <ArrowUpDown size={11} />
                </th>
                <th>Anomaly</th>
                <th onClick={() => handleSort('lastSeen')}>Last Seen</th>
                <th>Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {filteredDevices.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                    No devices match the specified search and filter criteria.
                  </td>
                </tr>
              ) : (
                filteredDevices.map(d => (
                  <tr 
                    key={d.id} 
                    className={selectedDeviceId === d.id ? 'selected-row' : ''}
                    onClick={() => onSelectDevice(d)}
                  >
                    <td className="font-mono" style={{ fontWeight: 600, color: 'var(--color-cyan)' }}>
                      {d.id}
                    </td>
                    <td>{d.type}</td>
                    <td>
                      <StatusBadge type="status" value={d.status} />
                    </td>
                    <td className="font-mono">
                      <span style={{ 
                        color: d.trustScore >= 80 ? 'var(--color-allow)' : d.trustScore >= 50 ? 'var(--color-monitor)' : 'var(--color-restrict)',
                        fontWeight: 700 
                      }}>
                        {d.trustScore}
                      </span>
                      <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>/100</span>
                    </td>
                    <td className="font-mono">
                      {d.powerKw} kW
                    </td>
                    <td>
                      <AnomalyBadge anomalyType={d.anomalyType} />
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                      {d.lastSeen}
                    </td>
                    <td>
                      <StatusBadge type="recommendation" value={d.recommendation} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
