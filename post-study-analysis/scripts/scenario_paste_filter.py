#!/usr/bin/env python3
"""
Scenario-paste filter for the high-interactivity condition.

Some participants opened their turn by pasting (or retyping) the scenario text
back into the chat instead of writing anything of their own. Those messages
inflate `num_user_turns` and `total_user_words`, the two quantities the
non-engager filter keys on, so a participant who pasted the scenario and said
nothing else looks like a full engager.

This script re-derives the engagement metrics and the non-engager exclusion
list with those messages removed.

Detection
---------
A user message is flagged as a scenario paste when, after normalisation
(NFKC, curly quotes/dashes folded, lowercased, punctuation stripped):

  1. the longest contiguous run it shares with the scenario covers
     >= PASTE_MSG_RATIO of the message  — the message is *nothing but* the
     scenario, not a quote embedded in the participant's own reasoning; and
  2. that same run covers >= PASTE_SCENARIO_RATIO of the scenario — it is the
     scenario being reproduced, not an incidental shared phrase.

Both conditions matter. (1) alone would flag a short reply that happens to
echo a stock phrase ("live and let live"); (2) alone would flag a participant
who quotes the scenario and then argues with it at length.

Outputs (all gitignored — participant data):
  data-derived/scenario_texts.csv                          — cached scenario prompts
  data-derived/scenario_paste_messages.csv                 — audit list of flagged messages
  data-derived/messages_clean_nopaste.csv                  — messages_clean minus pastes
  data-derived/conversation_engagement_metrics_nopaste.csv — recomputed metrics
  data-derived/exclude_words20_nopaste.csv                 — recomputed non-engager list
  data-derived/scenario_paste_summary.txt                  — before/after report
"""

import difflib
import os
import re
import unicodedata

import pandas as pd

ANALYSIS_DIR = "data-derived"
SCENARIOS_TS = os.path.join("..", "chat-research-interface", "src", "data", "scenarios.ts")

MESSAGES_CLEAN = os.path.join(ANALYSIS_DIR, "messages_clean.csv")
METRICS_PATH = os.path.join(ANALYSIS_DIR, "conversation_engagement_metrics.csv")

OUT_SCENARIOS = os.path.join(ANALYSIS_DIR, "scenario_texts.csv")
OUT_FLAGGED = os.path.join(ANALYSIS_DIR, "scenario_paste_messages.csv")
OUT_MESSAGES = os.path.join(ANALYSIS_DIR, "messages_clean_nopaste.csv")
OUT_METRICS = os.path.join(ANALYSIS_DIR, "conversation_engagement_metrics_nopaste.csv")
OUT_EXCLUDE = os.path.join(ANALYSIS_DIR, "exclude_words20_nopaste.csv")
OUT_SUMMARY = os.path.join(ANALYSIS_DIR, "scenario_paste_summary.txt")

# Detection thresholds. The observed distribution is strongly bimodal: flagged
# messages sit at 0.94-1.00, the next message down is 0.68, so anything in
# 0.70-0.90 gives the same answer. See scenario_paste_summary.txt.
PASTE_MSG_RATIO = 0.80
PASTE_SCENARIO_RATIO = 0.60

# Same non-engager rule as engagement_thresholds.py (approved threshold).
MIN_TURNS = 2
MIN_WORDS = 20
TEST_PROLIFIC_IDS = ["123456789101112", "methodologies"]

_QUOTE_FOLD = {"’": "'", "‘": "'", "“": '"', "”": '"',
               "—": " ", "–": " ", "…": " "}


def normalize(text):
    """Fold typographic variants so a paste survives Qualtrics/browser mangling."""
    t = unicodedata.normalize("NFKC", str(text))
    for src, dst in _QUOTE_FOLD.items():
        t = t.replace(src, dst)
    return " ".join(re.findall(r"[a-z0-9']+", t.lower()))


def load_scenarios(path=SCENARIOS_TS):
    """Parse the scenario prompts out of the study interface's scenarios.ts."""
    src = open(path, encoding="utf-8").read()
    pattern = r"id:\s*'([\w-]+)'.*?scenario:\s*\"(.*?)\",\n\s*botOpinion:\s*\"(.*?)\"\n"
    out = {}
    for m in re.finditer(pattern, src, re.S):
        out[m.group(1)] = {
            "scenario": m.group(2).replace('\\"', '"'),
            "bot_opinion": m.group(3).replace('\\"', '"'),
        }
    if not out:
        raise ValueError(f"No scenarios parsed from {path}")
    return out


def paste_scores(message, scenario):
    """(share of message that is scenario, share of scenario reproduced)."""
    a, b = normalize(message), normalize(scenario)
    if not a or not b:
        return 0.0, 0.0
    match = difflib.SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
    return match.size / len(a), match.size / len(b)


def word_count(text):
    return 0 if pd.isna(text) else len(str(text).split())


