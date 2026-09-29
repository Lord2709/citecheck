---
team: CiteCheck
session: 05
date: 2026-09-29
members:
  - name: Vyom
    github: vyom-1908
    hat: Product
  - name: Sakshaat
    github: SakshaatRaut
    hat: Engineering
  - name: Sahil
    github: Lord2709
    hat: Data&Eval
  - name: Ritika
    github: ritikakarande
    hat: Users&Research
north_star:
  metric: "Claim-level macro-F1 on SciFact dev, end-to-end (retrieve, then verify); tau tuned on train"
  value: "0.603 (95% CI 0.545-0.660), from eval/results/zero_shot_nli"
  previous: "not measured (first measurement; the Session 4 report had none)"
---

## Shipped this week
- End-to-end pipeline (claim + cited paper -> SUPPORTS / CONTRADICTS / NOT ENOUGH EVIDENCE with the evidence sentences shown), command line and Streamlit app, merged to `main`  (evidence: PR #12)
- SciFact loader with data card, evaluation harness (macro-F1 with bootstrap CI, false-SUPPORT rate, retrieval recall@k and MRR, abstract-level F1) and a baseline ladder: majority, word-overlap, zero-shot NLI, plus a hybrid-retrieval ablation  (evidence: PR #11; results in `eval/results/`, PR #14)
- User-test kit: protocol, consent script, seeded task stimuli, log anonymizer, evidence summarizer  (evidence: PR #13)
- MVP scope, user stories, north-star definition and the Oct 6 plan  (evidence: PR #10)
- Product is run locally with `streamlit run app/streamlit_app.py`; it is not deployed for outside users yet (planned for Session 7)  (evidence: PR #12)

## User evidence
- None this week: no outside participants have used the running product yet. The user-test kit (protocol, consent script, task stimuli, anonymizer, summarizer) is merged, but `evidence/session05/` contains only its index README, with no task-test results, usage logs or notes.
- What we changed as a result: nothing yet, since there is no user evidence to act on.

## Metrics snapshot
- Claim-level macro-F1: 0.603 (was: not measured), 95% bootstrap CI 0.545-0.660 (`eval/results/zero_shot_nli/results.json`)
- Baselines on the same claims: majority 0.181, word-overlap 0.520. Paired bootstrap of the zero-shot model against each: +0.421 (95% CI +0.359 to +0.482) vs majority and +0.083 (95% CI +0.010 to +0.159) vs word-overlap. Neither CI includes zero, but the lead over word-overlap is small.
- False-SUPPORT rate (safety metric): 0.108 (word-overlap 0.222); retrieval recall@3 0.841, MRR 0.810
- User tests: none run this week (see User evidence)
- Measured on: SciFact dev (300 claims); the abstain threshold tau was tuned on train claims, never on dev
- Is this the same model that is running in the product? Yes: `eval/results/deployed_config.json` (run `zero_shot_nli`) is what the app loads, and its sidebar shows this dev score.

## What did not work
- Our Session 4 BM25 script was tested on an arXiv keyword sample rather than SciFact, so it never connected to the north-star metric; we replaced it this week with a retriever evaluated on SciFact.
- Better retrieval did not give better verdicts: adding dense retrieval (hybrid) raised recall@3 from 0.841 to 0.870 but macro-F1 went from 0.603 to 0.587 (paired 95% CI -0.047 to +0.015, includes zero) and false-SUPPORT rose from 0.108 to 0.148, so we did not ship it. Even when given the gold paper and the gold sentences, the verifier reaches only 0.646: the verifier, not retrieval, is the bottleneck.
- A flaw in our own evaluation: end-to-end retrieval searches all 5,183 abstracts, but SciFact only labels the papers each claim cites. For NEI-labelled claims where our model gave a verdict, 30 of 37 verdicts came from a paper the claim does not cite, and some look correct (e.g. "Statins decrease blood cholesterol" is labelled NEI but supported by another paper in the corpus). The oracle-paper score (0.648) is closer to the product question "does the paper I cite support my claim" than the end-to-end number.
- The DOI lookup can feed the verifier the wrong text: for the SciFact paper's own DOI (10.18653/v1/2020.emnlp-main.609), OpenAlex returned a citation string (authors, venue, year) as the "abstract", so the tool abstained on metadata. The arXiv lookup of the same paper (arXiv:2004.14974) returned the real abstract.

## Challenges / blockers
- The dev set has only 300 claims, so differences smaller than the confidence interval are noise.
- The DOI and arXiv lookups have been tested against the live services once each (2026-09-29). The arXiv lookup worked; the DOI lookup found the right paper but used a citation string instead of the abstract (see above). Pasting an abstract always works.
- Fine-tuning (`eval.finetune_nli`) was not run this week; `eval/README.md` recommends a GPU/Colab, and our runs so far were on a laptop CPU (about 0.5 s per claim for the zero-shot model).
- No user tests have been run yet, so the key assumption (researchers find grounded verdicts useful) is still untested.

## Next week's goal
- Deliver the Oct 6 mid-semester presentation: live demo of the MVP, the real user evidence, our metric against the baseline, and a pivot-or-persevere decision using the rules written in `docs/midterm_oct6.md`.

## Individual contributions
- Vyom (Product): MVP scope, user stories, north-star definition, Oct 6 plan and decision rules  (evidence: PR #10)
- Sakshaat (Engineering): pipeline, CLI, Streamlit app, config that ties the app to the evaluated model, CI, preflight check  (evidence: PR #12)
- Sahil (Data&Eval): SciFact loader and data card, retrieval, verifiers, evaluation harness, error analysis; this week's evaluation runs with independent verification, and model licenses checked on the model cards  (evidence: PR #11, PR #14)
- Ritika (Users&Research): user-test protocol, consent script, task-stimuli picker, log anonymizer and task-test summarizer  (evidence: PR #13)

## Lean canvas changes (if any)
- None this week: `lean-canvas.md` has not changed since it was created on 2026-09-22 (PR #7). Proposed edits (sharper MVP job, false-SUPPORT guardrail metric, explicit biomedical-domain limit) are written up in `docs/lean_canvas_session05_changes.md` (PR #10) but have not been applied to the canvas yet.
