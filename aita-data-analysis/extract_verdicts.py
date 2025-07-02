import pandas as pd
import numpy as np
import re
from pathlib import Path
from config import (
    DATA_DIR, SAMPLES_DIR, SUBMISSION_FILE, COMMENT_FILE, create_directories
)

def load_data():
    """Load the original data files"""
    if not SUBMISSION_FILE.exists():
        raise FileNotFoundError(f"Submission file not found: {SUBMISSION_FILE}")
    if not COMMENT_FILE.exists():
        raise FileNotFoundError(f"Comment file not found: {COMMENT_FILE}")
    
    print("Loading data...")
    submissions = pd.read_csv(SUBMISSION_FILE)
    comments = pd.read_csv(COMMENT_FILE)
    print(f"Loaded {len(submissions):,} submissions and {len(comments):,} comments")
    return submissions, comments

def extract_verdict_from_comment(comment_text):
    """
    Extract verdict from comment text.
    AITA verdicts are typically: YTA, NTA, ESH, NAH
    """
    comment_lower = comment_text.lower()
    
    # Common verdict patterns
    verdict_patterns = {
        'asshole': [
            r'\byta\b',  # You're the asshole
            r'\byou\'?re the asshole\b',
            r'\byou are the asshole\b',
            r'\basshole\b'
        ],
        'not the asshole': [
            r'\bnta\b',  # Not the asshole
            r'\bnot the asshole\b',
            r'\bno asshole\b'
        ],
        'everyone sucks': [
            r'\besh\b',  # Everyone sucks here
            r'\beveryone sucks\b',
            r'\beverybody sucks\b'
        ],
        'no assholes here': [
            r'\bnah\b',  # No assholes here
            r'\bno assholes here\b',
            r'\bno one is the asshole\b'
        ]
    }
    
    # Check for verdict patterns
    for verdict, patterns in verdict_patterns.items():
        for pattern in patterns:
            if re.search(pattern, comment_lower):
                return verdict
    
    return None

def extract_verdicts_from_comments(comments, sample_size=None):
    """
    Extract verdicts from comments.
    If sample_size is provided, only process a sample of comments.
    """
    print("Extracting verdicts from comments...")
    
    if sample_size:
        print(f"Processing sample of {sample_size:,} comments...")
        sample_comments = comments.sample(n=min(sample_size, len(comments)), random_state=42)
    else:
        sample_comments = comments
    
    # Extract verdicts
    verdicts = []
    for idx, comment in sample_comments.iterrows():
        verdict = extract_verdict_from_comment(comment['message'])
        if verdict:
            verdicts.append({
                'comment_id': comment['comment_id'],
                'submission_id': comment['submission_id'],
                'message': comment['message'],
                'score': comment['score'],
                'verdict': verdict,
                'comment_length': len(comment['message'])
            })
    
    verdict_df = pd.DataFrame(verdicts)
    
    print(f"Extracted {len(verdict_df)} comments with verdicts")
    
    # Show distribution
    if len(verdict_df) > 0:
        print("\nVerdict distribution:")
        verdict_counts = verdict_df['verdict'].value_counts()
        for verdict, count in verdict_counts.items():
            print(f"  {verdict}: {count:,} comments")
    
    return verdict_df

def create_balanced_verdict_samples(verdict_df, samples_per_category=10, max_comment_chars=500):
    """
    Create balanced samples based on actual verdict data.
    """
    print(f"\nCreating balanced samples ({samples_per_category} per category)...")
    
    # Filter by length
    filtered_verdicts = verdict_df[verdict_df['comment_length'] <= max_comment_chars].copy()
    print(f"Filtered to {len(filtered_verdicts):,} comments within length limit")
    
    # Sample from each verdict category
    balanced_samples = []
    
    for verdict in filtered_verdicts['verdict'].unique():
        verdict_comments = filtered_verdicts[filtered_verdicts['verdict'] == verdict]
        
        if len(verdict_comments) >= samples_per_category:
            sampled = verdict_comments.sample(n=samples_per_category, random_state=42)
        else:
            print(f"Warning: Only {len(verdict_comments)} comments for '{verdict}', using all")
            sampled = verdict_comments
        
        balanced_samples.append(sampled)
    
    if balanced_samples:
        balanced_df = pd.concat(balanced_samples, ignore_index=True)
        
        print(f"\nBalanced sample created:")
        print(f"  Total comments: {len(balanced_df)}")
        for verdict in balanced_df['verdict'].unique():
            count = len(balanced_df[balanced_df['verdict'] == verdict])
            print(f"  {verdict}: {count} comments")
        
        return balanced_df
    else:
        print("No balanced samples could be created")
        return None

