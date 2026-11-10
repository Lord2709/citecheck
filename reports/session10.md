---
team: CiteCheck
session: 10
date: 2026-11-10
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
  - name: Hassan
    github: hassan-edwan
    hat: Operations
north_star:
  metric: "Claim-level macro-F1 on SciFact dev, end-to-end (retrieve, then verify); tau tuned on held-out train claims"
  value: "0.736 (95% CI 0.684-0.784), from eval/results/finetuned_nli_selector_v2_capped (model unchanged this week)"
  previous: "0.736 (Session 9; the same deployed run)"
---

## Shipped this week
- **No product change was merged this week.** The live site kept running the fine-tuned model deployed on 2026-11-03, and that is the version both participants used  (evidence: PR #41, PR #42, https://citecheck-877770798089.us-east4.run.app)
- **The first usage data from people outside the team**, exported from the site's database with codes instead of names and committed with this report  (evidence: `evidence/session10/`, https://citecheck-877770798089.us-east4.run.app)

## User evidence
- Two people outside the team used the live site on their own writing: U02 on 2026-11-04 (about 14 minutes) and U03 on 2026-11-10 (about 16 minutes). Both signed in, ticked both consent boxes, checked a paragraph with its references and searched for papers. A third account in the same export (U01) is the team's test account and is not counted.
- **Raw artifact**: `evidence/session10/README.md`, `evidence/session10/people.csv`, `evidence/session10/checks.csv`, `evidence/session10/votes.csv`, `evidence/session10/activity.csv` (the site's timestamped usage logs, exported 2026-11-10; the sentences participants pasted are left out)
- What happened:
  - **U02** pasted a paragraph on deep-learning vulnerability detection. The first two checks finished in under a second with all 6 citations unresolved: the paragraph used plain-number citation markers, and a reference-list line was read as a citing sentence. The third paste worked: of 5 citations, 1 supported, 1 not enough evidence and 3 could not be checked, in 60 s. U02 marked all five 👍, searched for papers three times (10, 0 and 10 results) and opened two of them.
  - **U03** checked a paragraph on LLM agents for network management (6 citations to 3 papers) in 101 s: 4 not enough evidence, 1 supported at confidence 0.502 (the threshold is 0.5) and 1 contradicted. U03 gave no 👍/👎, so we do not know whether these verdicts were right. Two paper searches: 0 results, then 10.
- What the participants asked for (told to the team after their sessions; not written down during them, so not in the logs):
  - **Two input boxes: one for the text with its citations, one for the reference list.** Today the site finds the reference list only after a line that says "References" (`src/claims.py`); without that line no citation can be matched to a paper. This fits U02's first two attempts, which read nothing.
  - **A way to mark each paper in "Find papers" as relevant or not to their research direction.** Today a search result can only be opened; the site has no way to record whether it helped.
- What we changed as a result: nothing in the product yet. Both requests are now planned for next week, with the fix for plain-number citation markers and the feedback fixes, and each session will ask the participant about every verdict.

## Metrics snapshot
- Claim-level macro-F1: 0.736 (was 0.736), 95% bootstrap CI 0.684-0.784 (`eval/results/finetuned_nli_selector_v2_capped/results.json`). Unchanged: no new model this week
- False-SUPPORT rate (guardrail): 0.091 (was 0.091)
- Outside participants: **2** (was 0; target 10)
- Draft checks by participants: 4, of which 2 read no citation at all (U02's first two attempts)
- Citations in the participants' working checks: 11. Supported 2, not enough evidence 5, contradicted 1, could not check 3
- Participants' judgements: 5 👍 and no 👎, all from U02, 3 of them on "could not check" results. U03 gave none. Too few to measure agreement
- Time to a result on the live site: 60 s for 5 citations (U02) and 101 s for 6 (U03)
- Paper search: 2 of the participants' 5 searches returned no papers
- Measured on: SciFact dev (300 claims) for the model; the site's own logs for the usage numbers
- Is this the same model that is running in the product? **Yes.** Both participants used the site after the 2026-11-03 redeploy, which runs `nli:hassanedwan/citecheck-nli-ft-base-sel` at tau 0.5, the run in `eval/results/deployed_config.json` (`docs/live_checks/2026-11-03_example_live_finetuned.md`)

## What did not work
- **Nothing was merged this week.** The feedback fixes planned for 2026-11-05 were not built, so the site still cannot record a judgement unless the participant clicks it; U03 left none.
- **Reading references failed on the first outside paragraph we got.** U02's text used plain-number markers, and a reference-list line was treated as a citing sentence; the site finds the reference list only after a "References" line, which participants do not always write. Two of three attempts read nothing and still reported "done" in under a second, with no message saying why.
- **Paper search found nothing in 2 of 5 participant searches.** The free Semantic Scholar and OpenAlex keys are still not added to the site.
- **Verdicts on real writing are mostly "not enough evidence"** (5 of the 8 citations that could be checked), as the first look at real citations in Session 9 suggested. U03's only "supported" was at confidence 0.502, just above the threshold; with uncalibrated scores, a verdict that close should probably be shown as uncertain.
- **A sentence that cites two papers is judged as a whole against each paper** (team test account, 2026-11-03, two 👎 with comments in `evidence/session10/votes.csv`): a sentence with a UK Biobank clause [4] and a Cox regression clause [5] got "not enough evidence" for both, although each paper supports its own clause.

## Challenges / blockers
- Recruiting: two people in a week. Each member needs to bring two participants and sit with them, so that every session has notes.
- Getting a judgement on every verdict: until the feedback fixes ship, the person running the session has to ask and write it down.
- No code was merged this week; the fixes above need Engineering time early in the week.

## Next week's goal
- At least 8 more outside participants (10 in total), each in a session with notes taken during it and the participant's judgement on every verdict, committed the same day in `evidence/session11/`. Before the sessions: ship the feedback fixes, a separate box for the reference list, relevant / not relevant buttons on paper-search results, and the fix for plain-number citation markers.

## Individual contributions
- Vyom (Product): next week, the task cards and closing questions for the sessions
- Sakshaat (Engineering): next week, the feedback fixes, the separate reference-list box, relevance buttons in "Find papers" and the plain-number citation-marker fix 
- Sahil (Data&Eval): exported the usage data from the site's database, removed what could identify a participant or their unpublished text, analysed the participants' checks, and wrote this report  
- Ritika (Users&Research): next week, recruiting and running the sessions with notes
- Hassan (Operations): next week, checking that each session's evidence is committed the same day

## Lean canvas changes (if any)
- None applied this week. The first outside use supports the key risk named in Session 9: on real writing, most citations end as "not enough evidence" or cannot be checked at all.
