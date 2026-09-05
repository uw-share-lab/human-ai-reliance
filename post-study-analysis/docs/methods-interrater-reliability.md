# Inter-rater reliability for engagement-depth coding

Reproduction script: [`scripts/interrater_reliability.py`](../scripts/interrater_reliability.py)

Engagement depth is coded by hand on a 0–4 ordinal rubric. Two coders
independently code an overlapping set of conversations so that reliability can
be established before the remaining conversations are split and coded singly.
This document records how that reliability is computed and which decisions in
the computation are consequential.

## Why three kappas

The rubric is **ordinal**, and plain Cohen's kappa ignores that. Unweighted
kappa is all-or-nothing: a 3-vs-4 disagreement is scored exactly as badly as a
0-vs-4. On a scale where the categories are ordered, that throws away most of
what is known about a disagreement.

Weighted kappa assigns partial credit by distance. On the 0–4 scale:

| Codes apart by | Unweighted | Linear | Quadratic |
|---|---|---|---|
| 0 (agree) | 1.000 | 1.000 | 1.000 |
| 1 | 0.000 | 0.750 | 0.938 |
| 2 | 0.000 | 0.500 | 0.750 |
| 3 | 0.000 | 0.250 | 0.438 |
| 4 | 0.000 | 0.000 | 0.000 |

Linear weighting is `w = 1 - |i-j|/R`; quadratic is `w = 1 - ((i-j)/R)^2`,
where `R` is the scale range. Quadratic-weighted kappa is equivalent to the
ICC under standard assumptions.

Weighting is **not** a way to make a number bigger. It raises observed and
chance agreement together, and kappa is `(Po - Pe)/(1 - Pe)`:

```
unweighted   Po=0.8250  Pe=0.3400  ->  0.735
linear       Po=0.9563  Pe=0.7691  ->  0.811
quadratic    Po=0.9891  Pe=0.9012  ->  0.889
```

If near-misses earn partial credit, then two coders guessing at random also
accumulate near-misses, so the bar for "better than chance" rises to match.

Quadratic is the most generous of the three. **Choose the scheme before seeing
the result.** Selecting it after an unweighted figure disappoints is a
post-hoc decision a reviewer can fairly challenge. The script always prints all
three so the choice is visible rather than buried.

## The window is a real methodological choice

Reliability is computed over a *window* of double-coded rows, and the two
coders calibrated the rubric as they went. Early rows therefore agree far less
well than recent ones, and the window boundary moves the answer across the
conventional 0.70 threshold:

| Window | n | Unweighted kappa |
|---|---|---|
| Last 40 double-coded rows (ids 69–108) | 40 | **0.735** |
| All rows after the first 60 (ids 61–108) | 48 | 0.683 |
| Everything (ids 1–108) | 108 | 0.380 |

Because the answer depends on the boundary, the boundary has to be stated and
justified rather than chosen for its result. `--compare` sweeps every window in
steps of 10 and makes the calibration point visible empirically:

```
last 10  0.667     last 50  0.692
last 20  0.767     last 60  0.540
last 30  0.710     last 80  0.512
last 40  0.735     all 108  0.380
```

Reliability is stable in a 0.69–0.77 band across the most recent 20–50 rows and
falls off sharply between "last 50" and "last 60" — the point at which the
window begins reaching back into pre-calibration coding. Reporting *that* is
considerably stronger than asserting a cut without evidence.

**Use `--rows A-B`, not `--last N`, for anything that goes in the paper.**
`--last N` is relative to the file's current state: as coding continues, the
same flag silently designates different rows. `--rows` pins the window.

## What else is reported, and why

A single kappa hides things that matter for deciding whether to split coding:

- **Exact vs. within-one agreement.** A rubric whose every disagreement is one
  point apart is in a very different state from one with the same kappa and
  scattered large misses. In the last-40 window, 7/7 disagreements are one
  point apart, and all 7 sit on the 2↔3 or 3↔4 boundary, which localises the
  remaining ambiguity to a specific part of the rubric — the distinction
  between answering, elaborating, and integrating.
- **A sign test on disagreement direction.** Symmetric noise largely cancels in
  downstream aggregate scores; a systematic offset — one coder consistently
  more lenient — biases every one of them. In the last-40 window the split is
  3 vs. 4 (p = 1.00), i.e. no detectable asymmetry.
- **Confidence intervals.** Both a percentile bootstrap and the Fleiss, Cohen &
  Everitt (1969) asymptotic SE for unweighted kappa. They agree closely
  (at n=108: 0.245–0.515 analytic vs. 0.236–0.509 bootstrap). At n=40 the CI
  is 0.55–0.89: the point estimate clears 0.70 but the interval does not
  exclude values below it, and the script says so explicitly rather than
  reporting a bare PASS.
- **Rows only one coder scored**, listed rather than silently dropped.

## Scale range

The weight matrix depends on the scale range `R`, which is taken from the whole
file rather than from the selected window. A window that happened to contain no
0s would otherwise be scored on a different scale from its neighbours, and the
windows would not be comparable. Override with `--scale MIN MAX` if the rubric
range changes.

## Reproduction

The coding workbook is participant data and is gitignored; obtain it from the
SHARE Lab SharePoint and pass the path directly.

```bash
source .venv/bin/activate

# headline figure for the current double-coded set
python scripts/interrater_reliability.py <path-to-coding-sheet.xlsx> --rows 69-108

# stability of the estimate across window sizes
python scripts/interrater_reliability.py <path-to-coding-sheet.xlsx> --compare

# a sheet whose columns are named differently
python scripts/interrater_reliability.py <path.csv> --coders "Coder A" "Coder B"
```

Columns are auto-detected by matching `* preliminary code`, with `#` as the row
id. Writes `outputs/interrater-reliability/` (gitignored).

The input file is opened **read-only and is never written back**. Do not add a
save path: the coding workbook carries formatting that `openpyxl` does not
round-trip, so a write would silently damage it.

## Status

As of 2026-09-05, with 108 double-coded rows, the last-40 window gives
unweighted kappa = 0.735 (quadratic-weighted 0.889), clearing the 0.70
threshold agreed for splitting the remaining conversations between coders.
The figures above should be regenerated as coding continues.
