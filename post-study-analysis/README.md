# Post-Study Analysis

Two-step post-processing pipeline for the **Human-AI Reliance** study ([SHARE Lab](https://uwshare-lab.ca), University of Waterloo). Takes the raw Supabase export from [chat-research-interface](https://github.com/LLM-Reliance-Project/chat-research-interface), de-dupes accidentally-restarted sessions, and produces engagement metrics + formatted transcripts ready for qualitative scoring.

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
   │      spreadsheet            │
   └─────────────────────────────┘
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
│   └── engagement_metrics.py                   # Step 2: metrics + transcripts → analysis/
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
│   └── conversation_transcripts_for_scoring.csv  ← fill score + notes by hand
│
└── backups/                                    (gitignored contents)
    └── db_cluster-*.backup.gz                  ← pg_dump archive, NOT used by any script
```

## Outputs

| File | Produced by | Description |
|---|---|---|
| `merged/conversations_merged.csv` | `fix_duplicates.py` | Conversations with duplicate `(prolific_id, scenario_id)` rows collapsed (earliest start, latest end, summed interactions). |
| `merged/messages_merged.csv` | `fix_duplicates.py` | All messages reassigned to the surviving conversation; per-conversation AI messages concatenated into one. |
| `merged/participants_merged.csv` | `fix_duplicates.py` | Pass-through, unchanged. |
| `analysis/messages_clean.csv` | `engagement_metrics.py` | Cleaned messages joined with conversation metadata; word counts attached. |
| `analysis/conversation_engagement_metrics.csv` | `engagement_metrics.py` | One row per conversation — quantitative metrics, ready to merge into the main study dataset. |
| `analysis/conversation_transcripts_for_scoring.csv` | `engagement_metrics.py` | Same rows + full formatted transcript; fill `qualitative_score` (1–5) and `notes` columns by hand. |

### Metrics produced

- `num_total_turns`, `num_user_turns`, `num_ai_turns`
- `total_user_words`, `total_ai_words`
- `avg_user_words_per_turn`, `avg_ai_words_per_turn`
- `duration_seconds` — DB `duration_ms` if present, else the span of message timestamps (`max - min`) as a fallback so abandoned sessions still get a real number
- `duration_source` — `db`, `messages`, or `missing`; lets you filter for sessions where the DB end_time was set vs. recovered from messages
- `exceeded_3_minutes` — `True` / `False`, or `None` only if duration cannot be resolved at all

## Data access

**No participant data is in this repo.** Every `*.csv`, `*.xlsx`, `*.gz`, and `*.backup` is gitignored — the rows contain Prolific IDs, IP addresses, user agents, and full transcripts. Request the Supabase export from the study authors.

The Supabase DDL is in [`schema.sql`](./schema.sql) for context only (not meant to be executed).

### Two raw-input formats

Supabase gives you two ways to export the participant data:

1. **Per-table CSV exports** (Supabase dashboard → table → "Export to CSV"). Suffix `_rows.csv`. This is what `fix_duplicates.py` consumes directly — put them in `raw/`.
2. **`pg_dump` cluster backup** (`.backup.gz`). Whole-cluster binary dump — needs `pg_restore` into a Postgres instance to read. **Not used by the scripts** — kept in `backups/` as a point-in-time archive for disaster recovery only.

If you only have the `.gz`, you'll need to restore it into a local Postgres and re-export the three tables as CSVs before running the pipeline.

## Setup

Requires Python 3.10+. Dependencies: `pandas`, `numpy`.

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
```

## Qualitative scoring

Open `analysis/conversation_transcripts_for_scoring.csv` in Excel or Google Sheets and fill the `qualitative_score` column using:

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Minimal | Single words, no real response to AI |
| 2 | Shallow | Short replies, no elaboration |
| 3 | Moderate | Some back-and-forth, partial engagement |
| 4 | Deep | User elaborates meaningfully |
| 5 | Very deep | Rich dialogue, user reflects and builds on the conversation |

Use `notes` for anything that doesn't fit the rubric (e.g. off-topic, tech issue).