def save_verdict_data(verdict_df, balanced_df, submissions, output_prefix="verdict"):
    """Save verdict data and balanced samples with submission context"""
    print(f"\nSaving verdict data with prefix '{output_prefix}'...")
    
    # Create verdict directory
    verdict_dir = SAMPLES_DIR / "verdict"
    verdict_dir.mkdir(exist_ok=True)
    
    # Save all verdicts
    all_verdicts_file = verdict_dir / f"{output_prefix}_all_verdicts.csv"
    verdict_df.to_csv(all_verdicts_file, index=False)
    print(f"Saved {len(verdict_df)} verdicts to {all_verdicts_file}")
    
    # Save balanced samples
    if balanced_df is not None:
        balanced_file = verdict_dir / f"{output_prefix}_balanced_samples.csv"
        balanced_df.to_csv(balanced_file, index=False)
        print(f"Saved {len(balanced_df)} balanced samples to {balanced_file}")
        
        # Get submission context for balanced samples
        submission_ids = balanced_df['submission_id'].unique()
        balanced_submissions = submissions[submissions['submission_id'].isin(submission_ids)].copy()
        
        # Save submission context
        submissions_file = verdict_dir / f"{output_prefix}_balanced_submissions.csv"
        balanced_submissions.to_csv(submissions_file, index=False)
        print(f"Saved {len(balanced_submissions)} submission contexts to {submissions_file}")
        
        # Create summary
        summary_file = verdict_dir / f"{output_prefix}_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Verdict Extraction Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total comments with verdicts: {len(verdict_df):,}\n")
            f.write(f"Balanced samples: {len(balanced_df):,}\n")
            f.write(f"Submission contexts: {len(balanced_submissions):,}\n\n")
            
            f.write("Verdict distribution (all):\n")
            for verdict, count in verdict_df['verdict'].value_counts().items():
                f.write(f"  {verdict}: {count:,}\n")
            
            f.write(f"\nBalanced sample distribution:\n")
            for verdict, count in balanced_df['verdict'].value_counts().items():
                f.write(f"  {verdict}: {count}\n")
        
        print(f"Saved summary to {summary_file}")
    
    return verdict_dir

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract verdicts from AITA comments")
    parser.add_argument("--sample-size", type=int, default=100000,
                       help="Number of comments to process (default: 100000)")
    parser.add_argument("--samples-per-category", type=int, default=10,
                       help="Number of balanced samples per category (default: 10)")
    parser.add_argument("--max-comment-chars", type=int, default=500,
                       help="Maximum comment length for balanced samples (default: 500)")
    parser.add_argument("--output-prefix", type=str, default="verdict",
                       help="Output file prefix (default: verdict)")
    
    args = parser.parse_args()
    
    try:
        # Create directories
        create_directories()
        
        # Load data
        submissions, comments = load_data()
        
        # Extract verdicts
        verdict_df = extract_verdicts_from_comments(comments, args.sample_size)
        
        if len(verdict_df) == 0:
            print("No verdicts found. You may need to adjust the extraction patterns.")
            return 1
        
        # Create balanced samples
        balanced_df = create_balanced_verdict_samples(
            verdict_df, 
            samples_per_category=args.samples_per_category,
            max_comment_chars=args.max_comment_chars
        )
        
        # Save data
        verdict_dir = save_verdict_data(verdict_df, balanced_df, submissions, args.output_prefix)
        
        print(f"\n✅ Verdict extraction complete!")
        print(f"Files saved in the '{verdict_dir}' directory")
        print(f"\nNext steps:")
        print(f"1. Review the extracted verdicts")
        print(f"2. Use the balanced samples for analysis")
        print(f"3. Adjust extraction patterns if needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 