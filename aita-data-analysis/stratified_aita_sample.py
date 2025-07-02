#!/usr/bin/env python3
"""
Stratified AITA Sampling - Sample submissions by verdict, then get their comments

This script:
1. Filters submissions and comments by length
2. Extracts verdicts from comments to categorize submissions
3. Creates balanced samples of submissions across verdict categories
4. Gets comments for each sampled submission
5. Provides 5x oversampling for selection flexibility
"""

import pandas as pd
import numpy as np
import argparse
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

def filter_by_length(submissions, comments, max_submission_chars, max_comment_chars):
    """Filter both submissions and comments by character length"""
    print(f"\nFiltering submissions to <= {max_submission_chars} characters...")
    filtered_submissions = submissions[submissions['selftext'].str.len() <= max_submission_chars].copy()
    print(f"Filtered to {len(filtered_submissions):,} submissions")
    
    print(f"Filtering comments to <= {max_comment_chars} characters...")
    filtered_comments = comments[comments['message'].str.len() <= max_comment_chars].copy()
    print(f"Filtered to {len(filtered_comments):,} comments")
    
    return filtered_submissions, filtered_comments

def extract_verdict_from_comment(comment_text):
    """Extract verdict from comment text"""
    comment_lower = comment_text.lower()
    
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
    
    for verdict, patterns in verdict_patterns.items():
        for pattern in patterns:
            if re.search(pattern, comment_lower):
                return verdict
    
    return None

def categorize_submissions_by_verdict(submissions, comments, sample_size=None):
    """
    Categorize submissions based on verdicts in their comments.
    Returns submissions with their dominant verdict category.
    """
    print("Categorizing submissions by verdict...")
    
    if sample_size:
        print(f"Processing sample of {sample_size:,} submissions...")
        sample_submissions = submissions.sample(n=min(sample_size, len(submissions)), random_state=42)
    else:
        sample_submissions = submissions
    
    # Get comments for these submissions
    submission_ids = sample_submissions['submission_id'].tolist()
    relevant_comments = comments[comments['submission_id'].isin(submission_ids)]
    
    print(f"Found {len(relevant_comments):,} comments for {len(sample_submissions):,} submissions")
    
    # Extract verdicts from comments
    verdicts = []
    for _, comment in relevant_comments.iterrows():
        verdict = extract_verdict_from_comment(comment['message'])
        if verdict:
            verdicts.append({
                'submission_id': comment['submission_id'],
                'comment_id': comment['comment_id'],
                'verdict': verdict,
                'score': comment['score']
            })
    
    verdict_df = pd.DataFrame(verdicts)
    
    if len(verdict_df) == 0:
        print("No verdicts found in comments")
        return pd.DataFrame()
    
    # Determine dominant verdict for each submission
    submission_verdicts = []
    for submission_id in submission_ids:
        submission_comment_verdicts = verdict_df[verdict_df['submission_id'] == submission_id]
        
        if len(submission_comment_verdicts) > 0:
            # Get the most common verdict for this submission
            dominant_verdict = submission_comment_verdicts['verdict'].mode()
            if len(dominant_verdict) > 0:
                submission_verdicts.append({
                    'submission_id': submission_id,
                    'dominant_verdict': dominant_verdict.iloc[0],
                    'verdict_count': len(submission_comment_verdicts)
                })
    
    verdict_categories = pd.DataFrame(submission_verdicts)
    
    # Merge with submissions
    categorized_submissions = sample_submissions.merge(
        verdict_categories, on='submission_id', how='inner'
    )
    
    print(f"Categorized {len(categorized_submissions):,} submissions")
    
    # Show distribution
    print("\nVerdict distribution:")
    verdict_counts = categorized_submissions['dominant_verdict'].value_counts()
    for verdict, count in verdict_counts.items():
        print(f"  {verdict}: {count:,} submissions")
    
    return categorized_submissions

def create_stratified_sample(submissions, samples_per_category=10, oversample_factor=5):
    """
    Create stratified sample of submissions across verdict categories.
    Returns oversampled submissions for selection flexibility.
    """
    print(f"\nCreating stratified sample ({samples_per_category} per category, {oversample_factor}x oversampling)...")
    
    total_samples_per_category = samples_per_category * oversample_factor
    stratified_samples = []
    
    for verdict in submissions['dominant_verdict'].unique():
        verdict_submissions = submissions[submissions['dominant_verdict'] == verdict]
        
        if len(verdict_submissions) >= total_samples_per_category:
            sampled = verdict_submissions.sample(n=total_samples_per_category, random_state=42)
        else:
            print(f"Warning: Only {len(verdict_submissions)} submissions for '{verdict}', using all")
            sampled = verdict_submissions
        
        stratified_samples.append(sampled)
    
    if stratified_samples:
        stratified_df = pd.concat(stratified_samples, ignore_index=True)
        
        print(f"\nStratified sample created:")
        print(f"  Total submissions: {len(stratified_df)}")
        for verdict in stratified_df['dominant_verdict'].unique():
            count = len(stratified_df[stratified_df['dominant_verdict'] == verdict])
            print(f"  {verdict}: {count} submissions")
        
        return stratified_df
    else:
        print("No stratified samples could be created")
        return None

