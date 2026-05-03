import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import CommandLog from './components/CommandLog';
import Settings from './components/Settings';
import SystemMonitor from './components/SystemMonitor';
import VoiceAnimation from './components/VoiceAnimation';

const TABS = [
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'monitor', label: 'System Monitor' },
  { id: 'logs', label: 'Command Logs' },
  { id: 'settings', label: 'Settings' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isListening, setIsListening] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);

  const addToHistory = (entry) => {
    setCommandHistory((prev) => [entry, ...prev].slice(0, 200));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1 className="logo">JARVIS</h1>
          <span className="subtitle">AI Assistant</span>
        </div>
        <nav className="tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
        <div className="header-right">
          <VoiceAnimation isListening={isListening} />
          <button
            className={`voice-btn ${isListening ? 'listening' : ''}`}
            onClick={() => setIsListening(!isListening)}
          >
            {isListening ? 'Stop' : 'Listen'}
          </button>
        </div>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && (
          <Dashboard addToHistory={addToHistory} />
        )}
        {activeTab === 'monitor' && <SystemMonitor />}
        {activeTab === 'logs' && <CommandLog history={commandHistory} />}
        {activeTab === 'settings' && <Settings />}
      </main>

      <footer className="app-footer">
        <span>Jarvis AI Assistant v1.0.0</span>
        <span>Powered by Ollama + FastAPI</span>
      </footer>
    </div>
  );
}
