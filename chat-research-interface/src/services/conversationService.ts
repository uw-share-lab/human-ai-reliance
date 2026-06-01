import { supabase } from './supabaseClient';
import { Message } from '../types';
import { v4 as uuidv4 } from 'uuid';

export class ConversationService {
  async createConversation(data: {
    prolificId: string;
    scenarioId: string;
    studyType: 'aita' | 'sexism';
  }): Promise<string> {
    console.log('Creating conversation with data:', data);
    const conversationId = uuidv4();
    const startTime = new Date().toISOString();

    try {
      // Create participant if not exists
      console.log('Creating/updating participant:', data.prolificId);
      await this.upsertParticipant(data.prolificId);
      console.log('Participant created/updated successfully');

      // Create conversation
      console.log('Creating conversation with ID:', conversationId);
      const { data: insertedData, error: conversationError } = await supabase
        .from('conversations')
        .insert({
          id: conversationId,
          prolific_id: data.prolificId,
          scenario_id: data.scenarioId,
          study_type: data.studyType,
          session_data: {},
          start_time: startTime,
          interaction_count: 0,
          completed_normally: false,
          timed_out: false,
          user_agent: navigator.userAgent,
        })
        .select();

      console.log('Conversation insert result:', { insertedData, conversationError });

      if (conversationError) {
        throw new Error(`Failed to create conversation: ${conversationError.message}`);
      }

      console.log('Conversation created successfully:', conversationId);
      return conversationId;
    } catch (error) {
      console.error('Error in createConversation:', error);
      throw error;
    }
  }

  async saveMessage(conversationId: string, message: Message): Promise<void> {
    const { error } = await supabase
      .from('messages')
      .insert({
        id: message.id,
        conversation_id: conversationId,
        message_type: message.type,
        content: message.content,
        timestamp: message.timestamp.toISOString(),
        sequence_number: message.sequenceNumber,
      });

    if (error) {
      throw new Error(`Failed to save message: ${error.message}`);
    }
  }

  async updateInteractionCount(conversationId: string, count: number): Promise<void> {
    const { error } = await supabase
      .from('conversations')
      .update({
        interaction_count: count,
        updated_at: new Date().toISOString()
      })
      .eq('id', conversationId);

    if (error) {
      throw new Error(`Failed to update interaction count: ${error.message}`);
    }
  }

  async endConversation(conversationId: string, timedOut: boolean = false): Promise<void> {
    const endTime = new Date().toISOString();

    // Get conversation start time to calculate duration
    const { data: conversation, error: getError } = await supabase
      .from('conversations')
      .select('start_time')
      .eq('id', conversationId)
      .single();

    if (getError) {
      throw new Error(`Failed to get conversation: ${getError.message}`);
    }

    const startTime = new Date(conversation.start_time);
    const duration = new Date().getTime() - startTime.getTime();

    const { error } = await supabase
      .from('conversations')
      .update({
        end_time: endTime,
        duration_ms: duration,
        completed_normally: !timedOut,
        timed_out: timedOut,
        updated_at: new Date().toISOString()
      })
      .eq('id', conversationId);

    if (error) {
      throw new Error(`Failed to end conversation: ${error.message}`);
    }
  }

  private async upsertParticipant(prolificId: string): Promise<void> {
    // Atomic upsert — safe under concurrent sessions for the same Prolific ID
    const { error } = await supabase
      .from('participants')
      .upsert(
        {
          id: uuidv4(),
          prolific_id: prolificId,
          first_seen: new Date().toISOString(),
          total_conversations: 1,
          metadata: {}
        },
        { onConflict: 'prolific_id', ignoreDuplicates: true }
      );

    if (error) {
      throw new Error(`Failed to upsert participant: ${error.message}`);
    }
  }
}

export const conversationService = new ConversationService();