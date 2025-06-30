import pandas as pd
import numpy as np
import argparse
import random
from config import (
    DATA_DIR, SAMPLES_DIR, SUBMISSION_FILE, COMMENT_FILE,
    DEFAULT_MAX_SUBMISSION_CHARS, DEFAULT_MAX_COMMENT_CHARS,
    DEFAULT_TARGET_N, DEFAULT_OVERSAMPLE_FACTOR,
    DEFAULT_COMMENTS_PER_SUBMISSION, DEFAULT_OUTPUT_PREFIX,
    ENGAGEMENT_TIERS, create_directories, get_sample_params,
    save_metadata, export_to_txt, METADATA_FILE, REVIEW_FILE
)

def create_directories():
    """Create necessary directories if they don't exist"""
    from config import create_directories as config_create_directories
    config_create_directories()

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
    """Filter data by character length"""
    print(f"\nFiltering submissions to <= {max_submission_chars} characters...")
    filtered_submissions = submissions[submissions['selftext'].str.len() <= max_submission_chars].copy()
    print(f"Filtered to {len(filtered_submissions):,} submissions")
    
    print(f"Filtering comments to <= {max_comment_chars} characters...")
    filtered_comments = comments[comments['message'].str.len() <= max_comment_chars].copy()
    print(f"Filtered to {len(filtered_comments):,} comments")
    
    return filtered_submissions, filtered_comments

def create_engagement_tiers(submissions):
    """Create engagement tiers based on score quintiles"""
    print("\nCreating engagement tiers...")
    submissions['engagement_tier'] = pd.qcut(
        submissions['score'], 
        q=5, 
        labels=ENGAGEMENT_TIERS
    )
    
    # Show distribution
    tier_counts = submissions['engagement_tier'].value_counts().sort_index()
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count:,} submissions")
    
    return submissions

def sample_by_tier(submissions, target_n, oversample_factor):
    """Sample submissions from each engagement tier"""
    print(f"\nSampling {target_n} submissions per tier (with {oversample_factor}x oversampling)...")
    
    sampled_submissions = []
    samples_per_tier = target_n * oversample_factor
    
    for tier in ENGAGEMENT_TIERS:
        tier_submissions = submissions[submissions['engagement_tier'] == tier]
        
        if len(tier_submissions) < samples_per_tier:
            print(f"  Warning: Only {len(tier_submissions)} submissions in {tier} tier")
            samples_per_tier = len(tier_submissions)
        
        tier_sample = tier_submissions.sample(n=samples_per_tier, random_state=42)
        sampled_submissions.append(tier_sample)
    
    return pd.concat(sampled_submissions, ignore_index=True)

def add_comment_metrics(submissions, comments):
    """Add comment count and average comment score to submissions"""
    print("\nAdding comment metrics...")
    
    # Calculate comment counts and average scores
    comment_stats = comments.groupby('submission_id').agg({
        'score': ['count', 'mean']
    }).reset_index()
    comment_stats.columns = ['submission_id', 'comment_count', 'avg_comment_score']
    
    # Merge with submissions
    submissions = submissions.merge(comment_stats, on='submission_id', how='left')
    submissions['comment_count'] = submissions['comment_count'].fillna(0)
    submissions['avg_comment_score'] = submissions['avg_comment_score'].fillna(0)
    
    return submissions

def get_top_comments(submissions, comments, comments_per_submission):
    """Get top comments for each sampled submission"""
    print(f"\nGetting top {comments_per_submission} comments per submission...")
    
    sampled_comment_ids = []
    
    for submission_id in submissions['submission_id']:
        submission_comments = comments[comments['submission_id'] == submission_id]
        
        if len(submission_comments) > 0:
            # Sort by score and take top comments
            top_comments = submission_comments.nlargest(comments_per_submission, 'score')
            sampled_comment_ids.extend(top_comments.index.tolist())
    
    sampled_comments = comments.loc[sampled_comment_ids].copy()
    print(f"Selected {len(sampled_comments):,} comments")
    
    return sampled_comments

