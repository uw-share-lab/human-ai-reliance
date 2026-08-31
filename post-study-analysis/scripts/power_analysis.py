#!/usr/bin/env python3
"""
Simulation-based power analysis for the condition effects.

Closed-form power formulas do not apply here: the design is crossed (each
participant sees several scenarios, each scenario is seen by many participants)
and the models carry a participant random intercept plus a scenario variance
component. Power is therefore simulated from the variance components actually
estimated on the data.

Two questions, which are different and are both worth reporting:

  SENSITIVITY  At the sample size we realised, what is the smallest condition
               effect we had 80% power to detect? This is the honest way to
               report a null: not "there is no effect" but "an effect larger
               than X would probably have been detected".

  REQUIRED N   For an effect the size of the one we observed, how many
               participants per condition would be needed for 80% power?
               For the significant effects this shows whether we were
               adequately powered; for the nulls it shows what a future study
               would need.

Usage:
  python scripts/power_analysis.py [--nsim 400] [--quick]

Writes outputs/power-analysis/.
"""

import argparse
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from joblib import Parallel, delayed

SRC = os.path.join("outputs", "directionalR-revisionFF-nopaste", "all_mod_filtered.csv")
OUT_DIR = os.path.join("outputs", "power-analysis")
ALPHA = 0.05
TARGET_POWER = 0.80

# (outcome, modality, conditions kept for variance estimation, reference level)
# The contrast simulated is always high vs REF. The paper's significant
# revision-magnitude results are high vs baseline, not high vs low, so both
# contrasts are simulated.
TARGETS = [
    ("R", "theme", ["low", "high"], "low"),
    ("R", "liwc", ["low", "high"], "low"),
    ("R", "stance", ["low", "high"], "low"),
    ("FF", "theme", ["low", "high", "baseline"], "low"),
    ("FF", "liwc", ["low", "high", "baseline"], "low"),
    ("FF", "detail_words", ["low", "high", "baseline"], "low"),
    ("FF", "theme", ["low", "high", "baseline"], "baseline"),
    ("FF", "liwc", ["low", "high", "baseline"], "baseline"),
    ("FF", "detail_words", ["low", "high", "baseline"], "baseline"),
]


def fit_mixed(d, formula, reml=True):
    d = d.copy()
    d["response_id"] = d["response_id"].astype(str)
    d["scenario"] = d["scenario"].astype(str)
    return smf.mixedlm(formula, d, groups=d["response_id"],
                       vc_formula={"scenario": "0 + C(scenario)"}, re_formula="1") \
              .fit(reml=reml, method="lbfgs", maxiter=300, disp=False)


def design_facts(d):
    """Realised structure: participants per condition and scenarios per participant."""
    per_cond = d.groupby("condition")["response_id"].nunique().to_dict()
    k = int(round(d.groupby("response_id")["scenario"].nunique().median()))
    return per_cond, max(k, 1)


def simulate_once(seed, n_per_cond, k, conditions, scenarios, delta,
                  ppt_sd, scen_sd, resid_sd, ref="low"):
    """One synthetic dataset -> p-value for the high-vs-low contrast."""
    rng = np.random.default_rng(seed)
    scen_eff = rng.normal(0, scen_sd, len(scenarios))
    rows = []
    pid = 0
    for ci, cond in enumerate(conditions):
        for _ in range(n_per_cond):
            pid += 1
            u = rng.normal(0, ppt_sd)
            picks = rng.choice(len(scenarios), size=min(k, len(scenarios)), replace=False)
            for si in picks:
                mu = delta if cond == "high" else 0.0
                rows.append((f"p{pid}", scenarios[si], cond,
                             mu + u + scen_eff[si] + rng.normal(0, resid_sd)))
    d = pd.DataFrame(rows, columns=["response_id", "scenario", "condition", "y"])
    try:
        res = fit_mixed(d, f"y ~ C(condition, Treatment('{ref}'))", reml=False)
        return float(res.pvalues.get(f"C(condition, Treatment('{ref}'))[T.high]", np.nan))
    except Exception:
        return np.nan


def power_at(delta, n_per_cond, k, conditions, scenarios, vc, nsim, seed0, n_jobs, ref="low"):
    ps = Parallel(n_jobs=n_jobs)(
        delayed(simulate_once)(seed0 + i, n_per_cond, k, conditions, scenarios, delta,
                               vc["ppt_sd"], vc["scen_sd"], vc["resid_sd"], ref)
        for i in range(nsim))
    ps = np.array([p for p in ps if np.isfinite(p)])
    if len(ps) == 0:
        return np.nan, 0
    return float((ps < ALPHA).mean()), len(ps)


