#!/usr/bin/env python3
"""
Resolve the hand-coded engagement-depth values and key them to the analysis.

The coding workbook holds four candidate codes per conversation: Sharon's
preliminary code, Jeevan's preliminary code, a reconciled Final code, and
nothing at all. Which one is authoritative depends on how the row was coded:

  rows #1-128    double-coded by both. A Final code was recorded only where
                 reconciliation had something to settle -- every row with a
                 blank Final is a row where the two preliminary codes are
                 IDENTICAL, so the blank is not missing work and the code is
                 unambiguous. (Verified: all 65 blank-Final rows have S == J.)
  rows #129-186  Sharon only.
  rows #187-254  Jeevan only.

Resolution order, therefore:  Final -> S if S == J -> whichever coder filled in.
A double-coded row with no Final and S != J would be a genuine unreconciled
conflict; none exist today, and the script fails loudly rather than guessing
if one ever appears.

Two data hazards this script handles rather than papers over:

  Excel scientific notation. The sheet stores an 8-character conversation_id
  prefix. A prefix like "282386e7" is a valid float literal, so Excel silently
  stored row #241 as the number 2823860000000 (= 282386e7). The repair is
  driven off the real conversation ids, never hardcoded: any numeric cell is
  matched back to the <mantissa>e<exponent> id that produces it.

  Coder calibration. The two solo blocks are not interchangeable at the top of
  the scale -- against the jointly-coded block's 6.2% 4s, Sharon's 58 rows have
  0% and Jeevan's 68 have 10.3%. The `coder` column is carried through so
  downstream models can absorb that as a covariate; it is not a nuisance to be
  dropped.

The workbook is opened READ-ONLY and never written back: it carries threaded
comments, a VML drawing and a sensitivity label that openpyxl does not
round-trip, and a load/save cycle has corrupted it before.

Usage:
  python scripts/engagement_depth_codes.py "<path to Full Coding Sheet.xlsx>"
  python scripts/engagement_depth_codes.py <path> --exclude-at 1

Writes data-derived/engagement_depth_resolved.csv and, for each --exclude-at
threshold, data-derived/exclude_depth<=N.csv in the same (prolific_id,
scenario_id) shape the notebook's Cell 3b already consumes.
"""

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd

SHEET = "Coding"
COL_N, COL_CID, COL_SCEN = "#", "conversation_id", "scenario"
COL_S, COL_J, COL_F = "Sharon preliminary code", "Jeevan preliminary code", "Final code"

DERIVED = "data-derived"
METRICS = os.path.join(DERIVED, "conversation_engagement_metrics.csv")
OUT_RESOLVED = os.path.join(DERIVED, "engagement_depth_resolved.csv")


def to_code(v):
    """Coerce a cell to an integer code, or None if it is not one."""
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return int(f) if float(f).is_integer() else None


def repair_prefix(raw, known_prefixes):
    """Undo Excel's scientific-notation coercion of a conversation-id prefix.

    Excel stores "282386e7" as the number 2823860000000. Rather than hardcode
    that one row, rebuild the mapping from the real ids: for every known prefix
    shaped <digits>e<digits>, compute the float Excel would have produced and
    match the cell against it.
    """
    s = str(raw).strip()
    if s in known_prefixes:
        return s
    try:
        val = float(s)
    except ValueError:
        return s
    for p in known_prefixes:
        if re.fullmatch(r"\d+e\d+", p, flags=re.I):
            try:
                if float(p) == val:
                    return p
            except ValueError:
                continue
    return s


