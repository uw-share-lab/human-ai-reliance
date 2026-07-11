import React from 'react';
import '../styles/StartOverlay.css';

interface StartOverlayProps {
  onStart: () => void;
  scenarioTitle: string;
}

const StartOverlay: React.FC<StartOverlayProps> = ({ onStart, scenarioTitle }) => {
  return (
    <div className="start-overlay">
      <div className="start-overlay-backdrop" />
      <div className="start-overlay-content">
        <div className="start-icon">🎯</div>
        <h2>Ready to Begin?</h2>
        <p>You're about to start the scenario:</p>
        <div className="scenario-title">{scenarioTitle}</div>
        <p className="start-instructions">
          Click "Start Scenario" when you're ready to begin the interaction. 
          Once started, your session timer will begin.
        </p>
        <button 
          className="start-button"
          onClick={onStart}
        >
          Start Scenario
        </button>
      </div>
    </div>
  );
};

export default StartOverlay;