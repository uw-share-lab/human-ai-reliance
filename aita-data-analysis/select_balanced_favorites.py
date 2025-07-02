import pandas as pd
import numpy as np
from pathlib import Path
from config import (
    SAMPLES_DIR, FAVORITES_DIR, create_directories, export_to_txt, FAVORITES_TXT_FILE
)

def load_balanced_data():
    """Load the balanced sample data"""
    # Look in verdict directory first (from extract_verdicts.py)
    verdict_dir = SAMPLES_DIR / "verdict"
    balanced_dir = SAMPLES_DIR / "balanced"
    
    # Look for balanced sample files
    comments_file = None
    submissions_file = None
    
    # Try verdict directory first
    if verdict_dir.exists():
        for file in verdict_dir.glob("*_balanced_samples.csv"):
            comments_file = file
            break
        
        # Look for corresponding submissions file
        for file in verdict_dir.glob("*_balanced_submissions.csv"):
            submissions_file = file
            break
    
    # If not found, try balanced directory
    if not comments_file and balanced_dir.exists():
        for file in balanced_dir.glob("*_comments.csv"):
            comments_file = file
            break
        
        for file in balanced_dir.glob("*_submissions.csv"):
            submissions_file = file
            break
    
    if not comments_file:
        print("Balanced sample files not found.")
        print("Please run the verdict extraction script first:")
        print("python extract_verdicts.py")
        return None, None
    
    print("Loading balanced sample data...")
    
    # Load the balanced samples file
    comments = pd.read_csv(comments_file)
    print(f"Loaded {len(comments):,} comments from balanced samples")
    
    # Load submission context
    if submissions_file and submissions_file.exists():
        submissions = pd.read_csv(submissions_file)
        print(f"Loaded {len(submissions):,} submission contexts")
    else:
        # Fallback to original submissions if context file not found
        from config import SUBMISSION_FILE
        if SUBMISSION_FILE.exists():
            submissions = pd.read_csv(SUBMISSION_FILE)
            print(f"Loaded {len(submissions):,} original submissions for context")
        else:
            submissions = pd.DataFrame()
            print("Warning: No submission context found")
    
    return comments, submissions

def display_comment(comment, submission, comment_num, total_comments, category):
    """Display a comment with its submission context"""
    print(f"\n{'='*80}")
    print(f"COMMENT {comment_num}/{total_comments} - {category.upper()}")
    print(f"{'='*80}")
    
    print(f"Comment ID: {comment['comment_id']}")
    print(f"Submission ID: {comment['submission_id']}")
    print(f"Score: {comment['score']}")
    print(f"Length: {len(comment['message'])} characters")
    print(f"Verdict: {comment['verdict']}")
    
    print(f"\nCOMMENT TEXT:")
    print(f"{comment['message']}")
    
    if submission is not None:
        print(f"\nSUBMISSION CONTEXT:")
        print(f"Title: {submission['title']}")
        print(f"Score: {submission['score']}")
        print(f"Submission Text: {submission['selftext'][:300]}...")
    
    print(f"\n{'='*80}")

