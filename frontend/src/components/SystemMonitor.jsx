import React, { useState, useEffect } from 'react';

export default function SystemMonitor() {
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSystemInfo = async () => {
    try {
      const res = await fetch('/api/monitoring/status');
      const data = await res.json();
      setSystemInfo(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch system info. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemInfo();
    const interval = setInterval(fetchSystemInfo, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="monitor loading-text">Loading system info...</div>;
  if (error) return <div className="monitor error-text">{error}</div>;

  const { cpu, memory, disk, network, battery } = systemInfo || {};

  return (
    <div className="system-monitor">
      <h2>System Monitor</h2>
      <div className="monitor-grid">
        <div className="monitor-card">
          <h3>CPU</h3>
          <div className="metric-value">{cpu?.percent ?? 'N/A'}%</div>
          <div className="metric-bar">
            <div className="bar-fill" style={{ width: `${cpu?.percent || 0}%` }}></div>
          </div>
          <p>Cores: {cpu?.count_logical ?? 'N/A'} logical / {cpu?.count_physical ?? 'N/A'} physical</p>
        </div>

        <div className="monitor-card">
          <h3>Memory</h3>
          <div className="metric-value">{memory?.percent ?? 'N/A'}%</div>
          <div className="metric-bar">
            <div className="bar-fill" style={{ width: `${memory?.percent || 0}%` }}></div>
          </div>
          <p>{memory?.used_gb ?? '?'} / {memory?.total_gb ?? '?'} GB</p>
        </div>

        <div className="monitor-card">
          <h3>Network</h3>
          <p>Sent: {network?.sent_mb ?? 'N/A'} MB</p>
          <p>Received: {network?.recv_mb ?? 'N/A'} MB</p>
        </div>

        {battery?.has_battery && (
          <div className="monitor-card">
            <h3>Battery</h3>
            <div className="metric-value">{battery.percent}%</div>
            <div className="metric-bar">
              <div className="bar-fill battery" style={{ width: `${battery.percent}%` }}></div>
            </div>
            <p>{battery.plugged_in ? 'Charging' : 'On Battery'}</p>
          </div>
        )}

        {disk?.map((d, i) => (
          <div key={i} className="monitor-card">
            <h3>Disk: {d.mountpoint}</h3>
            <div className="metric-value">{d.percent}%</div>
            <div className="metric-bar">
              <div className="bar-fill" style={{ width: `${d.percent}%` }}></div>
            </div>
            <p>{d.used_gb} / {d.total_gb} GB ({d.filesystem})</p>
          </div>
        ))}
      </div>

      <button className="refresh-btn" onClick={fetchSystemInfo}>Refresh</button>
    </div>
  );
}
