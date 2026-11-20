#!/usr/bin/env python3
"""
Initial agreement as a moderator (CHI 2027 revision, reviewer R3-4).

Does the static-vs-conversational effect depend on whether the participant
already agreed with the AI's verdict before seeing it? Participants who agreed
cannot move toward the AI in stance, so the condition effect could differ.

Each AI-condition trial is coded agree = 1 if the initial stance matched the
AI's verdict for that scenario (an initial "it depends" counts as not
matching). For directional change (DC = R), relative alignment (RA = R_alt)
and revision magnitude (RM = FF) we refit the static-vs-conversational model
with a condition x agreement interaction, using the main analysis's MixedLM
spec (participant random intercept + scenario variance component, ML), and
Holm-correct the interaction and agreement tests within each family.

Model-based p-values only; cluster-bootstrap CIs are in
initial_agreement_bootstrap.py.

Usage (from post-study-analysis/):
    python scripts/initial_agreement_moderator.py [OUTDIR]
Default OUTDIR: outputs/initial-agreement-moderator/  (gitignored)
"""
import os, sys, warnings, pandas as pd, numpy as np, statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("outputs", "initial-agreement-moderator")
os.makedirs(out, exist_ok=True)
B = "outputs/directionalR-revisionFF-coded0"
mod = pd.read_csv(f"{B}/all_mod_filtered.csv")
ra = pd.read_csv(f"{B}/rowlevel_alt_reliance_finalAI_minus_firstFinal.csv")
st = pd.read_csv("data/comprehensive_stance_file.csv")

def norm(v):
    v = str(v).lower()
    if "depend" in v: return "depends"
    if v.startswith("no") or "not sexist" in v: return "no"
    if v.startswith("yes") or "is sexist" in v: return "yes"
    return None
ai = st.dropna(subset=["ai_stance_final_norm"]).groupby("scenario").ai_stance_final_norm.first()
st["init"] = st.stance_first.map(norm)
st["agree"] = (st.init == st.scenario.map(ai)).astype(int)
st = st[st.init.notna()][["response_id", "scenario", "agree"]]

def fit(d, formula):
    d = d.copy(); d["response_id"] = d.response_id.astype(str); d["scenario"] = d.scenario.astype(str)
    m = smf.mixedlm(formula, d, groups=d.response_id, vc_formula={"scenario": "0 + C(scenario)"}, re_formula="1")
    return m.fit(reml=False, method="lbfgs", maxiter=300, disp=False)

rows = []
fams = [("DC", mod[mod.condition.isin(["low", "high"])].rename(columns={"R": "y"}), ["theme", "liwc", "stance"]),
        ("RA", ra[ra.condition.isin(["low", "high"])].rename(columns={"R_alt": "y"}), ["theme", "liwc", "stance"]),
        ("RM", mod[mod.condition.isin(["low", "high"])].rename(columns={"FF": "y"}), ["theme", "liwc", "detail_words", "stance"])]
for fam, d0, mods in fams:
    for m in mods:
        d = d0[d0.modality == m].merge(st, on=["response_id", "scenario"]).dropna(subset=["y"])
        d["conv"] = (d.condition == "high").astype(int)
        r = fit(d, "y ~ conv * agree")
        cell = d.groupby(["conv", "agree"]).y.agg(["mean", "size"])
        rows.append(dict(family=fam, modality=m, n=len(d),
            conv_effect_if_disagree=r.params["conv"], p_conv=r.pvalues["conv"],
            agree_effect=r.params["agree"], p_agree=r.pvalues["agree"],
            interaction=r.params["conv:agree"], p_interaction=r.pvalues["conv:agree"],
            mean_static_notagree=cell.loc[(0, 0), "mean"], mean_static_agree=cell.loc[(0, 1), "mean"],
            mean_conv_notagree=cell.loc[(1, 0), "mean"], mean_conv_agree=cell.loc[(1, 1), "mean"],
            n_static_notagree=cell.loc[(0, 0), "size"], n_static_agree=cell.loc[(0, 1), "size"],
            n_conv_notagree=cell.loc[(1, 0), "size"], n_conv_agree=cell.loc[(1, 1), "size"]))
res = pd.DataFrame(rows)
for col in ["p_interaction", "p_agree"]:
    res[col + "_holm"] = np.nan
    for fam in res.family.unique():
        i = res.family == fam
        res.loc[i, col + "_holm"] = multipletests(res.loc[i, col], method="holm")[1]
res.to_csv(f"{out}/initial_agreement_moderator.csv", index=False)
pd.set_option("display.width", 250)
print(res[["family", "modality", "n", "conv_effect_if_disagree", "p_conv", "agree_effect", "p_agree_holm", "interaction", "p_interaction", "p_interaction_holm"]].round(4).to_string(index=False))
print(res[["family", "modality", "mean_static_notagree", "mean_static_agree", "mean_conv_notagree", "mean_conv_agree", "n_static_notagree", "n_static_agree", "n_conv_notagree", "n_conv_agree"]].round(3).to_string(index=False))
