import pandas as pd
from config import SAMPLES_DIR, SUBMISSION_SAMPLE_FILE, COMMENT_SAMPLE_FILE

def preview_sampled_data():
    """Preview the sampled data in a readable format"""
    
    # Check if samples directory exists
    if not SAMPLES_DIR.exists():
        print(f"Samples directory {SAMPLES_DIR} not found.")
        print("Please run the sampling script first to generate sample files.")
        return
    
    # Check if sample files exist
    if not SUBMISSION_SAMPLE_FILE.exists():
        print(f"Sample submissions file not found: {SUBMISSION_SAMPLE_FILE}")
        print("Please run the sampling script first.")
        return
        
    if not COMMENT_SAMPLE_FILE.exists():
        print(f"Sample comments file not found: {COMMENT_SAMPLE_FILE}")
        print("Please run the sampling script first.")
        return
    
    # Load sampled data
    submissions = pd.read_csv(SUBMISSION_SAMPLE_FILE)
    comments = pd.read_csv(COMMENT_SAMPLE_FILE)
    
    print("=== SAMPLED DATA PREVIEW ===\n")
    
    # Show one example from each engagement tier
    for tier in ['Very Low', 'Low', 'Medium', 'High', 'Very High']:
        print(f"--- {tier.upper()} ENGAGEMENT TIER ---")
        
        # Get one sample from this tier
        tier_submissions = submissions[submissions['engagement_tier'] == tier]
        if len(tier_submissions) == 0:
            print(f"No submissions found for {tier} tier.")
            continue
            
        sample = tier_submissions.iloc[0]
        
        print(f"Submission ID: {sample['submission_id']}")
        print(f"Title: {sample['title']}")
        print(f"Score: {sample['score']}")
        print(f"Comment Count: {sample['comment_count']}")
        print(f"Length: {len(sample['selftext'])} characters")
        print(f"Text Preview: {sample['selftext'][:300]}...")
        
        # Get top comment for this submission
        sub_comments = comments[comments['submission_id'] == sample['submission_id']]
        if len(sub_comments) > 0:
            top_comment = sub_comments.iloc[0]
            print(f"Top Comment (Score: {top_comment['score']}): {top_comment['message'][:200]}...")
        
        print("\n" + "="*80 + "\n")
    
    # Show some statistics
    print("=== SAMPLE STATISTICS ===")
    print(f"Total submissions: {len(submissions)}")
    print(f"Total comments: {len(comments)}")
    print(f"Average submission length: {submissions['selftext'].str.len().mean():.1f} characters")
    print(f"Average comment length: {comments['message'].str.len().mean():.1f} characters")
    
    # Show length distribution
    print("\n=== LENGTH DISTRIBUTION ===")
    sub_lengths = submissions['selftext'].str.len()
    com_lengths = comments['message'].str.len()
    
    print("Submission lengths:")
    short_subs = (sub_lengths <= 500).sum()
    medium_subs = ((sub_lengths > 500) & (sub_lengths <= 1000)).sum()
    long_subs = ((sub_lengths > 1000) & (sub_lengths <= 2000)).sum()
    print(f"  Short (≤500 chars): {short_subs} ({(short_subs/len(submissions)*100):.1f}%)")
    print(f"  Medium (501-1000 chars): {medium_subs} ({(medium_subs/len(submissions)*100):.1f}%)")
    print(f"  Long (1001-2000 chars): {long_subs} ({(long_subs/len(submissions)*100):.1f}%)")
    
    print("\nComment lengths:")
    short_coms = (com_lengths <= 200).sum()
    medium_coms = ((com_lengths > 200) & (com_lengths <= 400)).sum()
    long_coms = ((com_lengths > 400) & (com_lengths <= 500)).sum()
    print(f"  Short (≤200 chars): {short_coms} ({(short_coms/len(comments)*100):.1f}%)")
    print(f"  Medium (201-400 chars): {medium_coms} ({(medium_coms/len(comments)*100):.1f}%)")
    print(f"  Long (401-500 chars): {long_coms} ({(long_coms/len(comments)*100):.1f}%)")

if __name__ == "__main__":
    preview_sampled_data() 