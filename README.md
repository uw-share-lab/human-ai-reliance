# Human-AI Reliance Study

Code and materials for the SHARE Lab study of human reliance on AI
explanations in moral judgment tasks (AITA scenarios).

## Pipeline

| Stage | Folder | What it does |
|---|---|---|
| 1. Scenario sampling | [`aita-data-analysis/`](aita-data-analysis/) | Samples and stratifies AITA posts into study stimuli |
| 2. Explanation generation | [`generating-explanations/`](generating-explanations/) | Generates AI verdicts/explanations for sampled scenarios |
| 3. Study interface | [`chat-research-interface/`](chat-research-interface/) | React chat interface participants use (Vercel + Supabase, embedded in Qualtrics) |
| 4. Post-study analysis | [`post-study-analysis/`](post-study-analysis/) | Reliance metrics, engagement coding (incl. inter-rater reliability), MLM bootstrap analysis |

Shared literature/construct tables live in [`data/`](data/); paper notes and
prototypes in [`docs/`](docs/).

Each stage has its own README and `requirements.txt` (or `package.json`).

## History

This monorepo consolidates four repos (now archived) with full commit history:
AITA-Data-Analysis, Generating-Explanations, chat-research-interface,
Post-Study-Analysis.

## Data

Participant data (transcripts, coding sheets, Prolific mappings) is **not** in
this repository and must never be committed — see the root `.gitignore`.
