# Session 05 results: SciFact dev baseline ladder + zero-shot NLI

Owner: Data & Evaluation (Sahil). Run on 2026-09-29.

**Where the numbers come from.** Every number in sections 1-5 is copied from a committed `eval/results/<run>/results.json`.
Numbers marked *(derived)* were recomputed from the committed `predictions.jsonl` files by the independent
verification script described in section 7. They are not stored in any `results.json`, so quote them as derived.

| | |
|---|---|
| Code | `main` at `a999d1f` (all four runs record `provenance.git_commit = a999d1fe5ea4…`, which is on `origin/main`) |
| Data | SciFact official S3 release. sha256 prefixes corpus `b8d6c89624cb`, train `f4c8fa82d8bd`, dev `86f0435d08fd`, test `558930d75215`; rows 5183 / 809 / 300 / 300 (`data/scifact/MANIFEST.json`) |
| Reported on | **dev**, n = 300 claims (124 SUPPORT, 64 CONTRADICT, 112 NEI, 0 MIXED) |
| tau | tuned on **200 train claims** (seeded random subset, seed 0), never on dev. `claims_test.jsonl` is never read |
| Machine | Windows 11, Intel Core Ultra 7 155H (CPU only), Python 3.9.2, torch 2.8.0+cpu, transformers 4.57.6 |
| Deployed | `eval/results/deployed_config.json` → **`zero_shot_nli`** |

## 1. All runs

| run | retriever | verifier | tau | macro-F1 [95% CI] | accuracy | false-SUPPORT | SUPPORT precision | coverage | recall@3 | recall@5 | MRR |
|---|---|---|---|---|---|---|---|---|---|---|---|
| majority | bm25 | always NEI | 0.5 | 0.181 [0.162, 0.200] | 0.373 | 0.000 | 0.000 | 0.000 | 0.841 | 0.882 | 0.810 |
| lexical | bm25 | word overlap | 0.65 | 0.520 [0.456, 0.580] | 0.557 | 0.222 | 0.639 | 0.530 | 0.841 | 0.882 | 0.810 |
| **zero_shot_nli** (deployed) | bm25 | DeBERTa-v3-base-mnli-fever-anli | 0.6 | **0.603 [0.545, 0.660]** | 0.613 | **0.108** | 0.791 | 0.563 | 0.841 | 0.882 | 0.810 |
| hybrid_nli | bm25 + MiniLM dense | DeBERTa-v3-base-mnli-fever-anli | 0.6 | 0.587 [0.526, 0.641] | 0.593 | 0.148 | 0.720 | 0.567 | 0.870 | 0.909 | 0.823 |

Per-class F1 (SUPPORT / CONTRADICT / NEI): lexical 0.595 / 0.348 / 0.617; zero_shot_nli 0.670 / 0.521 / 0.617;
hybrid_nli 0.618 / 0.539 / 0.603. CONTRADICT is the weakest class for every model.

zero_shot_nli confusion matrix (rows = gold, columns = predicted: SUPPORT, CONTRADICT, NEI):
SUPPORT [72, 19, 33], CONTRADICT [4, 37, 23], NEI [15, 22, 75]. The false-SUPPORT rate is (15 + 4) / 176 = 0.108.

Abstract-level F1 (SciFact-leaderboard *style*, **not** the official scorer), label-only / label+rationale:
lexical 0.347 / 0.298, zero_shot_nli 0.431 / 0.404, hybrid_nli 0.436 / 0.395.

**Retrieval, read this before comparing with the literature.** Recall@k, MRR and nDCG@10 above are computed over the
**188 dev claims that have gold evidence**, with the evidence papers as relevant. On that basis BM25 has recall@10 0.941
and nDCG@10 0.838. That nDCG is **not comparable** with published BEIR SciFact numbers. Scored BEIR-style (all 300 dev
claims, `cited_doc_ids` as relevant), BM25 nDCG@10 is **0.687** *(derived)*, in line with the ~0.67 usually published
for BM25 on SciFact. Hybrid scores 0.849 on our basis and 0.716 *(derived)* BEIR-style.

## 2. Is A really better than B? (paired bootstrap over the 300 claims, 1000 resamples, seed 0)

