# CiteCheck

A paper-judging tool for researchers. Submit a paper (link or DOI) along with a short note on your research direction, and get back a verdict on two things:

1. **Relevance** — does this paper actually fit your research direction?
2. **Citation support** — do the papers it cites genuinely support the claims they're attached to?

PDF upload is a possible future input method, still deciding on OCR handling.

## Who this is for

Students and researchers who read and cite papers weekly. Today they either skim abstracts and guess, or read full papers to check relevance, and when writing their own work, they cite sources without an easy way to verify the cited paper actually supports the claim it's attached to.

## Why this over the alternatives

- Manually reading full papers doesn't scale past a handful a week
- Google Scholar / Semantic Scholar surface papers but don't judge fit to a specific research direction or check citation support
- Asking a chatbot directly isn't grounded in retrieval and can hallucinate support that isn't there

CiteCheck is narrower and grounded: retrieval-backed verdicts, not open-ended summaries.

**Value proposition:** We help researchers judge whether a paper is worth reading and whether its citations hold up, faster than reading it themselves or trusting an ungrounded chatbot summary.

## North-star metric

F1 on citation-support judgments (SciFact / SciFact-Open) vs. a zero-shot baseline. Retrieval quality tracked separately via precision@k.

## Team

| Hat | Owner | Accountable for |
|---|---|---|
| Product | Vyom | The user, the roadmap, the lean canvas, the pitch |
| Engineering | Sakshaat | Architecture, code review, repo health, deployment |
| Data and Evaluation | Sahil | Data and licensing, the evaluation harness, metrics, error analysis |
| Users and Research | Ritika | Recruiting users, running sessions, capturing raw evidence |

## Repo structure

- `data/` — corpus and dataset handling
- `eval/` — evaluation harness and metrics
- `src/` — core pipeline (retrieval, classifier, inference)
- `reports/` — weekly progress reports (`sessionNN.md`)

## Status

Early stage. Problem statement and team roles are set. NLP pipeline and evaluation are in progress, see open issues and `reports/` for current state.
