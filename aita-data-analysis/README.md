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
│   ├── *_summary.txt               # Simple text summaries
│   ├── balanced/                   # Balanced sampling outputs
│   │   ├── balanced_comments.csv   # Balanced comments with placeholder categories
│   │   └── balanced_submissions.csv # Corresponding submission context
│   └── verdict/                    # Verdict extraction outputs
│       ├── verdict_all_verdicts.csv # All extracted verdicts
│       ├── verdict_balanced_samples.csv # Balanced samples based on actual verdicts
│       └── verdict_summary.txt     # Verdict distribution statistics
│
├── favorites/                  # Manually selected favorites
│   ├── engagement/                 # Engagement-based sampling favorites
│   │   ├── engagement_favorite_submissions.csv # CSV format for analysis
│   │   ├── engagement_favorite_comments.csv # CSV format for analysis
│   │   └── engagement_favorite_submissions.txt # Human-readable TXT format
│   ├── balanced/                   # Balanced sampling favorites
│   │   ├── balanced_favorite_comments.csv # Balanced sample favorites
│   │   ├── balanced_favorite_submissions.csv # Corresponding submission context
│   │   └── balanced_favorite_comments.txt # Human-readable balanced favorites
│   └── stratified/                 # Stratified sampling favorites
│       ├── stratified_favorite_submissions.csv # Stratified sample favorites
│       ├── stratified_favorite_comments.csv # All comments for stratified favorites
│       └── stratified_favorite_submissions.txt # Human-readable stratified favorites
│
├── Scripts
│   ├── sample_data.py          # Engagement-based sampling
│   ├── explore_data.py         # Data exploration and analysis
│   ├── preview_sample.py       # Preview sampled data
│   ├── simple_select.py        # Interactive selection
│   ├── extract_verdicts.py     # Verdict extraction and balanced sampling
│   ├── select_balanced_favorites.py # Balanced sample selection
│   ├── run_balanced_workflow.py # Complete balanced workflow
│   ├── stratified_aita_sample.py # Stratified AITA sampling
│   ├── select_stratified_favorites.py # Stratified sample selection
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

## 🎯 Complete Workflow Examples

### **Option A: Engagement-Based Sampling (Original Workflow)**

This approach samples based on post popularity and engagement:

```bash
# 1. Explore your data
python explore_data.py

# 2. Generate engagement-based sample
python sample_data.py --sample-type standard

# 3. Preview the sample
python preview_sample.py

# 4. Select your favorites
python simple_select.py
```

**Output**: `favorites/engagement/engagement_favorite_submissions.csv` and `favorites/engagement/engagement_favorite_comments.csv`

### **Option B: Verdict-Based Sampling (New Balanced Workflow)**

This approach creates balanced samples across verdict categories:

```bash
# 1. Run complete balanced workflow with interactive selection
python run_balanced_workflow.py --interactive

# OR run individual steps:

# 2a. Extract verdicts and create balanced samples
python extract_verdicts.py --sample-size 100000 --samples-per-category 10

# 2b. Select your favorites from balanced samples
python select_balanced_favorites.py
```

**Output**: `favorites/balanced/balanced_favorite_comments.csv` and `favorites/balanced/balanced_favorite_submissions.csv`

### **Option C: Stratified AITA Sampling (New! - Submission-Focused)**

This approach samples AITA submissions stratified by verdict, then lets you select your favorites:

```bash
# 1. Create stratified sample of submissions by verdict
python stratified_aita_sample.py

# 2. Select your favorite submissions from each verdict category
python select_stratified_favorites.py
```

**Output**: `favorites/stratified/stratified_favorite_submissions.csv` and `favorites/stratified/stratified_favorite_comments.csv`

**Key Features**:
- Samples **submissions** (not comments) stratified by dominant verdict
- Filters by length for manageable content
- 5x oversampling for selection flexibility
- Groups submissions by verdict category during selection
- Includes all comments for selected submissions

### **How Comments Connect to Favorites**

**Engagement-Based Workflow:**
- `sample_data.py` → creates `samples/sampled_submissions.csv` and `samples/sampled_comments.csv`
- `simple_select.py` → reads from samples, lets you select submissions
- Selected submissions + their top comments → saved to `favorites/engagement/`

