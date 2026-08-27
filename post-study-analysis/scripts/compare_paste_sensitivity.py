#!/usr/bin/env python3
"""
Side-by-side comparison of the two exclusion arms of the main analysis.

  outputs/directionalR-revisionFF/         — approved filter (<2 turns AND <20 words)
  outputs/directionalR-revisionFF-nopaste/ — same rule after scenario-paste
                                             messages are removed

Both arms come from executing the same notebook with HAI_EXCLUSION_MODE set, so
any difference here is attributable to the exclusion set alone.

The question is not "did the third decimal move" but "does a conclusion in the
paper change" — does a Holm-corrected decision flip, or does a *significant*
effect change sign. A sign flip on an effect that is null in both arms is
reported but is not a conclusion change.

Writes outputs/paste_sensitivity_comparison.{txt,csv}.
"""

import os

import pandas as pd

# Arms default to approved-filter vs paste-filtered; override to compare any two
# exclusion specifications, e.g. the paper's (no exclusion) against either.
BASE = os.environ.get("HAI_CMP_BASE", os.path.join("outputs", "directionalR-revisionFF"))
NOPASTE = os.environ.get("HAI_CMP_OTHER", BASE + "-nopaste")
_TAG = os.environ.get("HAI_CMP_TAG", "paste_sensitivity")
OUT_TXT = os.path.join("outputs", f"{_TAG}_comparison.txt")
OUT_CSV = os.path.join("outputs", f"{_TAG}_comparison.csv")

# (filename, join keys, estimate col, reported p col, Holm decision col)
# Keys must uniquely identify a row in both arms; the merge is validated 1:1 so
# a wrong key raises instead of silently producing a cartesian product.
SPECS = [
    ("primary_directionalR_results.csv", ["modality"],
     "estimate_high_minus_low", "p_holm_family", "reject_holm_0.05"),
    ("secondary_revisionFF_omnibus.csv", ["modality"],
     "coef_high_minus_low", "p_holm_family", "reject_holm_0.05"),
    ("secondary_revisionFF_posthoc_pairwise.csv", ["modality", "contrast"],
     "estimate", "p_holm_within_modality", "reject_holm_0.05"),
    ("sensitivity_finalAI_alignment_omnibus.csv", ["modality"],
     None, "p_holm_across_modalities", "reject_holm_0.05"),
    ("sensitivity_finalAI_alignment_pairwise.csv", ["modality", "contrast"],
     "estimate", "p_holm_across_modalities", "reject_holm_0.05"),
    ("SENS_A_directionalR_MWU.csv", ["modality"],
     None, "p_holm_across_modalities", "reject_holm_0.05"),
    ("SENS_B_relativeAlignment_RA_MWU.csv", ["modality"],
     None, "p_holm_across_modalities", "reject_holm_0.05"),
    ("SENS_C_finalAI_FA_MWU.csv", ["modality"],
     None, "p_holm_across_modalities", "reject_holm_0.05"),
    ("SENS_D1_revisionFF_KW_omnibus.csv", ["modality"],
     None, "p_holm_across_modalities", "reject_holm_0.05"),
    ("SENS_D2_revisionFF_pairwise_MWU.csv", ["modality", "comparison"],
     None, "p_holm_within_modality", "reject_holm_0.05"),
    ("perceived_by_condition_models.csv", ["dv", "model"],
     "estimate_high_minus_low", "p_holm_family", "reject_holm_0.05"),
    ("perceived_by_observedR_models.csv", ["dv", "predictor"],
     "estimate", "p_holm_family", "reject_holm_0.05"),
]

# Below this, a difference is optimiser/bootstrap noise, not a result change.
NOISE = 1e-6
ALPHA = 0.05


