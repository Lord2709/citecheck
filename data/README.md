# Data card: CiteCheck

Owner: Data & Evaluation (Sahil).  Last reviewed: 2026-09-29.

## What we use

| Dataset | What it is | Why we use it | License |
|---|---|---|---|
| **SciFact** (Wadden et al., EMNLP 2020, arXiv:2004.14974) | ~1.4k expert-written scientific claims, each labelled against the abstracts of the papers it cites, plus a corpus of ~5.2k abstracts | SciFact claims are *citation sentences re-written into atomic claims* and `cited_doc_ids` are the papers that citation pointed to. That is our exact product question: **does the cited paper support this claim?** | Claims + evidence annotations: **CC BY 4.0**. Abstracts (S2ORC): **ODC-By 1.0**. (Verified from `LICENSE.md` in github.com/allenai/scifact on 2026-09-28.) |
| **SciFact-Open** (Wadden et al., 2022) | Same task against a ~500k-abstract corpus | Stretch goal: a harder, more realistic retrieval test | see its repo before use |
| Pretrained models | NLI checkpoint `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, embedder `sentence-transformers/all-MiniLM-L6-v2`, reranker `cross-encoder/ms-marco-MiniLM-L-6-v2` | zero-shot verifier / retrieval | See "Model licenses" below (checked on each Hugging Face model card, 2026-09-29) |
| Live paper lookups (DOI / arXiv) | OpenAlex, Semantic Scholar, arXiv public APIs | letting a user check *their own* paper | API terms apply; we cache and never redistribute abstracts |

### Model licenses

Read from the `license:` field of each model card's metadata (README front-matter) and the Hugging Face
model API on **2026-09-29**. Only the model card's own declaration was checked; the licenses of the
datasets each model was trained on were **not verified**.

| Model | License on model card | Revision checked (commit sha) | Note |
|---|---|---|---|
| `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` | **MIT** | `6f5cf0a2b59c` | |
| `sentence-transformers/all-MiniLM-L6-v2` | **Apache-2.0** | `1110a243fdf4` | |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | **Apache-2.0** | `233902d25c44` | Repo was renamed to `cross-encoder/ms-marco-MiniLM-L6-v2`; the old id (used in `src/retrieval.py`) still redirects |

## Files (`data/scifact/`, created by `python -m data.fetch_scifact`)

`corpus.jsonl`, `claims_train.jsonl`, `claims_dev.jsonl`, `claims_test.jsonl`, and `MANIFEST.json`
(sha256 + row counts; **committed**).  The `.jsonl` files are git-ignored: re-download instead of
committing them.

Schema (from the SciFact repo):

```
corpus.jsonl  : {"doc_id": int, "title": str, "abstract": [sentence, ...], "structured": bool}
claims_*.jsonl: {"id": int, "claim": str,
                 "evidence": {doc_id: [{"label": "SUPPORT"|"CONTRADICT", "sentences": [int, ...]}]},
                 "cited_doc_ids": [int, ...]}
```

A claim with an **empty** `evidence` dict is *not enough information* (NEI).  `claims_test.jsonl`
has no `evidence` at all.

## Rules for the team

1. **train** = fitting and tuning (threshold tau, any fine-tuning).  **dev** = the one split we report
   on.  **test** = labels are hidden; we never use it.  `eval/run_eval.py` enforces this.
2. Never report a number from `tests/fixtures/**`; it is synthetic plumbing data.
3. Every reported number comes from a `eval/results/<run>/results.json`, which records data hashes,
   package versions, git commit and arguments.
4. Do not commit raw participant material (recordings with faces/voices, names, emails). Anonymize
   first (`tools/anonymize_log.py`) and see `evidence/README.md`.

## Known limitations and biases (say these out loud in the report and the talk)

* **Domain:** SciFact is biomedical/life-science. Results say nothing yet about CS, physics or social
  science papers. A general "citation checker" claim is not supported by this data.
* **Language and venue:** English abstracts, skewed to well-indexed, highly cited work.
* **Abstract-only:** evidence is judged from abstracts, not full text; claims whose support is in
  the methods/results sections are invisible to us (they show up as NEI).
* **Atomic claims:** SciFact claims were cleaned to be self-contained. Real citation sentences are
  messier (multiple claims, hedging, coreference). Expect a drop on real user text; the user task tests
  measure exactly that gap.
* **Small dev set (300):** a 95% bootstrap CI on macro-F1 is several points wide. We report it.
* **Label noise:** expert annotators disagree on some claims; error analysis should separate model
  errors from arguable gold labels.

## Personal data

SciFact contains published abstracts only. User claims typed into the app may contain unpublished ideas: the app logs claim *text* only in research mode with the participant's consent, and redacts e-mails/phone numbers (`src/text_utils.redact`).
