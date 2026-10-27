# Deployed site vs. local run: same draft, same verdicts (2026-10-26)

Owner: Data & Evaluation.  Purpose: check that the site people use runs the model we report numbers for.

| | Local run | Deployed site |
|---|---|---|
| When | 2026-10-25 17:31 ET | 2026-10-26 14:44 ET (18:44 UTC) |
| Where | Windows laptop used for the evaluation runs, `uvicorn` on localhost | https://citecheck-877770798089.us-east4.run.app (Google Cloud Run, 2 vCPU, 4 GiB) |
| Code | `main` at 0808273 (PR #34), plus the sign-in key change later merged in PR #35 | image built from `main` at 13224ed, with torch 2.8.0 and transformers 4.57.6 pinned in the build (the pins are in the open hosting PR) |
| Verifier | `nli:MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, tau 0.6, tau strict 0.85 | same |
| Input | the site's built-in example draft ("Try an example with real papers"), full text and suggestions on | same |
| Raw report | `2026-10-25_example_local.md` | `2026-10-26_example_live.md` |

| # | Citation | Local | Deployed | Same? |
|---|---|---|---|---|
| 1 | Vaswani 2017, "rely entirely on attention" | Supported, ≥ 0.99, abstract | Supported, ≥ 0.99, abstract | yes |
| 2 | Wadden 2020, SciFact description | Supported, ≥ 0.99, abstract | Supported, ≥ 0.99, abstract | yes |
| 3 | LeCun 2015 (Nature), no open abstract | Could not check: Semantic Scholar HTTP 429 | Could not check: no abstract from open sources | outcome yes, reason differs |
| 4 | Vaswani 2017, "always slower to train" | Contradicted, ≥ 0.99; replacement search checked 5 candidates, none ≥ 0.85 | Contradicted, ≥ 0.99; replacement search found no candidates | verdict yes, search differs |
| 5 | Vaswani 2017, "8 parallel attention heads" | Not enough evidence, 0.93, after reading the arXiv PDF (186 sentences) | Not enough evidence, 0.93, after reading the arXiv PDF (186 sentences) | yes |

**Result.** All four citations that could be checked got the same verdict with the same confidence, including the
full-text path on #5. The deployed site runs the evaluated verifier and behaves like the local run.

**Differences, both from the free paper services, not the model.**
- #3: locally Semantic Scholar refused the request (HTTP 429, no API key); on the deployed run it answered, and no
  open abstract exists for this paper. The site offers "paste the abstract" for this case.
- #4: the deployed run's replacement search returned no candidates, the local run found five. Most likely the search
  APIs throttle shared cloud addresses without a key; adding the free Semantic Scholar and OpenAlex keys as secrets is
  the planned fix. Not yet confirmed from the logs.

**A known error, visible in both runs.** #5 is wrong: the full text contains "In this work we employ h = 8 parallel
attention layers, or heads", the agent found that sentence, and the verifier still answered "not enough evidence"
(0.93). Retrieval and full-text reading worked; the verifier is the bottleneck, as `docs/agent_plan.md` says. Two
things to test on this case: judging each evidence sentence on its own instead of the three together, and the
fine-tuned verifier (E1).

One run of five citations on each side: this is a parity check, not an accuracy measurement.
