# Engagement depth in the models

Two questions, one new input. The hand-coded engagement-depth rubric (0–4,
254 conversational-condition conversations) enters the analysis in two places:

1. **As an exclusion rule** — replacing the turns/words heuristic with the
   coders' judgement of who did not meaningfully engage, then rerunning the
   whole notebook and diffing.
2. **As a predictor** — asking whether deeper engagement moved rationales
   further, within the conversational condition.

Nothing already on disk was overwritten: each arm writes to its own output
directory, and the pre-existing arms were snapshotted to
`outputs/_archive-2026-09-08/` first.

## Resolving the codes

`scripts/engagement_depth_codes.py` reads the workbook **read-only** and
resolves one code per conversation:

| Rows | Coding | Resolution |
|---|---|---|
| #1–128 | double-coded | `Final code` where present; otherwise the shared preliminary code |
| #129–186 | Sharon only | her column |
| #187–254 | Jeevan only | his column |

The 65 double-coded rows with a blank `Final code` are **not** unfinished
reconciliation — every one of them is a row where the two preliminary codes are
identical, so the blank carries no ambiguity. Final was recorded where
reconciliation had something to settle. A double-coded row that disagreed with
no Final recorded would be a genuine conflict; the script raises rather than
guessing. All 254 rows resolve.

Two hazards the script handles explicitly:

- **Excel scientific notation.** The sheet stores an 8-character
  `conversation_id` prefix. `282386e7` is a valid float literal, so Excel
  silently stored row #241 as `2823860000000`. The repair is derived from the
  real conversation ids rather than hardcoded, and the join is then checked
  against `scenario` so a wrong repair fails loudly.
- **Blank cells are NaN, not None.** A column of ints and blanks arrives from
  pandas as float64, and `NaN is not None` is `True` — testing identity against
  `None` would silently mark every row "reconciled". Resolution goes through an
  explicit blank test.

### Calibration across coding blocks

The blocks do not agree at the top of the scale:

| Block | n | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|---|
| double-coded #1–128 | 128 | 2.3% | 10.9% | 39.8% | 40.6% | **6.2%** |
| Sharon solo #129–186 | 58 | 3.4% | 5.2% | 55.2% | 36.2% | **0.0%** |
| Jeevan solo #187–254 | 68 | 0.0% | 4.4% | 41.2% | 44.1% | **10.3%** |

Against the jointly-coded block, Sharon's solo rows run low and Jeevan's run
high. This barely matters for an exclusion keyed to the bottom of the scale; it
matters directly for a slope, so the block is carried through as a covariate
and the double-coded rows are refit alone as a sensitivity check.

## 1. Depth as the exclusion rule

`HAI_EXCLUSION_MODE=coded`, with `HAI_DEPTH_CUT` choosing the cut:

| Cut | Rubric meaning | Conversations excluded | Output |
|---|---|---|---|
| `0` | "No meaningful moral input at all" | 5 | `outputs/directionalR-revisionFF-coded0` |
| `1` | also "passive assent" | 25 | `outputs/directionalR-revisionFF-coded1` |
| — | *(heuristic, for reference)* `<2` turns AND `<20` words, post-paste | 33 | `outputs/directionalR-revisionFF-nopaste` |

**The rubric explicitly instructs coders to ignore turn and word counts.** The
codes are therefore an independent instrument, not a recalibration of the same
one — which is what makes this rerun informative rather than circular.

The two instruments overlap but do not agree. Of the 33 conversations the
heuristic drops, the coders rated **14 at level 2 or above** — on-topic, and
four of them at level 3, "articulates their own justification". Six
conversations run the other way: coded 0–1, but wordy enough to clear the
heuristic.

### Result

Every conclusion in the paper survives **except one**, and it fails under both
cuts:

| Result | nopaste (reported) | coded ≤0 | coded ≤1 |
|---|---|---|---|
| Detail-length revision magnitude, High vs Low | p = .026 ✔ | p = .061 ✘ | p = .105 ✘ |
| Detail-length revision magnitude, High vs Baseline | p = .026 ✔ | p = .061 ✘ | p = .105 ✘ |
| Detail-length omnibus | p = .023 ✔ | p = .059 ✘ | p = .113 ✘ |

Everything else holds: the theme and LIWC revision-magnitude effects, all
High-vs-Baseline contrasts, the null primary directional-reliance result, the
perceived-reliance models, and every non-parametric sensitivity check. The two
sign flips reported in the diff are on effects that are null in both arms.

The detail-length finding is the one the 2026-08-27 filter decision *added* to
the manuscript, and it is also the one most exposed to this check: its outcome
is a word count and the heuristic exclusion is a word-count rule, so the
heuristic removes short conversations from a length-based outcome. When
non-engagement is judged on content instead, the effect does not reach
significance. This is a specification-dependence worth stating rather than
resolving by picking the arm that keeps it.

Reproduce:

```bash
PYTHONHASHSEED=0 HAI_EXCLUSION_MODE=coded HAI_DEPTH_CUT=0 \
  jupyter nbconvert --to notebook --execute --output <path outside repo> \
  notebooks/HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb

HAI_CMP_BASE=outputs/directionalR-revisionFF-nopaste \
HAI_CMP_OTHER=outputs/directionalR-revisionFF-coded0 \
HAI_CMP_TAG=coded0_vs_nopaste python scripts/compare_paste_sensitivity.py
```

## 2. Depth as a predictor

`scripts/engagement_depth_models.py` fits, on conversational-condition rows
only (240 conversations, 59 participants, 956 rows):

```
R  ~ depth + (1 | participant) + (1 | scenario)
FF ~ depth + (1 | participant) + (1 | scenario)
```

Depth cannot be added to the low-vs-high contrast as a covariate: it is
undefined for a participant who never saw a chat box. This is a
within-condition model, and unlike the randomised condition effect its
estimates are correlational — depth was chosen by the participant.

### Result: no dose-response

Every slope is null, on both outcomes, in all four modalities, under all three
specifications (main, coder covariate, double-coded only). Holm-corrected
p = 1 throughout; every bootstrap CI spans zero.

A Wald omnibus treating depth as an unordered factor is reported alongside, so
a non-monotone pattern cannot hide inside a null slope. It clears .05
uncorrected for theme and stance, but this does not support a finding:

- it does not survive Holm in the pre-specified spec (theme .030 → .121;
  stance .047 → .140);
- the pattern is not monotone — for theme, mean R is *highest* at depth 1
  (0.094), above depths 2, 3 and 4;
- the extreme cells are tiny: n = 3 at depth 0, n = 15 at depth 4.

Read plainly: how deeply a participant engaged does not predict how far their
rationale moved. That is a useful null for the paper's argument — it says the
condition effect is not merely "more engaged people move more."
