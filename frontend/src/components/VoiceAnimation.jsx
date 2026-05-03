import React from 'react';

export default function VoiceAnimation({ isListening }) {
  return (
    <div className={`voice-animation ${isListening ? 'active' : ''}`}>
      <div className="bar bar-1"></div>
      <div className="bar bar-2"></div>
      <div className="bar bar-3"></div>
      <div className="bar bar-4"></div>
      <div className="bar bar-5"></div>
    </div>
  );
}
