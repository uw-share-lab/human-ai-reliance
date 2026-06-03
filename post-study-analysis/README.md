# Post-Study Analysis

Statistical analysis pipeline for the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo). Processes engagement metrics from the Supabase chat database, identifies non-engagers for sensitivity filtering, and runs the primary/secondary MLM analyses on observed and perceived reliance.

## Directory layout

```
Post-Study-Analysis/
├── HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb   ← main analysis notebook
├── schema.sql                                                  ← Supabase DDL (context only)
├── requirements.txt
├── README.md
│
├── scripts/
│   ├── fix_duplicates.py          # Step 1: dedup raw Supabase exports → merged/
│   ├── engagement_metrics.py      # Step 2: compute turns/words/duration → analysis/
│   ├── generate_scoring_yaml.py   # Step 3: per-scenario YAML for qualitative scoring
│   └── engagement_thresholds.py   # Step 4: exclusion lists + distribution plots
│
├── data/                          (gitignored — participant data)
│   ├── H-AI_Subjectivity_Study_High_Interaction_filtered.csv   ← Qualtrics export, high cond.
│   ├── H-AI_Subjectivity_Study_Low_Interaction_filtered.csv    ← Qualtrics export, low cond.
│   ├── H-AI_Subjectivity_Study_Baseline_filtered.csv           ← Qualtrics export, baseline
│   └── ai_conflicts_high.xlsx                                  ← AI vs. participant stance conflicts
│
├── raw/                           (gitignored — Supabase row exports)
│   ├── conversations_rows.csv
│   ├── messages_rows.csv
│   └── participants_rows.csv
│
├── merged/                        (gitignored — fix_duplicates.py output)
│   ├── conversations_merged.csv
│   ├── messages_merged.csv
│   └── participants_merged.csv
│
├── analysis/                      (gitignored — engagement_metrics.py + threshold outputs)
│   ├── messages_clean.csv
│   ├── conversation_engagement_metrics.csv
│   ├── conversation_transcripts_for_scoring.csv
│   ├── engagement_thresholds.txt
│   ├── hard_exclusions_test_participants.csv
│   ├── threshold_turns2_words20.csv
│   ├── threshold_turns2_words30.csv
│   ├── exclude_words20.csv                    ← USE THIS for sensitivity run A
│   ├── exclude_words30.csv                    ← USE THIS for sensitivity run B
│   ├── prolific_to_response_mapping.csv       ← Qualtrics ResponseId ↔ Prolific ID (high cond.)
│   ├── scoring/                               (gitignored — per-scenario YAML, all conversations)
│   ├── scoring_words20/                       (gitignored — non-engagers removed)
│   └── scoring_words30/
│
├── outputs_updated_directionalR_revisionFF/   (gitignored — notebook output CSVs)
│
└── backups/                       (gitignored — pg_dump archive)
```

## Analysis notebook

`HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb` — the main statistical analysis. Run all cells in order.

**Required input files** (gitignored, place in the paths shown):

| File | Path | Source |
|---|---|---|
| `comprehensive_theme_file2.csv` | repo root | Qualtrics + theme cosine scores |
| `comprehensive_language_file2.csv` | repo root | Qualtrics + LIWC cosine scores |
| `comprehensive_detail_lengths2.csv` | repo root | Qualtrics + word/char counts |
| `comprehensive_stance_file.csv` | repo root | Qualtrics + stance classifications |
| `unified_theme_analysis_results_3.xlsx` | repo root | Combined theme + perceived reliance (**needed for perceived reliance cells 25–31**) |
| `H-AI_Subjectivity_Study_*_filtered.csv` | `data/` | Raw Qualtrics exports (all 3 conditions) |

### Cell structure

