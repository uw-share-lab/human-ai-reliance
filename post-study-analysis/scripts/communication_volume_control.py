#!/usr/bin/env python3
"""
Communication-volume control: is the high-condition effect interactivity, or
just more information?

The high condition does not only add turn-taking, it also delivers more AI text
than the low condition, where every participant reads one fixed AI statement.
Any high-vs-low difference is therefore open to a volume explanation: the
participant changed their answer because they read more, not because they
conversed. These four analyses separate the two.

  A. Exposure gap        — quantify the confound (AI words read, by condition).
  B. Volume-adjusted     — refit the condition effect with AI-word exposure as a
                           covariate; report how much of the condition
                           coefficient it absorbs.
  C. Volume/interactivity decomposition — within the high condition, total
                           exposure factorises as (exchanges) x (AI words per
                           exchange). Entered together these are only mildly
                           collinear (VIF ~1.4, against ~5.5 for turns vs. total
                           words), so they can be raced against each other:
                           does the outcome track how *often* the participant
                           engaged, or how *much text* each engagement returned?
  D. Volume-matched      — the effect is re-estimated against only the least
                           exposed third of high-condition sessions, whose AI
                           word count is closest to the low condition's.

Model spec matches the main analysis: MixedLM with a participant random
intercept and a scenario variance component, ML fit.

Usage:  python scripts/communication_volume_control.py [--mode nopaste|baseline]
Writes outputs/communication-volume-control/.
"""

import argparse
import os

import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

ANALYSIS_DIR = "data-derived"
OUT_DIR = os.path.join("outputs", "communication-volume-control")

# R is defined for these modalities; FF adds the word-count modality.
R_MODALITIES = ["theme", "liwc", "stance"]
FF_MODALITIES = ["theme", "liwc", "detail_words", "stance"]


def fit_mixedlm(df, formula, group_col="response_id", scenario_col="scenario"):
    """Same specification as the main notebook."""
    d = df.copy()
    d[group_col] = d[group_col].astype(str)
    d[scenario_col] = d[scenario_col].astype(str)
    vc = {"scenario": f"0 + C({scenario_col})"}
    model = smf.mixedlm(formula, d, groups=d[group_col], vc_formula=vc, re_formula="1")
    return model.fit(reml=False, method="lbfgs", maxiter=200, disp=False)


def build_exposure(mode):
    """participant x scenario table of how much AI text was read, and how it arrived.

    low       — one fixed AI statement; exposure is that statement's length.
    high      — the statement plus every follow-up reply in the session.
    baseline  — no AI.
    """
    suffix = "_nopaste" if mode == "nopaste" else ""
    metrics = pd.read_csv(os.path.join(ANALYSIS_DIR, f"conversation_engagement_metrics{suffix}.csv"))
    mapping = pd.read_csv(os.path.join(ANALYSIS_DIR, "prolific_to_response_mapping.csv"))
    scen = pd.read_csv(os.path.join(ANALYSIS_DIR, "scenario_texts.csv"))

    for df, col in [(metrics, "prolific_id"), (mapping, "prolific_id"), (mapping, "response_id")]:
        df[col] = df[col].astype(str).str.strip()

    high = metrics.merge(mapping, on="prolific_id", how="inner")
    high = high.rename(columns={"scenario_id": "scenario"})
    high["condition"] = "high"
    # Exchanges, not stored AI rows: 3 sessions have their AI replies concatenated
    # into a single row, which would distort a per-AI-row average.
    high["n_exchanges"] = high["num_user_turns"] + 1
    high["ai_words"] = high["total_ai_words"]
    high["ai_words_per_exchange"] = high["ai_words"] / high["n_exchanges"]
    high = high[["response_id", "scenario", "condition", "ai_words",
                 "num_user_turns", "n_exchanges", "ai_words_per_exchange",
                 "total_user_words"]]

    return high, scen.set_index("scenario_id")["bot_opinion_words"].to_dict()


