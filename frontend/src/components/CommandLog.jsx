import React from 'react';

export default function CommandLog({ history }) {
  return (
    <div className="command-log">
      <h2>Command History</h2>
      {history.length === 0 ? (
        <p className="empty">No commands yet. Start by typing in the Dashboard.</p>
      ) : (
        <table className="log-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Command</th>
              <th>Intent</th>
              <th>Response</th>
            </tr>
          </thead>
          <tbody>
            {history.map((entry, i) => (
              <tr key={i}>
                <td className="time">
                  {new Date(entry.timestamp).toLocaleTimeString()}
                </td>
                <td className="command">{entry.command}</td>
                <td>
                  <span className="intent-badge">{entry.intent || 'N/A'}</span>
                </td>
                <td className="response">{entry.response?.substring(0, 100)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
