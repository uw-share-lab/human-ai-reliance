"""
Task 3 — Engagement variables as predictors in the reliance / revision models.

Reviewer concern: "high-interactivity" participants who barely interacted may be
diluting the conversational condition. Task 2 addressed this by EXCLUDING non-engagers.
Task 3 addresses it a second, complementary way: MODEL engagement continuously and ask
whether the condition effects survive / whether engagement itself predicts reliance.

Engagement predictors (AI-side, per Sharon's spec), built for every (participant, scenario):
    ai_turns  : baseline = 0,  static/low = 1,  high = num_ai_turns   (from conversation logs)
    ai_words  : baseline = 0,  static/low = per-scenario explanation length,
                high = total_ai_words (cumulative conversation, from conversation logs)

Sources
    reliance/revision outcomes : data/comprehensive_{theme,language,detail,stance}*.csv
        R  (directional reliance) = move toward AI  (low & high only; baseline has no AI)
        FF (revision magnitude)   = |first -> final| change  (all three conditions)
    high engagement            : data-derived/conversation_engagement_metrics.csv
                                 (keyed prolific_id -> response_id via prolific_to_response_mapping.csv)
    static explanation length  : detail file low-condition `ai_words` (constant per scenario)

Three specifications (Q2 = "all three, compare"), each run for ai_words and ai_turns SEPARATELY:
    A  within-high        : outcome ~ engagement            (high only; cleanest, no collinearity)
    B  exposure continuum : outcome ~ engagement            (replaces condition with the dose)
    C  joint              : outcome ~ C(condition) + engagement   (Sharon's literal ask; + collinearity/VIF caveat)

Random-effects structure matches the main notebook: random participant intercept +
scenario variance component. Holm correction is applied across the 4 (or 3) modalities
within each (spec, outcome, predictor) family.

NOTE: uses UNFILTERED data (all high observations incl. low-engagers) — modeling engagement
continuously is the alternative to excluding them, so their full range is wanted here.

Outputs -> outputs/engagement-predictors/
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "outputs" / "engagement-predictors"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------------------
# 1. Load outcomes and reconstruct R / FF exactly as the main notebook (Cell 3)
# --------------------------------------------------------------------------------------
def norm_keys(df):
    df = df.copy()
    for c in ["condition", "response_id", "scenario"]:
        df[c] = df[c].astype(str).str.strip()
    df["condition"] = df["condition"].str.lower()
    df["scenario"] = df["scenario"].str.lower()
    return df

theme = norm_keys(pd.read_csv(BASE / "data/comprehensive_theme_file2.csv", low_memory=False))
liwc = norm_keys(pd.read_csv(BASE / "data/comprehensive_language_file2.csv", low_memory=False))
detail = norm_keys(pd.read_csv(BASE / "data/comprehensive_detail_lengths2.csv", low_memory=False))
stance = norm_keys(pd.read_csv(BASE / "data/comprehensive_stance_file.csv", low_memory=False))

theme["R"] = theme["cosine_final_ai"] - theme["cosine_first_ai"]
theme["FF"] = theme["cosine_first_final"]

liwc["R"] = liwc["cosine_final_ai_liwc"] - liwc["cosine_first_ai_liwc"]
liwc["FF"] = liwc["cosine_first_final_liwc"]

detail["R"] = detail["dist_words_first_ai"] - detail["dist_words_final_ai"]
detail["FF"] = detail["delta_words_first_final"].abs()

# stance (same normalization as notebook)
def norm_stance(x):
    if pd.isna(x):
        return np.nan
    t = str(x).strip().lower()
    if "depend" in t or "unsure" in t or "maybe" in t:
        return "depends"
    if t.startswith("y"):
        return "yes"
    if t.startswith("n"):
        return "no"
    return "depends"

ai_col = next(c for c in ["ai_stance_final_norm", "ai_stance", "ai_stance_norm", "ai_stance_norm_final"] if c in stance.columns)
first_col = "stance_first" if "stance_first" in stance.columns else "first_stance"
final_col = "stance_final" if "stance_final" in stance.columns else "final_stance"
mp_num = {"no": 0.0, "depends": 0.5, "yes": 1.0}
sf = stance[first_col].apply(norm_stance).map(mp_num)
sl = stance[final_col].apply(norm_stance).map(mp_num)
sa = stance[ai_col].apply(norm_stance).map(mp_num)
stance["R"] = (sf - sa).abs() - (sl - sa).abs()
stance["FF"] = (sl - sf).abs()

MODS = {"theme": theme, "liwc": liwc, "detail_words": detail, "stance": stance}
long = []
for name, df in MODS.items():
    m = df[["response_id", "scenario", "condition", "R", "FF"]].copy()
    m["modality"] = name
    long.append(m)
all_mod = pd.concat(long, ignore_index=True)

# --------------------------------------------------------------------------------------
# 2. Build the engagement predictors (ai_turns, ai_words) for every observation
# --------------------------------------------------------------------------------------
# static explanation length = low-condition ai_words (verified constant per scenario)
static_words = (detail[detail.condition == "low"]
                .groupby("scenario")["ai_words"].first().to_dict())

# high engagement from conversation logs
eng = pd.read_csv(BASE / "data-derived" / "conversation_engagement_metrics.csv")
mapdf = pd.read_csv(BASE / "data-derived" / "prolific_to_response_mapping.csv")
eng["prolific_id"] = eng["prolific_id"].astype(str).str.strip()
mapdf["prolific_id"] = mapdf["prolific_id"].astype(str).str.strip()
mapdf["response_id"] = mapdf["response_id"].astype(str).str.strip()
eng = eng.merge(mapdf[["prolific_id", "response_id"]], on="prolific_id", how="left")
eng["scenario"] = eng["scenario_id"].astype(str).str.lower().str.strip()
eng_high = (eng.dropna(subset=["response_id"])
            .drop_duplicates(["response_id", "scenario"])
            [["response_id", "scenario", "num_ai_turns", "total_ai_words"]])

def build_engagement(row):
    cond = row["condition"]
    if cond == "baseline":
        return pd.Series({"ai_turns": 0.0, "ai_words": 0.0})
    if cond == "low":
        return pd.Series({"ai_turns": 1.0, "ai_words": float(static_words.get(row["scenario"], np.nan))})
    return pd.Series({"ai_turns": np.nan, "ai_words": np.nan})  # high filled by merge

all_mod[["ai_turns", "ai_words"]] = all_mod.apply(build_engagement, axis=1)
# fill high from logs
hi_mask = all_mod["condition"] == "high"
merged = all_mod[hi_mask].merge(eng_high, on=["response_id", "scenario"], how="left", suffixes=("", "_log"))
all_mod.loc[hi_mask, "ai_turns"] = merged["num_ai_turns"].values
all_mod.loc[hi_mask, "ai_words"] = merged["total_ai_words"].values

# per-100-words scaling for interpretable coefficients
all_mod["ai_words100"] = all_mod["ai_words"] / 100.0

# coverage report (on real modeled observations only)
cov = []
for out in ["R", "FF"]:
    hi = all_mod[(all_mod.condition == "high") & all_mod[out].notna()]
    cov.append({"outcome": out, "high_obs": len(hi),
                "with_ai_words": int(hi["ai_words"].notna().sum()),
                "pct": round(100 * hi["ai_words"].notna().mean(), 1)})
pd.DataFrame(cov).to_csv(OUT / "engagement_coverage.csv", index=False)
print("Engagement coverage on modeled high obs:")
print(pd.DataFrame(cov).to_string(index=False))

# --------------------------------------------------------------------------------------
# 3. Model fitting helpers
# --------------------------------------------------------------------------------------
def fit(df, formula):
    d = df.copy()
    d["response_id"] = d["response_id"].astype(str)
    d["scenario"] = d["scenario"].astype(str)
    vc = {"scenario": "0 + C(scenario)"}
    m = smf.mixedlm(formula, d, groups=d["response_id"], vc_formula=vc, re_formula="1")
    return m.fit(reml=False, method="lbfgs", maxiter=300, disp=False)

def coef_row(res, term):
    if term not in res.params.index:
        return dict(estimate=np.nan, se=np.nan, ci_low=np.nan, ci_high=np.nan, p_raw=np.nan)
    ci = res.conf_int().loc[term]
    return dict(estimate=float(res.params[term]), se=float(res.bse[term]),
                ci_low=float(ci[0]), ci_high=float(ci[1]), p_raw=float(res.pvalues[term]))

def holm(df, pcol="p_raw"):
    df = df.copy()
    ok = df[pcol].notna()
    padj = np.full(len(df), np.nan)
    if ok.sum():
        _, p, _, _ = multipletests(df.loc[ok, pcol].values, method="holm", alpha=0.05)
        padj[ok.values] = p
    df["p_holm"] = padj
    df["reject_holm_.05"] = df["p_holm"] < 0.05
    return df

# predictor -> model term produced by the formula
PRED = {"ai_words100": "ai_words100", "ai_turns": "ai_turns"}
# R exists only for low & high; FF for all three
OUTCOME_CONDS = {"R": ["low", "high"], "FF": ["baseline", "low", "high"]}

# --------------------------------------------------------------------------------------
# 4. Spec A — within-high regression:  outcome ~ engagement   (high only)
# --------------------------------------------------------------------------------------
rowsA = []
for out in ["R", "FF"]:
    for pname, term in PRED.items():
        for mod in MODS:
            d = all_mod[(all_mod.modality == mod) & (all_mod.condition == "high")]
            d = d.dropna(subset=[out, pname])
            if d["response_id"].nunique() < 5 or d[pname].nunique() < 3:
                continue
            res = fit(d, f"{out} ~ {pname}")
            r = coef_row(res, term)
            r.update(spec="A_within_high", outcome=out, predictor=pname, modality=mod,
                     n_obs=len(d), n_participants=d["response_id"].nunique())
            rowsA.append(r)
A = pd.concat([holm(g) for _, g in pd.DataFrame(rowsA).groupby(["outcome", "predictor"])], ignore_index=True)
A.to_csv(OUT / "specA_within_high.csv", index=False)

# --------------------------------------------------------------------------------------
# 5. Spec B — exposure continuum:  outcome ~ engagement   (all applicable conditions)
# --------------------------------------------------------------------------------------
rowsB = []
for out in ["R", "FF"]:
    conds = OUTCOME_CONDS[out]
    for pname, term in PRED.items():
        for mod in MODS:
            d = all_mod[(all_mod.modality == mod) & (all_mod.condition.isin(conds))]
            d = d.dropna(subset=[out, pname])
            if d["response_id"].nunique() < 5:
                continue
            res = fit(d, f"{out} ~ {pname}")
            r = coef_row(res, term)
            r.update(spec="B_continuum", outcome=out, predictor=pname, modality=mod,
                     conditions="+".join(conds), n_obs=len(d), n_participants=d["response_id"].nunique())
            rowsB.append(r)
B = pd.concat([holm(g) for _, g in pd.DataFrame(rowsB).groupby(["outcome", "predictor"])], ignore_index=True)
B.to_csv(OUT / "specB_continuum.csv", index=False)

# --------------------------------------------------------------------------------------
# 6. Spec C — joint:  outcome ~ C(condition) + engagement   (+ collinearity diagnostics)
# --------------------------------------------------------------------------------------
def condition_engagement_vif(d, pname):
    """Crude collinearity read: R^2 of engagement regressed on condition dummies.
    VIF = 1/(1-R2). High VIF => condition & engagement are near-redundant."""
    dd = d.dropna(subset=[pname]).copy()
    import statsmodels.api as sm
    X = pd.get_dummies(dd["condition"].astype(str), drop_first=True).astype(float)
    X = sm.add_constant(X)
    y = dd[pname].astype(float).values
    try:
        r2 = sm.OLS(y, X).fit().rsquared
        return float(1.0 / (1.0 - r2)) if r2 < 1 else np.inf
    except Exception:
        return np.nan

rowsC = []
for out in ["R", "FF"]:
    conds = OUTCOME_CONDS[out]
    ref = conds[0]
    for pname, term in PRED.items():
        for mod in MODS:
            d = all_mod[(all_mod.modality == mod) & (all_mod.condition.isin(conds))]
            d = d.dropna(subset=[out, pname]).copy()
            if d["response_id"].nunique() < 5:
                continue
            d["condition"] = pd.Categorical(d["condition"], categories=conds, ordered=True)
            res = fit(d, f"{out} ~ C(condition) + {pname}")
            r = coef_row(res, term)  # engagement slope, adjusted for condition
            # condition effect(s) net of engagement
            hi_term = "C(condition)[T.high]"
            r_cond = coef_row(res, hi_term)
            r.update(spec="C_joint", outcome=out, predictor=pname, modality=mod,
                     conditions="+".join(conds), ref_condition=ref,
                     cond_high_estimate=r_cond["estimate"], cond_high_p=r_cond["p_raw"],
                     vif_condition_engagement=condition_engagement_vif(d, pname),
                     n_obs=len(d), n_participants=d["response_id"].nunique())
            rowsC.append(r)
C = pd.concat([holm(g) for _, g in pd.DataFrame(rowsC).groupby(["outcome", "predictor"])], ignore_index=True)
C.to_csv(OUT / "specC_joint.csv", index=False)

# --------------------------------------------------------------------------------------
# 7. Console summary
# --------------------------------------------------------------------------------------
pd.set_option("display.width", 200, "display.max_columns", 30)
show = ["outcome", "predictor", "modality", "estimate", "ci_low", "ci_high", "p_raw", "p_holm", "reject_holm_.05", "n_obs"]
print("\n================  SPEC A — within-high  (outcome ~ engagement, high only)  ================")
print(A[show].round(4).to_string(index=False))
print("\n================  SPEC B — exposure continuum  (outcome ~ engagement)  ================")
print(B[show + ["conditions"]].round(4).to_string(index=False))
print("\n================  SPEC C — joint  (outcome ~ C(condition) + engagement)  ================")
showC = show + ["cond_high_estimate", "cond_high_p", "vif_condition_engagement"]
print(C[showC].round(4).to_string(index=False))
print("\nSaved outputs ->", OUT)