def compare(fname, keys, est_col, p_col, dec_col):
    pa, pb = os.path.join(BASE, fname), os.path.join(NOPASTE, fname)
    if not (os.path.exists(pa) and os.path.exists(pb)):
        return None, [f"  (missing in one arm: {fname})"]
    a, b = pd.read_csv(pa), pd.read_csv(pb)

    missing = [k for k in keys if k not in a.columns or k not in b.columns]
    if missing:
        raise KeyError(f"{fname}: join key(s) {missing} not in columns {list(a.columns)}")
    # 1:1 so a non-unique key raises rather than fanning out into false "flips".
    m = a.merge(b, on=keys, suffixes=("_base", "_nop"), validate="one_to_one")

    rows, lines = [], []
    for _, r in m.iterrows():
        label = " / ".join(str(r[k]) for k in keys)
        rec = {"file": fname, "row": label}
        notes, changed = [], False

        p0 = p1 = None
        if p_col and f"{p_col}_base" in m.columns:
            p0, p1 = r[f"{p_col}_base"], r[f"{p_col}_nop"]
            rec.update(p_base=p0, p_nopaste=p1)
            if pd.notna(p0) and pd.notna(p1) and abs(p1 - p0) > NOISE:
                notes.append(f"p {p0:.4g} → {p1:.4g}")

        if est_col and f"{est_col}_base" in m.columns:
            e0, e1 = r[f"{est_col}_base"], r[f"{est_col}_nop"]
            rec.update(estimate_base=e0, estimate_nopaste=e1)
            if pd.notna(e0) and pd.notna(e1) and abs(e1 - e0) > NOISE:
                notes.append(f"est {e0:.5g} → {e1:.5g}")
            if pd.notna(e0) and pd.notna(e1) and (e0 > 0) != (e1 > 0):
                # Only a conclusion change if the effect was ever significant.
                sig = any(p is not None and pd.notna(p) and p < ALPHA for p in (p0, p1))
                if sig:
                    notes.append("** SIGN FLIP on a significant effect **")
                    changed = True
                else:
                    notes.append("sign flip (null in both arms — not a conclusion change)")

        if dec_col and f"{dec_col}_base" in m.columns:
            d0, d1 = bool(r[f"{dec_col}_base"]), bool(r[f"{dec_col}_nop"])
            rec.update(decision_base=d0, decision_nopaste=d1)
            if d0 != d1:
                notes.append(f"** HOLM DECISION FLIP {d0} → {d1} **")
                changed = True

        rec["conclusion_changed"] = changed
        rec["notes"] = "; ".join(notes) if notes else "unchanged"
        rows.append(rec)
        lines.append(f"  {label:<38} {rec['notes']}")
    return pd.DataFrame(rows), lines


def main():
    all_rows, report = [], []
    report.append("Scenario-paste sensitivity — does removing pasted scenarios change any result?")
    report.append("=" * 78)

    a = pd.read_csv(os.path.join(BASE, "all_mod_filtered.csv"))
    b = pd.read_csv(os.path.join(NOPASTE, "all_mod_filtered.csv"))
    ah, bh = a[a.condition == "high"], b[b.condition == "high"]
    report += [
        "",
        "Analysis sample:",
        f"  rows                       : {len(a)} → {len(b)}  ({len(a)-len(b)} removed)",
        f"  high-condition rows        : {len(ah)} → {len(bh)}",
        f"  high participant×scenario  : {ah.groupby(['response_id','scenario']).ngroups}"
        f" → {bh.groupby(['response_id','scenario']).ngroups}",
        f"  high participants retained : {ah.response_id.nunique()} → {bh.response_id.nunique()}",
        "",
    ]

    for spec in SPECS:
        df, lines = compare(*spec)
        report.append(f"--- {spec[0]}")
        report += lines
        report.append("")
        if df is not None:
            all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    flips = combined[combined["conclusion_changed"]] if len(combined) else combined

    report.append("=" * 78)
    if len(flips):
        report.append(f"VERDICT: {len(flips)} row(s) changed a conclusion:")
        for _, r in flips.iterrows():
            report.append(f"  {r['file']} :: {r['row']} :: {r['notes']}")
    else:
        report.append("VERDICT: no Holm decision flips; no significant effect changed sign.")
        report.append("Every reported conclusion is unchanged by the scenario-paste filter.")
        n_moved = int((combined["notes"] != "unchanged").sum()) if len(combined) else 0
        report.append(f"({n_moved} of {len(combined)} rows moved numerically; all stayed on the")
        report.append(" same side of every threshold.)")

    text = "\n".join(report)
    os.makedirs("outputs", exist_ok=True)
    open(OUT_TXT, "w").write(text + "\n")
    if len(combined):
        combined.to_csv(OUT_CSV, index=False)
    print(text)


if __name__ == "__main__":
    main()