def bisect_for_power(fn, lo, hi, target=TARGET_POWER, iters=6):
    """Find the smallest x in [lo,hi] with power(x) >= target."""
    plo, phi = fn(lo), fn(hi)
    if not np.isfinite(phi) or phi < target:
        return None, phi
    if plo >= target:
        return lo, plo
    for _ in range(iters):
        mid = (lo + hi) / 2
        pm = fn(mid)
        if pm >= target:
            hi, phi = mid, pm
        else:
            lo, plo = mid, pm
    return hi, phi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nsim", type=int, default=400)
    ap.add_argument("--quick", action="store_true", help="fewer sims, coarse grid")
    ap.add_argument("--n-jobs", type=int, default=-1)
    args = ap.parse_args()
    nsim = 120 if args.quick else args.nsim

    a = pd.read_csv(SRC)
    os.makedirs(OUT_DIR, exist_ok=True)
    lines = ["Simulation-based power analysis", "=" * 70,
             f"simulations per point: {nsim}   alpha = {ALPHA}   target power = {TARGET_POWER:.0%}",
             "Variance components are those estimated on the observed data (REML).", ""]
    rows = []

    for outcome, modality, conds, ref in TARGETS:
        d = a[(a.condition.isin(conds)) & (a.modality == modality)].dropna(subset=[outcome]).copy()
        d = d.rename(columns={outcome: "y"})
        term = f"C(condition, Treatment('{ref}'))[T.high]"
        res = fit_mixed(d, f"y ~ C(condition, Treatment('{ref}'))")
        obs_delta = float(res.params.get(term, np.nan))
        obs_p = float(res.pvalues.get(term, np.nan))

        vc = {"ppt_sd": np.sqrt(max(float(res.cov_re.iloc[0, 0]), 1e-12)),
              "scen_sd": np.sqrt(max(float(res.vcomp[0]) if len(res.vcomp) else 0.0, 1e-12)),
              "resid_sd": np.sqrt(max(float(res.scale), 1e-12))}
        total_sd = np.sqrt(vc["ppt_sd"] ** 2 + vc["scen_sd"] ** 2 + vc["resid_sd"] ** 2)

        per_cond, k = design_facts(d)
        n_real = int(np.floor(np.mean([per_cond.get(c, 0) for c in [ref, "high"]])))
        scenarios = sorted(d["scenario"].unique())
        seed0 = abs(hash((outcome, modality, ref))) % 10_000_000

        lines += [f"--- {outcome} / {modality}   (high vs {ref})",
                  f"  observed effect (high-low) : {obs_delta:+.4f}  (p = {obs_p:.3f})",
                  f"  observed effect in SD units : d = {obs_delta/total_sd:+.3f}",
                  f"  realised n per condition    : {n_real}   scenarios per participant: {k}",
                  f"  SDs  participant {vc['ppt_sd']:.4f} | scenario {vc['scen_sd']:.4f} | residual {vc['resid_sd']:.4f}"]

        # --- Sensitivity: minimum detectable effect at the realised N ---
        f_delta = lambda dl: power_at(dl, n_real, k, [ref, "high"], scenarios, vc,
                                      nsim, seed0, args.n_jobs, ref)[0]
        hi = max(abs(obs_delta) * 6, total_sd * 1.2)
        mde, mde_pow = bisect_for_power(f_delta, 0.0, hi)
        if mde is None:
            lines.append(f"  MDE at n={n_real}          : not reached even at {hi:.4f} "
                         f"(power {mde_pow:.2f})")
        else:
            lines.append(f"  MDE at n={n_real} (80% power) : {mde:.4f}  "
                         f"(d = {mde/total_sd:.3f})")

        # --- Required N for an effect the size of the observed one ---
        # Only meaningful when there is an effect to power for. Powering a study
        # to detect an estimate that is indistinguishable from zero just returns
        # "impossibly many"; for the nulls the MDE above is the informative number.
        need_n = None
        if obs_p < 0.10 and abs(obs_delta) > 1e-9:
            grid = [30, 60, 100, 150, 250, 400, 600, 1000]
            powers = []
            for nn in grid:
                pw, _ = power_at(obs_delta, nn, k, [ref, "high"], scenarios, vc,
                                 nsim, seed0 + 555, args.n_jobs, ref)
                powers.append(pw)
                if pw >= TARGET_POWER:
                    need_n = nn
                    break
            lines.append("  power for the observed effect by n/condition: " +
                         ", ".join(f"{nn}:{pw:.2f}" for nn, pw in zip(grid, powers)))
            lines.append(f"  n per condition needed for 80% power: "
                         f"{need_n if need_n else '>' + str(grid[len(powers)-1])}")
        else:
            lines.append("  (required-N skipped: the estimate is not distinguishable from"
                         " zero, so the MDE above is the informative figure)")
        lines.append("")

        rows.append(dict(outcome=outcome, modality=modality, obs_delta=obs_delta, obs_p=obs_p,
                         reference=ref, obs_d=obs_delta / total_sd,
                         n_realised=n_real, k_scenarios=k,
                         mde=mde, mde_d=(mde / total_sd) if mde else None,
                         n_needed_for_observed=need_n))

    pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "power_analysis.csv"), index=False)
    text = "\n".join(lines)
    open(os.path.join(OUT_DIR, "power_analysis.txt"), "w").write(text + "\n")
    print(text)
    print("Outputs →", OUT_DIR)


if __name__ == "__main__":
    main()
