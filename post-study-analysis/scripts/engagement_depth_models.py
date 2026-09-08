#!/usr/bin/env python3
"""
Does *how deeply* a participant engaged predict how far their rationale moved?

The condition contrast in the main analysis asks whether conversation helps at
all. It cannot ask whether deeper conversation helps more, because the depth
codes exist only for the conversational condition -- there is no depth to
assign a participant who never saw a chat box. So this is a within-condition
model, not a covariate bolted onto the low-vs-high contrast, and its estimates
are correlational in a way the randomised condition effect is not: depth was
chosen by the participant, not assigned.

Models, per modality, on conversational-condition rows only:

    R  ~ depth + (1 | participant) + (1 | scenario)     directional reliance
    FF ~ depth + (1 | participant) + (1 | scenario)     revision magnitude

Depth enters linearly (the rubric is ordered, and a linear term is the claim
with the most power and the least to explain); a Wald omnibus on depth as an
unordered factor is reported alongside, so a non-monotone pattern cannot hide
inside a null slope.

Holm correction runs across modalities within each outcome family, matching the
main analysis.

Two sensitivity fits, because the coding was not produced under one regime:

  --coder-covariate  adds the coding block as a fixed effect. Rows #1-128 were
                     double-coded and reconciled; #129-186 are Sharon's alone
                     and #187-254 Jeevan's alone, and the blocks disagree at
                     the top of the scale (0%, 6.2% and 10.3% level-4 codes
                     respectively). An uncorrected slope partly measures which
                     coder saw the row.
  --double-only      refits on the 128 double-coded rows only. Fewer rows, but
                     one measurement regime and no coder term needed.

Usage:
  python scripts/engagement_depth_models.py
  python scripts/engagement_depth_models.py --n-boot 200

Reads data-derived/engagement_depth_resolved.csv (scripts/engagement_depth_codes.py)
and the UNFILTERED outcome table from outputs/directionalR-revisionFF-noexclusion/
-- unfiltered by design: depth is the engagement measure here, so pre-removing
low-engagement rows on a different engagement rule would truncate the predictor.
Writes outputs/engagement-depth-models/.
"""

import argparse
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from joblib import Parallel, delayed
from statsmodels.stats.multitest import multipletests

ALL_MOD = os.path.join("outputs", "directionalR-revisionFF-noexclusion", "all_mod.csv")
DEPTH = os.path.join("data-derived", "engagement_depth_resolved.csv")
OUT_DIR = os.path.join("outputs", "engagement-depth-models")
MODALITIES = ["theme", "liwc", "detail_words", "stance"]


def fit_mixedlm(df, formula, group_col="response_id", scenario_col="scenario"):
    """Same random-effects structure as the main notebook: participant random
    intercept plus a scenario variance component."""
    d = df.copy()
    d[group_col] = d[group_col].astype(str)
    d[scenario_col] = d[scenario_col].astype(str)
    vc = {"scenario": f"0 + C({scenario_col})"}
    model = smf.mixedlm(formula, d, groups=d[group_col], vc_formula=vc, re_formula="1")
    return model.fit(reml=False, method="lbfgs", maxiter=200, disp=False)


def wald_omnibus(res, terms):
    idx = list(res.params.index)
    present = [t for t in terms if t in idx]
    if not present:
        return np.nan
    R = np.zeros((len(present), len(idx)))
    for i, t in enumerate(present):
        R[i, idx.index(t)] = 1.0
    return float(res.wald_test(R).pvalue)


def cluster_bootstrap_ci(df, stat_func, cluster_col="response_id", n_boot=100, seed=7):
    """Resample participants, not rows: the rows within a participant are not
    independent, so a row bootstrap would understate the interval."""
    rng = np.random.default_rng(seed)
    clusters = df[cluster_col].dropna().unique()
    if len(clusters) < 5:
        return (np.nan, np.nan)
    cg = {c: df[df[cluster_col] == c] for c in clusters}
    seeds = rng.integers(0, 2 ** 31, size=n_boot)

    def _one(s):
        r = np.random.default_rng(s)
        samp = r.choice(clusters, size=len(clusters), replace=True)
        parts = []
        for new_id, orig in enumerate(samp):
            chunk = cg[orig].copy()
            chunk[cluster_col] = f"_b{new_id}"
            parts.append(chunk)
        try:
            return stat_func(pd.concat(parts, ignore_index=True))
        except Exception:
            return np.nan

    vals = [v for v in Parallel(n_jobs=-1)(delayed(_one)(s) for s in seeds) if np.isfinite(v)]
    if len(vals) < n_boot // 2:
        return (np.nan, np.nan)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def build(args):
    allm = pd.read_csv(ALL_MOD)
    allm["condition"] = allm["condition"].astype(str).str.strip().str.lower()
    allm["response_id"] = allm["response_id"].astype(str).str.strip()
    allm["scenario"] = allm["scenario"].astype(str).str.strip().str.lower()
    high = allm[allm["condition"] == "high"].copy()

    depth = pd.read_csv(DEPTH)
    depth = depth[depth["response_id"].notna()].copy()
    depth["response_id"] = depth["response_id"].astype(str).str.strip()
    depth["scenario"] = depth["scenario"].astype(str).str.strip().str.lower()
    depth["block"] = depth["coder"].map(
        {"both": "double", "sharon": "solo_sharon", "jeevan": "solo_jeevan"})
    depth = depth[["response_id", "scenario", "depth", "block"]].drop_duplicates(
        subset=["response_id", "scenario"])

    d = high.merge(depth, on=["response_id", "scenario"], how="inner")
    print(f"conversational rows: {len(high)}  with a depth code: {len(d)} "
          f"({d[['response_id','scenario']].drop_duplicates().shape[0]} conversations, "
          f"{d.response_id.nunique()} participants)")
    return d


