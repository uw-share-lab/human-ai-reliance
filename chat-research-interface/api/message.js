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

  const { conversationId, message } = req.body ?? {};
  if (!conversationId || !message?.id || !message?.type || message?.content == null) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const { error } = await supabase()
    .from('messages')
    .insert({
      id: message.id,
      conversation_id: conversationId,
      message_type: message.type,
      content: message.content,
      timestamp: message.timestamp,
      sequence_number: message.sequenceNumber,
    });

  if (error) return res.status(500).json({ error: error.message });
  return res.status(200).json({ success: true });
};
