# Generating Explanations

This project generates AI explanations for two types of scenarios using OpenAI's GPT models:
1. **AITA (Am I The Asshole)** scenarios from Reddit posts
2. **Sexism detection** scenarios for bias classification

## Overview

The project uses GPT-4.1 to generate detailed explanations that analyze:
- Whether someone is at fault in AITA scenarios 
- Whether given scenarios contain sexist content or behavior

The generated explanations provide 3-5 sentence judgments with reasoning for each scenario.

## Project Structure

```
├── generation.ipynb           # Main Jupyter notebook for generating explanations
├── AITA_Examples.xlsx         # Input dataset with AITA scenarios
├── Sexism_Examples.xlsx       # Input dataset with sexism scenarios  
├── AITA_Final_Dataset.csv     # Processed AITA data with explanations
├── Sexism_Final_Dataset.csv   # Processed sexism data with explanations
├── AITA_explanations.txt      # Human-readable AITA explanations
├── Sexism_explanations.txt    # Human-readable sexism explanations
├── AITA_explanations.yaml     # Structured AITA explanations
├── Sexism_explanations.yaml   # Structured sexism explanations
└── venv/                      # Python virtual environment
```

## Requirements

- Python 3.11+
- OpenAI API key
- Required packages (see notebook imports):
  - openai
  - pandas
  - numpy
  - python-dotenv
  - pyyaml
  - openpyxl

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install openai pandas numpy python-dotenv pyyaml openpyxl
   ```

3. Set up environment variables:
   Create a `.env` file with your OpenAI API key:
   ```
   OPEN_AI_API=your_openai_api_key_here
   ```

## Usage

1. Open `generation.ipynb` in Jupyter Notebook or JupyterLab
2. Run all cells to process the datasets and generate explanations
3. The notebook will:
   - Load AITA and sexism scenarios from Excel files
   - Clean and process the AITA scenarios (combining multi-row posts)
   - Generate explanations using GPT-4.1
   - Save results in multiple formats (CSV, TXT, YAML)

## Output Files

### AITA Dataset
- **AITA_Final_Dataset.csv**: Complete dataset with titles, scenarios, verdicts, shortened scenarios, and GPT explanations
- **AITA_explanations.txt**: Human-readable format with titles and explanations
- **AITA_explanations.yaml**: Structured format for programmatic access

### Sexism Dataset  
- **Sexism_Final_Dataset.csv**: Complete dataset with scenarios, verdicts, and GPT explanations
- **Sexism_explanations.txt**: Human-readable format with explanations
- **Sexism_explanations.yaml**: Structured format for programmatic access

## Sample Output

### AITA Explanation
```
**Conclusion/TLDR:** The post author is not at fault in this scenario. They are simply asking others to follow the clearly posted, city-mandated leash laws for everyone's safety—a reasonable and responsible action...
```

### Sexism Explanation  
```
Yes, this scenario is sexist. It places an unfair expectation on women based solely on their gender, disregarding their personal autonomy and choices...
```

## Research Purpose

This project generates explanations for machine learning research on:
- Bias detection and classification
- Moral reasoning in AI systems
- Automated content moderation
- Social scenario analysis

The explanations can be used as training data or evaluation benchmarks for AI systems that need to understand and explain social situations and potential biases.