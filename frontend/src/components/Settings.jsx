import React, { useState, useEffect } from 'react';

export default function Settings() {
  const [preferences, setPreferences] = useState({});
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const res = await fetch('/api/memory/preferences');
      const data = await res.json();
      setPreferences(data.preferences || {});
    } catch {
      // Backend not running
    } finally {
      setLoading(false);
    }
  };

  const updatePreference = async (key, value) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
    try {
      await fetch('/api/memory/preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // ignore
    }
  };

  if (loading) return <div className="settings loading-text">Loading settings...</div>;

  return (
    <div className="settings">
      <h2>Settings</h2>
      {saved && <div className="saved-notice">Settings saved!</div>}

      <div className="settings-grid">
        <div className="setting-group">
          <h3>General</h3>
          <div className="setting-item">
            <label>Your Name</label>
            <input
              type="text"
              value={preferences.greeting_name || ''}
              onChange={(e) => updatePreference('greeting_name', e.target.value)}
            />
          </div>
          <div className="setting-item">
            <label>Language</label>
            <select
              value={preferences.language || 'en'}
              onChange={(e) => updatePreference('language', e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="auto">Auto-detect</option>
            </select>
          </div>
          <div className="setting-item">
            <label>Theme</label>
            <select
              value={preferences.theme || 'dark'}
              onChange={(e) => updatePreference('theme', e.target.value)}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>
        </div>

        <div className="setting-group">
          <h3>Voice</h3>
          <div className="setting-item">
            <label>Wake Word</label>
            <input
              type="text"
              value={preferences.wake_word || 'jarvis'}
              onChange={(e) => updatePreference('wake_word', e.target.value)}
            />
          </div>
          <div className="setting-item">
            <label>TTS Voice</label>
            <select
              value={preferences.tts_voice || 'en-US-GuyNeural'}
              onChange={(e) => updatePreference('tts_voice', e.target.value)}
            >
              <option value="en-US-GuyNeural">English Male</option>
              <option value="en-US-JennyNeural">English Female</option>
              <option value="hi-IN-MadhurNeural">Hindi Male</option>
              <option value="hi-IN-SwaraNeural">Hindi Female</option>
            </select>
          </div>
        </div>

        <div className="setting-group">
          <h3>Security</h3>
          <div className="setting-item">
            <label>Require Confirmation for Risky Actions</label>
            <input
              type="checkbox"
              checked={preferences.confirmation_required !== false}
              onChange={(e) => updatePreference('confirmation_required', e.target.checked)}
            />
          </div>
          <div className="setting-item">
            <label>Notification Sound</label>
            <input
              type="checkbox"
              checked={preferences.notification_sound !== false}
              onChange={(e) => updatePreference('notification_sound', e.target.checked)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
