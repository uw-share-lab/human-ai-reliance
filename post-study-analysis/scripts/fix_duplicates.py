#!/usr/bin/env python3
"""
Script to fix duplicate conversations and merge AI explanations.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

RAW_DIR = "raw"
MERGED_DIR = "merged"


def load_data():
    """Load CSV files into DataFrames"""
    conversations_df = pd.read_csv(os.path.join(RAW_DIR, 'conversations_rows.csv'))
    messages_df = pd.read_csv(os.path.join(RAW_DIR, 'messages_rows.csv'))
    participants_df = pd.read_csv(os.path.join(RAW_DIR, 'participants_rows.csv'))

    return conversations_df, messages_df, participants_df

def identify_duplicates(conversations_df):
    """Identify duplicate conversations per (prolific_id, scenario_id)"""
    duplicates = conversations_df.groupby(['prolific_id', 'scenario_id']).size()
    duplicates = duplicates[duplicates > 1].reset_index()
    duplicates.columns = ['prolific_id', 'scenario_id', 'count']
    
    print(f"Found {len(duplicates)} (prolific_id, scenario_id) pairs with duplicates:")
    print(duplicates.head(10))
    
    return duplicates

def merge_conversations(conversations_df, messages_df):
    """Merge split conversations and concatenate AI messages"""
    
    # Get all unique (prolific_id, scenario_id) combinations
    unique_pairs = conversations_df[['prolific_id', 'scenario_id']].drop_duplicates()
    
    merged_conversations = []
    merged_messages = []
    
    for _, row in unique_pairs.iterrows():
        prolific_id = row['prolific_id']
        scenario_id = row['scenario_id']
        
        # Get all conversations for this pair
        pair_conversations = conversations_df[
            (conversations_df['prolific_id'] == prolific_id) & 
            (conversations_df['scenario_id'] == scenario_id)
        ].copy()
        
        if len(pair_conversations) == 1:
            # No duplicates, keep as is
            merged_conversations.append(pair_conversations.iloc[0])
            
            # Get messages for this conversation
            conv_id = pair_conversations.iloc[0]['id']
            conv_messages = messages_df[messages_df['conversation_id'] == conv_id]
            merged_messages.extend(conv_messages.to_dict('records'))
            
        else:
            # Multiple conversations - merge them
            print(f"Merging {len(pair_conversations)} conversations for {prolific_id}, {scenario_id}")
            
            # Create merged conversation using the earliest start time
            earliest_conv = pair_conversations.loc[pair_conversations['start_time'].idxmin()]
            merged_conv = earliest_conv.copy()
            
            # Update timing info with the latest end time if available
            latest_end = pair_conversations['end_time'].dropna()
            if not latest_end.empty:
                merged_conv['end_time'] = latest_end.max()

            # Sum the durations of sessions that actually recorded an end time.
            # The old span-based recalculation (earliest_start → latest_end) was
            # wrong when one session was abandoned mid-way and the participant
            # restarted: the gap between sessions inflated the merged duration far
            # beyond 3 minutes even though each real session was ~3 min or less.
            valid_durations = pair_conversations['duration_ms'].dropna()
            if not valid_durations.empty:
                merged_conv['duration_ms'] = int(valid_durations.sum())
            else:
                merged_conv['duration_ms'] = None
            
            # Sum interaction counts
            merged_conv['interaction_count'] = pair_conversations['interaction_count'].sum()
            
            # Set completion status based on any completed conversation
            merged_conv['completed_normally'] = pair_conversations['completed_normally'].any()
            merged_conv['timed_out'] = pair_conversations['timed_out'].any()
            
            merged_conversations.append(merged_conv)
            
            # Collect all messages from all conversations for this pair
            all_messages = []
            for conv_id in pair_conversations['id']:
                conv_messages = messages_df[messages_df['conversation_id'] == conv_id].copy()
                all_messages.extend(conv_messages.to_dict('records'))
            
            # Sort messages by timestamp
            all_messages.sort(key=lambda x: x['timestamp'])
            
            # Reassign conversation_id and sequence numbers
            new_conv_id = merged_conv['id']
            ai_contents = []
            
            for i, msg in enumerate(all_messages, 1):
                msg['conversation_id'] = new_conv_id
                msg['sequence_number'] = i
                
                # Collect AI messages for concatenation
                if msg['message_type'] == 'ai':
                    ai_contents.append(msg['content'])
            
            # Create single concatenated AI explanation
            if ai_contents:
                concatenated_ai = '\n\n'.join(ai_contents)
                
                # Replace all AI messages with one concatenated message
                non_ai_messages = [msg for msg in all_messages if msg['message_type'] != 'ai']
                
                # Add the concatenated AI message at the end
                ai_message = {
                    'id': f"{new_conv_id}_ai_concat",
                    'conversation_id': new_conv_id,
                    'message_type': 'ai',
                    'content': concatenated_ai,
                    'timestamp': max([msg['timestamp'] for msg in all_messages if msg['message_type'] == 'ai']),
                    'sequence_number': len(non_ai_messages) + 1,
                    'response_time_seconds': None,
                    'created_at': datetime.now().isoformat() + '+00'
                }
                
                # Renumber non-AI messages
                for i, msg in enumerate(non_ai_messages, 1):
                    msg['sequence_number'] = i
                
                all_messages = non_ai_messages + [ai_message]
                
            merged_messages.extend(all_messages)
    
    # Convert back to DataFrames
    merged_conversations_df = pd.DataFrame(merged_conversations)
    merged_messages_df = pd.DataFrame(merged_messages)
    
    return merged_conversations_df, merged_messages_df

def main():
    print("Loading data...")
    conversations_df, messages_df, participants_df = load_data()
    
    print(f"Original conversations: {len(conversations_df)}")
    print(f"Original messages: {len(messages_df)}")
    
    print("\nIdentifying duplicates...")
    duplicates = identify_duplicates(conversations_df)
    
    print("\nMerging conversations and concatenating AI messages...")
    merged_conversations_df, merged_messages_df = merge_conversations(conversations_df, messages_df)
    
    print(f"Merged conversations: {len(merged_conversations_df)}")
    print(f"Merged messages: {len(merged_messages_df)}")
    
    # Save the merged data
    os.makedirs(MERGED_DIR, exist_ok=True)
    print("\nSaving merged data...")
    merged_conversations_df.to_csv(os.path.join(MERGED_DIR, 'conversations_merged.csv'), index=False)
    merged_messages_df.to_csv(os.path.join(MERGED_DIR, 'messages_merged.csv'), index=False)
    participants_df.to_csv(os.path.join(MERGED_DIR, 'participants_merged.csv'), index=False)  # unchanged

    print(f"Done! Files saved to {MERGED_DIR}/:")
    print("- conversations_merged.csv")
    print("- messages_merged.csv")
    print("- participants_merged.csv")
    
    # Show summary
    unique_pairs_original = conversations_df.groupby(['prolific_id', 'scenario_id']).size()
    unique_pairs_merged = merged_conversations_df.groupby(['prolific_id', 'scenario_id']).size()
    
    print(f"\nOriginal unique (prolific_id, scenario_id) pairs: {len(unique_pairs_original)}")
    print(f"Merged unique (prolific_id, scenario_id) pairs: {len(unique_pairs_merged)}")
    print(f"Duplicate pairs fixed: {len(duplicates)}")

if __name__ == "__main__":
    main()