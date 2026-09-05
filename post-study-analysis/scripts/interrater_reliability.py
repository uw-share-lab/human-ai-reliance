#!/usr/bin/env python3
"""
Inter-rater reliability for the engagement-depth coding sheet.

Reports Cohen's kappa three ways, because on an ordinal rubric the unweighted
figure alone is misleading in a specific direction:

  UNWEIGHTED   All-or-nothing. A 3-vs-4 disagreement is scored exactly as badly
               as a 0-vs-4. This is the conservative number and the one most
               readers assume when they see "Cohen's kappa" unqualified.

  LINEAR       Partial credit proportional to distance: w = 1 - |i-j|/R.

  QUADRATIC    Partial credit falling off with the square of the distance:
               w = 1 - ((i-j)/R)^2. A one-point miss on a 0-4 scale still earns
               93.8% credit. Equivalent to the ICC under standard assumptions.
               This is the most generous of the three, so choosing it *after*
               seeing an unweighted result you did not like is a post-hoc
               decision a reviewer can fairly challenge. Decide up front.

Weighting raises observed AND chance agreement together, so weighted kappa is
not simply "kappa but bigger" — the chance correction rises to match.

The weight matrix depends on the scale range R, so R is taken from the whole
file rather than the selected window. Otherwise a window that happens to
contain no 0s would silently be scored on a different scale than its
neighbours and the windows would not be comparable.

Also reported, because a single kappa hides both of them:

  - exact and within-one agreement (a rubric whose every disagreement is one
    point apart is in a very different state from one with the same kappa and
    scattered large misses)
  - a sign test on the direction of disagreements, which detects whether one
    coder is systematically more lenient. Symmetric noise mostly cancels in
    downstream scores; a systematic offset biases every one of them.
  - rows only one coder scored, listed rather than silently dropped.

The input file is opened READ-ONLY and is never written back. Do not add a
save path: the coding workbook has formatting that openpyxl does not round-trip.

Usage:
  python scripts/interrater_reliability.py coding/full_coding_sheet.xlsx
  python scripts/interrater_reliability.py <path> --last 40
  python scripts/interrater_reliability.py <path> --rows 69-108 --threshold 0.7
  python scripts/interrater_reliability.py <path.csv> --coders "Coder A" "Coder B"

Writes outputs/interrater-reliability/.
"""

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd

OUT_DIR = os.path.join("outputs", "interrater-reliability")
DEFAULT_SHEET = "Coding"
DEFAULT_ID_COL = "#"
CODER_COL_PATTERN = re.compile(r"preliminary\s+code", re.I)


# ---------------------------------------------------------------- loading

