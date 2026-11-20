#!/usr/bin/env python3
"""Cluster-bootstrap CIs for the condition x initial-agreement models
(CHI 2027 revision, reviewer R3-4; companion to initial_agreement_moderator.py).
Mirrors the main notebook's cluster_bootstrap_ci: resample participants with
replacement, relabel each draw's clusters, discard singular fits, percentile
intervals. Reports 95% and family-wise (Bonferroni 1 - .05/k, k = family size)
intervals, as the paper does for Holm families.
Seeds use hash(), so run with PYTHONHASHSEED=0 for reproducible intervals
(as for the main notebook). ~25 min for 2000 draws x 10 models on 8 cores.

Usage (from post-study-analysis/):
    PYTHONHASHSEED=0 python scripts/initial_agreement_bootstrap.py [OUTDIR] [N_BOOT]
Default OUTDIR: outputs/initial-agreement-moderator/  (gitignored); N_BOOT 2000.
"""
import os, sys, warnings, time, numpy as np, pandas as pd, statsmodels.formula.api as smf
from joblib import Parallel, delayed
warnings.filterwarnings("ignore")
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("outputs", "initial-agreement-moderator")
os.makedirs(out, exist_ok=True)
N_BOOT = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
B = "outputs/directionalR-revisionFF-coded0"
mod = pd.read_csv(f"{B}/all_mod_filtered.csv")
ra = pd.read_csv(f"{B}/rowlevel_alt_reliance_finalAI_minus_firstFinal.csv")
st = pd.read_csv("data/comprehensive_stance_file.csv")
def norm(v):
    v = str(v).lower()
    if "depend" in v: return "depends"
    if v.startswith("no") or "not sexist" in v: return "no"
    if v.startswith("yes") or "is sexist" in v: return "yes"
ai = st.dropna(subset=["ai_stance_final_norm"]).groupby("scenario").ai_stance_final_norm.first()
st["init"] = st.stance_first.map(norm); st["agree"] = (st.init == st.scenario.map(ai)).astype(int)
st = st[st.init.notna()][["response_id", "scenario", "agree"]]

def fit(d, formula):
    d = d.copy(); d["response_id"] = d.response_id.astype(str); d["scenario"] = d.scenario.astype(str)
    m = smf.mixedlm(formula, d, groups=d.response_id, vc_formula={"scenario": "0 + C(scenario)"}, re_formula="1")
    return m.fit(reml=False, method="lbfgs", maxiter=200, disp=False)
TERMS = ["conv:agree", "agree", "conv"]
def stat(d):
    r = fit(d, "y ~ conv * agree"); return [float(r.params[t]) for t in TERMS]

def cluster_boot(df, n_boot, seed):
    rng = np.random.default_rng(seed); clusters = df.response_id.dropna().unique()
    cg = {c: df[df.response_id == c] for c in clusters}; seeds = rng.integers(0, 2**31, size=n_boot)
    def one(s):
        r = np.random.default_rng(s); samp = r.choice(clusters, size=len(clusters), replace=True)
        parts = []
        for i, c in enumerate(samp):
            ch = cg[c].copy(); ch["response_id"] = f"_b{i}"; parts.append(ch)
        try: return stat(pd.concat(parts, ignore_index=True))
        except Exception: return [np.nan] * len(TERMS)
    return np.asarray(Parallel(n_jobs=-1)(delayed(one)(s) for s in seeds), dtype=float)

fams = [("DC", mod.rename(columns={"R": "y"}), ["theme", "liwc", "stance"]),
        ("RA", ra.rename(columns={"R_alt": "y"}), ["theme", "liwc", "stance"]),
        ("RM", mod.rename(columns={"FF": "y"}), ["theme", "liwc", "detail_words", "stance"])]
rows = []
for fam, d0, mods in fams:
    k = len(mods); a = 0.05 / k
    for m in mods:
        t0 = time.time()
        d = d0[(d0.modality == m) & d0.condition.isin(["low", "high"])].merge(st, on=["response_id", "scenario"]).dropna(subset=["y"])
        d["conv"] = (d.condition == "high").astype(int)
        est = stat(d)
        v = cluster_boot(d, N_BOOT, 100 + hash(fam + m) % 1000)
        ok = np.isfinite(v).all(axis=1); g = v[ok]
        row = dict(family=fam, modality=m, n=len(d), n_boot=N_BOOT, n_discarded=int((~ok).sum()), fw_level=1 - a)
        for j, t in enumerate(TERMS):
            nm = {"conv:agree": "interaction", "agree": "agree", "conv": "conv_if_notagree"}[t]
            row[nm] = est[j]
            row[nm + "_ci95_lo"], row[nm + "_ci95_hi"] = np.percentile(g[:, j], [2.5, 97.5])
            row[nm + "_cifw_lo"], row[nm + "_cifw_hi"] = np.percentile(g[:, j], [100 * a / 2, 100 * (1 - a / 2)])
        rows.append(row); print(f"{fam} {m}: {time.time()-t0:.0f}s, discarded {row['n_discarded']}", flush=True)
        pd.DataFrame(rows).to_csv(f"{out}/initial_agreement_bootstrap.csv", index=False)
print("done")