| comparison | macro-F1 difference | 95% CI | P(A better) | CI includes 0? |
|---|---|---|---|---|
| lexical − majority | +0.339 | [+0.272, +0.398] | 1.00 | no |
| zero_shot_nli − majority | +0.421 | [+0.359, +0.482] | 1.00 | no |
| zero_shot_nli − lexical | +0.083 | [+0.010, +0.159] | 0.99 | **no, but the lower end is only +0.010** |
| hybrid_nli − zero_shot_nli | −0.016 | [−0.047, +0.015] | 0.15 | **yes: no evidence of a difference** |
| hybrid_nli − lexical | +0.067 | [−0.002, +0.140] | 0.97 | **yes** |
| hybrid_nli − majority | +0.405 | [+0.340, +0.462] | 1.00 | no |

Plainly: zero-shot NLI beats both baselines. Its margin over word overlap is real at the 95% level but small; the CI
reaches down to +0.01. Hybrid retrieval is *not* distinguishable from BM25 + NLI, and its point estimate is lower.

## 3. Where the errors come from (oracle ablations, macro-F1)

| run | end-to-end | oracle paper | oracle paper + gold sentences | lost to retrieval | lost to sentence selection | remaining gap (verifier) |
|---|---|---|---|---|---|---|
| lexical | 0.520 | 0.539 | 0.381 | +0.020 | −0.158 | 0.619 |
| zero_shot_nli | 0.603 | 0.648 | 0.646 | +0.045 | −0.002 | 0.354 |
| hybrid_nli | 0.587 | 0.648 | 0.646 | +0.061 | −0.002 | 0.354 |

* **The verifier is the bottleneck.** Given the gold paper and the gold sentences, NLI still reaches only 0.646.
  Better retrieval could buy about 0.045 and better sentence selection about nothing.
* The oracle numbers are point estimates. **No CI is computed for them**, so whether the 0.045 retrieval gap is
  significant is **not verified**.
* For NLI, oracle-rationale ≈ oracle-paper (0.646 vs 0.648): no sign of a sentence-handling bug. The large lexical
  drop (0.539 → 0.381) is specific to the word-overlap scorer (known behaviour, see `eval/README.md`) and does not
  appear for NLI.

## 4. Error analysis (`zero_shot_nli/errors.md`, 116 errors out of 300)

| bucket | lexical | zero_shot_nli | hybrid_nli | meaning |
|---|---|---|---|---|
| MISSED_BY_VERIFIER | 48 | 41 | 44 | gold paper was among the 3 judged, but we answered NEI |
| WRONG_DIRECTION | 36 | 23 | 26 | SUPPORT ↔ CONTRADICT flipped |
| FALSE_CONTRADICT | 13 | 22 | 20 | gold NEI, predicted CONTRADICT |
| FALSE_SUPPORT | 21 | 15 | 19 | gold NEI, predicted SUPPORT |
| RETRIEVAL_MISS | 15 | 15 | 13 | gold paper not among the 3 judged |

Note: the FALSE_SUPPORT *bucket* counts only gold NEI → SUPPORT. The false-SUPPORT *rate* also counts gold
CONTRADICT → SUPPORT (4 claims for zero_shot_nli, filed under WRONG_DIRECTION), hence 19/176, not 15/176.

What the errors actually are (from reading the top examples; the human "your category" column in `errors.md` is still
empty, so these categories are provisional):

1. **An off-topic paper outvotes the right one.** The verdict comes from the most confident of the 3 retrieved
   papers, so one confident but irrelevant paper can override the gold paper.
   *#100* "All hematopoietic stem cells segregate their chromosomes randomly." (gold SUPPORT). The gold paper is ranked
   1st and the model says SUPPORT 0.85 on it. The rank-2 paper (bone-marrow transplant chromosome markers) gets
   CONTRADICT 1.00 and wins, so the final verdict is CONTRADICT. Given the cited paper alone
   (`python -m src.main verify --abstract-file …`), the same model answers SUPPORTS 0.85 and quotes the gold rationale sentence.
