#!/usr/bin/env python3
"""
Did the conversational AI move toward the participant? (CHI 2027 revision,
reviewers R2-1 / R3-5.)

Every conversation opens with a fixed per-scenario AI message (botOpinion in
chat-research-interface/src/data/scenarios.ts) stating the AI's verdict; the
system prompt never tells the model to hold or abandon it. For each
conversation with at least one AI turn after that opener, a coder records
where the AI's later turns left its opening verdict:

    MAINTAINED | NEUTRAL (questions / both sides only) | SOFTENED | REVERSED

  build      writes coding inputs: one transcript block per conversation, with
             the AI's opening stance and the participant's initial answer.
             Contains full transcripts -> participant data, stays in outputs/.
  summarize  joins codes (CSV: conversation_id, ai_end_position, ...) to the
             outcome-bearing sessions of the coded analysis and prints the
             tables reported in the paper.

The 2026-11-11 codes came from a single AI-assisted pass and are NOT
human-verified; recode a sample and report agreement before relying on them.

Usage (from post-study-analysis/):
    python scripts/ai_stance_shift.py build [OUTDIR]
    python scripts/ai_stance_shift.py summarize CODES.csv [CODES2.csv ...]
Default OUTDIR: outputs/ai-stance-shift/  (gitignored)
"""
import os, sys
import pandas as pd

DERIVED = "data-derived"
CODED = os.path.join("outputs", "directionalR-revisionFF-coded0", "all_mod_filtered.csv")
SEED = {"aita": {"yes": "the poster IS at fault", "no": "the poster is NOT at fault"},
        "sexism": {"yes": "it IS sexist", "no": "it is NOT sexist"}}


def norm(v):
    v = str(v).lower()
    if "depend" in v:
        return "depends"
    if v.startswith("no") or "not sexist" in v:
        return "no"
    if v.startswith("yes") or "is sexist" in v:
        return "yes"
    return None


def outcome_sessions():
    """Conversations linked to an outcome-bearing (response, scenario) unit."""
    e = pd.read_csv(os.path.join(DERIVED, "conversation_engagement_metrics.csv"))
    mp = pd.read_csv(os.path.join(DERIVED, "prolific_to_response_mapping.csv"))
    d = pd.read_csv(CODED)
    h = d[d.condition == "high"]
    hb = h.groupby(["response_id", "scenario"])[["R", "FF"]].apply(lambda g: g.notna().any().any())
    hb = hb[hb].reset_index()[["response_id", "scenario"]]
    x = e.merge(mp, on="prolific_id").merge(hb, left_on=["response_id", "scenario_id"],
                                           right_on=["response_id", "scenario"])
    st = pd.read_csv(os.path.join("data", "comprehensive_stance_file.csv"))
    st = st[st.condition == "high"][["response_id", "scenario", "stance_first", "stance_final",
                                     "ai_stance_final_norm"]]
    return x[["conversation_id", "response_id", "scenario"]].merge(st, on=["response_id", "scenario"], how="left")


def build(out):
    os.makedirs(out, exist_ok=True)
    m = pd.read_csv(os.path.join(DERIVED, "messages_clean.csv")).sort_values(["conversation_id", "sequence_number"])
    sess = outcome_sessions().set_index("conversation_id")
    n = 0
    with open(os.path.join(out, "coding_input.txt"), "w") as f:
        for cid, g in m.groupby("conversation_id"):
            if cid not in sess.index or (g.message_type == "ai").sum() < 2:
                continue
            r = sess.loc[cid]
            typ = r.scenario.split("-")[0]
            f.write(f"=== CONVERSATION {cid} | scenario {r.scenario} | AI opening stance: "
                    f"{SEED[typ].get(str(r.ai_stance_final_norm), 'UNKNOWN')} | "
                    f"participant initial answer: {r.stance_first}\n")
            for i, (_, x) in enumerate(g.iterrows()):
                who = "AI" if x.message_type == "ai" else "PARTICIPANT"
                txt = " ".join(str(x.content).split())
                if i == 0 and who == "AI":
                    txt = "[fixed opening rationale, same for every participant on this scenario]"
                f.write(f"[{who}] {txt}\n")
            f.write("\n")
            n += 1
    print(f"{n} conversations -> {out}/coding_input.txt")


def summarize(paths):
    c = pd.concat([pd.read_csv(p) for p in paths]).drop_duplicates("conversation_id")
    b = outcome_sessions().merge(c, on="conversation_id")
    b = b[b.stance_first.notna() & b.ai_stance_final_norm.notna()].copy()
    b["init"], b["fin"] = b.stance_first.map(norm), b.stance_final.map(norm)
    ai = b.ai_stance_final_norm
    b["rel"] = ["depends" if i == "depends" else ("agree" if i == a else "disagree") for i, a in zip(b.init, ai)]
    b["task"] = b.scenario.str.split("-").str[0]
    b["moved_to_ai"] = (b.init != ai) & (b.fin == ai)
    vc = b.ai_end_position.value_counts()
    print(f"n = {len(b)}\n", pd.concat([vc, (vc / len(b) * 100).round(1)], axis=1, keys=["n", "%"]))
    print("\nby initial relation to the AI:\n", pd.crosstab(b.rel, b.ai_end_position, margins=True))
    print("\nby task (%):\n", (pd.crosstab(b.task, b.ai_end_position, normalize="index") * 100).round(1))
    nd = b[b.rel != "agree"]
    print(f"\nnot initially sharing the AI's verdict: {len(nd)}; adopted it: {int(nd.moved_to_ai.sum())}")
    print(pd.crosstab(nd.ai_end_position, nd.moved_to_ai))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("build", "summarize"):
        sys.exit(__doc__)
    if sys.argv[1] == "build":
        build(sys.argv[2] if len(sys.argv) > 2 else os.path.join("outputs", "ai-stance-shift"))
    else:
        summarize(sys.argv[2:])
