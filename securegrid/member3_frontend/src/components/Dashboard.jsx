import React, { useState, useEffect, useCallback } from 'react';
import { 
  getDashboardSummary, 
  getDevices, 
  getThreatEvents, 
  checkApiHealth, 
  updateDeviceRecommendation,
  simulateTelemetryTick 
} from '../services/api';
import { Header } from './Header';
import { OverviewPage } from './OverviewPage';
import { DevicesPage } from './DevicesPage';
import { SecurityEnergyPage } from './SecurityEnergyPage';
import { DeviceDetail } from './DeviceDetail';

export function Dashboard() {
  // Navigation Page State: 'overview' | 'devices' | 'security_energy'
  const [activePage, setActivePage] = useState('overview');

  // Datasets
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);
  const [threatEvents, setThreatEvents] = useState([]);
  const [isLiveApi, setIsLiveApi] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');
  
  // Selection and Filter States
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [recommendationFilter, setRecommendationFilter] = useState('ALL');

  // Polling simulation
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadData = useCallback(async () => {
    const health = await checkApiHealth();
    setIsLiveApi(health.isLive);

    const sum = await getDashboardSummary();
    const devList = await getDevices();
    const threats = await getThreatEvents();

    setSummary(sum);
    setDevices(devList);
    setThreatEvents(threats);
    setLastUpdated(new Date().toLocaleTimeString());

    // Keep selected device object reference fresh
    if (selectedDevice) {
      const updatedSel = devList.find(d => d.id === selectedDevice.id);
      if (updatedSel) setSelectedDevice(updatedSel);
    }
  }, [selectedDevice]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Periodic Telemetry Simulation Stream
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      // Simulate telemetry oscillation
      const updated = simulateTelemetryTick();
      setDevices([...updated]);

      // Recalculate summary metrics
      getDashboardSummary().then(sum => setSummary(sum));
      setLastUpdated(new Date().toLocaleTimeString());
    }, 4000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const handleUpdateRecommendation = async (deviceId, newRec) => {
    await updateDeviceRecommendation(deviceId, newRec);
    await loadData();
  };

  const handleSelectDeviceById = (deviceId) => {
    const dev = devices.find(d => d.id === deviceId);
    if (dev) setSelectedDevice(dev);
  };

  const handleNavigate = (pageId) => {
    setActivePage(pageId);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-container">
      {/* Persistent Navigation Header */}
      <Header 
        activePage={activePage}
        onPageChange={handleNavigate}
        lastUpdated={lastUpdated}
        isLiveApi={isLiveApi}
        onRefresh={loadData}
        autoRefresh={autoRefresh}
        onToggleAutoRefresh={() => setAutoRefresh(!autoRefresh)}
      />

      {/* Main Page Render (3 Main Pages Only) */}
      <main className="main-content">
        {activePage === 'overview' && (
          <OverviewPage 
            summary={summary}
            devices={devices}
            threatEvents={threatEvents}
            onNavigate={handleNavigate}
            onSelectDevice={(dev) => setSelectedDevice(dev)}
          />
        )}

        {activePage === 'devices' && (
          <DevicesPage 
            devices={devices}
            selectedDeviceId={selectedDevice?.id}
            onSelectDevice={(dev) => setSelectedDevice(dev)}
            statusFilter={statusFilter}
            setStatusFilter={setStatusFilter}
            recommendationFilter={recommendationFilter}
            setRecommendationFilter={setRecommendationFilter}
          />
        )}

        {activePage === 'security_energy' && (
          <SecurityEnergyPage 
            devices={devices}
            threatEvents={threatEvents}
            selectedDevice={selectedDevice}
            onSelectDeviceById={handleSelectDeviceById}
          />
        )}
      </main>

      {/* Selected Device Deep Inspector Slide-Out Drawer / Modal */}
      {selectedDevice && (
        <DeviceDetail 
          device={selectedDevice}
          onClose={() => setSelectedDevice(null)}
          onUpdateRecommendation={handleUpdateRecommendation}
        />
      )}
    </div>
  );
}
