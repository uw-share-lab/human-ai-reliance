#!/usr/bin/env python3
"""
Generate per-scenario YAML files for qualitative scoring.

Each file (e.g. scoring/aita-1.yaml) contains all conversations for that
scenario as a YAML list. Scorers fill in `qualitative_score` and `notes`
directly in the file; the result can be read back into Python with:

    import yaml
    with open("scoring/aita-1.yaml") as f:
        records = yaml.safe_load(f)
"""

import os
import pandas as pd

TRANSCRIPTS_PATH = os.path.join("analysis", "conversation_transcripts_for_scoring.csv")
OUT_DIR = os.path.join("analysis", "scoring")


def _scalar(value):
    """Format a simple scalar value for YAML (no block scalars needed)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    # Quote if the string contains YAML-special leading characters or colons.
    if s and s[0] in ("#", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`", "{", "["):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if ": " in s or s.startswith("- "):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def write_record(f, row, first):
    prefix = "- " if first else "\n- "
    f.write(prefix)

    fields = [
        ("conversation_id", row["conversation_id"]),
        ("prolific_id", row["prolific_id"]),
        ("scenario_id", row["scenario_id"]),
        ("study_type", row["study_type"]),
        ("duration_seconds", None if pd.isna(row["duration_seconds"]) else round(float(row["duration_seconds"]), 1)),
        ("num_user_turns", int(row["num_user_turns"])),
        ("total_user_words", int(row["total_user_words"])),
        ("avg_user_words_per_turn", None if pd.isna(row["avg_user_words_per_turn"]) else round(float(row["avg_user_words_per_turn"]), 1)),
    ]

    lines = []
    for key, value in fields:
        lines.append(f"{key}: {_scalar(value)}")

    # Transcript as block scalar — indent each line by 4 spaces.
    transcript = row["transcript"] if pd.notna(row["transcript"]) else ""
    lines.append("transcript: |")
    for tline in transcript.split("\n"):
        lines.append("  " + tline)

    lines.append("qualitative_score: null")
    lines.append("notes: null")

    # First field shares the "- " bullet; subsequent lines are indented.
    f.write(lines[0] + "\n")
    for line in lines[1:]:
        f.write("  " + line + "\n")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(TRANSCRIPTS_PATH)
    df = df.sort_values(["scenario_id", "prolific_id"]).reset_index(drop=True)

    for scenario_id, group in df.groupby("scenario_id"):
        out_path = os.path.join(OUT_DIR, f"{scenario_id}.yaml")
        with open(out_path, "w", encoding="utf-8") as f:
            for i, (_, row) in enumerate(group.iterrows()):
                write_record(f, row, first=(i == 0))
        print(f"  {out_path}  ({len(group)} conversations)")

    print(f"\nDone. {len(df['scenario_id'].unique())} files written to {OUT_DIR}/")
    print("Fill in `qualitative_score` and `notes` in each file to score.")


if __name__ == "__main__":
    main()
