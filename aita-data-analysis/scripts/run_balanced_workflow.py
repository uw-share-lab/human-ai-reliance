#!/usr/bin/env python3
"""
Complete Balanced Sampling Workflow for AITA Data Analysis

This script runs the complete balanced sampling workflow:
1. Extract verdicts from comments
2. Create balanced samples
3. Optionally run interactive selection

Usage:
    python run_balanced_workflow.py [--interactive] [--sample-size N] [--samples-per-category N]
"""

import argparse
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Run complete balanced sampling workflow for AITA data analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic workflow with default parameters
  python run_balanced_workflow.py

  # Workflow with custom parameters and interactive selection
  python run_balanced_workflow.py --interactive --sample-size 50000 --samples-per-category 15

  # Quick workflow for testing
  python run_balanced_workflow.py --sample-size 10000 --samples-per-category 5
        """
    )
    
    parser.add_argument("--interactive", action="store_true",
                       help="Run interactive selection after creating balanced samples")
    parser.add_argument("--sample-size", type=int, default=100000,
                       help="Number of comments to process for verdict extraction (default: 100000)")
    parser.add_argument("--samples-per-category", type=int, default=10,
                       help="Number of balanced samples per category (default: 10)")
    parser.add_argument("--max-comment-chars", type=int, default=500,
                       help="Maximum comment length for balanced samples (default: 500)")
    parser.add_argument("--output-prefix", type=str, default="verdict",
                       help="Output file prefix (default: verdict)")
    
    args = parser.parse_args()
    
    print("🚀 Starting Balanced Sampling Workflow for AITA Data Analysis")
    print(f"Parameters:")
    print(f"  Sample size: {args.sample_size:,}")
    print(f"  Samples per category: {args.samples_per_category}")
    print(f"  Max comment length: {args.max_comment_chars}")
    print(f"  Output prefix: {args.output_prefix}")
    print(f"  Interactive selection: {args.interactive}")
    
    # Step 1: Extract verdicts and create balanced samples
    extract_cmd = (
        f"python extract_verdicts.py "
        f"--sample-size {args.sample_size} "
        f"--samples-per-category {args.samples_per_category} "
        f"--max-comment-chars {args.max_comment_chars} "
        f"--output-prefix {args.output_prefix}"
    )
    
    if not run_command(extract_cmd, "Extracting verdicts and creating balanced samples"):
        print("❌ Workflow failed at verdict extraction step")
        return 1
    
    # Step 2: Run interactive selection if requested
    if args.interactive:
        print(f"\n{'='*60}")
        print("Starting interactive selection...")
        print("You will now see comments from each verdict category.")
        print("For each comment, choose 'y' to select, 'n' to skip, or 'q' to quit.")
        print(f"{'='*60}")
        
        select_cmd = "python select_balanced_favorites.py"
        
        if not run_command(select_cmd, "Interactive selection of favorite comments"):
            print("❌ Workflow failed at selection step")
            return 1
    
    # Show results
    print(f"\n{'='*60}")
    print("✅ Balanced Sampling Workflow Complete!")
    print(f"{'='*60}")
    
    # Check what files were created
    samples_dir = Path("samples")
    verdict_dir = samples_dir / "verdict"
    favorites_dir = Path("favorites")
    
    print(f"\nGenerated files:")
    
    if verdict_dir.exists():
        print(f"  📁 Verdict data: {verdict_dir}")
        for file in verdict_dir.glob("*.csv"):
            print(f"    - {file.name}")
        for file in verdict_dir.glob("*.txt"):
            print(f"    - {file.name}")
    
    if args.interactive and favorites_dir.exists():
        print(f"  📁 Favorites: {favorites_dir}")
        for file in favorites_dir.glob("balanced_*"):
            print(f"    - {file.name}")
    
    print(f"\nNext steps:")
    print(f"1. Review the generated samples in the 'samples/verdict' directory")
    print(f"2. Check the balanced samples for quality and balance")
    if args.interactive:
        print(f"3. Review your selected favorites in the 'favorites' directory")
    else:
        print(f"3. Run interactive selection: python select_balanced_favorites.py")
    print(f"4. Use the samples for your analysis")
    
    return 0

if __name__ == "__main__":
    exit(main()) 