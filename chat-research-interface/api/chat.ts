const OPENAI_URL = 'https://api.openai.com/v1/chat/completions';
const MAX_RETRIES = 3;

export default async function handler(req: any, res: any) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'Server configuration error' });
  }

  const { messages, scenarioType } = req.body ?? {};
  if (!messages || !scenarioType) {
    return res.status(400).json({ error: 'Missing messages or scenarioType' });
  }

  const body = {
    model: 'gpt-4.1',
    messages: [buildSystemMessage(scenarioType), ...messages],
    max_tokens: 500,
    temperature: 0.7,
    presence_penalty: 0.1,
    frequency_penalty: 0.1,
  };

  let lastStatus = 500;
  let lastError = 'Unknown error';

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    if (attempt > 0) {
      await sleep(Math.pow(2, attempt - 1) * 1000);
    }

    let response: any;
    try {
      response = await fetch(OPENAI_URL, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
    } catch (_) {
      lastError = 'Network error contacting OpenAI';
      continue;
    }

    if (response.ok) {
      const data = await response.json();
      const content = data.choices?.[0]?.message?.content ?? '';
      return res.status(200).json({ content });
    }

    lastStatus = response.status;
    const errData = await response.json().catch(() => ({}));
    lastError = errData?.error?.message ?? `HTTP ${response.status}`;

    if (response.status !== 429 && response.status < 500) break;

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      if (retryAfter) await sleep(parseInt(retryAfter) * 1000);
    }
  }

  return res.status(lastStatus >= 400 ? lastStatus : 500).json({ error: lastError });
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function buildSystemMessage(scenarioType: string) {
  const base = `You are participating in a research study about moral reasoning and social judgments.

IMPORTANT: You will engage with a participant to help them make a decision regarding ${scenarioType === 'sexism' ? 'sexism' : 'fault/responsibility'} of a reddit post. Note that the participant is NOT the person who experienced the scenario - they are a third-party observer evaluating the situation, similar to your role.

CRITICAL: When discussing the scenario, NEVER use "you" or "you're" to refer to the person in the scenario. Always use "they/them/the person/the poster" instead. The participant you're talking to is evaluating someone else's situation.

You should:

1. Engage thoughtfully with the human's perspective
2. Ask follow-up questions to understand their reasoning
3. Present different viewpoints respectfully
4. Keep responses conversational and under 150 words
5. Stay focused on the scenario being discussed
6. Be curious about their thought process
7. Avoid being preachy or judgmental`;

  const specific = scenarioType === 'sexism'
    ? `\n\nThis conversation is about a scenario related to gender and potential sexism. Be especially thoughtful about:
- Different perspectives on gender-related issues
- How societal norms and expectations might influence judgments
- The complexity of gender dynamics in various situations
- Respectful dialogue about sensitive topics`
    : `\n\nThis conversation is about a moral dilemma scenario. Focus on:
- Understanding different ethical perspectives
- Exploring the reasoning behind moral judgments
- Considering various stakeholders and their perspectives
- Discussing fairness, responsibility, and consequences`;

  return { role: 'system', content: base + specific };
}
