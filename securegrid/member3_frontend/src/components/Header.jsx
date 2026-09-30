import React, { useState } from 'react';
import { Shield, RefreshCw, Activity, Cpu, Menu, X, LayoutDashboard, Server, ShieldAlert } from 'lucide-react';

export function Header({ 
  activePage, 
  onPageChange, 
  lastUpdated, 
  isLiveApi, 
  onRefresh, 
  autoRefresh, 
  onToggleAutoRefresh 
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'OVERVIEW', icon: LayoutDashboard },
    { id: 'devices', label: 'DEVICES', icon: Server },
    { id: 'security_energy', label: 'SECURITY & ENERGY', icon: ShieldAlert }
  ];

  const handleNavClick = (id) => {
    onPageChange(id);
    setMobileMenuOpen(false);
  };

  return (
    <header className="header-wrapper">
      {/* Cybersecurity Pipeline Banner */}
      <div className="pipeline-banner">
        <div className="pipeline-title">
          <Shield size={14} style={{ color: 'var(--color-cyan)' }} />
          <span>SECUREGRID PIPELINE:</span>
        </div>
        <div className="pipeline-flow">
          <span className="pipeline-step">Telemetry</span>
          <span className="pipeline-arrow">&rarr;</span>
          <span className="pipeline-step">Anomaly Detection</span>
          <span className="pipeline-arrow">&rarr;</span>
          <span className="pipeline-step">Combined Analysis</span>
          <span className="pipeline-arrow">&rarr;</span>
          <span className="pipeline-step">Dynamic Trust Score</span>
          <span className="pipeline-arrow">&rarr;</span>
          <span className="pipeline-step">Security Event</span>
          <span className="pipeline-arrow">&rarr;</span>
          <span className="pipeline-step pipeline-step-highlight">
            ALLOW / MONITOR / RESTRICT / QUARANTINE
          </span>
        </div>
      </div>

      {/* Main SOC persistent Navigation Header */}
      <div className="header-container">
        {/* Brand Logo & Name */}
        <div className="brand-section" onClick={() => handleNavClick('overview')} style={{ cursor: 'pointer' }}>
          <div className="brand-logo">SG</div>
          <div>
            <div className="brand-title">SECUREGRID</div>
            <div className="brand-subtitle">Smart Grid Cybersecurity & Energy Monitoring System</div>
          </div>
        </div>

        {/* 3 Main Desktop Page Navigation Tabs */}
        <nav className="desktop-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                className={`nav-tab-btn ${isActive ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* System Meta & Refresh Controls */}
        <div className="header-meta">
          <div className="meta-pill">
            <span className="dot-indicator dot-green"></span>
            <span style={{ color: 'var(--text-secondary)' }}>SYSTEM:</span>
            <strong style={{ color: 'var(--color-allow)' }}>ONLINE</strong>
          </div>

          <div className="meta-pill">
            <span className={`dot-indicator ${isLiveApi ? 'dot-green' : 'dot-amber'}`}></span>
            <span style={{ color: 'var(--text-secondary)' }}>MODE:</span>
            <strong style={{ color: isLiveApi ? 'var(--color-allow)' : 'var(--color-monitor)' }}>
              {isLiveApi ? 'LIVE API' : 'DEMO DATA'}
            </strong>
          </div>

          <div className="meta-pill hide-mobile">
            <Activity size={13} style={{ color: 'var(--text-muted)' }} />
            <span>{lastUpdated || 'Just now'}</span>
          </div>

          <button 
            className="btn-refresh" 
            onClick={onToggleAutoRefresh}
            title="Toggle simulated telemetry stream updates"
          >
            <Cpu size={14} style={{ color: autoRefresh ? '#10b981' : '#94a3b8' }} />
            <span className="hide-mobile">{autoRefresh ? 'POLLING ON' : 'PAUSED'}</span>
          </button>

          <button className="btn-refresh" onClick={onRefresh} title="Fetch latest telemetry data">
            <RefreshCw size={14} />
            <span className="hide-mobile">REFRESH</span>
          </button>

          {/* Mobile Menu Hamburger Toggle */}
          <button 
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Collapsible Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="mobile-nav-drawer">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                className={`mobile-nav-btn ${isActive ? 'active' : ''}`}
                onClick={() => handleNavClick(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}
