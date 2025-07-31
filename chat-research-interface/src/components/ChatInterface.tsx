import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { getScenarioById } from '../data/scenarios';
import { Message, ChatState } from '../types';
import { conversationService } from '../services/conversationService';
import { openaiService, ChatMessage } from '../services/openaiService';
import ProlificIdEntry from './ProlificIdEntry';
import StartOverlay from './StartOverlay';
import { v4 as uuidv4 } from 'uuid';
import '../styles/ChatInterface.css';

const DEFAULT_TIMEOUT = parseInt(process.env.REACT_APP_DEFAULT_TIMEOUT || '20') * 60; // Convert to seconds

const ChatInterface: React.FC = () => {
  const { scenarioId } = useParams<{ scenarioId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  // Detect iframe mode and prevent auto-scroll issues in Qualtrics
  useEffect(() => {
    const isInIframe = window.self !== window.top;
    if (isInIframe) {
      document.body.classList.add('iframe-mode');
      // Prevent initial focus that could cause page jumping
      document.body.style.scrollBehavior = 'auto';
    }
    
    return () => {
      document.body.classList.remove('iframe-mode');
    };
  }, []);
  
  const scenario = getScenarioById(scenarioId!);
  const [prolificId, setProlificId] = useState<string>('');
  const [isProlificIdValidated, setIsProlificIdValidated] = useState(false);
  const [showStartOverlay, setShowStartOverlay] = useState(true);
  
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    interactionCount: 0,
    startTime: new Date(),
    timeRemaining: DEFAULT_TIMEOUT,
  });
  
  const [conversationId, setConversationId] = useState<string>('');
  const [inputValue, setInputValue] = useState('');
  const [hasStarted, setHasStarted] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [sessionEndReason, setSessionEndReason] = useState<'timeout' | 'early' | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Timeout handler
  const handleTimeout = useCallback(async () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    try {
      await conversationService.endConversation(conversationId, true);
    } catch (error) {
      console.error('Failed to end conversation on timeout:', error);
    }

    setSessionEnded(true);
    setSessionEndReason('timeout');
    alert('Session time expired. The chat is now locked, but you can still view and copy your conversation history.');
  }, [conversationId]);

  // Handle Prolific ID validation
  const handleProlificIdSet = useCallback((id: string) => {
    setProlificId(id);
    setIsProlificIdValidated(true);
  }, []);

  // Handle start overlay
  const handleStartScenario = useCallback(() => {
    setShowStartOverlay(false);
  }, []);

  // Initialize conversation only after Prolific ID is validated
  useEffect(() => {
    if (!scenario) {
      navigate('/');
      return;
    }

    if (!isProlificIdValidated || !prolificId || showStartOverlay) {
      return; // Don't initialize conversation until Prolific ID is set and start overlay is dismissed
    }

    const initConversation = async () => {
      try {
        const id = await conversationService.createConversation({
          prolificId,
          scenarioId: scenario.id,
          studyType: scenario.type,
        });
        setConversationId(id);

        // Add initial bot message
        const botMessage: Message = {
          id: uuidv4(),
          type: 'ai',
          content: scenario.botOpinion,
          timestamp: new Date(),
          sequenceNumber: 1,
        };

        setChatState(prev => ({
          ...prev,
          messages: [botMessage],
        }));

        await conversationService.saveMessage(id, botMessage);
        setHasStarted(true);
      } catch (error) {
        console.error('Failed to initialize conversation:', error);
        alert('Failed to start the conversation. Please refresh and try again.');
      }
    };

    initConversation();
  }, [scenario, prolificId, isProlificIdValidated, showStartOverlay, navigate]);

  // Timer functionality
  useEffect(() => {
    if (!hasStarted) return;

    timerRef.current = setInterval(() => {
      setChatState(prev => {
        const newTimeRemaining = prev.timeRemaining - 1;
        if (newTimeRemaining <= 0) {
          handleTimeout();
          return prev;
        }
        return { ...prev, timeRemaining: newTimeRemaining };
      });
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [hasStarted, handleTimeout]);

  // Auto-scroll to bottom (only if not in iframe to prevent Qualtrics page jumping)
  useEffect(() => {
    const isInIframe = window.self !== window.top;
    if (!isInIframe) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } else {
      // In iframe: scroll within the container only, without affecting parent page
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [chatState.messages]);

  // Handle message sending
  const sendMessage = async () => {
    if (!inputValue.trim() || chatState.isLoading || !scenario) return;

    const userMessage: Message = {
      id: uuidv4(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
      sequenceNumber: chatState.messages.length + 1,
    };

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
    }));

    setInputValue('');

    try {
      // Save user message
      await conversationService.saveMessage(conversationId, userMessage);

      // Check content appropriateness
      if (!openaiService.isContentAppropriate(userMessage.content)) {
        const warningMessage: Message = {
          id: uuidv4(),
          type: 'ai',
          content: "I notice your message contains inappropriate content. Let's keep our discussion respectful and focused on the scenario. Could you please rephrase your thoughts?",
          timestamp: new Date(),
          sequenceNumber: chatState.messages.length + 2,
        };

        setChatState(prev => ({
          ...prev,
          messages: [...prev.messages, warningMessage],
          isLoading: false,
        }));

        await conversationService.saveMessage(conversationId, warningMessage);
        return;
      }

      // Prepare conversation history for OpenAI
      const chatHistory: ChatMessage[] = [...chatState.messages, userMessage].map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content,
      }));

      // Get AI response
      const aiResponse = await openaiService.sendMessage(chatHistory, scenario.type);

      const aiMessage: Message = {
        id: uuidv4(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        sequenceNumber: chatState.messages.length + 2,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, aiMessage],
        isLoading: false,
        interactionCount: prev.interactionCount + 1,
      }));

      await conversationService.saveMessage(conversationId, aiMessage);

    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: Message = {
        id: uuidv4(),
        type: 'ai',
        content: "I'm sorry, I'm having trouble responding right now. Please try again.",
        timestamp: new Date(),
        sequenceNumber: chatState.messages.length + 2,
      };

      setChatState(prev => ({
        ...prev,
        messages: [...prev.messages, errorMessage],
        isLoading: false,
      }));
    }
  };

  // Handle early end
  const handleEarlyEnd = async () => {
    if (!window.confirm('Are you sure you want to end this scenario early? The chat will be locked but you can still view your conversation.')) {
      return;
    }

    try {
      await conversationService.endConversation(conversationId, false);
    } catch (error) {
      console.error('Failed to end conversation:', error);
    }

    setSessionEnded(true);
    setSessionEndReason('early');
    alert('Scenario ended. The chat is now locked, but you can still view and copy your conversation history.');
  };

  // Copy scenario to clipboard
  const copyScenario = async () => {
    if (!scenario) return;
    
    try {
      await navigator.clipboard.writeText(scenario.scenario);
      alert('Scenario copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy scenario:', error);
      alert('Failed to copy scenario. Please copy it manually.');
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
    
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
  };

  // Format time remaining
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (!scenario) {
    return <div className="error">Scenario not found</div>;
  }

  // Show Prolific ID entry if not validated yet
  if (!isProlificIdValidated) {
    return <ProlificIdEntry onProlificIdSet={handleProlificIdSet} />;
  }

  // Show start overlay if not dismissed yet
  if (showStartOverlay) {
    return (
      <div className="chat-container">
        <div className="header">
          <h1 className="study-title">Interactive AI Research Study</h1>
          <p className="study-subtitle">University Research - Conversation Interface</p>
        </div>
        <div className="status-bar">
          <span className="participant-info">
            Participant ID: {prolificId} • Ready to Begin
          </span>
        </div>
        <StartOverlay 
          onStart={handleStartScenario} 
          scenarioTitle={scenario.title}
        />
      </div>
    );
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="header">
        <h1 className="study-title">Interactive AI Research Study</h1>
        <p className="study-subtitle">University Research - Conversation Interface</p>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <span className="participant-info">
          Participant ID: {prolificId} • Session Active
        </span>
        <span className={`timer ${chatState.timeRemaining < 60 ? 'warning' : ''}`}>
          Time Remaining: {formatTime(chatState.timeRemaining)}
        </span>
      </div>

      {/* Safety Notice for sensitive scenarios */}
      {scenario.type === 'sexism' && (
        <div className="safety-notice">
          <strong>Research Notice:</strong> This study involves discussion of scenarios related to 
          gender and workplace situations. Please maintain respectful dialogue throughout the 
          interaction. If you feel uncomfortable at any point, you may end the session early.
        </div>
      )}

      {/* Warning Banner */}
      <div className="warning-banner">
        <strong>Important:</strong> Your session will automatically end in 3 minutes. 
        Please ensure you complete your interaction within this timeframe.
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Scenario Panel */}
        <div className="scenario-panel">
          <div className="scenario-header">Study Scenario</div>
          <div className="scenario-content">
            <p><strong>{scenario.title}:</strong></p>
            <p>{scenario.scenario}</p>
          </div>
          <button 
            className="copy-button"
            onClick={copyScenario}
            disabled={chatState.isLoading}
          >
            Copy Scenario to Chat
          </button>
        </div>

        {/* Chat Panel */}
        <div className="chat-panel">
          <div className="chat-header">Conversation with AI Assistant</div>
          
          {sessionEnded && (
            <div className={`session-status ${sessionEndReason}`}>
              <strong>
                {sessionEndReason === 'timeout' 
                  ? '⏰ Session Time Expired' 
                  : '✋ Session Ended Early'
                }
              </strong>
              <br />
              The chat is now locked. You can still view and copy your conversation history.
            </div>
          )}

          <div className="chat-messages">
            {chatState.messages.map((message, index) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-avatar">
                  {message.type === 'ai' ? 'AI' : 'You'}
                </div>
                <div className="message-content">
                  <div>{message.content}</div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </div>
                </div>
              </div>
            ))}
            
            {chatState.isLoading && (
              <div className="message ai">
                <div className="message-avatar">AI</div>
                <div className="message-content">
                  <div className="loading">
                    <span>AI is typing</span>
                    <span className="loading-dots">...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <div className="input-group">
              <textarea
                ref={inputRef}
                className="input-field"
                placeholder={sessionEnded ? "Session ended - chat is locked" : "Type your message here..."}
                value={inputValue}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                rows={1}
                disabled={chatState.isLoading || sessionEnded}
              />
              <button
                className="send-button"
                onClick={sendMessage}
                disabled={chatState.isLoading || !inputValue.trim() || sessionEnded}
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="controls">
        <span className="interaction-counter">
          Interactions: {chatState.interactionCount} exchanges
        </span>
        <button className="end-button" onClick={handleEarlyEnd} disabled={sessionEnded}>
          {sessionEnded ? 'Session Ended' : 'End Session Early'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;