---
team: CiteCheck
session: 08
date: 2026-10-27
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
  metric: "Claim-level macro-F1 on SciFact dev, end-to-end (retrieve, then verify); tau tuned on train"
  value: "0.603 (95% CI 0.545-0.660), from eval/results/zero_shot_nli (verifier unchanged this week)"
  previous: "0.603 (Session 7; the same deployed run)"
---

## Shipped this week
- **The product is deployed**: https://citecheck-877770798089.us-east4.run.app, live since 2026-10-26. Anyone can sign in with a code e-mailed to them, choose what we may keep (both consent boxes start unticked), check a draft or a PDF with its reference list, search papers for a research direction, see their history and download a report. Hosting is Google Cloud Run on the free trial, the database and sign-in are Supabase's free plan, e-mail goes through a team Gmail account: $0 in total. Hugging Face now charges for Docker Spaces, and free hosts such as Render give 512 MB while the site needs about 2 GB, so we moved the deployment plan to Cloud Run  (evidence: the live site; PR #34, PR #35, PR #37)
- The website itself: React front end, FastAPI back end around the existing agent, draft checks that run in the background with live progress, per-user rate limits, consent-gated activity log, and an admin research export with salted-hash ids and no free text  (evidence: PR #34, `deploy/WEB.md`)
- Website clean-up and upkeep: simpler landing page, sign-in on Supabase's new publishable keys (the legacy keys retire in 2026), react-router 6.30.6 (fixes a high-severity redirect advisory), sign-in redirects limited to pages on this site, fonts served by the site instead of Google Fonts  (evidence: PR #35)
- Fixes from the first live run of the agent: full text is read even when no abstract exists, Unpaywall PDF links are tried in order, confidences shown as "≥ 0.99" instead of "1.00"  (evidence: PR #33)
- Fit/calibration split of SciFact train (647 fit / 162 calibration, stratified by label, seed 13), the first E3 run on SciFact dev and a hand-check of the cases the automatic score cannot judge  (evidence: PR #32, `data/splits/scifact_train_v1.json`, `eval/results/agent_swap_dev/`)
- Hosting made reproducible: torch 2.8.0, transformers 4.57.6 and sentence-transformers 5.1.2 pinned to the versions the reported numbers came from, the sign-in page also accepts codes of 6 to 10 digits as a safeguard, and `deploy/GCP.md` documents the Cloud Run setup, costs, updates and shutdown. The live image was built from `main` at 13224ed with the same pins applied in the build. Sign-in on the live site uses 6-digit codes; the 6-to-10-digit safeguard arrives with the next redeploy  (evidence: PR #37)
- Evidence that the live site runs the evaluated verifier: the first live source check (left out of PR #32) and the same example draft checked on a laptop and on the deployed site, with both raw reports  (evidence: PR #36, `docs/live_checks/`)

## User evidence
- None this week: no outside participant used the running product. The site went live on the afternoon of 2026-10-26, and only the team has used it so far, which does not count. 
- No raw user artifact this week. The deployment's own check, which is not user evidence, is in `docs/live_checks/2026-10-26_deployed_vs_local.md` with both raw reports.
- What we changed as a result: the blocker named in Session 7 (no deployed app) is gone. Participants now need only the link and an e-mail address, and the research export captures what consenting participants do, so a session's raw log no longer has to be saved by hand.

## Metrics snapshot
- Claim-level macro-F1: 0.603 (was 0.603), 95% bootstrap CI 0.545-0.660 (`eval/results/zero_shot_nli/results.json`). Unchanged: the verifier is the same zero-shot model; no fine-tuned model exists yet.
- False-SUPPORT rate (guardrail): 0.108 (was 0.108)
- **E3 swap test, first run** (new; SciFact dev, the 124 SUPPORT claims, each made to cite a wrong but plausible paper; `eval/results/agent_swap_dev/`):
  - wrong citation flagged: 0.911 [0.848, 0.950] (113/124)
  - wrong citation kept as "supports": 0.089 (11/124); after the hand-check, 0.040 [0.017, 0.091] (5/124), because 6 of the 11 "wrong" papers do support the claim
  - bad replacement suggestions after the hand-check: 0.053 [0.018, 0.144] (3/57). Target: at most 0.10. The point estimate meets it, but the interval reaches 0.144, so with 57 suggestions it is not yet shown
  - control, the correct paper cited: kept as "supports" only 0.516 [0.429, 0.602] (64/124), so the agent questions about half of correct citations
  - the 18 hand-check judgements were drafted with AI assistance and checked one by one by Data & Evaluation (`eval/results/agent_swap_dev/review_sheet.csv`)
- Live source check (2026-10-23, no API keys): 5 of 6 paper lookups returned an abstract; 4 of 5 planned sources answered; Semantic Scholar search answered HTTP 429 without a key
- Deployed vs local, the same example draft: 4 of 4 checkable citations got the same verdict and the same confidence (`docs/live_checks/2026-10-26_deployed_vs_local.md`, PR #36)
- User tests: 0 participants (target: at least 3 per week)
- Measured on: SciFact dev (300 claims; E3 on its 124 SUPPORT claims); tau tuned on train, never on dev. Tau strict (0.85) is still a placeholder, not yet tuned on the calibration part
- Is this the same model that is running in the product? **Yes**: the deployed site runs `zero_shot_nli` at tau 0.6 (`eval/results/deployed_config.json`), with the library versions recorded in that run's provenance (torch 2.8.0, transformers 4.57.6; pinned in PR #37), and the parity check above gives identical verdicts. The agent's own decisions (full-text reading, suggestions) are measured only by E3 so far

## What did not work
- Deploying took the whole week; recruiting did not start in parallel, and it should have.
- **A flaw in our own reproducibility.** The Docker image pinned torch 2.5.1 while the reported numbers were produced with torch 2.8.0, and `transformers` was not pinned at all. The first cloud build installed transformers 5.x, which needs torch 2.6 or newer, silently disabled PyTorch and failed. Had it not failed, the site could have run library versions we never evaluated. Fixed by pinning torch, transformers and sentence-transformers to the versions in the results' provenance (PR #37).
- **The agent questions half of the correct citations** (E3 control: 0.516 kept). For a writer this is the main annoyance: many "not enough evidence" answers on citations that are fine.
- **A clear verifier error in the example draft.** For "the base Transformer uses 8 parallel attention heads", the agent read the arXiv PDF and found "In this work we employ h = 8 parallel attention layers, or heads", and the verifier still answered "not enough evidence" (0.93). Retrieval worked; the verifier is the bottleneck, as the agent plan says.
- **Plan change forced by a free tier.** The Hugging Face Space we prepared in Session 7 now needs a paid plan, so that work was not used. The Google Cloud trial also ends (2027-01-25, or earlier if the $300 credit runs out).
- On the deployed site, one replacement search returned no candidates where the local run found five. Most likely the paper APIs throttle shared cloud addresses without a key; not yet confirmed.
- The first deployed sign-in failed: Supabase sent 8-digit codes and the page had six boxes. Setting Supabase back to 6-digit codes fixed it at once, and sign-in on the live site uses 6-digit codes now; the page will also accept 6–10 digits from the next redeploy (PR #37).
- Filing error: the live source check files were left out of PR #32, although its commit message mentions them. They are added in PR #36.
- Session 7 planned the first fine-tuning runs (E1) and the real-world set candidates for this week. Neither started.

## Challenges / blockers
- Recruiting at least 3 outside participants a week, and committing their raw evidence the same day.
- Free-tier limits: the trial credit (about $110 a month with the site always on; we can let it sleep between test sessions to save credit); paper-API rate limits on shared cloud addresses (free Semantic Scholar and OpenAlex keys requested next); Supabase pauses a free project after a week without activity.
- Fine-tuning (E1) moves to Data & Evaluation and starts this week. To keep our rule that whoever trains a model does not score it, another member runs the dev evaluation on the shared checkpoint, against the E1 target written in Session 7.

## Next week's goal
- At least 3 outside participants each check a paragraph of their own writing on the live site, with a task-test record and the anonymised research export committed the same day in `evidence/session09/`.

## Individual contributions
- Vyom (Product): no visible repo work this week  
- Sakshaat (Engineering): the website (front end, back end, sign-in, consent, history, research export), its clean-up and security update, fixes from the first live run; version pins, flexible sign-in codes and the Cloud Run guide; reviewed and merged PR #32 and PR #36  (evidence: PR #34, PR #35, PR #33, PR #37)
- Sahil (Data&Eval): fit/calibration split, first E3 run and its hand-check; live source check and deployed-vs-local parity check; set up and deployed the site on Google Cloud with the Supabase database and sign-in; reviewed and merged PRs #33 to #35 and #37  (evidence: PR #32, PR #36, the live site)
- Ritika (Users&Research): Session 8 report, reaching out to people on campus to market our product. No visible repo work this week.

## Lean canvas changes (if any)
- Not applied to `lean-canvas.md` this week. Proposed for Product to apply:
  - **Channels**: a public link with e-mail sign-in
  - **Cost structure**: hosting $0 on free tiers (Cloud Run trial credit, Supabase free plan, Gmail sender); the verifier runs on CPU, so a check costs no API fees
  - **Key risk**: dependence on free tiers that change without notice (Hugging Face Docker Spaces became paid this year; the cloud trial ends 2027-01-25; paper APIs rate-limit shared cloud addresses)