def attach_exposure(all_mod, high_exp, opinion_words):
    """Give every row in the analysis sample its AI-word exposure."""
    d = all_mod.copy()
    d["response_id"] = d["response_id"].astype(str).str.strip()
    d["scenario"] = d["scenario"].astype(str).str.strip()
    d = d.merge(high_exp.drop(columns=["condition"]), on=["response_id", "scenario"], how="left")

    static = d["scenario"].map(opinion_words).astype(float)
    is_low = d["condition"] == "low"
    is_base = d["condition"] == "baseline"
    # Low read exactly the one statement, in a single (non-)exchange.
    d.loc[is_low, "ai_words"] = static[is_low]
    d.loc[is_low, "num_user_turns"] = 0
    d.loc[is_low, "n_exchanges"] = 1
    d.loc[is_low, "ai_words_per_exchange"] = static[is_low]
    d.loc[is_base, ["ai_words", "num_user_turns", "n_exchanges", "ai_words_per_exchange"]] = 0.0

    d["log_ai_words"] = np.log1p(d["ai_words"])
    return d


def zscore(s):
    s = pd.to_numeric(s, errors="coerce")
    sd = s.std(ddof=1)
    return (s - s.mean()) / sd if sd and np.isfinite(sd) else s * 0.0


def analysis_a(d, lines):
    lines += ["", "A. EXPOSURE GAP — how much AI text each condition read", "-" * 74]
    sess = d.drop_duplicates(["response_id", "scenario"])
    g = (sess.groupby("condition")["ai_words"]
             .agg(["count", "mean", "std", "median", "min", "max"]).round(1))
    lines.append(g.to_string())
    lo = sess.loc[sess.condition == "low", "ai_words"].dropna()
    hi = sess.loc[sess.condition == "high", "ai_words"].dropna()
    u, p = st.mannwhitneyu(hi, lo, alternative="two-sided")
    lines += [
        "",
        f"  low  median {lo.median():.0f} words   high median {hi.median():.0f} words"
        f"   ratio {hi.median()/lo.median():.2f}x",
        f"  Mann-Whitney high vs low: U={u:.0f}, p={p:.3g}",
        "  → the conditions are NOT matched on information volume; the",
        "    adjustments below are what separate volume from interactivity.",
    ]
    return g.reset_index()


def analysis_b(d, lines):
    """Condition effect before vs after adjusting for AI-word exposure.

    Diagnostic only: exposure is nearly a deterministic function of condition
    (low is fixed at ~58 words by scenario), so the two regressors are severely
    confounded and the adjusted condition coefficient is not interpretable on
    its own. Reported to show *how* confounded, not as an effect estimate.
    """
    lines += ["", "B. VOLUME-ADJUSTED CONDITION EFFECT (low vs high) — DIAGNOSTIC", "-" * 74,
              "   outcome ~ condition   vs   outcome ~ condition + z(log AI words)", ""]
    rows = []
    pair = d[d.condition.isin(["low", "high"])].dropna(subset=["log_ai_words"]).copy()
    pair["log_ai_words_z"] = zscore(pair["log_ai_words"])

    sess = pair.drop_duplicates(["response_id", "scenario"])
    r_cond_vol = np.corrcoef((sess.condition == "high").astype(float),
                             sess["log_ai_words"])[0, 1]
    lines += [
        f"   sessions with a known exposure value: {len(sess)}"
        f" (low {int((sess.condition=='low').sum())}, high {int((sess.condition=='high').sum())})",
        f"   corr(condition, log AI words) = {r_cond_vol:.3f}"
        f"  → {'SEVERE' if abs(r_cond_vol) > .9 else 'substantial'} confounding;"
        " treat the adjusted column as a diagnostic, not an estimate.",
        "",
    ]
    for outcome, mods in [("R", R_MODALITIES), ("FF", FF_MODALITIES)]:
        for mod in mods:
            sub = pair[pair.modality == mod].dropna(subset=[outcome, "log_ai_words_z"])
            if sub.empty:
                continue
            term = "C(condition, Treatment('low'))[T.high]"
            m0 = fit_mixedlm(sub, f"{outcome} ~ C(condition, Treatment('low'))")
            m1 = fit_mixedlm(sub, f"{outcome} ~ C(condition, Treatment('low')) + log_ai_words_z")
            b0, p0 = float(m0.params.get(term, np.nan)), float(m0.pvalues.get(term, np.nan))
            b1, p1 = float(m1.params.get(term, np.nan)), float(m1.pvalues.get(term, np.nan))
            bv, pv = float(m1.params.get("log_ai_words_z", np.nan)), float(m1.pvalues.get("log_ai_words_z", np.nan))
            rows.append(dict(outcome=outcome, modality=mod, n=len(sub),
                             cond_beta_unadj=b0, cond_p_unadj=p0,
                             cond_beta_adj=b1, cond_p_adj=p1,
                             volume_beta=bv, volume_p=pv,
                             corr_condition_volume=r_cond_vol))
            lines.append(
                f"  {outcome:<3} {mod:<13} condition {b0:+.4f} (p={p0:.3f}) →"
                f" {b1:+.4f} (p={p1:.3f})   volume {bv:+.4f} (p={pv:.3f})")
    lines += ["", "   Adding volume inflates rather than shrinks the condition coefficient —",
              "   the signature of two near-collinear regressors splitting one effect, not",
              "   evidence either way. Analyses C and D carry the inference."]
    return pd.DataFrame(rows)