**Verdict-Based Workflow:**
- `extract_verdicts.py` → creates `samples/verdict/verdict_balanced_samples.csv` + `samples/verdict/verdict_balanced_submissions.csv`
- `select_balanced_favorites.py` → reads balanced samples, lets you select comments
- Selected comments + their full AITA submission context → saved to `favorites/balanced/`

**Stratified AITA Workflow:**
- `stratified_aita_sample.py` → creates `samples/stratified/*_submissions.csv` + `samples/stratified/*_comments.csv`
- `select_stratified_favorites.py` → reads stratified samples, lets you select submissions
- Selected submissions + all their comments → saved to `favorites/stratified/`

**Key Differences:**
- Engagement workflow: You select **submissions**, get their **comments**
- Verdict workflow: You select **comments**, get their **submission context**
- Stratified workflow: You select **submissions**, get **all their comments**

### **What You'll See During Selection**

**Engagement-Based Selection (`simple_select.py`):**
```
SUBMISSION 1/20 - HIGH ENGAGEMENT TIER
Title: AITA for refusing to babysit my nephew?
Score: 1540
TEXT: [Full submission text...]

TOP COMMENTS:
1. (Score: 45): NTA, it's not your responsibility...
2. (Score: 32): You're absolutely right to say no...

Select this submission? (y/n/q to quit):
```

**Verdict-Based Selection (`select_balanced_favorites.py`):**
```
COMMENT 1/6 - NOT THE ASSHOLE
Comment ID: jmjed4l
Submission ID: 13xix2x
Score: 1
Verdict: not the asshole

COMMENT TEXT:
NTA. Its not your child, not your responsibility...

SUBMISSION CONTEXT:
Title: AITA for denying my sister of babysitting my nephew?
Score: 1540
Submission Text: [First 300 characters...]

Select this comment? (y/n/q to quit):
```

**Stratified Selection (`select_stratified_favorites.py`):**
```
SUBMISSION 1/90 - NOT THE ASSHOLE
Submission ID: 13xix2x
Title: AITA for denying my sister of babysitting my nephew?
Score: 1540
Dominant Verdict: not the asshole
Verdict Count: 45
Length: 1,247 characters

AITA SUBMISSION:
[Full submission text...]

TOP COMMENTS (203 total):
Comment (Score: 45): NTA, it's not your responsibility...
Comment (Score: 32): You're absolutely right to say no...

Select this submission? (y/n/q to quit):
```

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
- `favorites/engagement/engagement_favorite_submissions.csv` — Your manually selected submissions
- `favorites/engagement/engagement_favorite_comments.csv` — Comments for your selected submissions

**Balanced Sampling Files**:
- `samples/verdict/verdict_all_verdicts.csv` — All extracted verdicts with metadata
- `samples/verdict/verdict_balanced_samples.csv` — Balanced samples based on actual verdicts
- `favorites/balanced/balanced_favorite_comments.csv` — Your selected favorites from balanced samples
- `favorites/balanced/balanced_favorite_submissions.csv` — Corresponding submission context

**Stratified Sampling Files**:
- `samples/stratified/*_submissions.csv` — Stratified submissions by verdict category
- `samples/stratified/*_comments.csv` — All comments for stratified submissions
- `favorites/stratified/stratified_favorite_submissions.csv` — Your selected favorite submissions
- `favorites/stratified/stratified_favorite_comments.csv` — All comments for selected submissions

### **TXT Files** (For Human Review)
- `samples/sampled_review.txt` — Complete human-readable sample with all submissions and comments
- `favorites/engagement/engagement_favorite_submissions.txt` — Your selected submissions in easy-to-read format
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

## 🎯 Sampling Approaches

This system offers two complementary sampling approaches:

### 1. Engagement-Based Sampling (Original)
Uses `sample_data.py` to create stratified samples based on post engagement (score quintiles).

### 2. Verdict-Based Sampling (New!)
Creates balanced samples across verdict categories for fair analysis.

#### Why Balanced Sampling?
The AITA dataset has a natural imbalance in verdicts:
- **not the asshole**: ~63% of comments
- **asshole**: ~31% of comments  
- **everyone sucks**: ~4% of comments
- **no assholes here**: ~2% of comments

Balanced sampling ensures equal representation across all verdict categories.

