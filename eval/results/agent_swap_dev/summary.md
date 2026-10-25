# agent_swap_dev: E3 swap test on SciFact dev

124 SUPPORT claims; each cites a wrong-but-plausible paper (best non-gold BM25 hit). Verifier `nli:MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, tau 0.6, tau_strict 0.85 (placeholder, not tuned).

| metric | rate [95% Wilson CI] (k/n) |
|---|---|
| wrong citation flagged (not 'supports') | 0.911 [0.848, 0.950] (113/124) |
| wrong citation kept as 'supports' | 0.089 [0.050, 0.152] (11/124) |
| a replacement was suggested | 0.435 [0.351, 0.523] (54/124) |
| a gold paper was among the suggestions | 0.403 [0.321, 0.491] (50/124) |
| suggestions that are gold papers | 0.877 [0.767, 0.939] (50/57) |
| suggestions that are not gold (UPPER bound on bad replacements) | 0.123 [0.061, 0.233] (7/57) |
| control: gold paper cited, kept as 'supports' | 0.516 [0.429, 0.602] (64/124) |

Non-gold suggestions are not necessarily wrong: SciFact labels only the papers each claim cites. Hand-check a sample before calling them bad.
