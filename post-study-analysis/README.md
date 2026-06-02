# Post-Study Analysis

Two-step post-processing pipeline for the **Human-AI Reliance** study (Ferguson lab, University of Waterloo). Takes the raw Supabase export from [chat-research-interface](https://github.com/LLM-Reliance-Project/chat-research-interface), de-dupes accidentally-restarted sessions, and produces engagement metrics + formatted transcripts ready for qualitative scoring.

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

## Outputs

| File | Produced by | Description |
|---|---|---|
| `conversations_merged.csv` | `fix_duplicates.py` | Conversations with duplicate `(prolific_id, scenario_id)` rows collapsed (earliest start, latest end, summed interactions). |
| `messages_merged.csv` | `fix_duplicates.py` | All messages reassigned to the surviving conversation; per-conversation AI messages concatenated into one. |
| `participants_merged.csv` | `fix_duplicates.py` | Pass-through, unchanged. |
| `messages_clean.csv` | `engagement_metrics.py` | Cleaned messages joined with conversation metadata; word counts attached. |
| `conversation_engagement_metrics.csv` | `engagement_metrics.py` | One row per conversation — quantitative metrics, ready to merge into the main study dataset. |
| `conversation_transcripts_for_scoring.csv` | `engagement_metrics.py` | Same rows + full formatted transcript; fill `qualitative_score` (1–5) and `notes` columns by hand. |

### Metrics produced

- `num_total_turns`, `num_user_turns`, `num_ai_turns`
- `total_user_words`, `total_ai_words`
- `avg_user_words_per_turn`, `avg_ai_words_per_turn`
- `duration_seconds` — DB `duration_ms` if present, else the span of message timestamps (`max - min`) as a fallback so abandoned sessions still get a real number
- `duration_source` — `db`, `messages`, or `missing`; lets you filter for sessions where the DB end_time was set vs. recovered from messages
- `exceeded_3_minutes` — `True` / `False`, or `None` only if duration cannot be resolved at all

## Data access

**No participant data is in this repo.** Every `*.csv`, `*.xlsx`, and DB backup is gitignored — the rows contain Prolific IDs, IP addresses, user agents, and full transcripts. Request the Supabase export from the study authors.

The Supabase DDL is in [`schema.sql`](./schema.sql) for context only (not meant to be executed).

## Setup

Requires Python 3.10+. Dependencies: `pandas`, `numpy`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Place the three raw exports in the repo root:

```
Post-Study-Analysis/
├── conversations_rows.csv
├── messages_rows.csv
└── participants_rows.csv
```

Then:

```bash
source .venv/bin/activate

python fix_duplicates.py          # step 1: dedup → *_merged.csv
python engagement_metrics.py      # step 2: metrics + transcripts
```

Both scripts read from and write to the current directory.

## Qualitative scoring

Open `conversation_transcripts_for_scoring.csv` in Excel or Google Sheets and fill the `qualitative_score` column using:

| Score | Label | Description |
|-------|-------|-------------|
| 1 | Minimal | Single words, no real response to AI |
| 2 | Shallow | Short replies, no elaboration |
| 3 | Moderate | Some back-and-forth, partial engagement |
| 4 | Deep | User elaborates meaningfully |
| 5 | Very deep | Rich dialogue, user reflects and builds on the conversation |

Use `notes` for anything that doesn't fit the rubric (e.g. off-topic, tech issue).
