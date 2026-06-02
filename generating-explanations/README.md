# Generating Explanations

GPT-generated explanations for the AITA and sexism scenarios used in the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo). These explanations are the AI-side stimulus shown to participants in the downstream interactive study.

Stage 2 of the study pipeline:

```
AITA-Data-Analysis  →  Generating-Explanations  →  chat-research-interface  →  Post-Study-Analysis
                          (this repo)                                             (analysis)
                                                                                       ↑
                                                                                Data_Wrangling
```

## What it does

For each scenario in `AITA_Examples.xlsx` and `Sexism_Examples.xlsx`, the notebook:
1. Cleans the input (e.g. combining multi-row AITA posts).
2. Calls OpenAI (GPT-4.1) to produce a 3–5 sentence judgment + reasoning.
3. Writes results in three formats — CSV (analysis), TXT (review), YAML (programmatic use).

## Project structure

```
├── generation.ipynb               # Main notebook — generates the explanations
└── data/
    ├── AITA/                      (gitignored contents)
    │   ├── AITA_Examples.xlsx         # Input: AITA scenarios
    │   ├── AITA_Final_Dataset.csv     # Output: scenarios + explanations
    │   └── AITA_explanations.{txt,yaml}
    └── Sexism/                    (gitignored contents)
        ├── Sexism_Examples.xlsx       # Input: sexism scenarios
        ├── Sexism_Final_Dataset.csv   # Output: scenarios + explanations
        └── Sexism_explanations.{txt,yaml}
```

## Data access

The input `.xlsx` files and all generated outputs (CSV / TXT / YAML) are **not in this repo** — they're gitignored because they contain study materials we don't redistribute publicly. The AITA scenarios are derived from the upstream [AITA-Data-Analysis](https://github.com/LLM-Reliance-Project/AITA-Data-Analysis) sampling pipeline; the final consumer is [chat-research-interface](https://github.com/LLM-Reliance-Project/chat-research-interface), which serves the explanations to study participants.

To run the notebook end-to-end you need both `AITA_Examples.xlsx` and `Sexism_Examples.xlsx` placed under `data/AITA/` and `data/Sexism/` respectively — request from the authors.

## Setup

Requires Python 3.11+ and an OpenAI API key.

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install openai pandas numpy python-dotenv pyyaml openpyxl
```

Create a `.env` file:

```
OPEN_AI_API=sk-...
```

> **Note:** `.env` is gitignored. Anyone with commit access should rotate the key if it ever lands in a tracked file.

## Run

```bash
jupyter notebook generation.ipynb
```

Run all cells. Generation is roughly linear in the number of scenarios × the average response length; budget a few minutes per dataset.

## Sample output

**AITA**
```
Conclusion/TLDR: The post author is not at fault in this scenario. They are
simply asking others to follow the clearly posted, city-mandated leash laws
for everyone's safety — a reasonable and responsible action...
```

**Sexism**
```
Yes, this scenario is sexist. It places an unfair expectation on women based
solely on their gender, disregarding their personal autonomy and choices...
```
