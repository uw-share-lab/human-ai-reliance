# Post-Study Analysis

Post-processing pipeline for the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo). Takes the raw Supabase export from [chat-research-interface](https://github.com/LLM-Reliance-Project/chat-research-interface), de-dupes accidentally-restarted sessions, produces engagement metrics, generates per-scenario YAML files for qualitative scoring, and identifies non-engagers for sensitivity analyses.

```
chat-research-interface (Supabase)
        │
        │ export tables → conversations_rows.csv,
        │                 messages_rows.csv,
        │                 participants_rows.csv
        ▼
   ┌─────────────────────────────┐
   │ 1. fix_duplicates.py        │  merges duplicate (prolific_id, scenario_id)
   │    → *_merged.csv           │  sessions; concatenates split AI messages
   └─────────────────────────────┘
        │
        ▼
   ┌─────────────────────────────┐
   │ 2. engagement_metrics.py    │  computes turns/words/duration; builds
   │    → metrics CSV + scoring  │  transcripts for human qualitative scoring
   │      CSV                    │
   └─────────────────────────────┘
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
   ┌─────────────────────────────┐    ┌─────────────────────────────┐
   │ 3. generate_scoring_yaml.py │    │ 4. engagement_thresholds.py │
   │    → analysis/scoring/      │    │    → exclusion CSVs + plots │
   │      <scenario_id>.yaml     │    │      for non-engager filter  │
   └─────────────────────────────┘    └─────────────────────────────┘
```

## Directory layout

```
Post-Study-Analysis/
├── schema.sql                                  # Supabase DDL, context only
├── requirements.txt
├── README.md
│
├── scripts/
│   ├── fix_duplicates.py                       # Step 1: dedup raw exports → merged/
│   ├── engagement_metrics.py                   # Step 2: metrics + transcripts → analysis/
│   ├── generate_scoring_yaml.py                # Step 3: per-scenario YAML → analysis/scoring/
│   └── engagement_thresholds.py               # Step 4: threshold analysis → analysis/
│
├── data/                                       (gitignored contents)
│   └── ai_conflicts_high.xlsx                  ← reference data
│
├── raw/                                        (gitignored contents)
│   ├── conversations_rows.csv                  ← Supabase "Export rows" CSV
│   ├── messages_rows.csv                       ← Supabase "Export rows" CSV
│   └── participants_rows.csv                   ← Supabase "Export rows" CSV
│
├── merged/                                     (gitignored contents)
│   ├── conversations_merged.csv                ← fix_duplicates.py output
│   ├── messages_merged.csv
│   └── participants_merged.csv
│
├── analysis/                                   (gitignored contents)
│   ├── messages_clean.csv                      ← engagement_metrics.py output
│   ├── conversation_engagement_metrics.csv     ← metrics, one row per conversation
│   ├── conversation_transcripts_for_scoring.csv  ← intermediate; input to steps 3 & 4
│   ├── engagement_thresholds.txt               ← exclusion counts across all thresholds
│   ├── hard_exclusions_test_participants.csv   ← test/pilot Prolific IDs to always drop
│   ├── threshold_turns2_words20.csv            ← non-engager list: turns<2 AND words<20
│   ├── threshold_turns2_words30.csv            ← non-engager list: turns<2 AND words<30
│   ├── plots/                                  ← distribution figures (png)
│   ├── scoring/                               (gitignored — contains participant data)
│   │   └── <scenario_id>.yaml                  ← all conversations
│   ├── scoring_words20/                       (gitignored — contains participant data)
│   │   └── <scenario_id>.yaml                  ← non-engagers (words<20) + test IDs removed
│   └── scoring_words30/                       (gitignored — contains participant data)
│       └── <scenario_id>.yaml                  ← non-engagers (words<30) + test IDs removed
│
└── backups/                                    (gitignored contents)
    └── db_cluster-*.backup.gz                  ← pg_dump archive, NOT used by any script
```

## Outputs

| File | Produced by | Description |
|---|---|---|
| `merged/conversations_merged.csv` | `fix_duplicates.py` | Conversations with duplicate `(prolific_id, scenario_id)` rows collapsed (earliest start, latest end, summed durations). |
| `merged/messages_merged.csv` | `fix_duplicates.py` | All messages reassigned to the surviving conversation; per-conversation AI messages concatenated into one. |
| `merged/participants_merged.csv` | `fix_duplicates.py` | Pass-through, unchanged. |
| `analysis/messages_clean.csv` | `engagement_metrics.py` | Cleaned messages joined with conversation metadata; word counts attached. |
| `analysis/conversation_engagement_metrics.csv` | `engagement_metrics.py` | One row per conversation — quantitative metrics, ready to merge into the main study dataset. |
| `analysis/conversation_transcripts_for_scoring.csv` | `engagement_metrics.py` | Same rows + full formatted transcript; intermediate input for steps 3 & 4. |
| `analysis/scoring/<scenario_id>.yaml` | `generate_scoring_yaml.py` | All conversations, one YAML per scenario. Scorers fill `qualitative_score` and `notes` in-place. |
| `analysis/scoring_words20/<scenario_id>.yaml` | `generate_scoring_yaml.py` | Same, with non-engagers (turns<2 AND words<20) and test participants removed (226 conversations). |
| `analysis/scoring_words30/<scenario_id>.yaml` | `generate_scoring_yaml.py` | Same, with non-engagers (turns<2 AND words<30) and test participants removed (211 conversations). |
| `analysis/engagement_thresholds.txt` | `engagement_thresholds.py` | Exclusion counts at every turns/words/combined threshold. Reference when deciding the non-engager cutoff. |
| `analysis/hard_exclusions_test_participants.csv` | `engagement_thresholds.py` | Pilot/test Prolific IDs (`123456789101112`, `methodologies`) — exclude from all analyses unconditionally. |
| `analysis/threshold_turns2_words20.csv` | `engagement_thresholds.py` | Non-engager list A: turns < 2 AND total words < 20 (24 conversation-scenario pairs). |
| `analysis/threshold_turns2_words30.csv` | `engagement_thresholds.py` | Non-engager list B: turns < 2 AND total words < 30 (39 conversation-scenario pairs). |
| `analysis/plots/` | `engagement_thresholds.py` | Distribution histograms, CDFs, exclusion curves, and turns-vs-words scatter. |

### Metrics produced

- `num_total_turns`, `num_user_turns`, `num_ai_turns`
- `total_user_words`, `total_ai_words`
- `avg_user_words_per_turn`, `avg_ai_words_per_turn`
- `duration_seconds` — DB `duration_ms` if present, else the span of message timestamps (`max - min`) as a fallback so abandoned sessions still get a real number
- `duration_source` — `db`, `messages`, or `missing`; lets you filter for sessions where the DB end_time was set vs. recovered from messages
- `exceeded_3_minutes` — `True` / `False`, or `None` only if duration cannot be resolved at all

## Data access

**No participant data is in this repo.** Every `*.csv`, `*.xlsx`, `*.gz`, `*.backup`, and `analysis/scoring/` is gitignored — the rows contain Prolific IDs, IP addresses, user agents, and full transcripts. Request the Supabase export from the study authors.

The Supabase DDL is in [`schema.sql`](./schema.sql) for context only (not meant to be executed).

### Two raw-input formats

Supabase gives you two ways to export the participant data:

1. **Per-table CSV exports** (Supabase dashboard → table → "Export to CSV"). Suffix `_rows.csv`. This is what `fix_duplicates.py` consumes directly — put them in `raw/`.
2. **`pg_dump` cluster backup** (`.backup.gz`). Whole-cluster binary dump — needs `pg_restore` into a Postgres instance to read. **Not used by the scripts** — kept in `backups/` as a point-in-time archive for disaster recovery only.

If you only have the `.gz`, you'll need to restore it into a local Postgres and re-export the three tables as CSVs before running the pipeline.

## Setup

Requires Python 3.10+. Dependencies: `pandas`, `numpy`, `pyyaml`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Place the three raw exports in `raw/`:

```
Post-Study-Analysis/
└── raw/
    ├── conversations_rows.csv
    ├── messages_rows.csv
    └── participants_rows.csv
```

Then run from the `Post-Study-Analysis/` root:

```bash
source .venv/bin/activate

python scripts/fix_duplicates.py          # step 1: dedup → merged/
python scripts/engagement_metrics.py      # step 2: metrics + transcripts → analysis/
python scripts/generate_scoring_yaml.py   # step 3: all + filtered YAML sets → analysis/scoring*/
python scripts/engagement_thresholds.py   # step 4: threshold analysis + exclusion lists → analysis/
```

## Non-engager filtering

`engagement_thresholds.py` produces two exclusion lists (prolific_id + scenario_id pairs) for sensitivity analyses:

| File | Criterion | Excluded |
|---|---|---|
| `threshold_turns2_words20.csv` | turns < 2 AND total words < 20 | 24 (9.4%) |
| `threshold_turns2_words30.csv` | turns < 2 AND total words < 30 | 39 (15.4%) |

**Hard exclusions** (`hard_exclusions_test_participants.csv`): pilot/test IDs that should be dropped from all analyses unconditionally, regardless of threshold — these have non-Prolific identifiers and were not real participants.

## Qualitative scoring

Step 3 produces one YAML file per scenario in `analysis/scoring/`. Each conversation entry looks like:

```yaml
- conversation_id: cc65dadc-...
  prolific_id: 546ec14d...
  scenario_id: sexism-2
  study_type: sexism
  duration_seconds: 189.6
  num_user_turns: 3
  total_user_words: 46
  avg_user_words_per_turn: 15.3
  transcript: |
    [AI]: Hi, my opinion on this scenario is that...

    [USER]: ...

    [AI]: ...
  qualitative_score: null
  notes: null
```

Open the relevant scenario file in any text editor, read the transcript, and fill in `qualitative_score` and `notes`. Use the rubric below:

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Minimal | Single words, no real response to AI |
| 2 | Shallow | Short replies, no elaboration |
| 3 | Moderate | Some back-and-forth, partial engagement |
| 4 | Deep | User elaborates meaningfully |
| 5 | Very deep | Rich dialogue, user reflects and builds on the conversation |

Use `notes` for anything that doesn't fit the rubric (e.g. off-topic, tech issue).

To read completed scores back into Python:

```python
import yaml

with open("analysis/scoring/aita-1.yaml") as f:
    records = yaml.safe_load(f)

scored = [r for r in records if r["qualitative_score"] is not None]
```
