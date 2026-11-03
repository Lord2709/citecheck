# Run `finetuned_rescore_pinned`  (dev split, n=300)

> Real data.

- retriever `bm25`, verifier `nli:hassanedwan/citecheck-nli-ft-base-sel`, k=3, sentences/paper=3, evidence unit=window, tau=0.5
- tau tuning: {'method': 'fixed', 'split': None}

## Claim-level (3-class: SUPPORT / CONTRADICT / NEI)
- **macro-F1 0.736**  95% CI [0.684, 0.784]  accuracy 0.747
- **false-SUPPORT rate 0.091**  SUPPORT precision 0.849  coverage 0.533
- claims excluded as MIXED gold: 0

| class | precision | recall | F1 | gold n |
|---|---|---|---|---|
| SUPPORT | 0.849 | 0.726 | 0.783 | 124 |
| CONTRADICT | 0.741 | 0.625 | 0.678 | 64 |
| NEI | 0.671 | 0.839 | 0.746 | 112 |

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
- label-only    P 0.598 R 0.598 F1 0.598
- label+rationale P 0.569 R 0.569 F1 0.569

**vs `zero_shot_nli`**: macro-F1 difference +0.133, 95% CI [+0.078, +0.186], P(this run better) = 1.00  (n=300)

**vs `finetuned_nli_selector_v2_capped`**: macro-F1 difference +0.000, 95% CI [+0.000, +0.000], P(this run better) = 0.00  (n=300)

## Sentence selection (`cross:hassanedwan/citecheck-sentence-selector`)
- a complete gold rationale is among the 3 selected sentences for 0.938 of 209 gold papers

## Cost / latency
retrieval 14.9 ms/claim, verification 1804.4 ms/claim, model params 184,424,451 on cpu. Local model: $0 per request (compute only).

> With ~300 dev claims a 95% CI is several F1 points wide: differences smaller than the CI are not evidence.
