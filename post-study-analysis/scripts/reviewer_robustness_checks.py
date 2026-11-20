#!/usr/bin/env python3
"""
Robustness checks for the CHI 2027 revision, run on the paper's analysis set
(outputs/directionalR-revisionFF-coded0: depth-0 sessions excluded, after the 2026-11-11 mapping fix).

Same MixedLM spec as the main models (participant random intercept + scenario variance
component, ML). Families as in the paper: DC (R; theme, liwc, stance), RA (R_alt; theme,
liwc, stance), RM (FF; theme, liwc, detail_words, stance). Holm across modalities within
each (check, family, term).

  1  AI exposure   within conversational: y ~ z(log AI words); y ~ z(AI turns)
                   static+conversational:  y ~ conv + z(log AI words)   (condition and exposure collinear)
  2  Depth         within conversational: y ~ depth (0-4 coded engagement depth)
  3  Scenario type y ~ condition * sexism; likelihood-ratio test of the interaction
  4  Demographics  y ~ condition + woman + visible_minority + degree; covariate tests and
                   change in the condition estimate vs the model without covariates

Usage (from post-study-analysis/): python scripts/reviewer_robustness_checks.py [OUTDIR]
Default OUTDIR: outputs/reviewer-robustness-checks/ (gitignored)
"""
import os, sys, warnings, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings("ignore")
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("outputs", "reviewer-robustness-checks")
os.makedirs(out, exist_ok=True)
B = "outputs/directionalR-revisionFF-coded0"
mod = pd.read_csv(f"{B}/all_mod_filtered.csv")
ra = pd.read_csv(f"{B}/rowlevel_alt_reliance_finalAI_minus_firstFinal.csv")
FAM = {"DC": (mod.rename(columns={"R": "y"}), ["theme", "liwc", "stance"], ["low", "high"]),
       "RA": (ra.rename(columns={"R_alt": "y"}), ["theme", "liwc", "stance"], ["low", "high"]),
       "RM": (mod.rename(columns={"FF": "y"}), ["theme", "liwc", "detail_words", "stance"], ["baseline", "low", "high"])}

# exposure (conversational, from chat logs; static = fixed rationale length, 1 turn)
eng = pd.read_csv("data-derived/conversation_engagement_metrics.csv")
mp = pd.read_csv("data-derived/prolific_to_response_mapping.csv")
eng = eng.merge(mp[["prolific_id", "response_id"]], on="prolific_id").rename(columns={"scenario_id": "scenario"})
eng = eng.sort_values("total_ai_words").drop_duplicates(["response_id", "scenario"], keep="last")
# static exposure = length of the static rationale participants saw (47-100 words), as in communication_volume_control.py
det = pd.read_csv("data/comprehensive_detail_lengths2.csv")
static_words = det[det.condition.str.lower() == "low"].groupby("scenario").ai_words.first()
depth = pd.read_csv("data-derived/engagement_depth_resolved.csv")[["response_id", "scenario", "depth"]].drop_duplicates(["response_id", "scenario"])

# demographics
dem = []
for f in ["Baseline", "Low_Interaction", "High_Interaction"]:
    d = pd.read_csv(f"data/H-AI_Subjectivity_Study_{f}_filtered.csv", low_memory=False)
    dem.append(d[["ResponseId", "Q11", "Q13", "Q14"]])
dem = pd.concat(dem).rename(columns={"ResponseId": "response_id"}).drop_duplicates("response_id")
dem["woman"] = (dem.Q11 == "Woman").astype(int)
dem["minority"] = (dem.Q13.astype(str).str.strip() != "Not a visible minority").astype(int)
dem["degree"] = dem.Q14.astype(str).str.contains("Bachelor|Master|Doctor|Professional|Graduate", case=False).astype(int)

def fit(d, formula):
    d = d.copy(); d["response_id"] = d.response_id.astype(str); d["scenario"] = d.scenario.astype(str)
    return smf.mixedlm(formula, d, groups=d.response_id, vc_formula={"scenario": "0 + C(scenario)"},
                       re_formula="1").fit(reml=False, method="lbfgs", maxiter=500, disp=False)
z = lambda s: (s - s.mean()) / s.std()
rows = []
def add(check, fam, m, term, r, n, **kw):
    rows.append(dict(check=check, family=fam, modality=m, term=term, n=n,
                     estimate=r.params.get(term, np.nan), p=r.pvalues.get(term, np.nan), **kw))

for fam, (d0, mods, conds) in FAM.items():
    for m in mods:
        d = d0[(d0.modality == m) & d0.condition.isin(conds)].dropna(subset=["y"]).copy()
        d["conv"] = (d.condition == "high").astype(int)
        d["sexism"] = d.scenario.str.startswith("sexism").astype(int)
        hi = d[d.condition == "high"].merge(eng[["response_id", "scenario", "total_ai_words", "num_ai_turns"]], on=["response_id", "scenario"])
        hi["lw"] = z(np.log(hi.total_ai_words)); hi["turns"] = z(hi.num_ai_turns.astype(float))
        add("1 exposure (within conv)", fam, m, "lw", fit(hi, "y ~ lw"), len(hi))
        add("1 exposure (within conv)", fam, m, "turns", fit(hi, "y ~ turns"), len(hi))
        sl = d[d.condition.isin(["low", "high"])].merge(eng[["response_id", "scenario", "total_ai_words"]], on=["response_id", "scenario"], how="left")
        sl["w"] = np.where(sl.condition == "low", sl.scenario.map(static_words), sl.total_ai_words)
        sl = sl.dropna(subset=["w"]); sl["lw"] = z(np.log(sl.w))
        r0, r1 = fit(sl, "y ~ conv"), fit(sl, "y ~ conv + lw")
        add("1 exposure (joint with condition)", fam, m, "lw", r1, len(sl),
            conv_without=r0.params["conv"], conv_with=r1.params["conv"], p_conv_with=r1.pvalues["conv"])
        hd = d[d.condition == "high"].merge(depth, on=["response_id", "scenario"])
        add("2 depth (within conv)", fam, m, "depth", fit(hd, "y ~ depth"), len(hd))
        cterm = "C(condition, Treatment('low'))"
        rf, rr = fit(d, f"y ~ {cterm} * sexism"), fit(d, f"y ~ {cterm} + sexism")
        lr = 2 * (rf.llf - rr.llf); dfree = len(rf.params) - len(rr.params)
        rows.append(dict(check="3 scenario type x condition", family=fam, modality=m, term="interaction (LR test)", n=len(d),
                         estimate=rf.params.get(f"{cterm}[T.high]:sexism", np.nan), p=stats.chi2.sf(lr, dfree),
                         conv_static_in_aita=rf.params.get(f"{cterm}[T.high]", np.nan)))
        dd = d.merge(dem[["response_id", "woman", "minority", "degree"]], on="response_id")
        r0, r1 = fit(dd, f"y ~ {cterm}"), fit(dd, f"y ~ {cterm} + woman + minority + degree")
        for t in ["woman", "minority", "degree"]:
            add("4 demographics", fam, m, t, r1, len(dd),
                conv_without=r0.params[f"{cterm}[T.high]"], conv_with=r1.params[f"{cterm}[T.high]"],
                p_conv_with=r1.pvalues[f"{cterm}[T.high]"])
res = pd.DataFrame(rows)
res["p_holm"] = res.groupby(["check", "family", "term"]).p.transform(lambda p: multipletests(p, method="holm")[1])
res.to_csv(f"{out}/reviewer_robustness_checks.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(res.round(4).to_string(index=False))
