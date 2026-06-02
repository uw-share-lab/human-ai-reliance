const { createClient } = require('@supabase/supabase-js');

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

  const { conversationId, timedOut = false } = req.body ?? {};
  if (!conversationId) {
    return res.status(400).json({ error: 'Missing conversationId' });
  }

  const db = supabase();

  const { data: conv, error: readErr } = await db
    .from('conversations')
    .select('start_time')
    .eq('id', conversationId)
    .single();

  if (readErr || !conv) {
    return res.status(404).json({ error: 'Conversation not found' });
  }

  const endTime = new Date().toISOString();
  const duration = Date.now() - new Date(conv.start_time).getTime();

  const { error } = await db
    .from('conversations')
    .update({
      end_time: endTime,
      duration_ms: duration,
      completed_normally: !timedOut,
      timed_out: timedOut,
      updated_at: endTime,
    })
    .eq('id', conversationId);

  if (error) return res.status(500).json({ error: error.message });
  return res.status(200).json({ success: true });
};
