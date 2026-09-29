# Run `zero_shot_nli`  (dev split, n=300)

> Real data.

- retriever `bm25`, verifier `nli:MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, k=3, sentences/paper=3, tau=0.6
- tau tuning: {'method': 'grid_max_macro_f1', 'split': 'train', 'n_claims': 200, 'tuned_macro_f1': 0.6799983556913632, 'leak': False}

## Claim-level (3-class: SUPPORT / CONTRADICT / NEI)
- **macro-F1 0.603**  95% CI [0.545, 0.660]  accuracy 0.613
- **false-SUPPORT rate 0.108**  SUPPORT precision 0.791  coverage 0.563
- claims excluded as MIXED gold: 0

| class | precision | recall | F1 | gold n |
|---|---|---|---|---|
| SUPPORT | 0.791 | 0.581 | 0.670 | 124 |
| CONTRADICT | 0.474 | 0.578 | 0.521 | 64 |
| NEI | 0.573 | 0.670 | 0.617 | 112 |

## Retrieval (claims with gold evidence: n=188, avg gold papers/claim 1.11)
| k | recall@k | precision@k |
|---|---|---|
| 1 | 0.722 | 0.734 |
| 3 | 0.841 | 0.294 |
| 5 | 0.882 | 0.186 |
| 10 | 0.941 | 0.102 |
| 20 | 0.958 | 0.052 |

MRR 0.810, nDCG@10 0.838. (precision@k is capped near 1/k when ~1 paper is relevant.)

## Abstract-level (SciFact-leaderboard style; NOT the official scorer)
- label-only    P 0.414 R 0.450 F1 0.431
- label+rationale P 0.388 R 0.421 F1 0.404

## Where do the errors come from? (macro-F1 with progressively more oracle help)
- end-to-end 0.603 -> oracle paper 0.648 -> oracle paper+sentences 0.646
- lost to retrieval +0.045; lost to sentence selection -0.002; remaining gap (verifier) 0.354

**vs `majority`**: macro-F1 difference +0.421, 95% CI [+0.359, +0.482], P(this run better) = 1.00  (n=300)

**vs `lexical`**: macro-F1 difference +0.083, 95% CI [+0.010, +0.159], P(this run better) = 0.99  (n=300)

## Cost / latency
retrieval 25.0 ms/claim, verification 456.9 ms/claim, model params 184,424,451 on cpu. Local model: $0 per request (compute only).

> With ~300 dev claims a 95% CI is several F1 points wide: differences smaller than the CI are not evidence.