2. **Gold NEI means "the cited abstract doesn't say", not "nothing in the corpus says".** For gold-NEI claims where
   zero_shot_nli committed to a verdict, **30 of 37** were driven by a paper the claim does not cite *(derived)*.
   Over all its committed verdicts, 59 of 169 came from an uncited paper *(derived)*.
   *#1099* "Statins decrease blood cholesterol." (gold NEI) → SUPPORT 0.94 from "Pleiotropic effects of statins"
   ("Statins are potent inhibitors of cholesterol biosynthesis"). Its mirror *#1100* "Statins increase blood
   cholesterol." → CONTRADICT 1.00. The cited paper itself is judged neutral (0.95 / 0.99). These are arguably correct
   judgements that the end-to-end metric scores as errors. Only this pair was checked by hand; how many of the 30 are
   like it is **not verified**.
3. **Negation.** *#208* "CHEK2 is not associated with breast cancer." (gold SUPPORT; the paper found "no convincing
   association"). The model gives CONTRADICT 0.86 on the gold paper itself.
4. **Verifier sees the evidence but says neutral.** Of the 41 MISSED_BY_VERIFIER errors, **30** had at least one gold
   rationale sentence among the sentences shown to the model; 11 did not *(derived)*.
   *#1024* "Recurrent mutations occur frequently within CTCF anchor sites adjacent to oncogenes." The gold sentence
   "…are a frequent site of mutations in cancer cells" was shown, and the model said neutral 1.00.

## 5. What did not work

* **Hybrid (BM25 + dense) retrieval.** It improves retrieval (recall@3 0.841 → 0.870, MRR 0.810 → 0.823) but not
  verdicts (macro-F1 −0.016, CI [−0.047, +0.015]), and it is less safe (false-SUPPORT 0.108 → 0.148). **Not promoted**
  (the rule was: promote only if the CI vs zero_shot_nli is entirely above 0 and false-SUPPORT is not worse).
  Consistent with section 3: retrieval is not where most of the error is.
* **The verifier caps us at ~0.65** even with perfect retrieval and perfect sentences. CONTRADICT is the weakest class
  (F1 0.521), and 22 gold-NEI claims are called CONTRADICT.
* **A flaw in our own evaluation:** end-to-end retrieval over the whole 5.2k-abstract corpus judges papers the claim
  never cited. SciFact only annotates cited papers, so some "errors" are unannotated evidence (section 4, item 2). The
  product question is "does *the paper I cite* support my claim". The oracle-paper setting (0.648) is closer to that
  than the end-to-end number (0.603).
* Word overlap is not far behind: zero-shot NLI's lead over it is +0.083 with a CI starting at +0.010.

## 6. Cost / latency (single run each, one laptop CPU; wall-clock, not a benchmark)

| run | retrieval ms/claim | verification ms/claim | notes |
|---|---|---|---|
| majority | 13.7 | 0.5 | |
| lexical | 14.2 | 1.0 | |
| zero_shot_nli | 25.0 | 456.9 | 184,424,451-parameter model on CPU; the no-cache re-run measured 15.8 / 382.0, so treat as ±20% |
| hybrid_nli | 149.5 | 512.5 | dense query encoding adds ~0.1 s per claim |

Local models: $0 per request (compute only). In batch evaluation one claim against 3 papers takes about 0.5 s on
this CPU. A single interactive CLI call (one claim, one abstract) reported 1991 ms, measured once.

## 7. Verification checks

An independent script (not committed) rebuilt the gold labels from `data/scifact/claims_dev.jsonl` with plain `json`
(empty `evidence` = NEI) and recomputed the metrics with scikit-learn.

