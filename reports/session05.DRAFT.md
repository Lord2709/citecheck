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
  value: "<<FILL: e.g. 0.58 (95% CI 0.52-0.64), from eval/results/zero_shot_nli>>"
  previous: "not measured (first measurement; the Session 4 report had none)"
---

<!--
HOW TO FINISH THIS FILE (delete this comment when done)
1. Save it as reports/session05.md (two digits, exactly). This DRAFT name is never graded.
2. Replace every double-angle FILL marker with something TRUE that you can point at. Delete bullets you cannot back up.
3. Numbers come from eval/results/*/results.json and evidence/session05/summary.md, never from memory.
4. Run: python -m tools.preflight --session 5 --gh --repo Lord2709/citecheck   and fix every FAIL.
5. Merge to main BEFORE 5:00pm Eastern Tuesday. The grader reads the commit on main at that moment.
Honesty is graded: a negative result, a loss to our own baseline, or a flaw found in our own evaluation scores higher than an unbacked win.
-->

## Shipped this week
- End-to-end pipeline (claim + cited paper -> SUPPORTS / CONTRADICTS / NOT ENOUGH EVIDENCE with the evidence sentences shown), command line and Streamlit app, merged to `main`  (evidence: PR #<<FILL>>, issue #<<FILL>>)
- SciFact loader with data card, evaluation harness (macro-F1 with bootstrap CI, false-SUPPORT rate, retrieval recall@k and MRR, abstract-level F1) and a baseline ladder: majority, word-overlap, zero-shot NLI  (evidence: PR #<<FILL>>, results in `eval/results/`)
- User-test kit: protocol, consent script, seeded task stimuli, log anonymizer, evidence summarizer  (evidence: PR #<<FILL>>)
- MVP scope, user stories, north-star definition and the Oct 6 plan  (evidence: PR #<<FILL>>)
- Product is <<FILL: run locally with `streamlit run app/streamlit_app.py`, or the deployed URL>>

## User evidence
- <<FILL: how many outside people, on which date, doing which tasks on the running product, and what happened (completion, time, what confused them)>>
- **Raw artifact**: `evidence/session05/task_tests.csv`, `evidence/session05/usage_logs/P01.jsonl`, `evidence/session05/notes/P01.md`
- Headline numbers are computed in `evidence/session05/summary.md` (task success rate, median time).
- What we changed as a result: <<FILL: the concrete change, with the issue or PR number>>

## Metrics snapshot
- Claim-level macro-F1: <<FILL: 0.xx>> (was: not measured), 95% bootstrap CI <<FILL>>
- Baselines on the same claims: majority <<FILL>>, word-overlap <<FILL>>; paired bootstrap of the zero-shot model against each: <<FILL: difference and CI, say plainly if the CI includes zero>>
- False-SUPPORT rate (safety metric): <<FILL>>; retrieval recall@3 <<FILL>>, MRR <<FILL>>
- User tests: task success rate <<FILL>> over <<FILL>> attempts (n is tiny; this describes those sessions only)
- Measured on: SciFact dev (<<FILL: n>> claims); the abstain threshold tau was tuned on train claims, never on dev
- Is this the same model that is running in the product? <<FILL: yes, `eval/results/deployed_config.json` (run `zero_shot_nli`) is what the app loads; or no, and why>>

## What did not work
- Our Session 4 BM25 script was tested on an arXiv keyword sample rather than SciFact, so it never connected to the north-star metric; we replaced it this week with a retriever evaluated on SciFact.
- <<FILL: the most useful negative result from `eval/results/*/errors.md`, for example a baseline that beat the neural model on some class, a class the model never predicts, or a flaw in our own evaluation. Only write what is true.>>

## Challenges / blockers
- The dev set has only 300 claims, so differences smaller than the confidence interval are noise.
- The DOI and arXiv lookups were built against the APIs' documentation and have <<FILL: been / not yet been>> tested against the live services; pasting an abstract always works.
- <<FILL: anything you need help with, for example a GPU for fine-tuning>>

## Next week's goal
- Deliver the Oct 6 mid-semester presentation: live demo of the MVP, the real user evidence, our metric against the baseline, and a pivot-or-persevere decision using the rules written in `docs/midterm_oct6.md`.

## Individual contributions
- Vyom (Product): MVP scope, user stories, north-star definition, Oct 6 plan and decision rules  (evidence: PR #<<FILL>>)
- Sakshaat (Engineering): pipeline, CLI, Streamlit app, config that ties the app to the evaluated model, CI, preflight check  (evidence: PR #<<FILL>>)
- Sahil (Data&Eval): SciFact loader and data card, retrieval, verifiers, evaluation harness, error analysis  (evidence: PR #<<FILL>>)
- Ritika (Users&Research): recruited and ran <<FILL: n>> task tests; protocol, consent script, anonymizer and summarizer  (evidence: PR #<<FILL>>)

## Lean canvas changes (if any)
- <<FILL: only if `lean-canvas.md` actually changed in a PR. Suggested: MVP job sharpened to "does the paper I cite support my claim"; relevance and citation audit demoted to secondary; false-SUPPORT rate added as a guardrail metric; domain limit (SciFact is biomedical) made explicit. Evidence: PR #NN>>
