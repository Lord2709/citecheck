# North-star metric: definition

Owner: Product, with Data & Evaluation.  **Status: proposed default.**  Resolves the open question in
`todo/todo-session5.md`: "Is it citation-support F1 alone, or task success in user tests too?"

## Proposal

| Role | Metric | Why |
|---|---|---|
| **North star** (the one number in every report's front matter) | **Claim-level macro-F1 on SciFact dev, end-to-end (retrieve then verify)**, tau tuned on train, 95% bootstrap CI | Measurable every week, tied to the model we actually ship, matches the lean canvas, and comparable week to week |
| **Guardrail** | **False-SUPPORT rate** (non-supporting claims we call SUPPORTS) | The canvas names false SUPPORTS the worst failure; a model can raise F1 while getting more dangerous |
| **Validation metrics** (reported next to it, from user tests) | Task success rate, median task time, agreement rate | These test the canvas's key assumption (researchers find grounded verdicts useful). n is 3-6, so they validate; they cannot be the weekly headline |
| Diagnostic | Recall@k, MRR, oracle ablations | Tell us whether retrieval, sentence selection or the verifier is the bottleneck |

**Why not task success as the north star?** With a handful of participants per week the number swings wildly, so "this week vs last
week" would be noise. It stays a first-class number in the report, and the midterm decision rules require it.

## Rules
1. The value in `reports/sessionNN.md` is copied from `eval/results/<run>/results.json`, and `tools/preflight.py` checks it.
2. The run reported is the run in `eval/results/deployed_config.json` (the model in the demo is the model in the report).
3. We report the CI. A difference smaller than the CI is not a win, and we say so.
4. Targets are set **after** the baseline ladder exists (Tuesday night) and **before** we see later results. Write them here:

| item | target | set on | by |
|---|---|---|---|
| zero-shot beats majority and word-overlap (paired-bootstrap 95% CI of the difference above 0) | yes | 2026-10-04 (after Session 5 results) | Product + Data & Evaluation |
| false-SUPPORT rate ceiling | 0.15 | 2026-10-04 (after Session 5 results) | Product + Data & Evaluation |
| user tests: completed and correct | >= 3 participants; >= 2 get every T1 task right without help; 0 misled | 2026-10-04 (before any user test) | Product + Users & Research |

The machine-readable copy is `docs/decision_rules.json`; `python -m tools.midterm_decision` applies it.

## Session 7 targets for the agent upgrade (written 2026-10-20, before any of these runs exist)

Proposed by Product and Data & Evaluation in the Session 7 PR; merging that PR with the team's approval makes them final. Change one
only in a reviewed PR, and never after seeing the result it decides. Experiments are defined in `docs/agent_plan.md`.

| experiment | target | data | why this number |
|---|---|---|---|
| E1 fine-tuned verifier vs deployed zero-shot | paired-bootstrap 95% CI of the macro-F1 difference entirely above 0, **and** false-SUPPORT rate at or below 0.108 (zero-shot's) | SciFact dev, tau tuned on the calibration part only | a win inside the CI is noise; a model that gains F1 by over-trusting citations is worse for users |
| E1 promotion rule | promote only if E1 passes; otherwise keep zero-shot and report the negative result | | the model in the demo is the model we report |
| E2 full-text escalation | at least 20% of the agent's abstract-only "Not enough evidence" answers on the real-world set become correct verdicts after reading the full text; median extra time per escalated citation at most 15 s | real-world set | escalation must earn its cost in time |
| E3 replacement suggestions | bad-replacement rate at most 10% of suggestions; when no candidate clears tau strict, the agent says so | SciFact swap test + hand-checked sample | a wrong suggestion is the agent's version of a false SUPPORT |
| E4 real-world gap | no target: we report the gap, with its CI | real-world set | it answers "will it work on my citations?" |
| real-world set quality | at least 100 citing sentences across two fields; Cohen's kappa at least 0.6 between the two labellers before we score on it, else we fix the labelling guide and report kappa | | labels we disagree on cannot judge a model |
| user tests | at least 3 outside participants per week from Session 7; at least 2 complete every task without help; 0 agree with a wrong verdict | evidence/sessionNN/ | unchanged from the midterm rule |
| guardrail (unchanged) | false-SUPPORT ceiling 0.15 for any run we deploy | SciFact dev | |

The north star in the report front matter stays **claim-level macro-F1 on SciFact dev** of the deployed run until a
fine-tuned model is promoted. Task success from user tests is reported next to it every week.