#### Quick Start - Balanced Sampling
```bash
# Complete workflow with interactive selection
python run_balanced_workflow.py --interactive

# Custom parameters
python run_balanced_workflow.py --samples-per-category 10 --max-comment-chars 500

# Individual steps
python extract_verdicts.py --sample-size 100000 --samples-per-category 10
python select_balanced_favorites.py
```

#### When to Use Each Approach

**Use Engagement-Based Sampling (`sample_data.py`) when:**
- Studying community engagement patterns
- Analyzing what makes posts popular
- Researching content virality
- Need diverse representation across popularity levels

**Use Verdict-Based Sampling (`extract_verdicts.py`) when:**
- Analyzing moral judgments and verdicts
- Studying community decision-making
- Need balanced representation across verdict categories
- Researching bias in community judgments
- Similar to your sexism study approach

**Use Stratified AITA Sampling (`stratified_aita_sample.py`) when:**
- Want to select **submissions** (not comments) as your primary unit
- Need balanced representation across verdict categories
- Want to see full AITA stories with all their comments
- Studying narrative patterns in AITA submissions
- Need submission-level analysis with complete comment context
- Similar to paper examples that sample submissions stratified by category

---

## 📊 Script Details

### Core Sampling Scripts

#### `sample_data.py` - Engagement-Based Sampling

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

#### `extract_verdicts.py` - Verdict Extraction

**Purpose**: Extracts actual verdicts from comments and creates balanced samples.

**Features**:
- Uses regex patterns to identify YTA, NTA, ESH, NAH in comment text
- Creates truly balanced samples based on actual verdict distribution
- Provides detailed statistics on verdict distribution
- Filters by comment length for manageable samples

**Usage**:
```bash
# Extract verdicts and create balanced samples
python extract_verdicts.py --sample-size 100000 --samples-per-category 10

# Custom parameters
python extract_verdicts.py --sample-size 50000 --samples-per-category 15 --max-comment-chars 400
```

#### `select_balanced_favorites.py` - Balanced Sample Selection

**Purpose**: Interactive selection from balanced verdict samples.

**Features**:
- Shows comments grouped by verdict category
- Displays submission context for each comment
- Allows manual selection of preferred comments
- Saves selections in multiple formats

**Usage**:
```bash
python select_balanced_favorites.py
```

#### `run_balanced_workflow.py` - Complete Workflow

**Purpose**: One-command execution of the entire balanced sampling workflow.

**Features**:
- Automates verdict extraction and balanced sampling
- Optional interactive selection
- Customizable parameters
- Comprehensive error handling

**Usage**:
```bash
# Complete workflow with interactive selection
python run_balanced_workflow.py --interactive

# Custom parameters
python run_balanced_workflow.py --samples-per-category 10 --max-comment-chars 500

# Quick test
python run_balanced_workflow.py --sample-size 10000 --samples-per-category 5
```

#### `stratified_aita_sample.py` - Stratified AITA Sampling

**Purpose**: Creates stratified samples of AITA submissions balanced by verdict category.

**Features**:
- Samples **submissions** (not comments) stratified by dominant verdict
- Filters by submission and comment length for manageable content
- 5x oversampling for selection flexibility
- Extracts verdicts from comments to categorize submissions
- Balances samples across verdict categories (YTA, NTA, ESH, NAH)

**Usage**:
```bash
# Default stratified sampling
python stratified_aita_sample.py

# Custom parameters
python stratified_aita_sample.py --max-submission-chars 2000 --max-comment-chars 500 --oversample-factor 3
```

**Output**: Creates `samples/stratified/` directory with balanced submission samples.

#### `select_stratified_favorites.py` - Stratified Sample Selection

**Purpose**: Interactive selection from stratified AITA submission samples.

**Features**:
- Shows submissions grouped by verdict category
- Displays full submission text with top comments
- Allows manual selection of preferred submissions
- Saves selections with all associated comments
- Exports to human-readable TXT format

**Usage**:
```bash
python select_stratified_favorites.py
```

**Output**: Creates `favorites/stratified/` directory with selected submissions and all their comments.

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
- `engagement_favorite_submissions.csv`: Manually selected submissions for analysis
- `engagement_favorite_comments.csv`: Comments for selected submissions
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