| # | check | result |
|---|---|---|
| 0 | Test suite: `python -m pytest` on `main` | **PASS**: 105 passed, 0 skipped (all tests on `a999d1f`); 109 passed with `evidence/user-test-kit` merged in a throwaway branch |
| 0 | SciFact download matches expected row counts and sha256 prefixes | **PASS** (all four files) |
| 0 | majority / lexical reproduce the earlier Linux run | **PASS**: identical `predictions.jsonl` and metrics (only timestamps, timings, package versions and the path separator differ) |
| a | `gold` field in every `predictions.jsonl` = gold rebuilt from raw dev | **PASS** (all 4 runs) |
| a | macro-F1, accuracy, per-class F1, false-SUPPORT, SUPPORT precision, coverage (sklearn) = `results.json` | **PASS** (all 4 runs; bit-exact except majority macro-F1, which differs in the 17th digit from summation order) |
| a | bootstrap CIs and paired-bootstrap differences re-derived (same seed, sklearn metric) | **PASS** (identical) |
| b | BM25 recall@10 > 0.5 | **PASS**: 0.941 (188 evidence claims); nDCG@10 0.838; BEIR-style nDCG@10 0.687 *(derived)* |
| b | recall@k, nDCG@10, MRR recomputed from rankings | **PASS** (MRR 0.8096 recomputed from the cached top-20 rankings) |
| c | Determinism: zero_shot_nli re-run with `--no-cache` | **PASS**: every metric block, the tau tuning and `predictions.jsonl` are byte-identical (max probability difference 0.0). Only latency differs |
| d | oracle_doc ≥ end_to_end | **PASS** (all runs) |
| d | no large unexplained oracle_rationale drop | **PASS** for NLI (0.648 → 0.646); the lexical drop 0.539 → 0.381 is the known lexical behaviour |
| e | `deployed_config.json` → zero_shot_nli, dev macro-F1 0.6027 | **PASS** |
| e | App sidebar (Streamlit AppTest, headless, no overrides) | **PASS**: "Validated configuration `zero_shot_nli`, SciFact dev macro-F1 0.60 (95% CI 0.54 to 0.66); false-SUPPORT rate 0.11", no warnings |
| e | CLI `src.main verify` with the real model | **PASS**: validated config loaded (tau 0.6); claim #100 + its cited abstract → SUPPORTS 0.85 with the gold rationale sentence shown |
| f | every `provenance.git_commit` is on `origin/main` | **PASS**: `a999d1f` (a merge commit of PR #12 on `origin/main`, not a local merge) |
| g | `provenance.versions.rank_bm25` | **KNOWN BUG, confirmed, not fixed**: it is `null` because `rank_bm25` has no `__version__`; `importlib.metadata.version("rank-bm25")` returns `0.2.2` |
| - | tau tuned on train, `leak: false`; `claims_test.jsonl` never read | **PASS** |

Other small issues found:
* `data.dir` is recorded as `data\scifact` on Windows (cosmetic).
* In `errors.md`, "top retrieved" shows the rank-1 title but "sentences the verifier saw" come from the *driver*
  paper, which may be a different one. That is confusing when reading #100-style errors.
* `cross-encoder/ms-marco-MiniLM-L-6-v2` has been renamed on the Hub to `cross-encoder/ms-marco-MiniLM-L6-v2`. The old id still redirects.

## 8. Not verified

* The app was checked headlessly (Streamlit AppTest runs the real app script and deployed config). Browser rendering
  was **not verified**.
* Latency is a single wall-clock measurement on one laptop.
* No CI on the oracle ablations.
* Whether the 30 "gold-NEI but committed via an uncited paper" cases are mostly correct judgements: only #1099/#1100
  were read.
* The human error taxonomy in `errors.md` (read ≥ 20 errors, fill "your category") is not done. Section 4's categories
  come from about 15 examples.
* `finetuned_nli` was not run.

## Reproduce

```bash
python -m data.fetch_scifact
python -m eval.run_eval --name majority --retriever bm25 --verifier majority
python -m eval.run_eval --name lexical --retriever bm25 --verifier lexical --oracle --compare-with eval/results/majority
python -m eval.run_eval --name zero_shot_nli --retriever bm25 --verifier nli --oracle --compare-with eval/results/majority --compare-with eval/results/lexical --promote
python -m eval.run_eval --name hybrid_nli --retriever hybrid --verifier nli --oracle --compare-with eval/results/zero_shot_nli --compare-with eval/results/lexical --compare-with eval/results/majority
python -m eval.error_analysis --run eval/results/<run>      # lexical, zero_shot_nli, hybrid_nli
python -m eval.plots --run zero_shot_nli                    # -> eval/results/figures/
```
