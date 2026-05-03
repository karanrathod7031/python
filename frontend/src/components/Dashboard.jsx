import React, { useState, useRef, useEffect } from 'react';
import useWebSocket from '../hooks/useWebSocket';

export default function Dashboard({ addToHistory }) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const { sendMessage, lastMessage, isConnected } = useWebSocket();

  useEffect(() => {
    if (lastMessage) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', ...lastMessage, timestamp: new Date().toISOString() },
      ]);
      addToHistory({
        command: lastMessage.raw_input || '',
        response: lastMessage.response || lastMessage.action || '',
        intent: lastMessage.intent || '',
        timestamp: new Date().toISOString(),
      });
      setIsLoading(false);
    }
  }, [lastMessage, addToHistory]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    if (isConnected) {
      sendMessage({ text: input });
    } else {
      try {
        const res = await fetch('/api/assistant/command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: input }),
        });
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', ...data, timestamp: new Date().toISOString() },
        ]);
        addToHistory({
          command: input,
          response: data.response || data.action || '',
          intent: data.intent || '',
          timestamp: new Date().toISOString(),
        });
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          { role: 'error', content: `Error: ${err.message}`, timestamp: new Date().toISOString() },
        ]);
      }
      setIsLoading(false);
    }

    setInput('');
  };

  return (
    <div className="dashboard">
      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Welcome to Jarvis</h2>
              <p>Your AI-powered personal assistant. Try typing a command or asking a question.</p>
              <div className="suggestions">
                {['Open Chrome', 'What time is it?', 'Show CPU usage', 'Search for Python tutorials'].map(
                  (s) => (
                    <button key={s} className="suggestion" onClick={() => setInput(s)}>
                      {s}
                    </button>
                  )
                )}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="message-header">
                <span className="role">{msg.role === 'user' ? 'You' : 'Jarvis'}</span>
                {msg.intent && <span className="intent-badge">{msg.intent}</span>}
                {msg.confidence > 0 && (
                  <span className="confidence">{(msg.confidence * 100).toFixed(0)}%</span>
                )}
              </div>
              <div className="message-body">
                {msg.content || msg.response || `Action: ${msg.action || 'processing...'}`}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message assistant loading">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a command or ask a question..."
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </div>

      <div className="status-bar">
        <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected (WebSocket)' : 'HTTP Mode'}
        </span>
      </div>
    </div>
  );
}