def resolve(row):
    """Return (depth, provenance, coder) for one sheet row.

    Reads the three code cells through _blank() rather than testing `is None`:
    a column of ints and Nones lands in pandas as float64, so every empty cell
    arrives as NaN -- and `NaN is not None` is True, which would silently make
    every row look reconciled.
    """
    def _blank(v):
        return v is None or (isinstance(v, float) and np.isnan(v)) or pd.isna(v)

    s = None if _blank(row[COL_S]) else int(row[COL_S])
    j = None if _blank(row[COL_J]) else int(row[COL_J])
    f = None if _blank(row[COL_F]) else int(row[COL_F])
    if f is not None:
        return f, "final", "both"
    if s is not None and j is not None:
        if s == j:
            return s, "agree", "both"
        return None, "CONFLICT", "both"
    if s is not None:
        return s, "solo_sharon", "sharon"
    if j is not None:
        return j, "solo_jeevan", "jeevan"
    return None, "uncoded", None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workbook", help="path to Full Coding Sheet.xlsx (read only)")
    ap.add_argument("--sheet", default=SHEET)
    ap.add_argument("--exclude-at", type=int, nargs="*", default=[0, 1],
                    help="write an exclusion list for every conversation coded <= N")
    ap.add_argument("--metrics", default=METRICS,
                    help="conversation metrics CSV supplying conversation_id/prolific_id")
    args = ap.parse_args()

    if not os.path.exists(args.workbook):
        raise SystemExit(f"No such workbook: {args.workbook}")

    df = pd.read_excel(args.workbook, sheet_name=args.sheet, engine="openpyxl")
    missing = [c for c in (COL_N, COL_CID, COL_SCEN, COL_S, COL_J, COL_F) if c not in df.columns]
    if missing:
        raise SystemExit(f"Coding sheet missing column(s): {missing}\nFound: {list(df.columns)}")

    df = df[df[COL_N].notna()].copy()
    for c in (COL_S, COL_J, COL_F):
        df[c] = df[c].map(to_code)
    df[COL_N] = df[COL_N].astype(float).astype(int)
    df[COL_SCEN] = df[COL_SCEN].astype(str).str.strip().str.lower()

    # --- key repair -------------------------------------------------------
    metrics = pd.read_csv(args.metrics)
    metrics["prefix"] = metrics["conversation_id"].astype(str).str[:8]
    known = set(metrics["prefix"])
    df["prefix"] = df[COL_CID].map(lambda v: repair_prefix(v, known))

    repaired = df[df[COL_CID].astype(str).str.strip() != df["prefix"]]
    for _, r in repaired.iterrows():
        print(f"  repaired Excel-coerced id: row #{r[COL_N]}  "
              f"{str(r[COL_CID]).strip()} -> {r['prefix']}")
    # The sheet's own conversation_id holds only the 8-char prefix and would
    # collide with the full id coming from the metrics file on merge.
    df = df.rename(columns={COL_CID: "cid_raw"})

    # --- resolve ----------------------------------------------------------
    res = df.apply(resolve, axis=1, result_type="expand")
    df["depth"], df["provenance"], df["coder"] = res[0], res[1], res[2]

    conflicts = df[df["provenance"] == "CONFLICT"]
    if len(conflicts):
        raise SystemExit(
            f"{len(conflicts)} double-coded row(s) disagree with no Final code recorded:\n"
            f"{conflicts[[COL_N, COL_S, COL_J]].to_string(index=False)}\n"
            "Reconcile these in the workbook before running the analysis."
        )
    uncoded = df[df["provenance"] == "uncoded"]
    if len(uncoded):
        print(f"  WARNING: {len(uncoded)} row(s) carry no code at all: "
              f"{list(uncoded[COL_N])}")

    # --- attach analysis keys --------------------------------------------
    out = df.merge(
        metrics[["prefix", "conversation_id", "prolific_id", "scenario_id"]],
        on="prefix", how="left",
    )
    unmatched = out[out["conversation_id"].isna()]
    if len(unmatched):
        raise SystemExit(
            f"{len(unmatched)} coded row(s) have no conversation in {args.metrics}: "
            f"{list(unmatched[COL_N])}"
        )
    bad_scen = out[out[COL_SCEN] != out["scenario_id"].astype(str).str.lower()]
    if len(bad_scen):
        raise SystemExit(f"Scenario mismatch on row(s) {list(bad_scen[COL_N])} — "
                         "the id repair produced a wrong join.")

    mapping_path = os.path.join(DERIVED, "prolific_to_response_mapping.csv")
    mapping = pd.read_csv(mapping_path)
    mapping["prolific_id"] = mapping["prolific_id"].astype(str).str.strip()
    out["prolific_id"] = out["prolific_id"].astype(str).str.strip()
    out = out.merge(mapping[["prolific_id", "response_id"]], on="prolific_id", how="left")

    out = out.rename(columns={COL_N: "row", COL_SCEN: "scenario"})
    out = out[["row", "conversation_id", "prolific_id", "response_id", "scenario",
               "depth", "provenance", "coder", COL_S, COL_J, COL_F]]
    os.makedirs(DERIVED, exist_ok=True)
    out.to_csv(OUT_RESOLVED, index=False)

    n_resp = out["response_id"].notna().sum()
    print(f"\nResolved {out['depth'].notna().sum()}/{len(out)} codes -> {OUT_RESOLVED}")
    print(f"  provenance : {out['provenance'].value_counts().to_dict()}")
    print(f"  depth dist : {out['depth'].value_counts().sort_index().to_dict()}")
    print(f"  keyed to a Qualtrics response_id: {n_resp}/{len(out)} "
          f"({len(out) - n_resp} had no survey response)")

    print("\n  depth distribution by coding block (calibration check):")
    for label, sub in [("double-coded #1-128", out[out.coder == "both"]),
                       ("Sharon solo", out[out.coder == "sharon"]),
                       ("Jeevan solo", out[out.coder == "jeevan"])]:
        n = len(sub)
        if not n:
            continue
        pct = " ".join(f"{k}:{(sub.depth == k).sum():3d}({100 * (sub.depth == k).mean():4.1f}%)"
                       for k in range(5))
        print(f"    {label:22s} n={n:3d}  {pct}")

    for thr in args.exclude_at:
        excl = out[out["depth"] <= thr][["prolific_id", "scenario"]].copy()
        excl = excl.rename(columns={"scenario": "scenario_id"}).drop_duplicates()
        path = os.path.join(DERIVED, f"exclude_depth{thr}.csv")
        excl.to_csv(path, index=False)
        print(f"\n  depth <= {thr}: {len(excl)} conversation(s) -> {path}")


if __name__ == "__main__":
    main()
