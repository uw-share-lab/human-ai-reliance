const { createClient } = require('@supabase/supabase-js');
const { v4: uuidv4 } = require('uuid');

const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN;

function supabase() {
  return createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );
}

module.exports = async function handler(req, res) {
  const origin = req.headers.origin;
  if (ALLOWED_ORIGIN && origin && origin !== ALLOWED_ORIGIN) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { prolificId, scenarioId, studyType } = req.body ?? {};
  if (!prolificId || !scenarioId || !studyType) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const db = supabase();

  const { error: participantError } = await db
    .from('participants')
    .upsert(
      { prolific_id: prolificId, first_seen: new Date().toISOString(), metadata: {} },
      { onConflict: 'prolific_id', ignoreDuplicates: true }
    );

  if (participantError) {
    return res.status(500).json({ error: participantError.message });
  }

  const conversationId = uuidv4();
  const startTime = new Date().toISOString();

  const { error: conversationError } = await db
    .from('conversations')
    .insert({
      id: conversationId,
      prolific_id: prolificId,
      scenario_id: scenarioId,
      study_type: studyType,
      session_data: {},
      start_time: startTime,
      interaction_count: 0,
      completed_normally: false,
      timed_out: false,
      user_agent: req.headers['user-agent'] ?? '',
    });

  if (conversationError) {
    return res.status(500).json({ error: conversationError.message });
  }

  return res.status(200).json({ conversationId });
};
