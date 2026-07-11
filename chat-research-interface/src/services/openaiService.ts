export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export class OpenAIService {
  async sendMessage(messages: ChatMessage[], scenarioType: 'aita' | 'sexism'): Promise<string> {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, scenarioType }),
    });

    const data = await response.json() as any;

    if (!response.ok) {
      const status = response.status;
      if (status === 429) throw new Error('Rate limit exceeded. Please try again later.');
      if (status === 401) throw new Error('Invalid API key. Please check your configuration.');
      if (status >= 500) throw new Error('OpenAI service is currently unavailable. Please try again later.');
      throw new Error(`OpenAI API Error: ${data.error ?? 'Unknown error'}`);
    }

    return data.content || 'I apologize, but I cannot respond at this time.';
  }

  isContentAppropriate(content: string): boolean {
    const severePatterns = [
      /\b(kill yourself|kys|die|murder)\b/gi,
      /\b(nazi|hitler|terrorist)\b/gi,
    ];
    return !severePatterns.some(pattern => pattern.test(content));
  }

  filterContent(content: string): string {
    return content
      .replace(/\b(kill yourself|kys)\b/gi, '[inappropriate content removed]')
      .replace(/\b(nazi|hitler)\b/gi, '[inappropriate content removed]');
  }
}

export const openaiService = new OpenAIService();
