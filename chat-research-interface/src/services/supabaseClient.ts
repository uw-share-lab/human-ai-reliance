import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL!;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY!;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export interface DatabaseConversation {
  id: string;
  prolific_id: string;
  scenario_id: string;
  study_type: 'aita' | 'sexism';
  session_data: any;
  start_time: string;
  end_time?: string;
  duration_ms?: number;
  interaction_count: number;
  completed_normally: boolean;
  timed_out: boolean;
  user_agent?: string;
  ip_address?: string;
}

export interface DatabaseMessage {
  id: string;
  conversation_id: string;
  message_type: 'user' | 'ai';
  content: string;
  timestamp: string;
  sequence_number: number;
  response_time_seconds?: number;
}

export interface DatabaseParticipant {
  id: string;
  prolific_id: string;
  first_seen: string;
  total_conversations: number;
  metadata?: any;
}