| Cells | Section |
|---|---|
| 1 | Imports, paths, output directory |
| 2 (helpers) | MixedLM fitter, bootstrap CI, Cohen's d |
| 3 (load) | Load CSVs, compute R and FF per modality |
| 3b (filter) | **Engagement filter** — removes non-engager (response_id, scenario) pairs |
| 4 | **Primary**: directional reliance R, low vs. high, Holm across 3 modalities |
| X | Alternative reliance (FinalAI − FirstFinal) |
| 5 | **Secondary**: revision magnitude FF omnibus (baseline/low/high) |
| 6 | Post-hoc FF pairwise contrasts + bootstrap CIs |
| 5/6 (FinalAI) | Alignment to AI final response |
| 7–master | Sensitivity checks (MWU, participant aggregation) |
| 25–31 | **Perceived reliance** — requires `unified_theme_analysis_results_3.xlsx` |

### Engagement filter (Cell 3b)

Approved exclusion criterion (Sharon, 2026-06-03): **turns < 2 AND total words < 20** in the high-interactivity chat condition.

- **Source list**: `analysis/exclude_words20.csv` — 28 `(prolific_id, scenario_id)` pairs
- **ID mapping**: `analysis/prolific_to_response_mapping.csv` — maps high-condition Prolific IDs to Qualtrics `ResponseId` (built from `Q84` column in the high-interaction Qualtrics export)
- **Result**: 21 `(response_id, scenario)` pairs removed; 7 pairs had no survey response and were already absent from the input CSVs

To regenerate the mapping from the Qualtrics export:

```python
import pandas as pd
df = pd.read_csv("data/H-AI_Subjectivity_Study_High_Interaction_filtered.csv")
mapping = df[["ResponseId","Q84"]].rename(columns={"ResponseId":"response_id","Q84":"prolific_id"})
mapping = mapping[mapping["prolific_id"].str.len() == 24].drop_duplicates("prolific_id")
mapping.to_csv("analysis/prolific_to_response_mapping.csv", index=False)
```

## Engagement pipeline

Separate from the main notebook — processes raw Supabase exports to compute per-conversation engagement metrics and identify non-engagers.

```
raw/*.csv  →  fix_duplicates.py  →  merged/*.csv
                                        ↓
                              engagement_metrics.py  →  analysis/
                                        ↓
                         generate_scoring_yaml.py  →  analysis/scoring*/
                                        ↓
                         engagement_thresholds.py  →  analysis/exclude_words*.csv
```

Run from the repo root (with `.venv` activated):

```bash
source .venv/bin/activate

python scripts/fix_duplicates.py
python scripts/engagement_metrics.py
python scripts/generate_scoring_yaml.py
python scripts/engagement_thresholds.py
```

**Exclusion files produced:**

| File | Criterion | Pairs excluded |
|---|---|---|
| `analysis/exclude_words20.csv` | turns < 2 AND words < 20, plus test participants | 28 |
| `analysis/exclude_words30.csv` | turns < 2 AND words < 30, plus test participants | 43 |

## Setup

Python 3.10+. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data access

**No participant data is committed to this repo.** All `*.csv`, `*.xlsx`, `*.gz`, `*.backup`, and `analysis/scoring*/` are gitignored — they contain Prolific IDs, IP addresses, and full transcripts. Request the Supabase export and Qualtrics exports from the study authors.

### Two raw-input formats

1. **Per-table CSV exports** (Supabase dashboard → table → Export to CSV) — suffix `_rows.csv`. Feed to `fix_duplicates.py`.
2. **`pg_dump` cluster backup** (`.backup.gz`) — not consumed by scripts. Kept in `backups/` for disaster recovery.

## Notebook outputs

All output CSVs land in `outputs_updated_directionalR_revisionFF/` (gitignored). Key files:

| File | Contents |
|---|---|
| `all_mod_filtered.csv` | Combined outcomes (R, FF) after engagement filter applied |
| `primary_directionalR_Holm.csv` | Primary family: R low vs. high, Holm-corrected |
| `secondary_FF_omnibus_Holm.csv` | Secondary family: FF omnibus across all conditions |
| `posthoc_FF_pairwise.csv` | Post-hoc FF pairwise contrasts + bootstrap CIs |
| `sensitivity_directionalR_MWU.csv` | Sensitivity: MWU R low vs. high |
| `master_sensitivity_checks.csv` | Master sensitivity table (R, RA, FA, FF) |
