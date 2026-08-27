# Methods additions — scenario-paste exclusion and communication-volume control

Drop-in text for the paper's Methods, plus the model specifications actually run.
All numbers below are produced by the scripts in `post-study-analysis/scripts/`
and are reproducible with the commands at the end of this file.

---

## 1. Refining the non-engagement exclusion: pasted scenarios

### Methods text

> **Non-engagement exclusions.** Participants in the high-interactivity condition
> were excluded from a given scenario if they contributed fewer than two
> conversational turns *and* fewer than 20 words to that session. Inspecting the
> transcripts revealed that this rule could be satisfied vacuously: some
> participants opened the exchange by pasting the scenario prompt back into the
> chat window rather than writing anything of their own, which inflated both
> turn and word counts without constituting engagement. We therefore identified
> and removed such messages before applying the criterion. A user message was
> classified as a scenario paste when, after Unicode normalisation, case folding
> and punctuation stripping, its longest contiguous overlap with the scenario
> prompt covered at least 80% of the message *and* at least 60% of the prompt —
> that is, the message consisted of essentially nothing but the prompt, rather
> than quoting it inside the participant's own reasoning. The two conditions
> together distinguish a bare paste from a substantive reply that happens to
> quote or to echo a stock phrase.
>
> This flagged 25 of 674 user messages (3.7%), contributed by 10 of 64
> high-interactivity participants across 23 sessions, and removed 1,805 user
> words. The classification is unambiguous: flagged messages had message-level
> overlap of 0.94–1.00, while the next-highest unflagged message scored 0.68, so
> any cutoff between 0.70 and 0.90 yields the same set. Re-applying the
> engagement criterion after removal excluded 5 additional participant×scenario
> sessions (24 → 29), reducing the analysis sample from 4,870 to 4,850
> observations and the high-interactivity condition from 467 to 462
> participant×scenario units. No participant was lost entirely.

### Sensitivity result (for a Results or Appendix footnote)

> **Robustness to the paste exclusion.** All models were re-estimated on the
> reduced sample. No Holm-corrected decision changed in any family, and no
> significant effect changed sign; estimates moved only in the third decimal or
> beyond. Where the revision-magnitude effects shifted at all they strengthened
> slightly (e.g. detail-length High vs. Baseline *p* = .032 → .026; LIWC High vs.
> Baseline *p* = .00058 → .00037), consistent with the removal of five sessions
> that had been mis-classified as engaged. We report the full-sample results
> throughout and note that they are unchanged under the stricter criterion.

Machine-checkable version of that claim: `outputs/paste_sensitivity_comparison.txt`,
whose verdict line reads *"no Holm decision flips; no significant effect changed
sign"* across 58 compared rows spanning all 12 result tables.

---

## 2. Controlling for level of communication

### The problem

The high-interactivity condition does not add turn-taking alone. Because every
exchange returns another AI reply, it also delivers substantially more AI text
than the low-interactivity condition, in which each participant reads one fixed
statement. Any high-vs-low difference is therefore open to a volume
explanation — participants revised because they *read more*, not because they
*conversed*. The following analyses separate the two.

### Methods text

