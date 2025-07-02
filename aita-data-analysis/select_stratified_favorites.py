#!/usr/bin/env python3
"""
Interactive Selection for Stratified AITA Samples

This script allows you to select your favorite AITA submissions from the stratified samples.
You'll see submissions grouped by verdict category and can select your preferred ones.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from config import (
    SAMPLES_DIR, FAVORITES_DIR, create_directories
)

def load_stratified_data():
    """Load the stratified sample data"""
    stratified_dir = SAMPLES_DIR / "stratified"
    
    # Look for stratified sample files
    submissions_file = None
    comments_file = None
    
    for file in stratified_dir.glob("*_submissions.csv"):
        submissions_file = file
        break
    
    for file in stratified_dir.glob("*_comments.csv"):
        comments_file = file
        break
    
    if not submissions_file or not comments_file:
        print("Stratified sample files not found.")
        print("Please run the stratified sampling script first:")
        print("python stratified_aita_sample.py")
        return None, None
    
    print("Loading stratified sample data...")
    submissions = pd.read_csv(submissions_file)
    comments = pd.read_csv(comments_file)
    print(f"Loaded {len(submissions):,} submissions and {len(comments):,} comments")
    return submissions, comments

def display_submission(submission, comments, submission_num, total_submissions, category):
    """Display a submission with its top comments"""
    print(f"\n{'='*80}")
    print(f"SUBMISSION {submission_num}/{total_submissions} - {category.upper()}")
    print(f"{'='*80}")
    
    print(f"Submission ID: {submission['submission_id']}")
    print(f"Title: {submission['title']}")
    print(f"Score: {submission['score']}")
    print(f"Dominant Verdict: {submission['dominant_verdict']}")
    print(f"Verdict Count: {submission['verdict_count']}")
    print(f"Length: {len(submission['selftext'])} characters")
    
    print(f"\nAITA SUBMISSION:")
    print(f"{submission['selftext']}")
    
    # Show top comments for this submission
    submission_comments = comments[comments['submission_id'] == submission['submission_id']]
    if len(submission_comments) > 0:
        print(f"\nTOP COMMENTS ({len(submission_comments)} total):")
        # Sort by score and show top 5
        top_comments = submission_comments.nlargest(5, 'score')
        for i, comment in top_comments.iterrows():
            print(f"\nComment (Score: {comment['score']}):")
            print(f"{comment['message']}")
        
        if len(submission_comments) > 5:
            print(f"\n... and {len(submission_comments) - 5} more comments")
    
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

def select_stratified_favorites():
    """Main function to select favorite submissions from stratified samples"""
    create_directories()
    
    # Load data
    submissions, comments = load_stratified_data()
    if submissions is None:
        return
    
    # Show submissions by verdict category
    selected_submissions = []
    selected_comments = []
    
    print("\n" + "="*80)
    print("SELECTING FAVORITE SUBMISSIONS FROM STRATIFIED SAMPLES")
    print("="*80)
    print("You will see submissions from each verdict category.")
    print("For each submission, choose 'y' to select it, 'n' to skip, or 'q' to quit.")
    print("="*80)
    
    submission_count = 0
    total_submissions = len(submissions)
    
    # Group by verdict category
    for category in submissions['dominant_verdict'].unique():
        print(f"\n--- {category.upper()} CATEGORY ---")
        
        category_submissions = submissions[submissions['dominant_verdict'] == category]
        print(f"Showing {len(category_submissions)} submissions in this category")
        
        for _, submission in category_submissions.iterrows():
            submission_count += 1
            
            # Get comments for this submission
            submission_comments = comments[comments['submission_id'] == submission['submission_id']]
            
            display_submission(submission, submission_comments, submission_count, total_submissions, category)
            
            selection = get_user_selection()
            if selection == 'quit':
                print("\nSelection process ended early.")
                break
            elif selection:
                selected_submissions.append(submission)
                # Add all comments for this submission
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
        
        # Create stratified subdirectory
        stratified_favorites_dir = FAVORITES_DIR / "stratified"
        stratified_favorites_dir.mkdir(exist_ok=True)
        
        # Save files
        submissions_file = stratified_favorites_dir / "stratified_favorite_submissions.csv"
        comments_file = stratified_favorites_dir / "stratified_favorite_comments.csv"
        
        favorites_submissions.to_csv(submissions_file, index=False)
        favorites_comments.to_csv(comments_file, index=False)
        
        # Export to human-readable TXT format
        favorites_txt = stratified_favorites_dir / "stratified_favorite_submissions.txt"
        export_stratified_to_txt(favorites_submissions, favorites_comments, favorites_txt, "STRATIFIED FAVORITE SUBMISSIONS")
        
        print(f"✅ Saved {len(favorites_submissions)} submissions to {submissions_file}")
        print(f"✅ Saved {len(favorites_comments)} comments to {comments_file}")
        print(f"✅ Saved human-readable version to {favorites_txt}")
        
        # Show summary
        print(f"\nSELECTION SUMMARY:")
        print(f"  Selected submissions: {len(favorites_submissions)}")
        print(f"  Selected comments: {len(favorites_comments)}")
        print(f"  Average submission length: {favorites_submissions['selftext'].str.len().mean():.1f} characters")
        print(f"  Average comment length: {favorites_comments['message'].str.len().mean():.1f} characters")
        
        # Show category distribution
        print(f"\nVerdict category distribution:")
        category_counts = favorites_submissions['dominant_verdict'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count} submissions")
        
        # Show comments per submission
        comment_counts = favorites_comments.groupby('submission_id').size()
        print(f"\nComments per selected submission:")
        print(f"  Mean: {comment_counts.mean():.1f}")
        print(f"  Median: {comment_counts.median():.1f}")
        print(f"  Min: {comment_counts.min()}")
        print(f"  Max: {comment_counts.max()}")
    
    else:
        print("\nNo submissions were selected.")

def export_stratified_to_txt(submissions, comments, output_file, title="STRATIFIED FAVORITES"):
    """Export stratified favorites to human-readable TXT format"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Submissions: {len(submissions):,}\n")
            f.write(f"Total Comments: {len(comments):,}\n\n")
            
            # Group by verdict category
            for category in submissions['dominant_verdict'].unique():
                category_submissions = submissions[submissions['dominant_verdict'] == category]
                
                f.write(f"=== {category.upper()} ===\n")
                f.write(f"Submissions in this category: {len(category_submissions)}\n\n")
                
                for idx, (_, submission) in enumerate(category_submissions.iterrows(), 1):
                    f.write(f"SUBMISSION {idx}: {submission['submission_id']}\n")
                    f.write(f"Title: {submission['title']}\n")
                    f.write(f"Score: {submission['score']}\n")
                    f.write(f"Dominant Verdict: {submission['dominant_verdict']}\n")
                    f.write(f"Verdict Count: {submission['verdict_count']}\n")
                    f.write(f"Length: {len(str(submission['selftext']))} characters\n")
                    f.write(f"TEXT:\n{submission['selftext']}\n\n")
                    
                    # Add comments for this submission
                    submission_comments = comments[comments['submission_id'] == submission['submission_id']]
                    if len(submission_comments) > 0:
                        f.write("COMMENTS:\n")
                        # Sort by score and show top 10
                        top_comments = submission_comments.nlargest(10, 'score')
                        for i, (_, comment) in enumerate(top_comments.iterrows(), 1):
                            f.write(f"{i}. (Score: {comment['score']}): {comment['message']}\n")
                        
                        if len(submission_comments) > 10:
                            f.write(f"... and {len(submission_comments) - 10} more comments\n")
                        f.write("\n")
                    
                    f.write("-" * 80 + "\n\n")
        
        print(f"✅ TXT export saved to {output_file}")
    except Exception as e:
        print(f"❌ Error creating TXT file: {e}")
        print(f"Attempting to create simple TXT file...")
        
        # Fallback: create a simple TXT file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Submissions: {len(submissions):,}\n")
                f.write(f"Total Comments: {len(comments):,}\n\n")
                
                for idx, (_, submission) in enumerate(submissions.iterrows(), 1):
                    f.write(f"SUBMISSION {idx}: {submission['submission_id']}\n")
                    f.write(f"Title: {submission['title']}\n")
                    f.write(f"Score: {submission['score']}\n")
                    f.write(f"Dominant Verdict: {submission['dominant_verdict']}\n")
                    f.write(f"TEXT:\n{submission['selftext']}\n\n")
                    f.write("-" * 80 + "\n\n")
            
            print(f"✅ Simple TXT export saved to {output_file}")
        except Exception as e2:
            print(f"❌ Failed to create even simple TXT file: {e2}")

if __name__ == "__main__":
    select_stratified_favorites() 