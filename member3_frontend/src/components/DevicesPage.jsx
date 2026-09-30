import React from 'react';
import { DeviceTable } from './DeviceTable';

export function DevicesPage({ 
  devices, 
  selectedDeviceId, 
  onSelectDevice,
  statusFilter,
  setStatusFilter,
  recommendationFilter,
  setRecommendationFilter
}) {
  return (
    <div className="page-container">
      {/* Page Header */}
      <div className="page-header" style={{ textAlign: 'center', marginBottom: 24 }}>
        <h1 className="page-title" style={{ fontSize: 26 }}>DEVICE MONITORING</h1>
        <p className="page-subtitle" style={{ fontSize: 14 }}>
          Search, filter, and inspect connected smart-grid devices across the substation network.
        </p>
      </div>

      {/* Spacious Full Device Table Component */}
      <div className="devices-table-full-wrapper">
        <DeviceTable 
          devices={devices}
          selectedDeviceId={selectedDeviceId}
          onSelectDevice={onSelectDevice}
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          recommendationFilter={recommendationFilter}
          setRecommendationFilter={setRecommendationFilter}
          isFullPage={true}
        />
      </div>
    </div>
  );
}