def save_samples(submissions, comments, output_prefix, sampling_params):
    """Save the sampled data in multiple formats"""
    print(f"\nSaving samples with prefix '{output_prefix}'...")
    
    # Save CSV files
    submissions_file = SAMPLES_DIR / f"{output_prefix}_submissions.csv"
    submissions.to_csv(submissions_file, index=False)
    print(f"Saved {len(submissions):,} submissions to {submissions_file}")
    
    comments_file = SAMPLES_DIR / f"{output_prefix}_comments.csv"
    comments.to_csv(comments_file, index=False)
    print(f"Saved {len(comments):,} comments to {comments_file}")
    
    # Save metadata to YAML
    metadata = {
        'sampling_parameters': sampling_params,
        'statistics': {
            'total_submissions': len(submissions),
            'total_comments': len(comments),
            'avg_submission_length': float(submissions['selftext'].str.len().mean()),
            'avg_comment_length': float(comments['message'].str.len().mean()),
            'engagement_distribution': submissions['engagement_tier'].value_counts().to_dict()
        },
        'files': {
            'submissions_csv': str(submissions_file),
            'comments_csv': str(comments_file),
            'review_txt': str(REVIEW_FILE),
            'metadata_yaml': str(METADATA_FILE)
        }
    }
    save_metadata(metadata)
    
    # Export to human-readable TXT format
    export_to_txt(submissions, comments, REVIEW_FILE, f"SAMPLE REVIEW - {output_prefix.upper()}")
    
    # Create simple summary
    summary_file = SAMPLES_DIR / f"{output_prefix}_summary.txt"
    with open(summary_file, 'w') as f:
        f.write(f"Sample Summary - {output_prefix}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total submissions: {len(submissions):,}\n")
        f.write(f"Total comments: {len(comments):,}\n")
        f.write(f"Average submission length: {submissions['selftext'].str.len().mean():.1f} characters\n")
        f.write(f"Average comment length: {comments['message'].str.len().mean():.1f} characters\n\n")
        
        f.write("Engagement tier distribution:\n")
        tier_counts = submissions['engagement_tier'].value_counts().sort_index()
        for tier, count in tier_counts.items():
            f.write(f"  {tier}: {count:,} submissions\n")
    
    print(f"Saved summary to {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="Sample Reddit AITA data with stratification")
    parser.add_argument("--max-submission-chars", type=int, default=DEFAULT_MAX_SUBMISSION_CHARS,
                       help=f"Maximum characters for submissions (default: {DEFAULT_MAX_SUBMISSION_CHARS})")
    parser.add_argument("--max-comment-chars", type=int, default=DEFAULT_MAX_COMMENT_CHARS,
                       help=f"Maximum characters for comments (default: {DEFAULT_MAX_COMMENT_CHARS})")
    parser.add_argument("--target-n", type=int, default=DEFAULT_TARGET_N,
                       help=f"Target number of samples per tier (default: {DEFAULT_TARGET_N})")
    parser.add_argument("--oversample-factor", type=int, default=DEFAULT_OVERSAMPLE_FACTOR,
                       help=f"Oversample factor (default: {DEFAULT_OVERSAMPLE_FACTOR})")
    parser.add_argument("--comments-per-submission", type=int, default=DEFAULT_COMMENTS_PER_SUBMISSION,
                       help=f"Number of top comments per submission (default: {DEFAULT_COMMENTS_PER_SUBMISSION})")
    parser.add_argument("--output-prefix", type=str, default=DEFAULT_OUTPUT_PREFIX,
                       help=f"Output file prefix (default: {DEFAULT_OUTPUT_PREFIX})")
    parser.add_argument("--sample-type", type=str, choices=['conservative', 'standard', 'large'],
                       help="Use predefined sample type instead of individual parameters")
    
    args = parser.parse_args()
    
    # Apply sample type if specified
    if args.sample_type:
        params = get_sample_params(args.sample_type)
        args.max_submission_chars = params['max_submission_chars']
        args.max_comment_chars = params['max_comment_chars']
        args.target_n = params['target_n']
        print(f"Using {args.sample_type} sample type: {params}")
    
    try:
        # Create directories
        create_directories()
        
        # Load data
        submissions, comments = load_data()
        
        # Filter by length
        filtered_submissions, filtered_comments = filter_by_length(
            submissions, comments, args.max_submission_chars, args.max_comment_chars
        )
        
        # Create engagement tiers
        filtered_submissions = create_engagement_tiers(filtered_submissions)
        
        # Sample by tier
        sampled_submissions = sample_by_tier(
            filtered_submissions, args.target_n, args.oversample_factor
        )
        
        # Add comment metrics
        sampled_submissions = add_comment_metrics(sampled_submissions, filtered_comments)
        
        # Get top comments
        sampled_comments = get_top_comments(
            sampled_submissions, filtered_comments, args.comments_per_submission
        )
        
        # Save samples
        sampling_params = {
            'max_submission_chars': args.max_submission_chars,
            'max_comment_chars': args.max_comment_chars,
            'target_n': args.target_n,
            'oversample_factor': args.oversample_factor,
            'comments_per_submission': args.comments_per_submission,
            'output_prefix': args.output_prefix
        }
        save_samples(sampled_submissions, sampled_comments, args.output_prefix, sampling_params)
        
        print(f"\n✅ Sampling complete! Generated {len(sampled_submissions):,} submissions and {len(sampled_comments):,} comments")
        print(f"Files saved in the '{SAMPLES_DIR}' directory")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 