> **Distinguishing interactivity from information volume.** Because the
> interactive condition necessarily delivers more model-generated text than the
> single-statement condition, a difference between them could reflect the
> quantity of information received rather than the act of interacting. We
> quantified and then controlled for this in four steps.
>
> *Exposure.* For each participant×scenario unit we computed the number of
> AI-generated words the participant read. In the low-interactivity condition
> this is the length of the fixed AI statement for that scenario (*M* = 57.6,
> *SD* = 3.4 words); in the high-interactivity condition it is that statement
> plus every follow-up reply in the session (*M* = 271.6, *SD* = 106.3). The
> conditions are thus badly unmatched on volume — a 4.5× difference in medians
> (260 vs. 58 words), *U* = 100,300, *p* < .001 — confirming that the confound
> is real and large enough to require treatment.
>
> *Volume as a covariate.* Refitting the condition effect with log AI-word
> exposure entered as a covariate is uninformative here, because exposure is
> nearly a deterministic function of condition (*r* = .95). As expected under
> near-collinearity, the condition coefficient inflates rather than attenuates.
> We report this specification as a diagnostic only, and base inference on the
> two designs below.
>
> *Decomposing exposure.* Within the high-interactivity condition, total
> exposure factorises as (number of exchanges) × (AI words per exchange). These
> two components are only weakly correlated (*r* = .07, VIF = 1.01, against
> VIF = 5.5 for turns vs. total words), so they can be entered simultaneously
> and raced against one another: does the outcome track how *often* a
> participant engaged, or how *much text* each engagement returned? We fitted
> `outcome ~ z(log exchanges) + z(log AI words per exchange)` with the same
> random-effects structure as the main models. Neither component predicted any
> of the seven outcome×modality combinations (all *p* ≥ .13 for exchanges, all
> *p* ≥ .17 for words per exchange). The condition effect is therefore not
> graded in either quantity — more text does not produce more revision, and
> neither does more turn-taking.
>
> *Volume-matched comparison.* Finally we re-estimated the high-vs-low contrast
> using only the least-exposed third of interactive sessions (≤ 221 AI words;
> 72 of 214 sessions with a transcript), narrowing the exposure gap from 260 vs.
> 58 to 188 vs. 58 median words. A volume account predicts the effect should
> shrink as exposure approaches the low condition's. It did not: all four
> revision-magnitude estimates retained at least 80% of their full-sample
> magnitude, and three of four increased (e.g. detail length +5.28 → +7.18;
> LIWC −0.016 → −0.025). Because the tertile restriction retains a third of the
> sessions, the Holm-corrected *p*-values in this subsample are not significant
> (*p* = .077–.088 for the two effects significant in the full sample); the
> point estimates rather than the *p*-values carry the argument.
>
> Taken together, these analyses indicate that what distinguishes the
> interactive condition is that an exchange occurred at all, rather than the
> volume of text it delivered. We note the corresponding limitation: the design
> cannot fully unconfound the two, since interaction cannot be held constant
> while volume varies without changing what interaction means.

### Reported quantities

