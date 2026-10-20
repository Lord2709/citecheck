# eval/ : the evaluation harness

Owner: Data & Evaluation.  **One command produces every number we report.**

```bash
# 0. one-time: get SciFact (writes data/scifact/*.jsonl + MANIFEST.json)
python -m data.fetch_scifact

# 1. the baseline ladder, on DEV. Run in this order; each compares itself with the previous one.
python -m eval.run_eval --name majority      --retriever bm25 --verifier majority
python -m eval.run_eval --name lexical       --retriever bm25 --verifier lexical --compare-with eval/results/majority
python -m eval.run_eval --name zero_shot_nli --retriever bm25 --verifier nli --oracle \
                        --compare-with eval/results/majority --compare-with eval/results/lexical --promote

# 2. what went wrong, and the figures
python -m eval.error_analysis --run eval/results/zero_shot_nli
python -m eval.plots --run zero_shot_nli

# 3. improvements (each is one row in the ablation table)
python -m eval.run_eval --name hybrid_nli --retriever hybrid --verifier nli --compare-with eval/results/zero_shot_nli
python -m eval.finetune_nli --out models/citecheck-nli-ft            # stretch; GPU/Colab recommended
python -m eval.run_eval --name finetuned_nli --retriever bm25 --verifier nli --model models/citecheck-nli-ft \
                        --oracle --compare-with eval/results/zero_shot_nli
```

Smoke test with 20 claims first (`--limit 20`; the run is flagged *partial* and cannot be promoted).
The first NLI run downloads the model from Hugging Face (~700 MB) and the first dense/hybrid run embeds the
corpus once (cached in `data/cache/`).

## What is measured

| Question | Metric | Where |
|---|---|---|
| Does the system judge citations correctly? (**north star**) | claim-level 3-class **macro-F1** on dev, with 95% bootstrap CI | `claim_level` |
| Is it dangerously over-confident? | **false-SUPPORT rate** (gold is not SUPPORT, we said SUPPORT), SUPPORT precision, coverage | `claim_level` |
| Do we find the right paper? | Recall@k, Precision@k (capped near 1/k), MRR, nDCG@10 | `retrieval` |
| Can we compare with the literature? | abstract-level P/R/F1, label-only and label+rationale (SciFact-leaderboard style, **not** the official scorer) | `abstract_level` |
| Where do errors come from? | end-to-end vs oracle-paper vs oracle-paper+sentences | `error_attribution` |
| Is A really better than B? | paired bootstrap over claims: difference, 95% CI, P(A better) | `paired_comparisons` |
| What does a request cost? | ms per claim (retrieval, verification), model parameters, device; local model = $0 | `timing` |

## Rules that keep us honest

* **tau (the abstain threshold) is tuned on `train`, reported on `dev`.** Tuning on dev is refused unless `--allow-leak`.
* `claims_test.jsonl` has no public labels. We never use it.
* Runs on `tests/fixtures/**` are flagged `synthetic_fixture` and can never be promoted or quoted.
* `--promote` writes `eval/results/deployed_config.json`; the app loads exactly that configuration and shows its dev score.
  That is how "the model we report is the model in the demo" stays true.
* With n=300, differences smaller than the CI are noise. Say so in the report; do not claim a win the CI does not support.
* Publish negative results: if the fine-tuned model loses to zero-shot, that is a result (the guidelines credit it).

## Sanity checks before you trust a number

* BM25 recall@10 on SciFact should be clearly above 0.5. If it is near 0, the loader or tokenizer is broken.
* `majority` macro-F1 should be low (it only ever predicts NEI; ~0.2 at best).
* `oracle_doc` should be >= `end_to_end` unless retrieval already finds every gold paper. `oracle_rationale` is usually >= `oracle_doc` for a good verifier, but a weak or quirky one can score lower on gold rationales (the lexical baseline does); a LARGE unexplained drop is a red flag for a bug in sentence handling.
* Re-run the same command twice: the numbers must be identical (seeded; the cache makes this fast).

## Files written per run (`eval/results/<name>/`)

`results.json` (everything, with provenance), `predictions.jsonl` (per-claim predictions and probabilities),
`summary.md` (human-readable), later `errors.md` / `errors.csv`.  `eval/results/LATEST.md` is the table of all runs.
**Commit `eval/results/` (small) but not `eval/cache/` or `models/`.**

## Fit / calibration split of train (Session 7, for fine-tuning)

```
python -m eval.train_split                     # writes data/splits/scifact_train_v1.json (claim ids only; commit it)
python -m eval.finetune_nli --split-file data/splits/scifact_train_v1.json --pairs-only      # pair counts, no torch
python -m eval.run_eval --name <run> ... --tune-split-file data/splits/scifact_train_v1.json  # tau tuned on the calib part
```

Training uses only the **fit** part; calibration and every threshold (tau, later tau strict and the escalation rule) use
only the **calib** part; dev is for reporting only. Runs of a model that never saw SciFact (zero-shot) may keep the old
default (tau on 200 random train claims); any model trained on SciFact must use `--tune-split-file`, otherwise tau is tuned
on claims it was trained on. See `docs/agent_plan.md`, Part 2.

## Agent evaluation (Session 7): `eval/agent_eval.py`

```
python -m eval.agent_eval swap --name agent_swap --verifier nli --split dev            # E3, offline, ~minutes on CPU
python -m eval.agent_eval escalation --gold data/cache/realworld/gold_v1.jsonl          # E2, needs internet + the real-world set
```

E3 cites a wrong-but-plausible paper (best non-gold BM25 hit) for each SciFact SUPPORT claim and measures whether the
agent flags it and what it suggests instead; "suggestions that are not gold" is an UPPER bound on bad replacements,
because SciFact labels only the papers each claim cites. tau is the deployed one (tuned on train); tau_strict is the
agent's placeholder until it is tuned on the calibration part. Targets: `docs/north_star.md`.