def main():
    scenarios = load_scenarios()
    pd.DataFrame(
        [{"scenario_id": k, "scenario": v["scenario"], "bot_opinion": v["bot_opinion"],
          "scenario_words": len(v["scenario"].split()),
          "bot_opinion_words": len(v["bot_opinion"].split())}
         for k, v in scenarios.items()]
    ).to_csv(OUT_SCENARIOS, index=False)

    msgs = pd.read_csv(MESSAGES_CLEAN)

    # --- Score every user message against its own scenario ---
    user_mask = msgs["message_type"] == "user"
    scores = msgs.loc[user_mask].apply(
        lambda r: paste_scores(r["content"], scenarios.get(str(r["scenario_id"]), {}).get("scenario", "")),
        axis=1, result_type="expand",
    )
    msgs["paste_msg_ratio"] = 0.0
    msgs["paste_scenario_ratio"] = 0.0
    msgs.loc[user_mask, ["paste_msg_ratio", "paste_scenario_ratio"]] = scores.to_numpy()
    msgs["is_scenario_paste"] = (
        user_mask
        & (msgs["paste_msg_ratio"] >= PASTE_MSG_RATIO)
        & (msgs["paste_scenario_ratio"] >= PASTE_SCENARIO_RATIO)
    )

    flagged = msgs[msgs["is_scenario_paste"]].copy()
    flagged["word_count"] = flagged["content"].apply(word_count)
    flagged[[
        "conversation_id", "prolific_id", "scenario_id", "sequence_number",
        "word_count", "paste_msg_ratio", "paste_scenario_ratio", "content",
    ]].sort_values(["prolific_id", "scenario_id"]).to_csv(OUT_FLAGGED, index=False)

    kept = msgs[~msgs["is_scenario_paste"]].copy()
    kept.to_csv(OUT_MESSAGES, index=False)

    # --- Recompute the two metrics the non-engager rule depends on ---
    # Only user-side turns/words change; AI-side counts are untouched.
    metrics = pd.read_csv(METRICS_PATH)
    removed = (
        flagged.groupby("conversation_id")
        .agg(paste_turns=("content", "size"), paste_words=("word_count", "sum"))
        .reset_index()
    )
    m = metrics.merge(removed, on="conversation_id", how="left")
    m[["paste_turns", "paste_words"]] = m[["paste_turns", "paste_words"]].fillna(0).astype(int)
    m["num_user_turns"] = m["num_user_turns"] - m["paste_turns"]
    m["total_user_words"] = m["total_user_words"] - m["paste_words"]
    m["num_total_turns"] = m["num_total_turns"] - m["paste_turns"]
    m["avg_user_words_per_turn"] = (
        m["total_user_words"] / m["num_user_turns"].where(m["num_user_turns"] > 0)
    ).round(1)
    m.drop(columns=["paste_turns", "paste_words"]).to_csv(OUT_METRICS, index=False)

    # --- Recompute the non-engager exclusion list ---
    def excl_mask(df):
        return (df["num_user_turns"] < MIN_TURNS) & (df["total_user_words"] < MIN_WORDS)

    before = excl_mask(metrics)
    after = excl_mask(m)
    hard = m["prolific_id"].astype(str).isin(TEST_PROLIFIC_IDS)

    (m.loc[after | hard, ["prolific_id", "scenario_id"]]
       .drop_duplicates()
       .sort_values(["prolific_id", "scenario_id"])
       .to_csv(OUT_EXCLUDE, index=False))

    # --- Report ---
    newly = m.loc[after & ~before, [
        "prolific_id", "scenario_id", "num_user_turns", "total_user_words"]]
    orig = metrics.set_index(["prolific_id", "scenario_id"])
    lines = [
        "Scenario-paste filter — high-interactivity condition",
        "=" * 70,
        f"Detection: message-coverage >= {PASTE_MSG_RATIO}, scenario-coverage >= {PASTE_SCENARIO_RATIO}",
        "",
        f"User messages scored          : {int(user_mask.sum())}",
        f"Flagged as scenario pastes    : {len(flagged)}",
        f"Conversations affected        : {flagged['conversation_id'].nunique()} / {len(metrics)}",
        f"User words removed            : {int(flagged['word_count'].sum())}",
        "",
        "Flagged by scenario:",
        f"  {flagged.groupby('scenario_id').size().astype(int).to_dict()}",
        "",
        "Non-engager exclusions (turns<2 AND words<20, test IDs added):",
        f"  before filter : {int(before.sum())} conversations",
        f"  after  filter : {int(after.sum())} conversations",
        f"  newly excluded: {int((after & ~before).sum())}",
        "",
        "Newly excluded conversations (was → now):",
    ]
    for _, r in newly.iterrows():
        o = orig.loc[(r["prolific_id"], r["scenario_id"])]
        lines.append(
            f"  {r['prolific_id']}  {r['scenario_id']:<9} "
            f"turns {int(o['num_user_turns'])}→{int(r['num_user_turns'])}, "
            f"words {int(o['total_user_words'])}→{int(r['total_user_words'])}"
        )

    # Sensitivity: how far can the cut move before the answer changes?
    lines += ["", "Threshold sensitivity (message-coverage cut → n flagged):"]
    user_scores = msgs.loc[user_mask]
    for cut in [0.60, 0.70, 0.80, 0.90, 0.95]:
        n = int(((user_scores["paste_msg_ratio"] >= cut)
                 & (user_scores["paste_scenario_ratio"] >= PASTE_SCENARIO_RATIO)).sum())
        lines.append(f"  >= {cut:.2f} : {n}")

    report = "\n".join(lines)
    open(OUT_SUMMARY, "w").write(report + "\n")
    print(report)
    print("\nOutputs written:")
    for p in [OUT_SCENARIOS, OUT_FLAGGED, OUT_MESSAGES, OUT_METRICS, OUT_EXCLUDE, OUT_SUMMARY]:
        print(f"  {p}")


if __name__ == "__main__":
    main()