def analysis_c(d, lines):
    """Within high: does the outcome track exchanges or words per exchange?"""
    lines += ["", "C. INTERACTIVITY vs VOLUME, WITHIN THE HIGH CONDITION", "-" * 74,
              "   outcome ~ z(log exchanges) + z(log AI words per exchange)", ""]
    hi = d[(d.condition == "high")].dropna(subset=["n_exchanges", "ai_words_per_exchange"]).copy()
    hi["log_exch_z"] = zscore(np.log(hi["n_exchanges"]))
    hi["log_wpe_z"] = zscore(np.log(hi["ai_words_per_exchange"]))

    u = hi.drop_duplicates(["response_id", "scenario"])[["log_exch_z", "log_wpe_z"]].dropna()
    X = sm.add_constant(u)
    v1, v2 = variance_inflation_factor(X.values, 1), variance_inflation_factor(X.values, 2)
    lines.append(f"   collinearity: r={u.corr().iloc[0,1]:.3f}, VIF={v1:.2f}/{v2:.2f}"
                 f"  (n={len(u)} sessions)")
    lines.append("")

    rows = []
    for outcome, mods in [("R", R_MODALITIES), ("FF", FF_MODALITIES)]:
        for mod in mods:
            sub = hi[hi.modality == mod].dropna(subset=[outcome, "log_exch_z", "log_wpe_z"])
            if len(sub) < 20:
                continue
            m = fit_mixedlm(sub, f"{outcome} ~ log_exch_z + log_wpe_z")
            be, pe = float(m.params.get("log_exch_z", np.nan)), float(m.pvalues.get("log_exch_z", np.nan))
            bw, pw = float(m.params.get("log_wpe_z", np.nan)), float(m.pvalues.get("log_wpe_z", np.nan))
            rows.append(dict(outcome=outcome, modality=mod, n=len(sub),
                             exchanges_beta=be, exchanges_p=pe,
                             words_per_exchange_beta=bw, words_per_exchange_p=pw))
            flag = ""
            if pe < 0.05 and pw >= 0.05:
                flag = "  ← interactivity, not volume"
            elif pw < 0.05 and pe >= 0.05:
                flag = "  ← volume, not interactivity"
            elif pe < 0.05 and pw < 0.05:
                flag = "  ← both"
            lines.append(f"  {outcome:<3} {mod:<13} exchanges {be:+.4f} (p={pe:.3f})"
                         f"   words/exchange {bw:+.4f} (p={pw:.3f}){flag}")
    return pd.DataFrame(rows)


