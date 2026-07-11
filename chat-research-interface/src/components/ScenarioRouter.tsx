import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import ChatInterface from './ChatInterface';
import { getScenarioById } from '../data/scenarios';

const ScenarioRouter: React.FC = () => {
  const { scenarioId } = useParams<{ scenarioId: string }>();

  // Validate scenario exists
  const scenario = getScenarioById(scenarioId!);
  if (!scenario) {
    return <Navigate to="/" replace />;
  }

  // ChatInterface now handles Prolific ID validation internally
  return <ChatInterface />;
};

export default ScenarioRouter;