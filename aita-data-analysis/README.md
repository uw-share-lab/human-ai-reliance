# Reddit AITA Data Sampling System

This repository contains a comprehensive system for sampling and analyzing Reddit "Am I The Asshole" (AITA) data. The system helps researchers and analysts work with large Reddit datasets by creating manageable, stratified samples.

## 📁 File Structure

```
AITA-Data-Analysis/
├── data/                       # Original data files
│   ├── submission.csv          # ~31K submissions (30MB+)
│   ├── comment.csv             # ~9.1M comments (2GB+)
│   └── AmItheAsshole.sqlite    # SQLite database
│
├── config/                     # Configuration files
│   └── sampling_config.yaml    # YAML configuration for sampling parameters
│
├── samples/                    # Generated sample files
│   ├── sampled_submissions.csv     # CSV format for analysis
│   ├── sampled_comments.csv        # CSV format for analysis
│   ├── sampled_review.txt          # Human-readable TXT format
│   ├── sampled_metadata.yaml       # YAML metadata with statistics
│   └── *_summary.txt               # Simple text summaries
│
├── favorites/                  # Manually selected favorites
│   ├── favorite_submissions.csv    # CSV format for analysis
│   ├── favorite_comments.csv       # CSV format for analysis
│   └── favorite_submissions.txt    # Human-readable TXT format
│
├── Scripts
│   ├── sample_data.py          # Main sampling script
│   ├── explore_data.py         # Data exploration and analysis
│   ├── preview_sample.py       # Preview sampled data
│   ├── simple_select.py        # Interactive selection
│   └── reading_data.ipynb      # Jupyter notebook for data loading
│
└── README.md                   # This file
```

## 🚀 How to Use

### 1. Setup the Project

#### **Option A: Automated Setup (Recommended)**
```bash
# Run the setup script to create directories and install dependencies
python setup.py
```

#### **Option B: Manual Setup with Virtual Environment**
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data samples favorites config
```

#### **Option C: Manual Setup without Virtual Environment**
```bash
# Install dependencies globally (not recommended)
pip install -r requirements.txt