def get_user_selection():
    """Get user selection for a comment"""
    while True:
        response = input("Select this comment? (y/n/q to quit): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        elif response in ['q', 'quit']:
            return 'quit'
        else:
            print("Please enter 'y', 'n', or 'q'")

def select_balanced_favorites():
    """Main function to select favorite comments from balanced samples"""
    create_directories()
    
    # Load data
    comments, submissions = load_balanced_data()
    if comments is None:
        return
    
    # Show comments by category
    selected_comments = []
    selected_submissions = []
    
    print("\n" + "="*80)
    print("SELECTING FAVORITE COMMENTS FROM BALANCED SAMPLES")
    print("="*80)
    print("You will see comments from each verdict category.")
    print("For each comment, choose 'y' to select it, 'n' to skip, or 'q' to quit.")
    print("="*80)
    
    comment_count = 0
    total_comments = len(comments)
    
    # Group by verdict category
    for category in comments['verdict'].unique():
        print(f"\n--- {category.upper()} CATEGORY ---")
        
        category_comments = comments[comments['verdict'] == category]
        print(f"Showing {len(category_comments)} comments in this category")
        
        for _, comment in category_comments.iterrows():
            comment_count += 1
            
            # Get submission context
            submission = submissions[submissions['submission_id'] == comment['submission_id']]
            submission_context = submission.iloc[0] if len(submission) > 0 else None
            
            display_comment(comment, submission_context, comment_count, total_comments, category)
            
            selection = get_user_selection()
            if selection == 'quit':
                print("\nSelection process ended early.")
                break
            elif selection:
                selected_comments.append(comment)
                if submission_context is not None:
                    # Avoid duplicates
                    if not any(s['submission_id'] == submission_context['submission_id'] for s in selected_submissions):
                        selected_submissions.append(submission_context)
                print(f"✅ Selected! (Total selected: {len(selected_comments)})")
            else:
                print("⏭️  Skipped.")
        
        if selection == 'quit':
            break
    
    # Save selected favorites
    if selected_comments:
        print(f"\nSaving {len(selected_comments)} selected comments...")
        
        # Convert to DataFrame
        favorites_comments = pd.DataFrame(selected_comments)
        favorites_submissions = pd.DataFrame(selected_submissions)
        
        # Create balanced subdirectory
        balanced_favorites_dir = FAVORITES_DIR / "balanced"
        balanced_favorites_dir.mkdir(exist_ok=True)
        
        # Save files
        comments_file = balanced_favorites_dir / "balanced_favorite_comments.csv"
        submissions_file = balanced_favorites_dir / "balanced_favorite_submissions.csv"
        
        favorites_comments.to_csv(comments_file, index=False)
        favorites_submissions.to_csv(submissions_file, index=False)
        
        # Export to human-readable TXT format
        balanced_favorites_txt = balanced_favorites_dir / "balanced_favorite_comments.txt"
        export_balanced_to_txt(favorites_comments, favorites_submissions, balanced_favorites_txt, "BALANCED FAVORITE COMMENTS")
        
        print(f"✅ Saved {len(favorites_comments)} comments to {comments_file}")
        print(f"✅ Saved {len(favorites_submissions)} submissions to {submissions_file}")
        print(f"✅ Saved human-readable version to {balanced_favorites_txt}")
        
        # Show summary
        print(f"\nSELECTION SUMMARY:")
        print(f"  Selected comments: {len(favorites_comments)}")
        print(f"  Selected submissions: {len(favorites_submissions)}")
        print(f"  Average comment length: {favorites_comments['message'].str.len().mean():.1f} characters")
        
        # Show category distribution
        print(f"\nVerdict category distribution:")
        category_counts = favorites_comments['verdict'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count} comments")
    
    else:
        print("\nNo comments were selected.")

def export_balanced_to_txt(comments, submissions, output_file, title="BALANCED FAVORITES"):
    """Export balanced favorites to human-readable TXT format"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Comments: {len(comments):,}\n")
        f.write(f"Total Submissions: {len(submissions):,}\n\n")
        
        # Group by verdict category
        for category in comments['verdict'].unique():
            category_comments = comments[comments['verdict'] == category]
            
            f.write(f"=== {category.upper()} ===\n")
            f.write(f"Comments in this category: {len(category_comments)}\n\n")
            
            for idx, (_, comment) in enumerate(category_comments.iterrows(), 1):
                f.write(f"COMMENT {idx}: {comment['comment_id']}\n")
                f.write(f"SUBMISSION ID: {comment['submission_id']}\n")
                f.write(f"SCORE: {comment['score']}\n")
                f.write(f"LENGTH: {len(comment['message'])} characters\n")
                f.write(f"VERDICT: {comment['verdict']}\n")
                f.write(f"TEXT:\n{comment['message']}\n\n")
                
                # Add submission context if available
                submission = submissions[submissions['submission_id'] == comment['submission_id']]
                if len(submission) > 0:
                    sub = submission.iloc[0]
                    f.write(f"SUBMISSION CONTEXT:\n")
                    f.write(f"Title: {sub['title']}\n")
                    f.write(f"Score: {sub['score']}\n")
                    f.write(f"Submission Text: {sub['selftext'][:200]}...\n\n")
                
                f.write("-" * 80 + "\n\n")
    
    print(f"✅ TXT export saved to {output_file}")

if __name__ == "__main__":
    select_balanced_favorites() 