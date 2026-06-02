import os
import pandas as pd

MERGED_DIR = "merged"
ANALYSIS_DIR = "analysis"

MESSAGES_PATH = os.path.join(MERGED_DIR, "messages_merged.csv")
CONVERSATIONS_PATH = os.path.join(MERGED_DIR, "conversations_merged.csv")
OUT_MESSAGES_CLEAN = os.path.join(ANALYSIS_DIR, "messages_clean.csv")
OUT_METRICS = os.path.join(ANALYSIS_DIR, "conversation_engagement_metrics.csv")
OUT_TRANSCRIPTS = os.path.join(ANALYSIS_DIR, "conversation_transcripts_for_scoring.csv")

THREE_MINUTES_MS = 3 * 60 * 1000


def word_count(text):
    if pd.isna(text):
        return 0
    return len(str(text).split())


def build_transcript(group):
    lines = []
    for _, row in group.iterrows():
        speaker = "[USER]" if row["message_type"] == "user" else "[AI]"
        lines.append(f"{speaker}: {str(row['content']).strip()}")
    return "\n\n".join(lines)


def main():
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    # --- Load ---
    msgs = pd.read_csv(MESSAGES_PATH)
    conv_df = pd.read_csv(CONVERSATIONS_PATH)

    # --- Clean messages ---
    original_count = len(msgs)
    msgs = msgs[msgs["message_type"].isin(["user", "ai"])].copy()
    dropped = original_count - len(msgs)
    if dropped:
        print(f"Dropped {dropped} messages with invalid message_type")

    msgs.sort_values(["conversation_id", "sequence_number"], inplace=True)
    msgs.reset_index(drop=True, inplace=True)
    msgs["word_count"] = msgs["content"].apply(word_count)
    msgs["timestamp"] = pd.to_datetime(msgs["timestamp"], utc=True, errors="coerce")

    # --- Output 0: cleaned messages joined with conversation metadata ---
    conv_meta = conv_df[
        ["id", "prolific_id", "scenario_id", "study_type", "duration_ms", "start_time", "end_time"]
    ].rename(columns={"id": "conversation_id"})
    msgs.merge(conv_meta, on="conversation_id", how="left").to_csv(OUT_MESSAGES_CLEAN, index=False)

    # --- Per-conversation message metrics ---
    user_msgs = msgs[msgs["message_type"] == "user"]
    ai_msgs = msgs[msgs["message_type"] == "ai"]

    total_turns = msgs.groupby("conversation_id").size().rename("num_total_turns")
    user_turns = user_msgs.groupby("conversation_id").size().rename("num_user_turns")
    ai_turns = ai_msgs.groupby("conversation_id").size().rename("num_ai_turns")
    total_user_words = user_msgs.groupby("conversation_id")["word_count"].sum().rename("total_user_words")
    total_ai_words = ai_msgs.groupby("conversation_id")["word_count"].sum().rename("total_ai_words")

    # Fallback duration: span of message timestamps, in ms.
    # Used when conversations.duration_ms is NULL (session abandoned without
    # a normal end — we still have messages and can recover a real duration).
    msg_span_ms = (
        msgs.groupby("conversation_id")["timestamp"]
        .agg(lambda s: (s.max() - s.min()).total_seconds() * 1000 if s.notna().any() else None)
        .rename("msg_span_ms")
    )

    msg_metrics = pd.concat(
        [total_turns, user_turns, ai_turns, total_user_words, total_ai_words], axis=1
    ).fillna(0).astype(int)
    msg_metrics = msg_metrics.join(msg_span_ms).reset_index()

    msg_metrics["avg_user_words_per_turn"] = (
        msg_metrics["total_user_words"] / msg_metrics["num_user_turns"].where(msg_metrics["num_user_turns"] > 0)
    ).astype(float).round(1)
    msg_metrics["avg_ai_words_per_turn"] = (
        msg_metrics["total_ai_words"] / msg_metrics["num_ai_turns"].where(msg_metrics["num_ai_turns"] > 0)
    ).astype(float).round(1)

    # --- Transcripts ---
    transcripts = (
        msgs.groupby("conversation_id")
        .apply(build_transcript, include_groups=False)
        .rename("transcript")
        .reset_index()
    )

    # --- Merge with conversation metadata + resolve duration ---
    conv_cols = conv_df[
        ["id", "prolific_id", "scenario_id", "study_type", "duration_ms"]
    ].rename(columns={"id": "conversation_id"})

    metrics = conv_cols.merge(msg_metrics, on="conversation_id", how="left")

    # Resolve effective duration: DB value if present, else message-timestamp span.
    db_ms = metrics["duration_ms"]
    span_ms = metrics["msg_span_ms"]
    metrics["effective_duration_ms"] = db_ms.where(db_ms.notna(), span_ms)
    metrics["duration_source"] = db_ms.notna().map({True: "db", False: "messages"})
    # If neither DB nor messages give us anything, mark as missing.
    metrics.loc[metrics["effective_duration_ms"].isna(), "duration_source"] = "missing"

    metrics["duration_seconds"] = (metrics["effective_duration_ms"] / 1000).round(1)
    metrics["exceeded_3_minutes"] = metrics["effective_duration_ms"].apply(
        lambda ms: None if pd.isna(ms) else bool(ms > THREE_MINUTES_MS)
    )

    metrics = metrics.drop(columns=["duration_ms", "msg_span_ms", "effective_duration_ms"])

    metric_cols = [
        "conversation_id", "prolific_id", "scenario_id", "study_type",
        "duration_seconds", "duration_source", "exceeded_3_minutes",
        "num_total_turns", "num_user_turns", "num_ai_turns",
        "total_user_words", "total_ai_words",
        "avg_user_words_per_turn", "avg_ai_words_per_turn",
    ]
    metrics = metrics[metric_cols]

    # --- Output 1: quantitative metrics ---
    metrics.to_csv(OUT_METRICS, index=False)

    # --- Output 2: transcripts for qualitative scoring ---
    scoring = metrics.merge(transcripts, on="conversation_id", how="left")
    scoring["qualitative_score"] = ""
    scoring["notes"] = ""
    scoring_cols = [
        "conversation_id", "prolific_id", "scenario_id", "study_type",
        "duration_seconds", "duration_source", "exceeded_3_minutes",
        "num_user_turns", "total_user_words", "avg_user_words_per_turn",
        "num_ai_turns", "total_ai_words",
        "transcript", "qualitative_score", "notes",
    ]
    scoring[scoring_cols].to_csv(OUT_TRANSCRIPTS, index=False)

    # --- Summary ---
    src_counts = metrics["duration_source"].value_counts()
    print("\n=== Engagement Metrics Summary ===")
    print(f"Conversations processed : {len(metrics)}")
    print(f"Messages used           : {len(msgs)}")
    print(f"Duration source         : {dict(src_counts)}")
    print(f"Exceeded 3 minutes      : {metrics['exceeded_3_minutes'].sum()} / {metrics['exceeded_3_minutes'].notna().sum()} non-null")
    print(f"\nAvg turns per conversation  : {metrics['num_total_turns'].mean():.1f}")
    print(f"Avg user words/conversation : {metrics['total_user_words'].mean():.1f}")
    print(f"Avg AI words/conversation   : {metrics['total_ai_words'].mean():.1f}")
    print("\nOutputs written:")
    print(f"  {OUT_MESSAGES_CLEAN}")
    print(f"  {OUT_METRICS}")
    print(f"  {OUT_TRANSCRIPTS}")


if __name__ == "__main__":
    main()