def run_family(d, outcome, formula, term, label, n_boot, extra_cols=None):
    rows = []
    for mod in MODALITIES:
        sub = d[d["modality"] == mod].dropna(subset=[outcome, "depth"]).copy()
        if len(sub) < 20 or sub["depth"].nunique() < 2:
            continue
        res = fit_mixedlm(sub, formula)
        est = float(res.params.get(term, np.nan))
        p = float(res.pvalues.get(term, np.nan))

        cat = fit_mixedlm(sub, formula.replace("depth", "C(depth)"))
        p_om = wald_omnibus(cat, [t for t in cat.params.index if t.startswith("C(depth)")])

        lo, hi = cluster_bootstrap_ci(
            sub, lambda b: float(fit_mixedlm(b, formula).params.get(term, np.nan)),
            n_boot=n_boot)

        row = {"outcome": outcome, "spec": label, "modality": mod,
               "n_rows": len(sub), "n_participants": sub["response_id"].nunique(),
               "slope_per_depth_level": est, "ci_low": lo, "ci_high": hi,
               "p_raw": p, "p_omnibus_depth_as_factor": p_om,
               "mean_depth": float(sub["depth"].mean())}
        for c in (extra_cols or []):
            row[c] = float(res.params.get(c, np.nan))
        rows.append(row)

    out = pd.DataFrame(rows)
    if len(out):
        rej, padj, _, _ = multipletests(out["p_raw"].fillna(1.0).values, method="holm", alpha=0.05)
        out["p_holm_across_modalities"] = padj
        out["reject_holm_0.05"] = rej
        # The factor omnibus is corrected on the same family as the slope. Left
        # raw it reads as a finding: theme and stance clear .05 uncorrected,
        # neither survives Holm, and the pattern behind them is non-monotone
        # over cells as small as n=3. Report the corrected column.
        rej_o, padj_o, _, _ = multipletests(
            out["p_omnibus_depth_as_factor"].fillna(1.0).values, method="holm", alpha=0.05)
        out["p_omnibus_holm"] = padj_o
        out["reject_omnibus_holm_0.05"] = rej_o
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-boot", type=int, default=100)
    args = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)

    d = build(args)
    print("\n  depth distribution over analysed rows:",
          d.drop_duplicates(["response_id", "scenario"])["depth"].value_counts().sort_index().to_dict())

    frames = []
    for outcome in ("R", "FF"):
        frames.append(run_family(d, outcome, f"{outcome} ~ depth", "depth",
                                 "main", args.n_boot))
        frames.append(run_family(d, outcome, f"{outcome} ~ depth + C(block)", "depth",
                                 "coder_covariate", args.n_boot,
                                 extra_cols=["C(block)[T.solo_jeevan]",
                                             "C(block)[T.solo_sharon]"]))
        dd = d[d["block"] == "double"]
        frames.append(run_family(dd, outcome, f"{outcome} ~ depth", "depth",
                                 "double_coded_only", args.n_boot))

    res = pd.concat([f for f in frames if len(f)], ignore_index=True)
    path = os.path.join(OUT_DIR, "engagement_depth_models.csv")
    res.to_csv(path, index=False)

    pd.set_option("display.width", 200, "display.max_columns", 50)
    for outcome in ("R", "FF"):
        print(f"\n=== {outcome} ~ depth "
              f"({'directional reliance' if outcome == 'R' else 'revision magnitude'}) ===")
        show = res[res.outcome == outcome][
            ["spec", "modality", "n_rows", "slope_per_depth_level", "ci_low", "ci_high",
             "p_raw", "p_holm_across_modalities", "reject_holm_0.05",
             "p_omnibus_depth_as_factor", "p_omnibus_holm"]]
        print(show.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()
