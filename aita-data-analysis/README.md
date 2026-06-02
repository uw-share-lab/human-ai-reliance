# AITA Data Analysis

Sampling and selection pipeline for Reddit r/AmItheAsshole (AITA) posts, used to build the moral-reasoning scenario set for the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo).

This repo is the first stage of the study pipeline:

```
AITA-Data-Analysis  →  Generating-Explanations  →  chat-research-interface  →  Post-Study-Analysis
   (this repo)              (LLM judgments)            (participant study)         (engagement metrics)
                                                              ↑
                                                        Data_Wrangling
                                                        (DB-export merge)
```

It ingests the raw Reddit dump (submissions + comments), produces stratified samples by engagement or by verdict, and provides interactive scripts for selecting the final scenarios used downstream.

## File structure

```
AITA-Data-Analysis/
├── config/
│   └── sampling_config.yaml         # All sampling parameters
├── config.py                        # Path constants shared by every script
├── requirements.txt
│
├── scripts/
│   ├── reading_data.ipynb           # SQLite → CSV export notebook
│   ├── explore_data.py              # Inspect distributions before sampling
│   ├── sample_data.py               # Engagement-stratified sample
│   ├── stratified_aita_sample.py    # Verdict-stratified submission sample
│   ├── extract_verdicts.py          # Regex-extract YTA/NTA/ESH/NAH; balanced comment sample
│   ├── run_balanced_workflow.py     # Wraps extract_verdicts + selection
│   ├── preview_sample.py            # Print a readable summary of a generated sample
│   ├── simple_select.py             # Interactive y/n select from engagement sample
│   ├── select_balanced_favorites.py # Interactive select from verdict-balanced comments
│   ├── select_stratified_favorites.py # Interactive select from stratified submissions
│   └── setup.py                     # One-shot dir/venv/deps bootstrap
│
├── data/        (gitignored)        # Raw inputs: submission.csv, comment.csv, AmItheAsshole.sqlite
├── samples/     (gitignored)        # Generated samples
└── favorites/   (gitignored)        # Final selected scenarios
```

## Data access

The raw Reddit dump and any generated samples / favorites are **not in this repo** (gitignored — they're either too large or contain content we don't redistribute). To reproduce:

- Source: the AITA SQLite database `AmItheAsshole.sqlite` (Reddit dump). Place it under `data/` and run `reading_data.ipynb` to export `submission.csv` and `comment.csv`.
- The final selected scenarios used in the study are tracked in the downstream [Generating-Explanations](https://github.com/LLM-Reliance-Project/Generating-Explanations) repo (`AITA_Examples.xlsx`).

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Or use the bundled bootstrap:

```bash
python scripts/setup.py
```

## Workflows

The repo supports three sampling strategies, picked by what you want to balance over.

### A — Engagement-based (samples by post popularity)

```bash
python scripts/explore_data.py                # inspect distributions
python scripts/sample_data.py                 # generate sample
python scripts/preview_sample.py              # eyeball it
python scripts/simple_select.py               # interactive y/n picker
```

Output: `favorites/engagement/engagement_favorite_{submissions,comments}.csv`

### B — Verdict-based (balanced YTA / NTA / ESH / NAH from comments)

The AITA corpus is naturally imbalanced (~63% NTA, ~31% YTA, ~4% ESH, ~2% NAH). This workflow balances across verdict categories.

```bash
python scripts/run_balanced_workflow.py --interactive
# or piece-wise:
python scripts/extract_verdicts.py --sample-size 100000 --samples-per-category 10
python scripts/select_balanced_favorites.py
```

Output: `favorites/balanced/balanced_favorite_{comments,submissions}.csv`

### C — Stratified submissions (samples submissions, balanced by dominant verdict)

This is what the study used: pick whole AITA submissions (not individual comments), stratified by the verdict the community converged on.

```bash
python scripts/stratified_aita_sample.py
python scripts/select_stratified_favorites.py
```

Output: `favorites/stratified/stratified_favorite_{submissions,comments}.csv`

## Tuning

Every script reads defaults from `config/sampling_config.yaml` and accepts CLI overrides. Common knobs:

```bash
python scripts/sample_data.py \
  --max-submission-chars 1000 \
  --max-comment-chars 300 \
  --target-n 30 \
  --oversample-factor 5 \
  --comments-per-submission 3
```

Run any script with `--help` for the full flag list. To change output locations, edit `config.py`.

## Notes

- All three workflows oversample (default 5x) so the interactive selection step has slack.
- TXT outputs (`*_summary.txt`, `*_review.txt`) are written alongside CSVs for human review.
- YAML metadata (`samples/sampled_metadata.yaml`) records the parameters of each run for reproducibility.

## License

Code is provided for research and educational use. Reddit content is subject to Reddit's [API Terms](https://www.redditinc.com/policies/data-api-terms) and [User Agreement](https://www.redditinc.com/policies/user-agreement) — respect those when working with the raw dump.
