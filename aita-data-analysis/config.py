"""
Configuration file for AITA Data Analysis project
"""

import yaml
from pathlib import Path
from datetime import datetime

# Project paths
PROJECT_ROOT = Path(__file__).parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = PROJECT_ROOT / "samples"
FAVORITES_DIR = PROJECT_ROOT / "favorites"

# Load YAML configuration
CONFIG_FILE = CONFIG_DIR / "sampling_config.yaml"

def load_config():
    """Load configuration from YAML file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Fallback to default configuration
        return get_default_config()

def get_default_config():
    """Return default configuration if YAML file doesn't exist"""
    return {
        'sampling': {
            'conservative': {
                'max_submission_chars': 1000,
                'max_comment_chars': 300,
                'target_n': 30,
                'oversample_factor': 5,
                'comments_per_submission': 3
            },
            'standard': {
                'max_submission_chars': 2000,
                'max_comment_chars': 500,
                'target_n': 50,
                'oversample_factor': 5,
                'comments_per_submission': 3
            },
            'large': {
                'max_submission_chars': 3000,
                'max_comment_chars': 800,
                'target_n': 100,
                'oversample_factor': 5,
                'comments_per_submission': 3
            }
        },
        'defaults': {
            'max_submission_chars': 2000,
            'max_comment_chars': 500,
            'target_n': 50,
            'oversample_factor': 5,
            'comments_per_submission': 3,
            'output_prefix': 'sampled'
        },
        'engagement': {
            'tiers': ['Very Low', 'Low', 'Medium', 'High', 'Very High']
        },
        'files': {
            'submissions': 'submission.csv',
            'comments': 'comment.csv',
            'sampled_submissions': 'sampled_submissions.csv',
            'sampled_comments': 'sampled_comments.csv',
            'favorite_submissions': 'favorite_submissions.csv',
            'favorite_comments': 'favorite_comments.csv',
            'metadata': 'sampled_metadata.yaml',
            'review': 'sampled_review.txt',
            'favorites_txt': 'favorite_submissions.txt'
        }
    }

# Load configuration
config = load_config()

# Data file paths
SUBMISSION_FILE = DATA_DIR / config['files']['submissions']
COMMENT_FILE = DATA_DIR / config['files']['comments']
SQLITE_FILE = DATA_DIR / "AmItheAsshole.sqlite"

# Sample file paths
SUBMISSION_SAMPLE_FILE = SAMPLES_DIR / config['files']['sampled_submissions']
COMMENT_SAMPLE_FILE = SAMPLES_DIR / config['files']['sampled_comments']

# Favorite file paths
FAVORITE_SUBMISSIONS_FILE = FAVORITES_DIR / config['files']['favorite_submissions']
FAVORITE_COMMENTS_FILE = FAVORITES_DIR / config['files']['favorite_comments']

# Additional output files
METADATA_FILE = SAMPLES_DIR / config['files']['metadata']
REVIEW_FILE = SAMPLES_DIR / config['files']['review']
FAVORITES_TXT_FILE = FAVORITES_DIR / config['files']['favorites_txt']

# Default sampling parameters
DEFAULT_MAX_SUBMISSION_CHARS = config['defaults']['max_submission_chars']
DEFAULT_MAX_COMMENT_CHARS = config['defaults']['max_comment_chars']
DEFAULT_TARGET_N = config['defaults']['target_n']
DEFAULT_OVERSAMPLE_FACTOR = config['defaults']['oversample_factor']
DEFAULT_COMMENTS_PER_SUBMISSION = config['defaults']['comments_per_submission']
DEFAULT_OUTPUT_PREFIX = config['defaults']['output_prefix']

# Engagement tiers
ENGAGEMENT_TIERS = config['engagement']['tiers']

# Sample types
SAMPLE_TYPES = config['sampling']

def create_directories():
    """Create all necessary directories"""
    for directory in [CONFIG_DIR, DATA_DIR, SAMPLES_DIR, FAVORITES_DIR]:
        directory.mkdir(exist_ok=True)

def get_sample_params(sample_type='standard'):
    """Get sampling parameters for a specific sample type"""
    if sample_type not in SAMPLE_TYPES:
        raise ValueError(f"Unknown sample type: {sample_type}. Available types: {list(SAMPLE_TYPES.keys())}")
    
    return SAMPLE_TYPES[sample_type].copy()

def save_metadata(metadata_dict, output_file=None):
    """Save sampling metadata to YAML file"""
    if output_file is None:
        output_file = METADATA_FILE
    
    metadata_dict['timestamp'] = datetime.now().isoformat()
    
    with open(output_file, 'w') as f:
        yaml.dump(metadata_dict, f, default_flow_style=False, indent=2)
    
    print(f"✅ Metadata saved to {output_file}")

def export_to_txt(submissions, comments, output_file, title="SAMPLE REVIEW"):
    """Export submissions and comments to human-readable TXT format"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Submissions: {len(submissions):,}\n")
        f.write(f"Total Comments: {len(comments):,}\n\n")
        
        # Group by engagement tier
        for tier in ENGAGEMENT_TIERS:
            tier_submissions = submissions[submissions['engagement_tier'] == tier]
            if len(tier_submissions) == 0:
                continue
                
            f.write(f"=== {tier.upper()} ENGAGEMENT TIER ===\n")
            f.write(f"Submissions in this tier: {len(tier_submissions)}\n\n")
            
            for idx, (_, submission) in enumerate(tier_submissions.iterrows(), 1):
                f.write(f"SUBMISSION {idx}: {submission['submission_id']}\n")
                f.write(f"TITLE: {submission['title']}\n")
                f.write(f"SCORE: {submission['score']}\n")
                f.write(f"COMMENT COUNT: {submission.get('comment_count', 'N/A')}\n")
                f.write(f"LENGTH: {len(submission['selftext'])} characters\n")
                f.write(f"TIER: {submission['engagement_tier']}\n")
                f.write(f"TEXT:\n{submission['selftext']}\n\n")
                
                # Add top comments for this submission
                submission_comments = comments[comments['submission_id'] == submission['submission_id']]
                if len(submission_comments) > 0:
                    f.write("TOP COMMENTS:\n")
                    for i, (_, comment) in enumerate(submission_comments.head(3).iterrows(), 1):
                        f.write(f"{i}. (Score: {comment['score']}): {comment['message']}\n")
                    f.write("\n")
                
                f.write("-" * 80 + "\n\n")
    
    print(f"✅ TXT export saved to {output_file}") 