def get_comments_for_submissions(submissions, comments):
    """Get comments for the sampled submissions"""
    print(f"\nGetting comments for {len(submissions)} submissions...")
    
    submission_ids = submissions['submission_id'].unique()
    relevant_comments = comments[comments['submission_id'].isin(submission_ids)].copy()
    
    # Add submission context to comments
    relevant_comments = relevant_comments.merge(
        submissions[['submission_id', 'dominant_verdict']], 
        on='submission_id', 
        how='left'
    )
    
    print(f"Found {len(relevant_comments):,} comments")
    
    return relevant_comments

def save_stratified_samples(submissions, comments, output_prefix="stratified"):
    """Save the stratified samples"""
    print(f"\nSaving stratified samples with prefix '{output_prefix}'...")
    
    # Create stratified samples directory
    stratified_dir = SAMPLES_DIR / "stratified"
    stratified_dir.mkdir(exist_ok=True)
    
    # Save CSV files
    submissions_file = stratified_dir / f"{output_prefix}_submissions.csv"
    comments_file = stratified_dir / f"{output_prefix}_comments.csv"
    
    submissions.to_csv(submissions_file, index=False)
    comments.to_csv(comments_file, index=False)
    
    print(f"Saved {len(submissions)} submissions to {submissions_file}")
    print(f"Saved {len(comments)} comments to {comments_file}")
    
    # Create summary
    summary_file = stratified_dir / f"{output_prefix}_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Stratified AITA Sample Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total submissions: {len(submissions):,}\n")
        f.write(f"Total comments: {len(comments):,}\n")
        f.write(f"Average submission length: {submissions['selftext'].str.len().mean():.1f} characters\n")
        f.write(f"Average comment length: {comments['message'].str.len().mean():.1f} characters\n\n")
        
        f.write("Verdict distribution:\n")
        for verdict, count in submissions['dominant_verdict'].value_counts().items():
            f.write(f"  {verdict}: {count:,} submissions\n")
        
        f.write(f"\nComments per submission:\n")
        comment_counts = comments.groupby('submission_id').size()
        f.write(f"  Mean: {comment_counts.mean():.1f}\n")
        f.write(f"  Median: {comment_counts.median():.1f}\n")
        f.write(f"  Min: {comment_counts.min()}\n")
        f.write(f"  Max: {comment_counts.max()}\n")
    
    print(f"Saved summary to {summary_file}")
    
    return stratified_dir

def main():
    parser = argparse.ArgumentParser(description="Create stratified AITA samples by verdict")
    parser.add_argument("--max-submission-chars", type=int, default=2000,
                       help="Maximum characters for submissions (default: 2000)")
    parser.add_argument("--max-comment-chars", type=int, default=500,
                       help="Maximum characters for comments (default: 500)")
    parser.add_argument("--samples-per-category", type=int, default=10,
                       help="Number of samples per verdict category (default: 10)")
    parser.add_argument("--oversample-factor", type=int, default=5,
                       help="Oversample factor for selection flexibility (default: 5)")
    parser.add_argument("--submission-sample-size", type=int, default=10000,
                       help="Number of submissions to process for verdict extraction (default: 10000)")
    parser.add_argument("--output-prefix", type=str, default="stratified",
                       help="Output file prefix (default: stratified)")
    
    args = parser.parse_args()
    
    try:
        # Create directories
        create_directories()
        
        # Load data
        submissions, comments = load_data()
        
        # Filter by length
        filtered_submissions, filtered_comments = filter_by_length(
            submissions, comments, args.max_submission_chars, args.max_comment_chars
        )
        
        # Categorize submissions by verdict
        categorized_submissions = categorize_submissions_by_verdict(
            filtered_submissions, filtered_comments, args.submission_sample_size
        )
        
        if len(categorized_submissions) == 0:
            print("No submissions could be categorized. Try increasing the sample size.")
            return 1
        
        # Create stratified sample
        stratified_submissions = create_stratified_sample(
            categorized_submissions, 
            samples_per_category=args.samples_per_category,
            oversample_factor=args.oversample_factor
        )
        
        if stratified_submissions is None:
            print("No stratified samples could be created.")
            return 1
        
        # Get comments for sampled submissions
        stratified_comments = get_comments_for_submissions(stratified_submissions, filtered_comments)
        
        # Save samples
        stratified_dir = save_stratified_samples(stratified_submissions, stratified_comments, args.output_prefix)
        
        print(f"\n✅ Stratified sampling complete!")
        print(f"Generated {len(stratified_submissions)} submissions across {len(stratified_submissions['dominant_verdict'].unique())} verdict categories")
        print(f"Files saved in the '{stratified_dir}' directory")
        print(f"\nNext steps:")
        print(f"1. Review the stratified samples in {stratified_dir}")
        print(f"2. Use the selection script to pick your favorites")
        print(f"3. Final sample will be {args.samples_per_category} submissions per category")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 