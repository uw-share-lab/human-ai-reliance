import { Message } from '../types';

async function apiPost(path: string, body: unknown): Promise<unknown> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: string };
    throw new Error(err.error ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export class ConversationService {
  async createConversation(data: {
    prolificId: string;
    scenarioId: string;
    studyType: 'aita' | 'sexism';
  }): Promise<string> {
    const result = await apiPost('/api/conversation/create', {
      prolificId: data.prolificId,
      scenarioId: data.scenarioId,
      studyType: data.studyType,
    }) as { conversationId: string };
    return result.conversationId;
  }

  async saveMessage(conversationId: string, message: Message): Promise<void> {
    await apiPost('/api/message', {
      conversationId,
      message: {
        id: message.id,
        type: message.type,
        content: message.content,
        timestamp: message.timestamp.toISOString(),
        sequenceNumber: message.sequenceNumber,
      },
    });
  }

  async updateInteractionCount(conversationId: string, count: number): Promise<void> {
    await apiPost('/api/conversation/update', { conversationId, interactionCount: count });
  }

  async endConversation(conversationId: string, timedOut: boolean = false): Promise<void> {
    await apiPost('/api/conversation/end', { conversationId, timedOut });
  }
}

export const conversationService = new ConversationService();
