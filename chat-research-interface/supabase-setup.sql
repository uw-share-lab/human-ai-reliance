-- Supabase Database Schema for LLM Research Interface
-- Run this in your Supabase SQL editor to set up the database

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  prolific_id TEXT NOT NULL,
  scenario_id TEXT NOT NULL,
  study_type TEXT NOT NULL CHECK (study_type IN ('aita', 'sexism')),
  session_data JSONB NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ,
  duration_ms INTEGER,
  interaction_count INTEGER DEFAULT 0,
  completed_normally BOOLEAN DEFAULT false,
  timed_out BOOLEAN DEFAULT false,
  user_agent TEXT,
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create participants table for tracking participant info
CREATE TABLE IF NOT EXISTS participants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  prolific_id TEXT UNIQUE NOT NULL,
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  total_conversations INTEGER DEFAULT 0,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create messages table for detailed message analysis
CREATE TABLE IF NOT EXISTS messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  message_type TEXT NOT NULL CHECK (message_type IN ('user', 'ai')),
  content TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  sequence_number INTEGER NOT NULL,
  response_time_seconds NUMERIC,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_conversations_prolific_id ON conversations(prolific_id);
CREATE INDEX IF NOT EXISTS idx_conversations_scenario_id ON conversations(scenario_id);
CREATE INDEX IF NOT EXISTS idx_conversations_study_type ON conversations(study_type);
CREATE INDEX IF NOT EXISTS idx_conversations_start_time ON conversations(start_time);
CREATE INDEX IF NOT EXISTS idx_conversations_completed ON conversations(completed_normally);

CREATE INDEX IF NOT EXISTS idx_participants_prolific_id ON participants(prolific_id);
CREATE INDEX IF NOT EXISTS idx_participants_first_seen ON participants(first_seen);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_conversations_updated_at ON conversations;
CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_participants_updated_at ON participants;
CREATE TRIGGER update_participants_updated_at 
    BEFORE UPDATE ON participants 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust as needed for your security requirements)
-- Note: For research data, you might want more restrictive policies

-- Allow anonymous users to insert conversations (for data collection)
CREATE POLICY "Allow anonymous inserts" ON conversations
  FOR INSERT TO anon
  WITH CHECK (true);

-- Allow anonymous users to insert participants
CREATE POLICY "Allow anonymous participant inserts" ON participants
  FOR INSERT TO anon
  WITH CHECK (true);

-- Allow anonymous users to insert messages
CREATE POLICY "Allow anonymous message inserts" ON messages
  FOR INSERT TO anon
  WITH CHECK (true);

-- Allow authenticated users to read all data (for researchers)
CREATE POLICY "Allow authenticated read access" ON conversations
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Allow authenticated participant read" ON participants
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "Allow authenticated message read" ON messages
  FOR SELECT TO authenticated
  USING (true);

-- Create a view for easy data analysis
CREATE OR REPLACE VIEW conversation_summary AS
SELECT 
  c.id,
  c.prolific_id,
  c.scenario_id,
  c.study_type,
  c.start_time,
  c.end_time,
  c.duration_ms,
  ROUND(c.duration_ms::numeric / 60000, 2) as duration_minutes,
  c.interaction_count,
  c.completed_normally,
  c.timed_out,
  (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as total_messages,
  (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id AND m.message_type = 'user') as user_messages,
  (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id AND m.message_type = 'ai') as ai_messages,
  c.created_at
FROM conversations c
ORDER BY c.start_time DESC;

-- Create a function to get research statistics
CREATE OR REPLACE FUNCTION get_research_stats()
RETURNS TABLE (
  total_conversations bigint,
  unique_participants bigint,
  aita_conversations bigint,
  sexism_conversations bigint,
  completed_conversations bigint,
  timed_out_conversations bigint,
  avg_duration_minutes numeric,
  total_messages bigint
) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*) as total_conversations,
    COUNT(DISTINCT prolific_id) as unique_participants,
    COUNT(*) FILTER (WHERE study_type = 'aita') as aita_conversations,
    COUNT(*) FILTER (WHERE study_type = 'sexism') as sexism_conversations,
    COUNT(*) FILTER (WHERE completed_normally = true) as completed_conversations,
    COUNT(*) FILTER (WHERE timed_out = true) as timed_out_conversations,
    ROUND(AVG(duration_ms::numeric / 60000), 2) as avg_duration_minutes,
    (SELECT COUNT(*) FROM messages) as total_messages
  FROM conversations;
END;
$$;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON conversations TO anon, authenticated;
GRANT ALL ON participants TO anon, authenticated;
GRANT ALL ON messages TO anon, authenticated;
GRANT SELECT ON conversation_summary TO authenticated;
GRANT EXECUTE ON FUNCTION get_research_stats() TO authenticated;

-- Insert sample data (optional - remove in production)
-- INSERT INTO conversations (prolific_id, scenario_id, study_type, session_data, start_time, end_time, duration_ms, interaction_count, completed_normally)
-- VALUES ('SAMPLE123', 'aita-test', 'aita', '{"test": "data"}', NOW() - INTERVAL '1 hour', NOW() - INTERVAL '30 minutes', 1800000, 5, true);

COMMENT ON TABLE conversations IS 'Stores complete conversation sessions between participants and AI';
COMMENT ON TABLE participants IS 'Tracks participant information and metadata';
COMMENT ON TABLE messages IS 'Stores individual messages for detailed analysis';
COMMENT ON VIEW conversation_summary IS 'Convenient view for analyzing conversation data';