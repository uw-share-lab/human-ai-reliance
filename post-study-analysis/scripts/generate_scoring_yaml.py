#!/usr/bin/env python3
"""
Generate per-scenario YAML files for qualitative scoring.

Produces three sets of files:
  data-derived/scoring/              — all conversations (unfiltered)
  data-derived/scoring_words20/      — non-engagers removed (turns<2 AND words<20 + hard exclusions)
  data-derived/scoring_words30/      — non-engagers removed (turns<2 AND words<30 + hard exclusions)

Scorers fill in `qualitative_score` and `notes` directly in the file.
To read completed scores back into Python:

    import yaml
    with open("data-derived/scoring/aita-1.yaml") as f:
        records = yaml.safe_load(f)
"""

import os
import pandas as pd

TRANSCRIPTS_PATH  = os.path.join("data-derived", "conversation_transcripts_for_scoring.csv")
HARD_EXCL_PATH    = os.path.join("data-derived", "hard_exclusions_test_participants.csv")
EXCL_WORDS20_PATH = os.path.join("data-derived", "threshold_turns2_words20.csv")
EXCL_WORDS30_PATH = os.path.join("data-derived", "threshold_turns2_words30.csv")


def _scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if s and s[0] in ("#", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`", "{", "["):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if ": " in s or s.startswith("- "):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def write_record(f, row, first):
    f.write("- " if first else "\n- ")
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
    lines = [f"{k}: {_scalar(v)}" for k, v in fields]
    transcript = row["transcript"] if pd.notna(row["transcript"]) else ""
    lines.append("transcript: |")
    for tline in transcript.split("\n"):
        lines.append("  " + tline)
    lines += ["qualitative_score: null", "notes: null"]
    f.write(lines[0] + "\n")
    for line in lines[1:]:
        f.write("  " + line + "\n")


def _load_exclusion_set(*paths):
    """Return a set of (prolific_id, scenario_id) tuples from one or more CSV paths."""
    frames = [pd.read_csv(p)[["prolific_id", "scenario_id"]] for p in paths if os.path.exists(p)]
    if not frames:
        return set()
    combined = pd.concat(frames).drop_duplicates()
    return set(zip(combined["prolific_id"], combined["scenario_id"]))


def write_scenario_files(df, out_dir, label):
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for scenario_id, group in df.groupby("scenario_id"):
        out_path = os.path.join(out_dir, f"{scenario_id}.yaml")
        with open(out_path, "w", encoding="utf-8") as f:
            for i, (_, row) in enumerate(group.iterrows()):
                write_record(f, row, first=(i == 0))
        total += len(group)
        print(f"  {out_path}  ({len(group)} conversations)")
    print(f"  → {label}: {total} conversations across {df['scenario_id'].nunique()} files\n")


def main():
    df = pd.read_csv(TRANSCRIPTS_PATH)
    df = df.sort_values(["scenario_id", "prolific_id"]).reset_index(drop=True)
    n_total = len(df)

    hard_excl   = _load_exclusion_set(HARD_EXCL_PATH)
    excl_words20 = _load_exclusion_set(HARD_EXCL_PATH, EXCL_WORDS20_PATH)
    excl_words30 = _load_exclusion_set(HARD_EXCL_PATH, EXCL_WORDS30_PATH)

    def apply_excl(df, excl_set):
        mask = df.apply(lambda r: (r["prolific_id"], r["scenario_id"]) not in excl_set, axis=1)
        return df[mask]

    sets = [
        (df,                          os.path.join("data-derived", "scoring"),          "all conversations (unfiltered)"),
        (apply_excl(df, excl_words20), os.path.join("data-derived", "scoring_words20"), "filtered: turns<2 AND words<20 + hard exclusions"),
        (apply_excl(df, excl_words30), os.path.join("data-derived", "scoring_words30"), "filtered: turns<2 AND words<30 + hard exclusions"),
    ]

    for filtered_df, out_dir, label in sets:
        n_excl = n_total - len(filtered_df)
        print(f"=== {label}  ({len(filtered_df)} kept, {n_excl} excluded) ===")
        write_scenario_files(filtered_df, out_dir, label)

    print("Done. Fill in `qualitative_score` and `notes` in each file to score.")


if __name__ == "__main__":
    main()
