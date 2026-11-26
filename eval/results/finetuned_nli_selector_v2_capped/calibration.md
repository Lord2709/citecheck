# Calibration of `finetuned_nli_selector_v2_capped` (SUPPORTS and CONTRADICTS verdicts, n=160)

- expected calibration error (ECE): **0.166**
- verdicts at confidence ≥ 0.99: 57% of all; 4 of them wrong

| confidence | n | mean confidence | share right |
|---|---|---|---|
| 0.50–0.60 | 2 | 0.536 | 1.000 |
| 0.60–0.70 | 6 | 0.653 | 0.333 |
| 0.70–0.80 | 4 | 0.767 | 1.000 |
| 0.80–0.90 | 11 | 0.867 | 0.455 |
| 0.90–0.95 | 8 | 0.930 | 0.250 |
| 0.95–0.99 | 37 | 0.978 | 0.730 |
| 0.99–1.00 | 92 | 0.997 | 0.957 |

> Analysis only. A gap between the two columns means the shown confidence should not be read as a probability of being right.
