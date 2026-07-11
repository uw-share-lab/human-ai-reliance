import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import ScenarioRouter from './components/ScenarioRouter';
import './App.css';

// Simple status pages
const TimeoutPage: React.FC = () => (
  <div className="status-page">
    <div className="status-container">
      <h1>Session Timeout</h1>
      <p>Your session has timed out. Thank you for your participation in this research study.</p>
      <p>Please return to your survey to continue.</p>
    </div>
  </div>
);

const CompletePage: React.FC = () => (
  <div className="status-page">
    <div className="status-container">
      <h1>Session Complete</h1>
      <p>Thank you for participating in this research study!</p>
      <p>Please return to your survey to complete the remaining questions.</p>
    </div>
  </div>
);

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scenario/:scenarioId" element={<ScenarioRouter />} />
          <Route path="/timeout" element={<TimeoutPage />} />
          <Route path="/complete" element={<CompletePage />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;