# Create directories
mkdir -p data samples favorites config
```

### 2. Add Your Data

Place your data files in the `data/` directory:
- `data/submission.csv`
- `data/comment.csv`

If you have a SQLite database, you can use the provided notebook to export CSVs:
```bash
jupyter notebook reading_data.ipynb
```

### 3. Explore Your Data

Get a sense of your dataset and decide on filtering parameters:
```bash
python explore_data.py
```

### 4. Generate a Sample

Create a stratified, balanced sample of submissions and comments:
```bash
python sample_data.py
```
You can customize the sample with options (see below).

### 5. Preview the Sample

See examples from each engagement tier and review sample statistics:
```bash
python preview_sample.py
```

### 6. Select Your Favorites

Interactively choose your preferred samples for detailed analysis:
```bash
python simple_select.py
```
Your selections will be saved in the `favorites/` directory.

---

## ⚙️ Customization

- **Change sample size or filtering:**  
  Use command-line options with `sample_data.py`, e.g.:
  ```bash
  python sample_data.py --max-submission-chars 1000 --max-comment-chars 300 --target-n 30
  ```
- **Use a preset sample type:**  
  ```bash
  python sample_data.py --sample-type conservative
  # or: --sample-type standard, --sample-type large
  ```

- **Change output locations:**  
  All paths are managed in `config.py`. Edit this file to change directory names or file locations.

---

## 🗂️ Output Files

### **CSV Files** (For Analysis)
- `samples/sampled_submissions.csv` — Sampled submissions with engagement metrics
- `samples/sampled_comments.csv` — Top comments for each sampled submission
- `favorites/favorite_submissions.csv` — Your manually selected submissions
- `favorites/favorite_comments.csv` — Comments for your selected submissions

### **TXT Files** (For Human Review)
- `samples/sampled_review.txt` — Complete human-readable sample with all submissions and comments
- `favorites/favorite_submissions.txt` — Your selected submissions in easy-to-read format
- `samples/*_summary.txt` — Simple text summaries of sampling statistics

### **YAML Files** (For Configuration & Metadata)
- `config/sampling_config.yaml` — All sampling parameters and configurations
- `samples/sampled_metadata.yaml` — Detailed metadata about each sampling run

---

## 📝 Notes

- All scripts use the paths defined in `config.py` and `config/sampling_config.yaml`
- TXT files are perfect for manual review and sharing with collaborators
- YAML files store configuration and metadata for reproducibility
- CSV files remain the primary format for data analysis

## 🔧 Virtual Environment Management

### **Creating a Virtual Environment**
```bash
# Create a new virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python
```

### **Working with the Virtual Environment**
```bash
# Install dependencies in the virtual environment
pip install -r requirements.txt

# Run scripts (make sure venv is activated)
python explore_data.py
python sample_data.py

# Deactivate when done
deactivate
```

### **Why Use Virtual Environments?**
- **Isolation**: Prevents conflicts between project dependencies
- **Reproducibility**: Ensures consistent environment across different machines
- **Cleanup**: Easy to remove all project dependencies by deleting the venv folder
- **Best Practice**: Standard practice for Python development

### **Troubleshooting**
- **If you see "command not found"**: Make sure the virtual environment is activated
- **If packages aren't found**: Run `pip install -r requirements.txt` again
- **To remove the environment**: Simply delete the `venv/` folder

## 📊 Script Details

### `sample_data.py` - Main Sampling Engine

**Purpose**: Creates stratified, balanced samples from large Reddit datasets.

**Key Features**:
- **Character filtering**: Limits content length for manageable analysis
- **Engagement stratification**: Balances samples across popularity levels
- **Oversampling**: Generates 5x more samples than needed for selection
- **Representative comments**: Includes top-scoring comments for each submission

**Parameters**:
```bash
python sample_data.py [OPTIONS]

Options:
  --max-submission-chars INT    Maximum characters for submissions (default: 2000)
  --max-comment-chars INT       Maximum characters for comments (default: 500)
  --target-n INT                Target number of samples (default: 50)
  --oversample-factor INT       Oversample factor (default: 5)
  --comments-per-submission INT Number of top comments per submission (default: 3)
  --output-prefix STR           Output file prefix (default: sampled)
```

**Example Usage**:
```bash
# Conservative sample (shorter content)
python sample_data.py --max-submission-chars 1000 --max-comment-chars 300 --target-n 30

# Large sample (longer content)
python sample_data.py --max-submission-chars 3000 --max-comment-chars 800 --target-n 100
```

### `explore_data.py` - Data Analysis

**Purpose**: Analyzes data distributions to inform sampling decisions.

**Outputs**:
- Character length distributions for submissions and comments
- Score/engagement statistics
- Impact analysis of different filtering thresholds
- Sample submissions for manual review

**Usage**:
```bash
python explore_data.py
```

### `preview_sample.py` - Sample Preview

**Purpose**: Shows readable previews of generated samples.

**Features**:
- One example from each engagement tier
- Sample statistics and distributions
- Length breakdowns
- Top comment previews

**Usage**:
```bash
python preview_sample.py
```

### `simple_select.py` - Interactive Selection

**Purpose**: Streamlined tool for manually selecting preferred samples.

**Features**:
- Shows 2 samples from each engagement tier
- Simple y/n/q interface
- Automatic saving of selections
- Error handling and validation

**Usage**:
```bash
python simple_select.py
```

## 📈 Sampling Strategy

### 1. **Character Filtering**
- **Submissions**: Filter by `selftext` length
- **Comments**: Filter by `message` length
- **Rationale**: Shorter content is easier to analyze and annotate

### 2. **Engagement Stratification**
- **5 Tiers**: Very Low, Low, Medium, High, Very High
- **Based on**: Submission score (upvotes)
- **Balance**: Equal representation across popularity levels
- **Rationale**: Ensures diverse perspectives, not just viral posts

### 3. **Oversampling**
- **Factor**: 5x target size
- **Purpose**: Provides selection flexibility
- **Example**: Target 50 → Generate 250 → Select 5-10 favorites

### 4. **Comment Selection**
- **Method**: Top-scoring comments per submission
- **Count**: 2-3 comments per submission
- **Rationale**: Representative community responses

## 📋 Data Schema

### Submissions (`submission.csv`)
```csv
id,submission_id,title,selftext,created_utc,permalink,score
```

### Comments (`comment.csv`)
```csv
id,submission_id,message,comment_id,parent_id,created_utc,score
```

### Sampled Submissions (with metrics)
```csv
id,submission_id,title,selftext,created_utc,permalink,score,comment_count,avg_comment_score,engagement_tier
```

## 🎯 Use Cases

### Research Applications
- **Content Analysis**: Study narrative patterns in AITA posts
- **Community Dynamics**: Analyze voting patterns and engagement
- **Linguistic Studies**: Examine writing styles and argument structures
- **Social Psychology**: Study moral reasoning and judgment

### Data Science Projects
- **Text Classification**: Train models to predict verdicts
- **Sentiment Analysis**: Analyze emotional content
- **Topic Modeling**: Identify common themes and issues
- **Engagement Prediction**: Model what makes posts popular

## 🔧 Customization

### Adjusting Character Limits
```bash
# For very short content (easier annotation)
python sample_data.py --max-submission-chars 500 --max-comment-chars 200

# For longer content (more context)
python sample_data.py --max-submission-chars 4000 --max-comment-chars 1000
```

### Changing Sample Sizes
```bash
# Small pilot study
python sample_data.py --target-n 10 --oversample-factor 3

# Large comprehensive study
python sample_data.py --target-n 200 --oversample-factor 2
```

### Modifying Comment Selection
```bash
# More comments per submission
python sample_data.py --comments-per-submission 5

# Fewer comments (faster processing)
python sample_data.py --comments-per-submission 1
```

## 📊 Sample Outputs

### Generated Files
- `*_submissions.csv`: Sampled submissions with engagement metrics
- `*_comments.csv`: Top comments for each sampled submission
- `*_summary.txt`: Detailed sampling statistics and distributions
- `favorite_submissions.csv`: Manually selected submissions for analysis
- `favorite_comments.csv`: Comments for selected submissions
- `favorite_summary.txt`: Complete text and metadata for selected samples

### Summary Statistics
```
SAMPLING SUMMARY
==================================================

Total submissions sampled: 250
Total comments sampled: 750

ENGAGEMENT TIER DISTRIBUTION:
  Very Low: 50
  Low: 50
  Medium: 50
  High: 50
  Very High: 50

SCORE STATISTICS:
  Mean score: 1649.60
  Median score: 410.50
  Min score: 1
  Max score: 26634
```

## 🚨 Troubleshooting

### Memory Issues
- **Problem**: Large datasets cause memory errors
- **Solution**: Use smaller character limits or process in chunks

### File Not Found
- **Problem**: Script can't find CSV files
- **Solution**: Ensure `submission.csv` and `comment.csv` are in the same directory

### Empty Samples
- **Problem**: No data after filtering
- **Solution**: Increase character limits or check data format

### Selection Script Issues
- **Problem**: `select_favorites.py` crashes or doesn't respond
- **Solution**: Use `simple_select.py` instead (more robust)
- **Problem**: Script shows "nothing happens"
- **Solution**: Check that sample files exist and try the simple version first

## 📚 Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations
- **pyyaml**: YAML file handling
- **matplotlib/seaborn**: Data visualization (optional)

## 🤝 Contributing

To extend this system:

1. **Add new stratification methods** (e.g., by topic, time period)
2. **Implement different sampling strategies** (e.g., cluster sampling)
3. **Add data validation and cleaning** steps
4. **Create visualization tools** for sample analysis

## 🎯 Example Workflow

### Complete Example
```bash
# 1. Explore your data
python explore_data.py

# 2. Generate a conservative sample
python sample_data.py --max-submission-chars 1000 --max-comment-chars 300 --target-n 30 --oversample-factor 3

# 3. Preview the sample
python preview_sample.py

# 4. Select your favorites
python simple_select.py

# 5. Review your selections
cat favorite_summary.txt
```

### Expected Output
After running the complete workflow, you'll have:
- **10-15 manually selected samples** across all engagement tiers
- **Complete text and comments** for each selected sample
- **Balanced representation** of different popularity levels
- **Ready-to-analyze data** for your research

## 📄 License

This code is provided for research and educational purposes. Please respect Reddit's terms of service and data usage policies. 