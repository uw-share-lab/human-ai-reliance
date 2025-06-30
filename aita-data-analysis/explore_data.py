import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

# Import configuration
from config import DATA_DIR, SUBMISSION_FILE, COMMENT_FILE

def explore_data_distributions():
    """Explore data distributions to help determine filtering parameters"""
    print("Loading data for exploration...")
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"Data directory {DATA_DIR} not found. Creating it...")
        DATA_DIR.mkdir(exist_ok=True)
        print("Please place your data files in the 'data' directory:")
        print(f"  - {SUBMISSION_FILE}")
        print(f"  - {COMMENT_FILE}")
        return
    
    # Load data
    if not SUBMISSION_FILE.exists():
        print(f"Submission file not found: {SUBMISSION_FILE}")
        print("Please ensure the file exists in the data directory.")
        return
        
    if not COMMENT_FILE.exists():
        print(f"Comment file not found: {COMMENT_FILE}")
        print("Please ensure the file exists in the data directory.")
        return
    
    submissions = pd.read_csv(SUBMISSION_FILE)
    comments = pd.read_csv(COMMENT_FILE)
    
    print(f"Data loaded: {len(submissions):,} submissions, {len(comments):,} comments")
    
    # Analyze submission lengths
    submission_lengths = submissions['selftext'].str.len()
    comment_lengths = comments['message'].str.len()
    
    print("\n=== SUBMISSION LENGTH ANALYSIS ===")
    print(f"Mean submission length: {submission_lengths.mean():.1f} characters")
    print(f"Median submission length: {submission_lengths.median():.1f} characters")
    print(f"95th percentile: {submission_lengths.quantile(0.95):.1f} characters")
    print(f"99th percentile: {submission_lengths.quantile(0.99):.1f} characters")
    
    print("\n=== COMMENT LENGTH ANALYSIS ===")
    print(f"Mean comment length: {comment_lengths.mean():.1f} characters")
    print(f"Median comment length: {comment_lengths.median():.1f} characters")
    print(f"95th percentile: {comment_lengths.quantile(0.95):.1f} characters")
    print(f"99th percentile: {comment_lengths.quantile(0.99):.1f} characters")
    
    # Analyze score distributions
    print("\n=== SCORE ANALYSIS ===")
    print(f"Submission scores - Mean: {submissions['score'].mean():.1f}, Median: {submissions['score'].median():.1f}")
    print(f"Comment scores - Mean: {comments['score'].mean():.1f}, Median: {comments['score'].median():.1f}")
    
    # Show what different character limits would give us
    print("\n=== FILTERING IMPACT ANALYSIS ===")
    
    submission_limits = [500, 1000, 1500, 2000, 2500, 3000]
    comment_limits = [200, 300, 400, 500, 600, 800]
    
    print("Submission character limits and resulting counts:")
    for limit in submission_limits:
        count = (submission_lengths <= limit).sum()
        percentage = (count / len(submissions)) * 100
        print(f"  <= {limit} chars: {count:,} submissions ({percentage:.1f}%)")
    
    print("\nComment character limits and resulting counts:")
    for limit in comment_limits:
        count = (comment_lengths <= limit).sum()
        percentage = (count / len(comments)) * 100
        print(f"  <= {limit} chars: {count:,} comments ({percentage:.1f}%)")
    
    # Show engagement distribution
    print("\n=== ENGAGEMENT DISTRIBUTION ===")
    score_quartiles = pd.qcut(submissions['score'], q=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
    engagement_dist = score_quartiles.value_counts().sort_index()
    
    for tier, count in engagement_dist.items():
        percentage = (count / len(submissions)) * 100
        print(f"  {tier}: {count:,} submissions ({percentage:.1f}%)")
    
    # Sample some short submissions for manual review
    print("\n=== SAMPLE SHORT SUBMISSIONS FOR REVIEW ===")
    short_submissions = submissions[submission_lengths <= 1000].sample(n=5, random_state=42)
    
    for idx, row in short_submissions.iterrows():
        print(f"\nSubmission {row['submission_id']} (Score: {row['score']}):")
        print(f"Title: {row['title']}")
        print(f"Length: {len(row['selftext'])} characters")
        print(f"Text preview: {row['selftext'][:200]}...")
        print("-" * 50)

if __name__ == "__main__":
    explore_data_distributions() 