import pandas as pd
import random
from config import (
    SAMPLES_DIR, FAVORITES_DIR, SUBMISSION_SAMPLE_FILE, COMMENT_SAMPLE_FILE,
    FAVORITE_SUBMISSIONS_FILE, FAVORITE_COMMENTS_FILE, ENGAGEMENT_TIERS,
    export_to_txt, FAVORITES_TXT_FILE
)

def create_directories():
    """Create necessary directories if they don't exist"""
    from config import create_directories as config_create_directories
    config_create_directories()

def load_sample_data():
    """Load the sampled data"""
    if not SUBMISSION_SAMPLE_FILE.exists():
        print(f"Sample submissions file not found: {SUBMISSION_SAMPLE_FILE}")
        print("Please run the sampling script first.")
        return None, None
        
    if not COMMENT_SAMPLE_FILE.exists():
        print(f"Sample comments file not found: {COMMENT_SAMPLE_FILE}")
        print("Please run the sampling script first.")
        return None, None
    
    print("Loading sample data...")
    submissions = pd.read_csv(SUBMISSION_SAMPLE_FILE)
    comments = pd.read_csv(COMMENT_SAMPLE_FILE)
    print(f"Loaded {len(submissions):,} submissions and {len(comments):,} comments")
    return submissions, comments

def display_submission(submission, comments, submission_num, total_submissions):
    """Display a submission with its top comments"""
    print(f"\n{'='*80}")
    print(f"SUBMISSION {submission_num}/{total_submissions}")
    print(f"{'='*80}")
    
    print(f"ID: {submission['submission_id']}")
    print(f"Title: {submission['title']}")
    print(f"Score: {submission['score']}")
    print(f"Engagement Tier: {submission['engagement_tier']}")
    print(f"Comment Count: {submission['comment_count']}")
    print(f"Length: {len(submission['selftext'])} characters")
    print(f"\nTEXT:")
    print(f"{submission['selftext']}")
    
    # Show top comments
    submission_comments = comments[comments['submission_id'] == submission['submission_id']]
    if len(submission_comments) > 0:
        print(f"\nTOP COMMENTS:")
        for i, comment in submission_comments.head(3).iterrows():
            print(f"\nComment {i+1} (Score: {comment['score']}):")
            print(f"{comment['message']}")
    
    print(f"\n{'='*80}")

def get_user_selection():
    """Get user selection for a submission"""
    while True:
        response = input("Select this submission? (y/n/q to quit): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['q', 'quit']:
            return 'quit'
        else:
            print("Please enter 'y', 'n', or 'q'")

def select_favorites():
    """Main function to select favorite submissions"""
    create_directories()
    
    # Load data
    submissions, comments = load_sample_data()
    if submissions is None:
        return
    
    # Show 2 samples from each engagement tier
    selected_submissions = []
    selected_comments = []
    
    print("\n" + "="*80)
    print("SELECTING FAVORITE SUBMISSIONS")
    print("="*80)
    print("You will see 2 submissions from each engagement tier.")
    print("For each submission, choose 'y' to select it, 'n' to skip, or 'q' to quit.")
    print("="*80)
    
    submission_count = 0
    total_to_show = 10  # 2 from each of 5 tiers
    
    for tier in ENGAGEMENT_TIERS:
        print(f"\n--- {tier.upper()} ENGAGEMENT TIER ---")
        
        tier_submissions = submissions[submissions['engagement_tier'] == tier]
        if len(tier_submissions) == 0:
            print(f"No submissions found for {tier} tier.")
            continue
        
        # Show 2 samples from this tier
        tier_samples = tier_submissions.sample(n=min(2, len(tier_submissions)), random_state=42)
        
        for _, submission in tier_samples.iterrows():
            submission_count += 1
            display_submission(submission, comments, submission_count, total_to_show)
            
            selection = get_user_selection()
            if selection == 'quit':
                print("\nSelection process ended early.")
                break
            elif selection:
                selected_submissions.append(submission)
                # Get comments for this submission
                submission_comments = comments[comments['submission_id'] == submission['submission_id']]
                selected_comments.extend(submission_comments.to_dict('records'))
                print(f"✅ Selected! (Total selected: {len(selected_submissions)})")
            else:
                print("⏭️  Skipped.")
        
        if selection == 'quit':
            break
    
    # Save selected favorites
    if selected_submissions:
        print(f"\nSaving {len(selected_submissions)} selected submissions...")
        
        # Convert to DataFrame
        favorites_submissions = pd.DataFrame(selected_submissions)
        favorites_comments = pd.DataFrame(selected_comments)
        
        # Save files
        submissions_file = FAVORITE_SUBMISSIONS_FILE
        comments_file = FAVORITE_COMMENTS_FILE
        
        favorites_submissions.to_csv(submissions_file, index=False)
        favorites_comments.to_csv(comments_file, index=False)
        
        # Export to human-readable TXT format
        export_to_txt(favorites_submissions, favorites_comments, FAVORITES_TXT_FILE, "FAVORITE SUBMISSIONS")
        
        print(f"✅ Saved {len(favorites_submissions)} submissions to {submissions_file}")
        print(f"✅ Saved {len(favorites_comments)} comments to {comments_file}")
        print(f"✅ Saved human-readable version to {FAVORITES_TXT_FILE}")
        
        # Show summary
        print(f"\nSELECTION SUMMARY:")
        print(f"  Selected submissions: {len(favorites_submissions)}")
        print(f"  Selected comments: {len(favorites_comments)}")
        print(f"  Average submission length: {favorites_submissions['selftext'].str.len().mean():.1f} characters")
        print(f"  Average comment length: {favorites_comments['message'].str.len().mean():.1f} characters")
        
        # Show tier distribution
        print(f"\nEngagement tier distribution:")
        tier_counts = favorites_submissions['engagement_tier'].value_counts().sort_index()
        for tier, count in tier_counts.items():
            print(f"  {tier}: {count} submissions")
    
    else:
        print("\nNo submissions were selected.")

if __name__ == "__main__":
    select_favorites() 