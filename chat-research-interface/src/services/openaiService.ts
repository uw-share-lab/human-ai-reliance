import axios from 'axios';

const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export class OpenAIService {
  private apiKey: string;

  constructor() {
    this.apiKey = process.env.REACT_APP_OPENAI_API_KEY!;
    if (!this.apiKey) {
      throw new Error('OpenAI API key not found in environment variables');
    }
  }

  async sendMessage(
    messages: ChatMessage[],
    scenarioType: 'aita' | 'sexism'
  ): Promise<string> {
    const systemMessage = this.getSystemMessage(scenarioType);
    
    const fullMessages = [systemMessage, ...messages];

    try {
      const response = await axios.post(
        OPENAI_API_URL,
        {
          model: 'gpt-4.1',
          messages: fullMessages,
          max_tokens: 500,
          temperature: 0.7,
          presence_penalty: 0.1,
          frequency_penalty: 0.1,
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      return response.data.choices[0]?.message?.content || 'I apologize, but I cannot respond at this time.';
    } catch (error) {
      console.error('OpenAI API Error:', error);
      
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const message = error.response?.data?.error?.message || error.message;
        
        if (status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.');
        } else if (status === 401) {
          throw new Error('Invalid API key. Please check your configuration.');
        } else if (status && status >= 500) {
          throw new Error('OpenAI service is currently unavailable. Please try again later.');
        } else {
          throw new Error(`OpenAI API Error: ${message}`);
        }
      }
      
      throw new Error('Failed to get response from AI. Please try again.');
    }
  }

  private getSystemMessage(scenarioType: 'aita' | 'sexism'): ChatMessage {
    const baseInstructions = `You are participating in a research study about moral reasoning and social judgments. 

IMPORTANT: You will engage with a participant to help them make a decision regarding ${scenarioType === 'sexism' ? 'sexism' : 'fault/responsibility'} of a reddit post. Note that the participant is not the person who experienced the scenario - they are a third-party observer evaluating the situation, similar to your role. When referring to the person in the scenario, use "they/them" rather than "you."

You should:

1. Engage thoughtfully with the human's perspective
2. Ask follow-up questions to understand their reasoning
3. Present different viewpoints respectfully
4. Keep responses conversational and under 150 words
5. Stay focused on the scenario being discussed
6. Be curious about their thought process
7. Avoid being preachy or judgmental`;

    const specificInstructions = scenarioType === 'sexism' 
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

    return {
      role: 'system',
      content: baseInstructions + specificInstructions
    };
  }

  // Content moderation for safety
  isContentAppropriate(content: string): boolean {
    // Flag severe content
    const severePatterns = [
      /\b(kill yourself|kys|die|murder)\b/gi,
      /\b(nazi|hitler|terrorist)\b/gi,
    ];

    return !severePatterns.some(pattern => pattern.test(content));
  }

  filterContent(content: string): string {
    // Basic content filtering - replace severe inappropriate content
    const filtered = content
      .replace(/\b(kill yourself|kys)\b/gi, '[inappropriate content removed]')
      .replace(/\b(nazi|hitler)\b/gi, '[inappropriate content removed]');
    
    return filtered;
  }
}

export const openaiService = new OpenAIService();