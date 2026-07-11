export interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  sequenceNumber: number;
}

export interface ConversationData {
  conversationId: string;
  prolificId: string;
  scenarioId: string;
  studyType: 'aita' | 'sexism';
  startTime: Date;
  endTime?: Date;
  durationMs?: number;
  interactionCount: number;
  completedNormally: boolean;
  timedOut: boolean;
  messages: Message[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  interactionCount: number;
  startTime: Date;
  timeRemaining: number;
}

export interface ProlificParams {
  PROLIFIC_PID?: string;
  STUDY_ID?: string;
  SESSION_ID?: string;
}