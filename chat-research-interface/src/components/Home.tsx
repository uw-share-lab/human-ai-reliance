import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { scenarios } from '../data/scenarios';
import '../styles/Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const handleScenarioSelect = (scenarioId: string) => {
    // Preserve URL parameters when navigating
    const params = new URLSearchParams(searchParams);
    navigate(`/scenario/${scenarioId}?${params.toString()}`);
  };

  const prolificId = searchParams.get('PROLIFIC_PID');

  return (
    <div className="home-container">
      <div className="header">
        <h1 className="study-title">Interactive AI Research Study</h1>
        <p className="study-subtitle">University Research - Scenario Selection</p>
      </div>

      {prolificId && (
        <div className="participant-info">
          <span>Participant ID: {prolificId}</span>
        </div>
      )}

      <div className="scenarios-grid">
        <div className="scenario-category">
          <h2>AITA Scenarios</h2>
          <p>Moral reasoning and ethical judgment scenarios</p>
          <div className="scenarios-list">
            {scenarios
              .filter(s => s.type === 'aita')
              .map((scenario) => (
                <div key={scenario.id} className="scenario-card">
                  <h3>{scenario.title}</h3>
                  <p>{scenario.scenario.substring(0, 150)}...</p>
                  <button 
                    className="select-button"
                    onClick={() => handleScenarioSelect(scenario.id)}
                  >
                    Start Discussion
                  </button>
                </div>
              ))
            }
          </div>
        </div>

        <div className="scenario-category">
          <h2>Sexism Scenarios</h2>
          <p>Gender dynamics and workplace bias scenarios</p>
          <div className="scenarios-list">
            {scenarios
              .filter(s => s.type === 'sexism')
              .map((scenario) => (
                <div key={scenario.id} className="scenario-card">
                  <h3>{scenario.title}</h3>
                  <p>{scenario.scenario.substring(0, 150)}...</p>
                  <button 
                    className="select-button"
                    onClick={() => handleScenarioSelect(scenario.id)}
                  >
                    Start Discussion
                  </button>
                </div>
              ))
            }
          </div>
        </div>
      </div>

      <div className="instructions">
        <h3>Instructions</h3>
        <ul>
          <li>Select a scenario to begin the conversation</li>
          <li>You will have 20 minutes to discuss the scenario with an AI assistant</li>
          <li>Your conversation will be automatically saved</li>
          <li>You can end the session early if needed</li>
        </ul>
      </div>
    </div>
  );
};

export default Home;