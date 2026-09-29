# Run `majority`  (dev split, n=300)

> Real data.

- retriever `bm25`, verifier `majority`, k=3, sentences/paper=3, tau=0.5
- tau tuning: {'method': 'default_0.5', 'split': None}

## Claim-level (3-class: SUPPORT / CONTRADICT / NEI)
- **macro-F1 0.181**  95% CI [0.162, 0.200]  accuracy 0.373
- **false-SUPPORT rate 0.000**  SUPPORT precision 0.000  coverage 0.000
- claims excluded as MIXED gold: 0

| class | precision | recall | F1 | gold n |
|---|---|---|---|---|
| SUPPORT | 0.000 | 0.000 | 0.000 | 124 |
| CONTRADICT | 0.000 | 0.000 | 0.000 | 64 |
| NEI | 0.373 | 1.000 | 0.544 | 112 |

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
- label-only    P 0.000 R 0.000 F1 0.000
- label+rationale P 0.000 R 0.000 F1 0.000

## Cost / latency
retrieval 13.7 ms/claim, verification 0.5 ms/claim. Local model: $0 per request (compute only).

> With ~300 dev claims a 95% CI is several F1 points wide: differences smaller than the CI are not evidence.
