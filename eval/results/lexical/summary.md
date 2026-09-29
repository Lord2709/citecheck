# Run `lexical`  (dev split, n=300)

> Real data.

- retriever `bm25`, verifier `lexical`, k=3, sentences/paper=3, tau=0.65
- tau tuning: {'method': 'grid_max_macro_f1', 'split': 'train', 'n_claims': 200, 'tuned_macro_f1': 0.5466628668234101, 'leak': False}

## Claim-level (3-class: SUPPORT / CONTRADICT / NEI)
- **macro-F1 0.520**  95% CI [0.456, 0.580]  accuracy 0.557
- **false-SUPPORT rate 0.222**  SUPPORT precision 0.639  coverage 0.530
- claims excluded as MIXED gold: 0

| class | precision | recall | F1 | gold n |
|---|---|---|---|---|
| SUPPORT | 0.639 | 0.556 | 0.595 | 124 |
| CONTRADICT | 0.392 | 0.312 | 0.348 | 64 |
| NEI | 0.553 | 0.696 | 0.617 | 112 |

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
- label-only    P 0.325 R 0.373 F1 0.347
- label+rationale P 0.279 R 0.321 F1 0.298

## Where do the errors come from? (macro-F1 with progressively more oracle help)
- end-to-end 0.520 -> oracle paper 0.539 -> oracle paper+sentences 0.381
- lost to retrieval +0.020; lost to sentence selection -0.158; remaining gap (verifier) 0.619

**vs `majority`**: macro-F1 difference +0.339, 95% CI [+0.272, +0.398], P(this run better) = 1.00  (n=300)

## Cost / latency
retrieval 14.2 ms/claim, verification 1.0 ms/claim. Local model: $0 per request (compute only).

> With ~300 dev claims a 95% CI is several F1 points wide: differences smaller than the CI are not evidence.