def load_table(path, sheet):
    """Read the coding sheet. Read-only; the source file is never modified."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm", ".xls"):
        # read_only + data_only: no write handle, formulas resolved to values.
        return pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    if ext == ".csv":
        return pd.read_csv(path)
    raise SystemExit(f"Unsupported file type {ext!r}; expected .xlsx or .csv")


def resolve_coder_cols(df, explicit):
    if explicit:
        missing = [c for c in explicit if c not in df.columns]
        if missing:
            raise SystemExit(f"Column(s) not found: {missing}\nAvailable: {list(df.columns)}")
        return list(explicit)
    found = [c for c in df.columns if CODER_COL_PATTERN.search(str(c))]
    if len(found) != 2:
        raise SystemExit(
            f"Auto-detection found {len(found)} column(s) matching 'preliminary code': "
            f"{found}\nPass --coders \"<col A>\" \"<col B>\" explicitly.\n"
            f"Available: {list(df.columns)}"
        )
    return found


def is_blank(v):
    """True for an empty cell. pandas reads blanks as NaN, whose str() is the
    truthy string 'nan', so a plain truthiness test flags every empty cell."""
    if v is None:
        return True
    if isinstance(v, float) and np.isnan(v):
        return True
    return not str(v).strip()


def to_code(v):
    """Coerce a cell to an integer code, or None if it is not one."""
    if is_blank(v):
        return None
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return int(v) if float(v).is_integer() else None
    s = str(v).strip()
    if not s:
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return int(f) if f.is_integer() else None


def extract(df, id_col, coder_cols):
    """Return (paired rows, partially-coded rows, uncodeable cells)."""
    a_col, b_col = coder_cols
    paired, partial, junk = [], [], []
    for _, row in df.iterrows():
        rid = to_code(row.get(id_col))
        if rid is None:
            continue
        raw_a, raw_b = row.get(a_col), row.get(b_col)
        a, b = to_code(raw_a), to_code(raw_b)
        if a is not None and b is not None:
            paired.append((rid, a, b))
            continue
        # Distinguish "blank" from "there is something here we could not read".
        for raw, code, who in ((raw_a, a, a_col), (raw_b, b, b_col)):
            if code is None and not is_blank(raw):
                junk.append((rid, who, raw))
        if (a is None) != (b is None):
            partial.append((rid, a, b))
    return paired, partial, junk


# ---------------------------------------------------------------- kappa

def weight_fn(mode, lo, hi):
    R = hi - lo
    if R <= 0 or mode == "unweighted":
        return lambda i, j: float(i == j)
    if mode == "linear":
        return lambda i, j: 1.0 - abs(i - j) / R
    if mode == "quadratic":
        return lambda i, j: 1.0 - ((i - j) / R) ** 2
    raise ValueError(mode)


def kappa(pairs, mode, lo, hi):
    """Return (kappa, Po, Pe). pairs is a list of (a, b) code tuples."""
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    w = weight_fn(mode, lo, hi)
    cats = list(range(lo, hi + 1))
    a = [x[0] for x in pairs]
    b = [x[1] for x in pairs]
    ca = {c: a.count(c) / n for c in cats}
    cb = {c: b.count(c) / n for c in cats}
    po = sum(w(x, y) for x, y in zip(a, b)) / n
    pe = sum(w(i, j) * ca[i] * cb[j] for i in cats for j in cats)
    if np.isclose(pe, 1.0):
        # Every rating fell in one category: kappa is undefined, not 1.0.
        return float("nan"), po, pe
    return (po - pe) / (1.0 - pe), po, pe


def kappa_se_fleiss(pairs, lo, hi):
    """Asymptotic SE of UNWEIGHTED kappa (Fleiss, Cohen & Everitt 1969).

    Large-sample approximation; at n<50 treat it as indicative and prefer the
    bootstrap interval, which makes no normality assumption.
    """
    n = len(pairs)
    if n < 2:
        return float("nan")
    cats = list(range(lo, hi + 1))
    k, po, pe = kappa(pairs, "unweighted", lo, hi)
    if not np.isfinite(k) or np.isclose(pe, 1.0):
        return float("nan")
    p = {(i, j): 0.0 for i in cats for j in cats}
    for x, y in pairs:
        p[(x, y)] += 1.0 / n
    row = {i: sum(p[(i, j)] for j in cats) for i in cats}   # coder A marginals
    col = {j: sum(p[(i, j)] for i in cats) for j in cats}   # coder B marginals
    A = sum(p[(i, i)] * (1 - (row[i] + col[i]) * (1 - k)) ** 2 for i in cats)
    B = (1 - k) ** 2 * sum(
        p[(i, j)] * (col[i] + row[j]) ** 2
        for i in cats for j in cats if i != j
    )
    C = (k - pe * (1 - k)) ** 2
    var = (A + B - C) / (n * (1 - pe) ** 2)
    return float(np.sqrt(var)) if var > 0 else float("nan")


def bootstrap_ci(pairs, mode, lo, hi, reps, rng):
    """Percentile bootstrap CI, resampling rows with replacement."""
    n = len(pairs)
    if n < 2 or reps <= 0:
        return float("nan"), float("nan")
    arr = np.array(pairs)
    stats = []
    for _ in range(reps):
        idx = rng.integers(0, n, n)
        k, _, _ = kappa([tuple(x) for x in arr[idx]], mode, lo, hi)
        if np.isfinite(k):
            stats.append(k)
    if len(stats) < reps * 0.5:
        # Mostly degenerate resamples (e.g. a window with one category).
        return float("nan"), float("nan")
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def sign_test(diffs):
    """Two-sided exact binomial on disagreement direction. Returns (n+, n-, p)."""
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    m = pos + neg
    if m == 0:
        return 0, 0, float("nan")
    from math import comb
    k = min(pos, neg)
    tail = sum(comb(m, i) for i in range(0, k + 1)) / (2 ** m)
    return pos, neg, min(1.0, 2 * tail)


# ---------------------------------------------------------------- windowing

def select_window(paired, args):
    """Apply --rows / --exclude-first / --last, in that order."""
    rows = list(paired)
    label = "all double-coded rows"
    if args.rows:
        m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", args.rows)
        if not m:
            raise SystemExit("--rows expects a range like 69-108")
        a, b = int(m.group(1)), int(m.group(2))
        rows = [r for r in rows if a <= r[0] <= b]
        label = f"rows {a}-{b}"
    if args.exclude_first:
        rows = [r for r in rows if r[0] > args.exclude_first]
        label = f"{label}, excluding ids <= {args.exclude_first}"
    if args.last:
        rows = sorted(rows, key=lambda r: r[0])[-args.last:]
        label = f"last {args.last} double-coded rows"
    return rows, label


# ---------------------------------------------------------------- reporting

def short_name(col, fallback):
    """First word of a coder column name, for compact tables."""
    parts = re.split(r"[\s_]+", str(col).strip())
    return parts[0] if parts and parts[0] else fallback


def confusion(pairs, lo, hi, short):
    cats = list(range(lo, hi + 1))
    m = pd.DataFrame(0, index=cats, columns=cats)
    for a, b in pairs:
        m.loc[a, b] += 1
    m.index.name = f"{short[0]}\\{short[1]}"
    return m


def report(rows, label, lo, hi, names, args, rng):
    L = []
    add = L.append
    n = len(rows)
    add(f"=== {label} ===")
    if n == 0:
        add("  no double-coded rows in this window")
        return "\n".join(L), None
    ids = [r[0] for r in rows]
    pairs = [(r[1], r[2]) for r in rows]
    add(f"  n = {n}   (ids {min(ids)}-{max(ids)})   scale {lo}-{hi}")

    exact = sum(1 for a, b in pairs if a == b)
    within1 = sum(1 for a, b in pairs if abs(a - b) <= 1)
    add(f"  exact agreement    {exact}/{n} = {exact/n:.1%}")
    add(f"  within 1 point     {within1}/{n} = {within1/n:.1%}")
    add("")

    res = {}
    add(f"  {'scheme':<11} {'Po':>7} {'Pe':>7} {'kappa':>7}   95% CI (bootstrap)")
    for mode in ("unweighted", "linear", "quadratic"):
        k, po, pe = kappa(pairs, mode, lo, hi)
        ci = bootstrap_ci(pairs, mode, lo, hi, args.boot, rng)
        res[mode] = dict(kappa=k, po=po, pe=pe, ci_lo=ci[0], ci_hi=ci[1])
        ci_s = "n/a" if not np.isfinite(ci[0]) else f"{ci[0]:.3f} to {ci[1]:.3f}"
        add(f"  {mode:<11} {po:>7.4f} {pe:>7.4f} {k:>7.3f}   {ci_s}")
    se = kappa_se_fleiss(pairs, lo, hi)
    if np.isfinite(se):
        k = res["unweighted"]["kappa"]
        add(f"  unweighted analytic SE {se:.3f} (Fleiss)  ->  "
            f"{k - 1.96*se:.3f} to {k + 1.96*se:.3f}")
        res["unweighted"]["se_fleiss"] = se
    add("")

    if args.threshold is not None:
        t = args.threshold
        k = res["unweighted"]["kappa"]
        lo_ci = res["unweighted"]["ci_lo"]
        verdict = "PASS" if k > t else "FAIL"
        add(f"  threshold {t}: unweighted kappa = {k:.3f} -> {verdict}")
        if np.isfinite(lo_ci) and k > t and lo_ci < t:
            add(f"    caution: the CI lower bound ({lo_ci:.3f}) is below {t}, so this")
            add(f"    passes on the point estimate but is not a firm claim at n={n}.")
        add("")

    short = (short_name(names[0], "A"), short_name(names[1], "B"))
    diffs = [a - b for a, b in pairs if a != b]
    pos, neg, p = sign_test(diffs)
    add(f"  disagreements: {len(diffs)}")
    if diffs:
        spread = pd.Series([abs(d) for d in diffs]).value_counts().sort_index()
        add("    by size:  " + ", ".join(f"{int(d)} pt x{c}" for d, c in spread.items()))
        add(f"    direction: {short[0]} higher x{pos}, {short[1]} higher x{neg}"
            f"   sign test p = {p:.3f}")
        if np.isfinite(p) and p < 0.05:
            add("    ^ asymmetric: one coder is systematically higher. A constant offset")
            add("      biases every downstream score, unlike symmetric noise.")
        add("    rows: " + ", ".join(
            f"{r}:{a}/{b}" for r, a, b in rows if a != b))
    add("")
    add(f"  confusion matrix (rows = {short[0]}, cols = {short[1]}):")
    for line in confusion(pairs, lo, hi, short).to_string().splitlines():
        add("    " + line)

    flat = dict(window=label, n=n, id_min=min(ids), id_max=max(ids),
                exact=exact, exact_pct=exact / n, within1=within1,
                within1_pct=within1 / n, n_disagreements=len(diffs),
                sign_pos=pos, sign_neg=neg, sign_p=p)
    for mode, d in res.items():
        for key, val in d.items():
            flat[f"{mode}_{key}"] = val
    return "\n".join(L), flat


def main():
    ap = argparse.ArgumentParser(
        description="Cohen's kappa (unweighted / linear / quadratic) for a coding sheet.")
    ap.add_argument("path", help="path to the coding sheet (.xlsx or .csv)")
    ap.add_argument("--sheet", default=DEFAULT_SHEET, help=f"xlsx sheet (default: {DEFAULT_SHEET})")
    ap.add_argument("--id-col", default=DEFAULT_ID_COL, help=f"row id column (default: {DEFAULT_ID_COL})")
    ap.add_argument("--coders", nargs=2, metavar=("COL_A", "COL_B"),
                    help="the two code columns (default: auto-detect '* preliminary code')")
    ap.add_argument("--rows", help="restrict to an id range, e.g. 69-108")
    ap.add_argument("--exclude-first", type=int, metavar="N", help="drop rows with id <= N")
    ap.add_argument("--last", type=int, metavar="N", help="use only the last N double-coded rows")
    ap.add_argument("--scale", nargs=2, type=int, metavar=("MIN", "MAX"),
                    help="rubric range for the weight matrix (default: observed across the file)")
    ap.add_argument("--threshold", type=float, default=0.70,
                    help="pass/fail threshold on unweighted kappa (default: 0.70)")
    ap.add_argument("--boot", type=int, default=5000, help="bootstrap reps (default: 5000; 0 to skip)")
    ap.add_argument("--seed", type=int, default=20260905, help="bootstrap seed")
    ap.add_argument("--out", default=OUT_DIR, help=f"output dir (default: {OUT_DIR})")
    ap.add_argument("--no-write", action="store_true", help="print only, write nothing")
    ap.add_argument("--compare", action="store_true",
                    help="also report every 'last N' window in steps of 10, to show stability")
    args = ap.parse_args()

    df = load_table(args.path, args.sheet)
    coder_cols = resolve_coder_cols(df, args.coders)
    if args.id_col not in df.columns:
        raise SystemExit(f"id column {args.id_col!r} not found. Available: {list(df.columns)}")

    paired, partial, junk = extract(df, args.id_col, coder_cols)
    if not paired:
        raise SystemExit("No rows have codes from both coders.")

    # Scale from the whole file, not the window, so windows stay comparable.
    if args.scale:
        lo, hi = args.scale
    else:
        allc = [c for _, a, b in paired for c in (a, b)]
        lo, hi = min(allc), max(allc)

    head = []
    head.append(f"file          {args.path}")
    head.append(f"coders        {coder_cols[0]!r}  vs  {coder_cols[1]!r}")
    head.append(f"double-coded  {len(paired)} rows (ids {paired[0][0]}-{paired[-1][0]})")
    head.append(f"scale         {lo}-{hi}" + ("  (from --scale)" if args.scale else "  (observed)"))
    ids = sorted(r[0] for r in paired)
    gaps = [i for i in range(ids[0], ids[-1] + 1) if i not in set(ids)]
    if gaps:
        head.append(f"gaps          ids in range with no pair: {gaps}")
    if partial:
        head.append(f"partial       {len(partial)} row(s) coded by only one coder, excluded: "
                    + ", ".join(str(r[0]) for r in partial))
    if junk:
        shown = ", ".join(f"id {r} [{c}]={v!r}" for r, c, v in junk[:10])
        more = f" (+{len(junk) - 10} more)" if len(junk) > 10 else ""
        head.append(f"unreadable    {len(junk)} cell(s) present but not numeric: {shown}{more}")
    header = "\n".join(head)
    print(header + "\n")

    rng = np.random.default_rng(args.seed)
    windows = []
    rows, label = select_window(paired, args)
    windows.append((rows, label))
    if args.compare:
        total = len(paired)
        for n in range(10, total + 1, 10):
            windows.append((sorted(paired, key=lambda r: r[0])[-n:], f"last {n}"))
        windows.append((sorted(paired, key=lambda r: r[0]), f"all {total}"))

    chunks, flats = [], []
    for rows, label in windows:
        text, flat = report(rows, label, lo, hi, coder_cols, args, rng)
        print(text + "\n")
        chunks.append(text)
        if flat:
            flats.append(flat)

    if args.no_write:
        return
    os.makedirs(args.out, exist_ok=True)
    txt = os.path.join(args.out, "interrater_reliability.txt")
    csv = os.path.join(args.out, "interrater_reliability.csv")
    open(txt, "w").write(header + "\n\n" + "\n\n".join(chunks) + "\n")
    pd.DataFrame(flats).to_csv(csv, index=False)
    print("Outputs →", args.out)


if __name__ == "__main__":
    sys.exit(main())
