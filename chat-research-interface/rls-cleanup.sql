-- Remove all anon write and read access now that every Supabase write goes
-- through Vercel serverless functions using the service_role key.
-- Run this in your Supabase SQL editor after deploying the updated functions.

-- Drop overly-permissive anon policies added by rls-fix.sql and supabase-setup.sql
DROP POLICY IF EXISTS "Allow anonymous inserts"               ON conversations;
DROP POLICY IF EXISTS "Allow anonymous conversation select"   ON conversations;
DROP POLICY IF EXISTS "Allow anonymous conversation updates"  ON conversations;

DROP POLICY IF EXISTS "Allow anonymous participant inserts"   ON participants;
DROP POLICY IF EXISTS "Allow anonymous participant select"    ON participants;
DROP POLICY IF EXISTS "Allow anonymous participant updates"   ON participants;

DROP POLICY IF EXISTS "Allow anonymous message inserts"       ON messages;

-- Revoke all privileges granted to the anon role.
-- The service_role key used by the Vercel functions bypasses RLS entirely,
-- so it is unaffected by these revocations.
REVOKE ALL ON conversations FROM anon;
REVOKE ALL ON participants  FROM anon;
REVOKE ALL ON messages      FROM anon;

-- Researchers (authenticated role) retain full read access.
-- "Allow authenticated read access", "Allow authenticated participant read",
-- and "Allow authenticated message read" policies are left in place.
