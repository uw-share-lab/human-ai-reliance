#!/usr/bin/env python3
"""
Setup script for AITA Data Analysis project
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['config', 'data', 'samples', 'favorites']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}/")
        else:
            print(f"📁 Directory already exists: {directory}/")

def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    # Check if we're in a virtual environment
    import sys
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected. Consider creating one:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On macOS/Linux")
        print("   venv\\Scripts\\activate     # On Windows")
    
    # Try to install using pip
    if run_command("pip install -r requirements.txt", "Installing dependencies with pip"):
        return True
    
    # Fallback to pip3
    if run_command("pip3 install -r requirements.txt", "Installing dependencies with pip3"):
        return True
    
    print("❌ Failed to install dependencies. Please install them manually:")
    print("pip install pandas numpy matplotlib seaborn pyyaml")
    return False

def check_data_files():
    """Check if data files exist and provide instructions"""
    data_dir = Path("data")
    required_files = ["submission.csv", "comment.csv"]
    
    print("\nChecking for data files...")
    
    missing_files = []
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"✅ Found: {file}")
        else:
            missing_files.append(file)
            print(f"❌ Missing: {file}")
    
    if missing_files:
        print(f"\n📋 To get started, you need to:")
        print(f"1. Place your data files in the 'data/' directory:")
        for file in missing_files:
            print(f"   - data/{file}")
        print(f"2. Run the data loading notebook: jupyter notebook reading_data.ipynb")
        print(f"3. Or manually copy your CSV files to the data/ directory")
    else:
        print("✅ All required data files found!")

def main():
    """Main setup function"""
    print("🚀 Setting up AITA Data Analysis project...")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Check data files
    check_data_files()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Place your data files in the 'data/' directory")
    print("2. Run: python explore_data.py")
    print("3. Run: python sample_data.py")
    print("4. Run: python preview_sample.py")
    print("5. Run: python simple_select.py")
    print("\nFor help, see README.md")

if __name__ == "__main__":
    main() 