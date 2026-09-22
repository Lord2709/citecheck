---
team: CiteCheck
session: 04
date: 2026-09-22
members:
  - name: Vyom
    github: vyom-1908
    hat: Product
  - name: Sakshaat
    github: SakshaatRaut
    hat: Engineering
  - name: Sahil
    github: Lord2709
    hat: Data&Eval
  - name: Ritika
    github: ritikakarande
    hat: Users&Research
north_star:
  metric: Citation-support F1 (SciFact/SciFact-Open) vs. zero-shot baseline
  value: not yet measured
  previous: n/a (first report)
---

## Shipped this week
- Repo scaffolding (`src/`, `data/`, `eval/`) merged to `main` (PR #3)
- Problem statement, users, and value proposition written into the README (PR #1, PR #2)
- Lean canvas committed (issue #5, PR #7)
- A first BM25 retrieval baseline (`data/fetch_parser.py` pulls a small arXiv sample, `src/retrieval.py` indexes and ranks it with `rank_bm25`) (PR #4)
- Session 5 todo list committed so next week's work is scoped before it starts (PR #6)

This is repo setup and a first retrieval script, not a working product yet. `src/main.py` is still a placeholder that does not call `retrieval.py`, and the arXiv sample corpus (`data/sample_papers.json`) that the script reads is not committed, so nothing here is runnable end to end from a clean checkout.

## User evidence
None this week. There is no running product yet to put in front of a user, so no session recording, usage log, or task test exists to commit.

> We know an interview or a reaction to a mockup would not count even if we had one. We have not done that either. This is the one area we are behind on, and it is the top priority for next week: recruit 3 users and get a task test in front of the running pipeline (see session 5 todo).

## Metrics snapshot
- Citation-support F1: not measured. `eval/` is scaffolded but empty; the zero-shot baseline has not been run against SciFact dev.
- Retrieval precision@k: not measured. The BM25 script has only been smoke-tested manually against a small arXiv keyword sample, not SciFact.
- Is this the same model running in the product? No product exists yet to compare against.

## What did not work
- We spent the week on scaffolding and a first retrieval pass rather than a runnable pipeline, so we have no metric and no user evidence to report in our first week, both of which are graded criteria.
- The BM25 baseline was built and tested against a generic arXiv keyword-search sample rather than SciFact, so it does not yet connect to the north-star metric we committed to in the lean canvas.
- We have not touched user recruitment yet. Cold outreach was called out as an immediate action item when we scoped the project, and it still has not started.

## Challenges / blockers
- Need to verify branch protection on `main` (one approving review required) is actually turned on before Session 4; all six PRs merged this week were reviewed by a teammate, but we have not confirmed the repository setting itself.
- No eval harness yet, so we cannot tell if retrieval or classification will be the bottleneck once the classifier exists.
- User recruitment has not started; we need to settle outreach channels (UMD labs, academic Discord/Slack) and start this week, not next.

## Next week's goal
Ship a runnable end-to-end pipeline (DOI/link → retrieval → verdict) behind a minimal Streamlit/Gradio UI, get a zero-shot F1 baseline on SciFact dev into `eval/`, and run the first task test with a real user against the running product.

## Individual contributions
- Sahil (Data&Eval): README problem statement and value proposition (PR #1, #2); BM25 retrieval baseline and arXiv fetch script (PR #4)
- Sakshaat (Engineering): repo scaffolding (PR #3); reviewed PR #1, #2, #6
- Vyom (Product): lean canvas (issue #5, PR #7)
- Ritika (Users&Research): session 5 todo/work plan (PR #6); reviewed PR #3, #4

## Lean canvas changes (if any)
First version committed this week. Direction is finalized as CiteCheck (citation-support and relevance verification), replacing an earlier idea (ChartVoice, accessible alt-text for data visualizations) that we set aside before Session 3.