Figures below are from the `nopaste` arm. The control was also run under
`baseline` and under `none` (the draft's current specification): the verdict is
the same in all three — no volume dose-response, effects preserved at matched
volume. The only cross-arm difference worth noting is that under `none`, stance
revision magnitude does show an exchange-count effect (β = −0.033, *p* = .022)
with no words-per-exchange effect, which points the same way (interactivity, not
volume) but is uncorrected across 14 tests and disappears once non-engagers are
excluded.

| Quantity | Low | High |
|---|---|---|
| AI words read, *M* (*SD*) | 57.6 (3.4) | 271.6 (106.3) |
| Median | 58 | 260 |
| Range | 53–64 | 54–963 |
| Sessions | 472 | 214 (transcript-backed) |

**A note on the high-condition sample.** High-interactivity participants
answered all eight scenarios in Qualtrics but held a chat on a randomised
subset — two AITA and two sexism scenarios for 60 of 64 participants. Outcome
measures were scored only for the chatted scenarios, so the remaining rows carry
no outcome values (8 of 248 are non-empty) and are already dropped by every model
in the main analysis. Restricting the volume analyses to transcript-backed units
therefore matches the estimation sample of the main models rather than narrowing
it.

Within-high decomposition: *r* = .07 between components, VIF = 1.01/1.01,
*n* = 214 sessions; smallest *p* across all outcomes is .129 (exchanges) and
.166 (words per exchange).

Volume-matched contrast (high − low), full sample → matched subsample:

| Outcome | Modality | Full | Matched | *p*<sub>raw</sub> | *p*<sub>Holm</sub> |
|---|---|---|---|---|---|
| FF | theme | −0.0528 | −0.0510 | .137 | .274 |
| FF | liwc | −0.0157 | −0.0245 | .029 | .088 |
| FF | detail_words | +5.278 | +7.176 | .019 | .077 |
| FF | stance | +0.0016 | +0.0099 | .700 | .700 |

---

## 3. Model specifications (the code that was run)

All models use the same random-effects structure as the main analysis: a
participant random intercept with a scenario variance component, ML fit.

```python
def fit_mixedlm(df, formula, group_col="response_id", scenario_col="scenario"):
    d = df.copy()
    d[group_col] = d[group_col].astype(str)
    d[scenario_col] = d[scenario_col].astype(str)
    vc = {"scenario": f"0 + C({scenario_col})"}
    model = smf.mixedlm(formula, d, groups=d[group_col], vc_formula=vc, re_formula="1")
    return model.fit(reml=False, method="lbfgs", maxiter=200, disp=False)
```

**Scenario-paste detection.** Contiguous overlap, not bag-of-words, so that a
short reply sharing vocabulary with the prompt is not mistaken for a paste:

```python
def paste_scores(message, scenario):
    """(share of message that is scenario, share of scenario reproduced)."""
    a, b = normalize(message), normalize(scenario)
    match = difflib.SequenceMatcher(None, a, b).find_longest_match(0, len(a), 0, len(b))
    return match.size / len(a), match.size / len(b)

is_paste = (paste_msg_ratio >= 0.80) & (paste_scenario_ratio >= 0.60)
```

**Exposure measure.** Normalised per exchange rather than per stored AI row,
because three sessions have their AI replies concatenated into a single record:

```python
n_exchanges          = num_user_turns + 1
ai_words             = total_ai_words                  # high condition
ai_words             = bot_opinion_words               # low condition (fixed per scenario)
ai_words_per_exchange = ai_words / n_exchanges
```

**A. Exposure gap.**

```python
st.mannwhitneyu(high_ai_words, low_ai_words, alternative="two-sided")
```

**B. Volume as covariate (diagnostic).**

```python
m0 = fit_mixedlm(sub, "R ~ C(condition, Treatment('low'))")
m1 = fit_mixedlm(sub, "R ~ C(condition, Treatment('low')) + log_ai_words_z")
```

**C. Interactivity vs. volume, within the high condition.**

```python
hi["log_exch_z"] = zscore(np.log(hi["n_exchanges"]))
hi["log_wpe_z"]  = zscore(np.log(hi["ai_words_per_exchange"]))
m = fit_mixedlm(hi_mod, "FF ~ log_exch_z + log_wpe_z")
```

**D. Volume-matched subsample.**

```python
cut     = high_sessions["ai_words"].quantile(1/3)
matched = pd.concat([low_rows, high_rows[high_rows.ai_words <= cut]])
m       = fit_mixedlm(matched_mod, "FF ~ C(condition, Treatment('low'))")
# Holm across modalities within each outcome family, as in the main analysis
```

---

## 4. Reproduction

```bash
cd post-study-analysis

# 1. flag and remove scenario pastes; rebuild metrics + exclusion list
python scripts/scenario_paste_filter.py

# 2. run the main notebook under both exclusion sets
PYTHONHASHSEED=0 HAI_EXCLUSION_MODE=baseline \
  python -m nbconvert --to notebook --execute \
  --output /tmp/_out_baseline.ipynb \
  notebooks/HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb
PYTHONHASHSEED=0 HAI_EXCLUSION_MODE=nopaste \
  python -m nbconvert --to notebook --execute \
  --output /tmp/_out_nopaste.ipynb \
  notebooks/HAI_analysis_directionalR_revisionFF_MLM_bootstrap.ipynb

# 3. diff every result table between the two arms
python scripts/compare_paste_sensitivity.py

# 4. communication-volume control (run under either exclusion set)
python scripts/communication_volume_control.py --mode nopaste
python scripts/communication_volume_control.py --mode baseline
```

Execute the notebook to a path **outside the repository**: its stored outputs
contain Qualtrics ResponseIds, which are deliberately cleared in the committed
copy.

### Known reproducibility issue

The primary family's bootstrap CIs are seeded with
`seed=100 + hash(mod) % 1000`. Python randomises string hashing per process, so
these CIs differ between runs unless `PYTHONHASHSEED` is fixed. Point estimates,
*p*-values and Holm decisions are unaffected. The commands above pin
`PYTHONHASHSEED=0`; a permanent fix is to replace `hash(mod)` with a stable
digest, e.g. `zlib.crc32(mod.encode())`.

---

## 5. Reconciling the paper draft with the analysis code

**Finding: the current draft reports the analysis with no engagement exclusion applied.**

The values in `sections/results.tex` reproduce exactly when the notebook is run
with `HAI_EXCLUSION_MODE=none` — i.e. on `all_mod.csv`, before Cell 3b's
non-engager filter:

| Reported in draft | Paper | `none` | `baseline` (approved filter) | `nopaste` |
|---|---|---|---|---|
| DR theme, est / *p* | +0.004 / .783 | **+0.0044 / .783** | −0.0014 / .932 | −0.0024 / .880 |
| DR language, est / *p* | −0.002 / .815 | **−0.0018 / .815** | −0.0024 / .760 | −0.0016 / .843 |
| DR stance, est / *p* | −0.012 / .520 | **−0.0122 / .520** | −0.0197 / .293 | −0.0196 / .285 |
| RM theme, high vs baseline | −0.089 | **−0.0893** | −0.0918 | −0.0918 |
| RM language, high vs baseline | −0.0285 | **−0.0285** | −0.0299 | −0.0311 |

### What changes if the exclusion is adopted

Applying the approved criterion (`<2` turns AND `<20` words) **adds a
significant finding the draft does not currently report**:

| Result | `none` (draft) | `baseline` | `nopaste` |
|---|---|---|---|
| RM detail-length, omnibus | *p* = .057 (n.s.) | ***p* = .029** | ***p* = .023** |
| RM detail-length, conversational vs static | *p* = .060 (n.s.) | ***p* = .032** | ***p* = .026** |
| RM detail-length, conversational vs baseline | *p* = .060 (n.s.) | ***p* = .032** | ***p* = .026** |

All Holm-corrected. The flip is produced by the **engagement exclusion**; the
scenario-paste filter deepens it but does not cause it. Nothing else in any
family flips: the directional-reliance nulls stay null and the theme/language
revision-magnitude effects stay significant.

Relative alignment (the *d* = −1.30 language result) is essentially unmoved:

| Arm | estimate | *p* | *d* |
|---|---|---|---|
| `none` (draft: −0.076, *d* = −1.30) | −0.0760 | 9.0e−13 | −1.30 |
| `baseline` | −0.0759 | 3.0e−12 | −1.25 |
| `nopaste` | −0.0732 | 2.9e−11 | −1.18 |

**Caveat on that row:** Cell X (alternative reliance / RA) reloads the raw
modality files and never applies the exclusion set, whatever `EXCLUSION_MODE`
is. The numbers above were recomputed by hand with the exclusion applied. If the
exclusion is adopted, Cell X needs to be filtered too.

### Bottom line

- *Does the scenario-paste filter change the paper?* No.
- *Does the engagement exclusion change the paper?* Yes — one new significant
  result, and small updates to the RM and RA figures quoted in the text.

---

## 6. A citable definition of subjective decisions

The cleanest definition comes from a paper first-authored by Sharon Ferguson:

> "a decision is contextual, open to interpretation, and based on one's beliefs
> and values"
>
> — Ferguson, Aoyagui, Kim & Kuzminykh (2024), *Just Like Me: The Role of
> Opinions and Personal Experiences in The Perception of Explanations in
> Subjective Decision-Making.* TREW Workshop, CHI 2024. arXiv:2404.12558

**Not currently in `sample-base.bib`.** Suggested entry:

```bibtex
@inproceedings{ferguson2024justlikeme,
  title     = {Just Like Me: The Role of Opinions and Personal Experiences in
               The Perception of Explanations in Subjective Decision-Making},
  author    = {Ferguson, Sharon and Aoyagui, Paula Akemi and Kim, Young-Ho and
               Kuzminykh, Anastasia},
  booktitle = {Trust and Reliance in Evolving Human-AI Workflows (TREW)
               Workshop at CHI 2024},
  year      = {2024},
  eprint    = {2404.12558},
  archivePrefix = {arXiv},
  primaryClass  = {cs.HC}
}
```

Alternatives already in the bibliography, if a workshop paper is too light a cite:

| Cite key | Quotable characterization |
|---|---|
| `aoyagui2025matter` | "In subjective tasks, the decision is based on contextual interpretation and multiple decision outcomes can be applicable" (CHI '25 — archival, same author group) |
| `schaekermann2020ambiguity` / `inkpen2019human` | "not all decision-making is objective, and often decisions have to be made about nuanced and contextually-dependant scenarios" |
| `lai2021towards` | survey framing of tasks lacking ground truth |
| `MITAMURA2017101` | domain-specific: sexism assessment depends on personal values and gender ideologies |

Suggested composite for the Background's *Subjective Contexts* subsection:

> Following \citet{ferguson2024justlikeme}, we treat a decision as
> \emph{subjective} when it is contextual, open to interpretation, and grounded
> in the decision-maker's beliefs and values, such that multiple outcomes may be
> defensible and no single response can be scored as correct
> \cite{aoyagui2025matter, schaekermann2020ambiguity, lai2021towards}.
