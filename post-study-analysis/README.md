# Post-Study Analysis

Statistical analysis pipeline for the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo). Processes engagement metrics from the Supabase chat database, identifies non-engagers for sensitivity filtering, and runs the primary/secondary MLM analyses on observed and perceived reliance.

## Directory layout

```
Post-Study-Analysis/
├── notebooks/
│   └── HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb   ← main analysis notebook
├── schema.sql                                                  ← Supabase DDL (context only)
├── requirements.txt
├── README.md
│
├── scripts/
│   ├── fix_duplicates.py          # Step 1: dedup raw Supabase exports → merged/
│   ├── engagement_metrics.py      # Step 2: compute turns/words/duration → data-derived/
│   ├── generate_scoring_yaml.py   # Step 3: per-scenario YAML for qualitative scoring
│   └── engagement_thresholds.py   # Step 4: exclusion lists + distribution plots
│
├── data/                          (gitignored — participant data)
│   ├── comprehensive_theme_file2.csv                            ← Qualtrics + theme cosine scores
│   ├── comprehensive_language_file2.csv                         ← Qualtrics + LIWC cosine scores
│   ├── comprehensive_detail_lengths2.csv                        ← Qualtrics + word/char counts
│   ├── comprehensive_stance_file.csv                            ← Qualtrics + stance classifications
│   ├── unified_theme_analysis_results_3.xlsx                    ← combined theme + perceived reliance
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
├── coding/                        (gitignored except engagement_rubric_literature.md — rubrics, coding sheets, double-coding output)
│   ├── engagement_rubric_literature.md        ← tracked
│   ├── engagement_rubric_v0.md
│   ├── engagement_depth_rubric.docx
│   ├── engagement_depth_table.docx
│   ├── full_coding_sheet.xlsx
│   ├── double_coding_sheet.xlsx
│   ├── double_coding_answer_key.csv
│   └── engagement_depth_coded.csv
│
├── data-derived/                  (gitignored except engagement_thresholds.txt — engagement_metrics.py + threshold outputs)
│   ├── messages_clean.csv
│   ├── conversation_engagement_metrics.csv
│   ├── conversation_transcripts_for_scoring.csv
│   ├── engagement_thresholds.txt               ← tracked
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
├── plots/                         ← engagement_thresholds.py distribution figures (tracked)
│   ├── engagement_distributions.png
│   ├── exclusion_curves.png
│   └── turns_vs_words_scatter.png
│
├── outputs/                       (gitignored — model/notebook output CSVs)
│   ├── engagement-predictors/     ← engagement_predictor_models.py output
│   └── directionalR-revisionFF/   ← main notebook output
│
└── backups/                       (gitignored — pg_dump archive)
```

## Analysis notebook

`HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb` — the main statistical analysis. Run all cells in order.

**Required input files** (gitignored, place in the paths shown):

| File | Path | Source |
|---|---|---|
| `comprehensive_theme_file2.csv` | `data/` | Qualtrics + theme cosine scores |
| `comprehensive_language_file2.csv` | `data/` | Qualtrics + LIWC cosine scores |
| `comprehensive_detail_lengths2.csv` | `data/` | Qualtrics + word/char counts |
| `comprehensive_stance_file.csv` | `data/` | Qualtrics + stance classifications |
| `unified_theme_analysis_results_3.xlsx` | `data/` | Combined theme + perceived reliance (**needed for perceived reliance cells 25–31**) |
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

- **Source list**: `data-derived/exclude_words20.csv` — 28 `(prolific_id, scenario_id)` pairs
- **ID mapping**: `data-derived/prolific_to_response_mapping.csv` — maps high-condition Prolific IDs to Qualtrics `ResponseId` (built from `Q84` column in the high-interaction Qualtrics export)
- **Result**: 21 `(response_id, scenario)` pairs removed; 7 pairs had no survey response and were already absent from the input CSVs

To regenerate the mapping from the Qualtrics export:

```python
import pandas as pd
df = pd.read_csv("data/H-AI_Subjectivity_Study_High_Interaction_filtered.csv")
mapping = df[["ResponseId","Q84"]].rename(columns={"ResponseId":"response_id","Q84":"prolific_id"})
mapping = mapping[mapping["prolific_id"].str.len() == 24].drop_duplicates("prolific_id")
mapping.to_csv("data-derived/prolific_to_response_mapping.csv", index=False)
```

## Engagement pipeline

Separate from the main notebook — processes raw Supabase exports to compute per-conversation engagement metrics and identify non-engagers.

```
raw/*.csv  →  fix_duplicates.py  →  merged/*.csv
                                        ↓
                              engagement_metrics.py  →  data-derived/
                                        ↓
                         generate_scoring_yaml.py  →  data-derived/scoring*/
                                        ↓
                         engagement_thresholds.py  →  data-derived/exclude_words*.csv
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
| `data-derived/exclude_words20.csv` | turns < 2 AND words < 20, plus test participants | 28 |
| `data-derived/exclude_words30.csv` | turns < 2 AND words < 30, plus test participants | 43 |

## Setup

Python 3.10+. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data access

**No participant data is committed to this repo.** All `*.csv`, `*.xlsx`, `*.gz`, `*.backup`, and `data-derived/scoring*/` are gitignored — they contain Prolific IDs, IP addresses, and full transcripts. Request the Supabase export and Qualtrics exports from the study authors.

### Two raw-input formats

1. **Per-table CSV exports** (Supabase dashboard → table → Export to CSV) — suffix `_rows.csv`. Feed to `fix_duplicates.py`.
2. **`pg_dump` cluster backup** (`.backup.gz`) — not consumed by scripts. Kept in `backups/` for disaster recovery.

## Notebook outputs

All output CSVs land in `outputs/directionalR-revisionFF/` (gitignored). Key files:

| File | Contents |
|---|---|
| `all_mod.csv` | Combined outcomes (R, FF) before engagement filter |
| `all_mod_filtered.csv` | Combined outcomes (R, FF) after engagement filter applied |
| `primary_directionalR_results.csv` | Primary family: R low vs. high, Holm-corrected (Cell 4) |
| `rowlevel_alt_reliance_finalAI_minus_firstFinal.csv` | Alternative reliance row-level data (Cell X) |
| `secondary_revisionFF_omnibus.csv` | Secondary family: FF omnibus across all conditions, Holm-corrected (Cell 5) |
| `secondary_revisionFF_posthoc_pairwise.csv` | Post-hoc FF pairwise contrasts + bootstrap CIs (Cell 6) |
| `SENS_A_directionalR_MWU.csv` | Sensitivity A: non-parametric R low vs. high (MWU) |
| `SENS_B_relativeAlignment_RA_MWU.csv` | Sensitivity B: relative alignment (RA) MWU |
| `SENS_C_finalAI_FA_MWU.csv` | Sensitivity C: final-AI alignment (FA) MWU |
| `SENS_D1_revisionFF_KW_omnibus.csv` | Sensitivity D1: FF Kruskal-Wallis omnibus |
| `SENS_D2_revisionFF_pairwise_MWU.csv` | Sensitivity D2: FF pairwise MWU contrasts |
| `perceived_by_condition_means.csv` | Perceived reliance means by condition (low/high) |
| `perceived_by_condition_models.csv` | Perceived reliance MLM: condition effect |
| `perceived_by_observedR_models.csv` | Perceived reliance MLM: observed R as predictor |
