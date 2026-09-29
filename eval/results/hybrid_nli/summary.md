# Run `hybrid_nli`  (dev split, n=300)

> Real data.

- retriever `hybrid(bm25+dense)`, verifier `nli:MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, k=3, sentences/paper=3, tau=0.6
- tau tuning: {'method': 'grid_max_macro_f1', 'split': 'train', 'n_claims': 200, 'tuned_macro_f1': 0.684858692254136, 'leak': False}

## Claim-level (3-class: SUPPORT / CONTRADICT / NEI)
- **macro-F1 0.587**  95% CI [0.526, 0.641]  accuracy 0.593
- **false-SUPPORT rate 0.148**  SUPPORT precision 0.720  coverage 0.567
- claims excluded as MIXED gold: 0

| class | precision | recall | F1 | gold n |
|---|---|---|---|---|
| SUPPORT | 0.720 | 0.540 | 0.618 | 124 |
| CONTRADICT | 0.494 | 0.594 | 0.539 | 64 |
| NEI | 0.562 | 0.652 | 0.603 | 112 |

## Retrieval (claims with gold evidence: n=188, avg gold papers/claim 1.11)
| k | recall@k | precision@k |
|---|---|---|
| 1 | 0.720 | 0.739 |
| 3 | 0.870 | 0.305 |
| 5 | 0.909 | 0.194 |
| 10 | 0.954 | 0.104 |
| 20 | 0.974 | 0.054 |

MRR 0.823, nDCG@10 0.849. (precision@k is capped near 1/k when ~1 paper is relevant.)

## Abstract-level (SciFact-leaderboard style; NOT the official scorer)
- label-only    P 0.416 R 0.459 F1 0.436
- label+rationale P 0.377 R 0.416 F1 0.395

## Where do the errors come from? (macro-F1 with progressively more oracle help)
- end-to-end 0.587 -> oracle paper 0.648 -> oracle paper+sentences 0.646
- lost to retrieval +0.061; lost to sentence selection -0.002; remaining gap (verifier) 0.354

**vs `zero_shot_nli`**: macro-F1 difference -0.016, 95% CI [-0.047, +0.015], P(this run better) = 0.15  (n=300)

**vs `lexical`**: macro-F1 difference +0.067, 95% CI [-0.002, +0.140], P(this run better) = 0.97  (n=300)

**vs `majority`**: macro-F1 difference +0.405, 95% CI [+0.340, +0.462], P(this run better) = 1.00  (n=300)

## Cost / latency
retrieval 149.5 ms/claim, verification 512.5 ms/claim, model params 184,424,451 on cpu. Local model: $0 per request (compute only).

> With ~300 dev claims a 95% CI is several F1 points wide: differences smaller than the CI are not evidence.
