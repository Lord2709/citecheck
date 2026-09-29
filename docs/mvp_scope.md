# MVP scope (for the Oct 6 mid-semester demo)

Owner: Product (Vyom).  **Status: proposed by the Session 5 drop; Vyom edits and owns.**  Answers the Session 5 todo:
"what's in, what's out."

## The one job

> **Check whether the paper I cite really supports my claim, and show me the sentences that decide it.**

Everything in the MVP serves that sentence. The lean canvas lists three ideas (relevance, citation support, PDF upload);
risk #5 in the canvas already says a broad MVP is dangerous. We commit to the first job and ship the others only as clearly
labelled secondary features.

## In (must work in the live demo)

| Feature | Acceptance test (what a stranger must be able to do) |
|---|---|
| **Check a citation**: claim + the paper (DOI / arXiv / link, or a pasted abstract) -> SUPPORTS / CONTRADICTS / NOT ENOUGH EVIDENCE | Given a claim and an abstract, a first-time user reaches a verdict in under 2 minutes with no help |
| **Evidence shown with every verdict** (the sentences the model used, per-paper probabilities) | The user can point at the sentence that convinced them |
| **Abstains when unsure** (threshold tuned on train data) | On claims the abstract does not address, the tool says NOT ENOUGH EVIDENCE instead of guessing |
| **Honest status banner**: validated dev score, or DEMO / UNVALIDATED warning | The sidebar never claims a score the running model did not earn |
| **Agree / disagree button per verdict** + usage log | Every user test leaves a timestamped log with agreement clicks |
| **Search the SciFact corpus** when no paper is given | Works offline once data is downloaded |

## Secondary (built, labelled, not promoted in the pitch)

* **Is this paper relevant to my direction?** Transparent overlap score with matched terms; bands are uncalibrated.
* **Audit a paper's citations (experimental).** Needs Semantic Scholar contexts; no gold labels exist for this setting.

## Out (say "not yet" out loud when asked)

PDF upload and OCR; full-text reading (we read abstracts only); non-biomedical validation; accounts and history;
batch upload of a whole manuscript; browser extension; summaries of papers; any claim that the tool proves a claim true.

## Definition of done for Oct 6

- [ ] App runs from `main` on the presenting laptop with the sidebar showing **Validated configuration**
- [ ] Live demo path works with **no internet** (paste-an-abstract) and a recorded backup exists
- [ ] Baseline ladder committed in `eval/results/` (majority, word-overlap, zero-shot NLI) with CIs
- [ ] >= 3 outside participants' task tests committed (`evidence/session05/` and any later session)
- [ ] Pivot/persevere decision written with the rules in `docs/midterm_oct6.md` applied honestly
