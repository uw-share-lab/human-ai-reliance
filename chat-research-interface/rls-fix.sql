-- Fix RLS policies to allow anonymous access for data collection

-- Allow anonymous users to SELECT participants (needed for upsert operations)
DROP POLICY IF EXISTS "Allow anonymous participant select" ON participants;
CREATE POLICY "Allow anonymous participant select" ON participants
  FOR SELECT TO anon
  USING (true);

-- Allow anonymous users to UPDATE participants (for upsert operations)  
DROP POLICY IF EXISTS "Allow anonymous participant updates" ON participants;
CREATE POLICY "Allow anonymous participant updates" ON participants
  FOR UPDATE TO anon
  USING (true);

-- Allow anonymous users to SELECT conversations (needed for some operations)
DROP POLICY IF EXISTS "Allow anonymous conversation select" ON conversations;
CREATE POLICY "Allow anonymous conversation select" ON conversations
  FOR SELECT TO anon
  USING (true);

-- Allow anonymous users to UPDATE conversations (for ending sessions)
DROP POLICY IF EXISTS "Allow anonymous conversation updates" ON conversations;
CREATE POLICY "Allow anonymous conversation updates" ON conversations
  FOR UPDATE TO anon
  USING (true);