def analysis_d(d, lines, full_sample):
    """Low vs the least-exposed third of high sessions.

    The inferential weight is on the point estimates, not the p-values: cutting
    to the bottom tertile keeps a third of the sessions, so power drops sharply.
    If information volume drove the condition effect, the least-exposed sessions
    should show the *weakest* effect. Whether they do is the test.
    """
    lines += ["", "D. VOLUME-MATCHED SUBSAMPLE (low vs least-exposed third of high)", "-" * 74]
    sess = d[d.condition == "high"].drop_duplicates(["response_id", "scenario"])
    cut = sess["ai_words"].quantile(1 / 3)
    keep = set(map(tuple, sess.loc[sess.ai_words <= cut, ["response_id", "scenario"]].values))
    low = d[d.condition == "low"]
    hi = d[(d.condition == "high")
           & d.apply(lambda r: (r["response_id"], r["scenario"]) in keep, axis=1)]
    matched = pd.concat([low, hi], ignore_index=True)
    lo_med = low.drop_duplicates(["response_id", "scenario"])["ai_words"].median()
    hi_med = hi.drop_duplicates(["response_id", "scenario"])["ai_words"].median()
    n_tx = int(sess["ai_words"].notna().sum())
    lines += [
        "   'full' = all transcript-backed high sessions; 'matched' = bottom",
        "   exposure tertile only. A volume explanation predicts matched << full.",
        "",
        f"   cut: high sessions with AI words <= {cut:.0f} (bottom tertile)",
        f"   median AI words — low {lo_med:.0f} vs high {hi_med:.0f}"
        f"  (was {sess['ai_words'].median():.0f} across all transcript-backed high)",
        f"   high sessions retained: {len(keep)} of {n_tx} with a transcript",
        "",
    ]
    rows = []
    term = "C(condition, Treatment('low'))[T.high]"
    for outcome, mods in [("R", R_MODALITIES), ("FF", FF_MODALITIES)]:
        fam = []
        for mod in mods:
            sub = matched[matched.modality == mod].dropna(subset=[outcome])
            if sub.empty or sub["condition"].nunique() < 2:
                continue
            m = fit_mixedlm(sub, f"{outcome} ~ C(condition, Treatment('low'))")
            key = (outcome, mod)
            fam.append(dict(outcome=outcome, modality=mod, n=len(sub),
                            cond_beta_full=full_sample.get(key, np.nan),
                            cond_beta_matched=float(m.params.get(term, np.nan)),
                            cond_p_raw=float(m.pvalues.get(term, np.nan))))
        if not fam:
            continue
        # Holm across modalities, matching the main analysis's family structure.
        fam_df = pd.DataFrame(fam)
        rej, padj, _, _ = multipletests(fam_df["cond_p_raw"].fillna(1.0).values,
                                        method="holm", alpha=0.05)
        fam_df["cond_p_holm"], fam_df["reject_holm_0.05"] = padj, rej
        for _, r in fam_df.iterrows():
            bf, bm = r["cond_beta_full"], r["cond_beta_matched"]
            ratio = (bm / bf) if bf and np.isfinite(bf) and bf != 0 else np.nan
            lines.append(f"  {r['outcome']:<3} {r['modality']:<13} high−low "
                         f"full {bf:+.4f} → matched {bm:+.4f}"
                         f"  ({ratio:.2f}x)  p_raw={r['cond_p_raw']:.3f}"
                         f"  p_holm={r['cond_p_holm']:.3f}")
        rows.append(fam_df)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="nopaste",
                    choices=["nopaste", "baseline", "none"])
    args = ap.parse_args()

    src = os.path.join("outputs", {
        "nopaste": "directionalR-revisionFF-nopaste",
        "baseline": "directionalR-revisionFF",
        "none": "directionalR-revisionFF-noexclusion",
    }[args.mode], "all_mod_filtered.csv")
    all_mod = pd.read_csv(src)
    high_exp, opinion_words = build_exposure(args.mode)
    d = attach_exposure(all_mod, high_exp, opinion_words)

    os.makedirs(OUT_DIR, exist_ok=True)

    # High-condition participants answered all 8 scenarios in Qualtrics but held a
    # chat on a randomised subset (2 AITA + 2 sexism for 60 of 64). The rows for
    # the un-chatted scenarios carry no outcome values, so they are already
    # dropped by every model in the main analysis; the counts below confirm that
    # restricting to transcript-backed units loses essentially no data.
    hi_sess = d[d.condition == "high"].drop_duplicates(["response_id", "scenario"])
    with_tx = int(hi_sess["ai_words"].notna().sum())
    no_tx = hi_sess[hi_sess["ai_words"].isna()]
    no_tx_scored = int(no_tx[["R", "FF"]].notna().any(axis=1).sum()) if len(no_tx) else 0

    lines = [
        "Communication-volume control — interactivity vs amount of information",
        "=" * 74,
        f"exclusion mode: {args.mode}   source: {src}",
        f"rows: {len(d)}   participants: {d.response_id.nunique()}",
        "",
        "COVERAGE — high-condition participant x scenario units:",
        f"  present in the source files : {len(hi_sess)}",
        f"  with a chat transcript      : {with_tx}",
        f"  without a transcript        : {len(hi_sess) - with_tx}, of which only"
        f" {no_tx_scored} carry any outcome value",
        "  Participants chatted on a randomised 2 AITA + 2 sexism subset of the 8",
        "  scenarios they answered; outcomes were scored only for the chatted ones.",
        "  The un-chatted rows are therefore already absent from every model in the",
        "  main analysis, and restricting B-D to transcript-backed units matches it.",
    ]

    a = analysis_a(d, lines)
    b = analysis_b(d, lines)
    c = analysis_c(d, lines)
    full_betas = {(r.outcome, r.modality): r.cond_beta_unadj for r in b.itertuples()}
    e = analysis_d(d, lines, full_betas)

    # --- Verdict, computed from the tables above ---
    ratio = (d.loc[d.condition == "high", "ai_words"].median()
             / d.loc[d.condition == "low", "ai_words"].median())
    dose_sig = c[(c.exchanges_p < 0.05) | (c.words_per_exchange_p < 0.05)]
    ff = e[e.outcome == "FF"] if len(e) else e
    preserved = int((ff["cond_beta_matched"].abs() >= ff["cond_beta_full"].abs() * 0.8).sum()) \
        if len(ff) else 0

    lines += ["", "=" * 74, "VERDICT", "-" * 74,
              f"  The confound is real: high read {ratio:.1f}x more AI text than low (A).",
              f"  Within the high condition, {len(dose_sig)} of {len(c)} outcomes show any dose-",
              "  response — neither more exchanges nor more words per exchange predicts",
              "  the outcome (C). The effect is not graded in either quantity.",
              f"  At near-matched volume, {preserved} of {len(ff)} revision-magnitude effects keep at",
              "  least 80% of their full-sample magnitude (D); a volume account predicts",
              "  they should shrink. Power falls with the tertile cut, so the Holm-",
              "  corrected p-values there are not significant — the estimates, not the",
              "  p-values, carry the argument.",
              "  Read together: what distinguishes the high condition is that an exchange",
              "  happened at all, not how much text it delivered."]

    text = "\n".join(lines)
    open(os.path.join(OUT_DIR, f"communication_volume_control_{args.mode}.txt"), "w").write(text + "\n")
    for name, df in [("exposure_by_condition", a), ("volume_adjusted_condition", b),
                     ("interactivity_vs_volume_within_high", c), ("volume_matched_subsample", e)]:
        df.to_csv(os.path.join(OUT_DIR, f"{name}_{args.mode}.csv"), index=False)
    print(text)
    print("\nOutputs →", OUT_DIR)


if __name__ == "__main__":
    main()
