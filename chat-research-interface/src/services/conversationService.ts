import { supabase, DatabaseConversation, DatabaseMessage } from './supabaseClient';
import { ConversationData, Message } from '../types';
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

    // Update interaction count
    await this.updateInteractionCount(conversationId);
  }

  async updateInteractionCount(conversationId: string): Promise<void> {
    const { data, error: countError } = await supabase
      .from('messages')
      .select('id')
      .eq('conversation_id', conversationId)
      .eq('message_type', 'user');

    if (countError) {
      throw new Error(`Failed to get message count: ${countError.message}`);
    }

    const interactionCount = data.length;

    const { error: updateError } = await supabase
      .from('conversations')
      .update({ 
        interaction_count: interactionCount,
        updated_at: new Date().toISOString()
      })
      .eq('id', conversationId);

    if (updateError) {
      throw new Error(`Failed to update interaction count: ${updateError.message}`);
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
    console.log('Checking for existing participant:', prolificId);
    const { data: existing, error: selectError } = await supabase
      .from('participants')
      .select('id, total_conversations')
      .eq('prolific_id', prolificId)
      .single();

    console.log('Participant check result:', { existing, selectError });

    if (selectError && selectError.code !== 'PGRST116') {
      console.error('Error checking participant:', selectError);
      throw new Error(`Failed to check participant: ${selectError.message}`);
    }

    if (existing) {
      // Update existing participant
      console.log('Updating existing participant:', existing);
      const { error: updateError } = await supabase
        .from('participants')
        .update({
          total_conversations: existing.total_conversations + 1,
          updated_at: new Date().toISOString()
        })
        .eq('prolific_id', prolificId);

      if (updateError) {
        console.error('Error updating participant:', updateError);
        throw new Error(`Failed to update participant: ${updateError.message}`);
      }
      console.log('Participant updated successfully');
    } else {
      // Create new participant
      console.log('Creating new participant for:', prolificId);
      const { data: insertedData, error: insertError } = await supabase
        .from('participants')
        .insert({
          id: uuidv4(),
          prolific_id: prolificId,
          first_seen: new Date().toISOString(),
          total_conversations: 1,
          metadata: {}
        })
        .select();

      console.log('Participant insert result:', { insertedData, insertError });

      if (insertError) {
        console.error('Error creating participant:', insertError);
        throw new Error(`Failed to create participant: ${insertError.message}`);
      }
      console.log('New participant created successfully');
    }
  }
}

export const conversationService = new ConversationService();