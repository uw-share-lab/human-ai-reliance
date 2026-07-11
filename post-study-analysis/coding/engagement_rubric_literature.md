# Literature support for the depth-of-engagement rubric (v0)

Sources from HCI / human-AI interaction / learning sciences that back each element of
`engagement_rubric_v0.md`. Organized by rubric component; each entry says what it supports.

---

## 1. The 0–4 ordinal depth scale itself

**Chi & Wylie (2014). The ICAP Framework: Linking Cognitive Engagement to Active Learning Outcomes. *Educational Psychologist*.**
https://www.tandfonline.com/doi/abs/10.1080/00461520.2014.965823 · [PDF](https://education.asu.edu/sites/g/files/litvpz656/files/lcl/chiwylie2014icap_2.pdf)
The strongest anchor for the whole scale. ICAP orders overt engagement behaviors as
Passive < Active < Constructive < Interactive, with the hypothesis (and meta-analytic support)
that outcomes improve monotonically along the ordering. Our levels map almost one-to-one:
Level 1 passive assent ≈ Passive; Level 2 minimal/reactive ≈ Active; Level 3 substantive
reasoning (generating one's own justification beyond the given material) ≈ Constructive;
Level 4 deep/dialogic (co-constructing through genuine turn exchange) ≈ Interactive.
Crucially, ICAP defines Interactive as requiring *both* constructive contributions *and*
mutual turn-taking — which is exactly our 3-vs-4 boundary and independently justifies the
"deep monologue = 3, not 4" call. Recently applied to GenAI use, e.g.
[Sun et al. 2024, *Int. J. Management Education*](https://www.sciencedirect.com/science/article/abs/pii/S1472811724000296).

**Fleck & Fitzpatrick (2010). Reflecting on reflection: framing a design landscape. *OzCHI*.**
Widely used in HCI (e.g. [CHI 2022 review of reflection in personal informatics](https://dl.acm.org/doi/fullHtml/10.1145/3491102.3501991); [Chalmers overview PDF](https://research.chalmers.se/publication/529987/file/529987_Fulltext.pdf))
An HCI precedent for exactly our methodological move: an ordinal 5-level coding scheme
(R0 description → R4 critical reflection) applied to open-text/behavioral data, with each level
building on the last. Good citation both for the ordinal-rubric method and for the
Reflection/uncertainty sub-tag (their R2 "dialogic reflection" ≈ our weighing-of-sides).

## 2. Why turns/words are not enough (quantity ≠ depth)

**Buçinca, Malaya & Gajos (2021). To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI. *CSCW*.**
https://dl.acm.org/doi/10.1145/3449287 · [arXiv](https://arxiv.org/abs/2102.09692)
Core argument: people rarely engage *analytically* with AI recommendations even when nominally
interacting with them — they use heuristics. Engagement is a cognitive property, not a
behavioral count; interventions must be judged by whether they induce analytic processing.
Directly motivates a depth measure that goes beyond automatic turn/word metrics.

**Gajos & Mamykina (2022). Do People Engage Cognitively with AI? Impact of AI Assistance on Incidental Learning. *IUI*.**
https://dl.acm.org/doi/10.1145/3490099.3511138 · [PDF](https://www.eecs.harvard.edu/~kgajos/papers/2022/gajos2022people.pdf)
Shows that merely being exposed to AI advice/explanations produces no learning; gains appear
only when people *critically process* the explanation. Empirical demonstration that exposure
(≈ words seen) and cognitive engagement dissociate — the same dissociation our
high-turn/shallow vs. 1-turn/deep anchors show.

**Petty & Cacioppo — Elaboration Likelihood Model; Need for Cognition.**
[ELM overview](https://en.wikipedia.org/wiki/Elaboration_likelihood_model) · applied to automation bias in AI-based selection: [Kupfer et al. 2023, *Frontiers in Psychology*](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2023.1118723/full)
Dual-process grounding: central (elaborated) vs. peripheral (heuristic) processing of the same
message length. Two 20-word replies can sit on different routes — the theoretical reason a
rubric must code *content*, not volume. NFC also moderates engagement with AI explanations
(Buçinca et al. 2021; Gajos & Mamykina 2022), supporting individual-differences framing.

## 3. Level 4 (dialogic) and the Responsiveness sub-tag

**Demszky et al. (2021). Measuring Conversational Uptake: A Case Study on Student-Teacher Interactions. *ACL*.**
https://aclanthology.org/2021.acl-long.130/ · [arXiv](https://arxiv.org/abs/2106.03873)
"Uptake" = building on the interlocutor's prior contribution (acknowledging, reformulating,
extending), annotated by experts and linked to better outcomes. This is precisely our
Responsiveness tag (0 ignores AI · 2 builds on AI prompts), and precedent for later
LLM-assisted scaling of the coding.

**On Selective, Mutable and Dialogic XAI (CHI 2023).**
https://dl.acm.org/doi/10.1145/3544548.3581314
Frames *dialogic* explanation — progressive, contingent, two-way — as qualitatively distinct
from one-shot explanation. Supports treating genuine dialogue (Level 4) as a different kind of
engagement rather than "more" engagement.

**Beyond One-Shot Explanations: A Systematic Literature Review of Dialogue-Based XAI (2024). *AI Review*.**
https://link.springer.com/article/10.1007/s10462-024-11007-7
Positions multi-turn explanatory dialogue against static explanation; useful related-work
citation for why our high-interactivity condition and its depth measure matter.

**Is Conversational XAI All You Need? (IUI 2025).**
https://dl.acm.org/doi/abs/10.1145/3708359.3712133
Recent empirical human-AI decision-making study with a conversational XAI assistant; users who
engaged more deeply with specific questions showed the largest understanding gains — engagement
*quality* mediating outcomes.

## 4. Criticality-toward-AI sub-tag

**Chiang, Lu, Li & Yin (2024). Enhancing AI-Assisted Group Decision Making through LLM-Powered Devil's Advocate. *IUI*.**
https://dl.acm.org/doi/10.1145/3640543.3645199
Challenging/disagreeing with the AI reduces overreliance — evidence that our Criticality tag
(0 defers · 2 challenges) captures a behavior with known consequences for reliance, i.e. the
outcome we want depth to predict.

**Schemmer et al. (2023). Appropriate Reliance on AI Advice: Conceptualization and the Effect of Explanations. *IUI*.**
https://dl.acm.org/doi/10.1145/3581641.3584066 · [arXiv](https://arxiv.org/pdf/2302.02187)
Conceptualizes appropriate reliance as requiring the human to *evaluate* AI advice rather than
accept or reject wholesale. Links the criticality/elaboration tags to the paper's reliance DVs.

**Lee et al. (2025). The Impact of Generative AI on Critical Thinking. *CHI*.**
https://dl.acm.org/doi/full/10.1145/3706598.3713778
Knowledge workers' confidence in GenAI is associated with *less* critical thinking; critical
engagement (verifying, questioning output) is the active ingredient. Motivates measuring
critical engagement specifically in conversational AI use.

## 5. Level 0 (invalid) and the Validity sub-tag

**Prolific researcher guidance on low-effort responses** — [Who should I reject?](https://researcher-help.prolific.com/en/article/f75ea9) · [Improving data quality](https://www.prolific.com/resources/how-to-improve-your-data-quality)
Gibberish/few-word answers to open-ended prompts are standard, platform-sanctioned exclusion
criteria — supports treating pasted-ID/gibberish (Level 0) as invalid data (and ties to the
Task 2 non-engager filter).

**Data Quality in Online Crowdsourced Surveys (2023). *Survey Practice*.**
https://www.surveypractice.org/article/160218-data-quality-in-online-crowdsourced-surveys-methodological-challenges-and-analytic-insights-in-survey-research
Open-ended response quality as a screening indicator; methodological citation for the
exclusion decision.

## 6. Elaboration sub-tag / Level 3 (constructive reasoning)

Covered by ICAP's Constructive mode (self-generated inferences beyond given material — Chi &
Wylie 2014, §1) and by Gajos & Mamykina 2022 (§2): generating one's own conclusion from
explanations is what produced learning. Cognitive forcing works *because* it induces
elaboration (Buçinca et al. 2021, §2; see also
[Cognitive Forcing Through Partial Explanations, PACM HCI 2025](https://dl.acm.org/doi/10.1145/3710946)).

---

## Suggested framing sentence for the paper

> Our depth scale follows the ICAP framework's ordering of cognitive engagement
> (passive → active → constructive → interactive; Chi & Wylie, 2014), adapted to human-AI
> deliberation: it distinguishes passive assent, reactive response, self-generated reasoning,
> and genuinely dialogic exchange, while sub-codes for uptake (Demszky et al., 2021),
> criticality (Chiang et al., 2024), and reflection (Fleck & Fitzpatrick, 2010) capture
> dimensions that automatic turn- and word-counts miss (Buçinca et al., 2021;
> Gajos & Mamykina, 2022).

## Gaps / verify before citing
- Fleck & Fitzpatrick (2010) original OzCHI paper: fetch the DOI (10.1145/1952222.1952269) to confirm details.
- Check the docs folder lit review (`docs/Empirical Studies of Human–AI Decision-Making (CHI 2024–2025).docx`) — several of its CHI 2024/25 reliance studies are complementary for the reliance DV side, though none code engagement depth qualitatively (which is our contribution/novelty claim).
- Verify page numbers / venue details in ACM DL before camera-ready; links above were retrieved 2026-07-08.
