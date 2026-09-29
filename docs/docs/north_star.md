# North-star metric: definition

Owner: Product (Vyom) with Data & Evaluation (Sahil).  **Status: proposed default.**  Resolves the open question in
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
| zero-shot beats majority and word-overlap (paired-bootstrap 95% CI of the difference above 0) | yes/no | <<TBD>> | Vyom + Sahil |
| false-SUPPORT rate ceiling | <<TBD, decide after seeing the zero-shot number>> | <<TBD>> | Vyom + Sahil |
| user tests: completed and correct | <<TBD, e.g. at least 2 of 3 participants on T1>> | <<TBD>> | Vyom + Ritika |
