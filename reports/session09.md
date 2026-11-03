---
team: CiteCheck
session: 09
date: 2026-11-03
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
  value: "0.736 (95% CI 0.684-0.784), from eval/results/finetuned_nli_selector_v2_capped; re-scored independently with identical predictions in eval/results/finetuned_rescore_pinned"
  previous: "0.603 (Session 8; eval/results/zero_shot_nli)"
---

## Shipped this week
- **A fine-tuned verifier with a learned evidence selector (E1), merged and promoted.** The DeBERTa-v3-base NLI model is fine-tuned on SciFact train (609 claims for training; 200 held out to tune tau and pick the best epoch), and a second fine-tuned model (a cross-encoder) picks the three evidence sentences it reads. Both models are public on Hugging Face, and `eval/results/deployed_config.json` now points to them. The E1 target written in Session 7 is met: macro-F1 0.736 vs 0.603, paired-bootstrap CI of the gain [+0.078, +0.186], false-SUPPORT 0.091 (ceiling 0.108)  (evidence: PR #39, `eval/results/finetuned_nli_selector_v2_capped/`)
- **Independent re-score of the promoted model**, keeping our rule that whoever trains a model does not score it: re-run on a laptop CPU with the versions the site pins (torch 2.8.0, transformers 4.57.6), it gives identical predictions to the training-side GPU run (difference +0.000)  (evidence: PR #40, `eval/results/finetuned_rescore_pinned/`)
- **The live site now runs the fine-tuned model**: https://citecheck-877770798089.us-east4.run.app, redeployed on 2026-11-03 shortly before 16:00 ET (Cloud Run revision `citecheck-00003-2m5`, built from `main` at 0597229)  (evidence: PR #41, the live site, `docs/live_checks/2026-11-03_example_live_finetuned.md`). PR #41 changed two files:
  - `Dockerfile.web`: the image now loads the promoted verifier and the sentence selector at build time, so both are baked in, and a model that cannot load fails the build instead of letting the site fall back silently to the demo backend  (evidence: PR #41)
  - About page: the new numbers (macro-F1 0.74, 95% CI 0.68-0.78; 9% wrongly "supported", against 0.60 and 11% for the model it replaced), a note that the model was picked among several versions tried on the same claims so its true score is probably a little lower, the "concern about half of correct citations" figure marked as the previous model's and being re-measured, and the verifier described as fine-tuned by the team with a second model that picks the evidence sentences  (evidence: PR #41)
- Experiments that are merged but off in the product: evidence units (whole abstract, single sentences), a larger fine-tuned model, a real-citation collector with 80 citing-sentence pairs and AI-drafted labels (unreviewed), a citation-context gate and LLM claim extraction. Each is behind a switch and off by default  (evidence: PR #39, commit 431de11, `data/realcite/README.md`)

## User evidence
- None this week: no outside participant used the running product. This is the fifth report in a row without user evidence (Session 5, the midterm, Session 7, Session 8, Session 9).
- No raw user artifact this week. Team members used the live site to check that feedback and activity are stored as designed; that is not user evidence, but it found the data-collection and paper-search problems listed under "What did not work".
- What we changed as a result: nothing in the product yet. Next week is given over to user sessions, with at least 10 outside participants, and the data-collection fixes go in first so each participant's judgement is recorded per citation (plan under "Next week's goal").

## Metrics snapshot
- Claim-level macro-F1: **0.736** (was 0.603), 95% bootstrap CI 0.684-0.784 (`eval/results/finetuned_nli_selector_v2_capped/results.json`)
- False-SUPPORT rate (guardrail): **0.091** (was 0.108)
- Gain over the zero-shot verifier: +0.133, 95% CI [+0.078, +0.186], paired bootstrap on the same 300 dev claims
- Independent re-score: macro-F1 0.736 [0.684, 0.784], false-SUPPORT 0.091, identical predictions (`eval/results/finetuned_rescore_pinned/results.json`)
- Evidence selection: a complete gold rationale is among the 3 selected sentences for 0.938 of 209 gold papers
- Variants scored on dev, and why they were not promoted:
  - `finetuned_nli_large`: 0.720 [0.663, 0.774], but false-SUPPORT 0.125, above the ceiling
  - `finetuned_nli_selector_v2` (tau 0.1): 0.729 [0.676, 0.780], false-SUPPORT 0.142; the promoted run is the same model with tau tuned under a false-SUPPORT cap of 0.10
  - `finetuned_nli_sentence` (one sentence at a time): 0.696 [0.640, 0.748], false-SUPPORT 0.227
  - `finetuned_nli`, no learned selector: 0.693 [0.636, 0.749], false-SUPPORT 0.068
- Speed on the same laptop CPU: verification 1.80 s per claim, vs 0.46 s for the zero-shot run (about 4 times slower, probably because the selector scores every sentence of each retrieved abstract). Not yet measured on the 2-vCPU site
- Live example on the new model (the site's built-in draft, one run, not an accuracy measurement): the error named in Session 8 is fixed. For "the base Transformer uses 8 parallel attention heads", the zero-shot verifier answered "not enough evidence" (0.93) after reading the full text; the fine-tuned one answers "supported" (0.81) from the sentence "In this work we employ h = 8 parallel attention layers, or heads". The other three checkable citations got the same verdicts as in Session 8. The 5-citation example took about 45 s on the site, timed by hand
- E3 swap test: not re-run with the new verifier; the Session 8 E3 numbers still describe the zero-shot verifier
- User tests: 0 participants (target: at least 3 per week)
- Measured on: SciFact dev (300 claims). Tau tuned on 200 held-out train claims, never on dev. The choice among the eight fine-tuned variants was made on dev, so 0.736 is somewhat optimistic
- Is this the same model that is running in the product? **Yes, since 2026-11-03 shortly before 16:00 ET.** The report the live site produced for its built-in example names `nli:hassanedwan/citecheck-nli-ft-base-sel` at threshold 0.5, the promoted run in `eval/results/deployed_config.json` (`docs/live_checks/2026-11-03_example_live_finetuned.md`), and the image pins the library versions the independent re-score used. Anything the site produced before that time came from the zero-shot verifier

## What did not work
- **No outside user, for the fifth report in a row.** The site has been live since 2026-10-26 and no outside session has been run on it yet.
- **Correction to Session 8.** We wrote that fine-tuning (E1) had not started. It had: most of it was done in a fork between 2026-10-11 and 2026-10-16, and the team learned of it only when PR #39 arrived this week, because work in progress was not visible in the shared repo. From now on, work in progress goes up as a draft PR the day it starts.
- **The headline number is optimistic.** Eight fine-tuned variants were scored on the same 300 dev claims and the best safe one was promoted, so its dev score is a little inflated. We have no untouched labelled test set; the reviewed real-citation set will be the first.
- **Bigger was not safer.** The large fine-tuned model scored 0.720 but called 12.5% of non-supporting claims "supported", above our 10.8% ceiling. Judging single sentences scored 0.696 with false-SUPPORT 0.227.
- **The new verifier is about 4 times slower** (1.80 s vs 0.46 s per claim on the same CPU). A 20-citation draft needs about 36 s for verification alone, before any full-text reading; the 5-citation example already takes about 45 s on the site.
- **Real citations look much harder than SciFact (not a result yet).** On the 40 held-out real citing sentences, with AI-drafted labels that no person has reviewed, the fine-tuned verifier (without the selector) reached macro-F1 0.278 [0.183, 0.360] and recognised 4 of 15 supported pairs, and 21 of 80 citing contexts were not checkable claims at all (`eval/results/realcite_audit_v2/`). If review confirms this, our SciFact numbers overstate how CiteCheck does on real writing.
- **Our usage data cannot answer our questions yet** (found while checking the live site):
  - a 👎 is saved only if the person also presses "Send", so disagreement is under-counted
  - the research export cannot link a 👎 to the verdict it was about
  - checks do not record which model produced them, which matters now that the model changes
  - team accounts are not separated from participants
  - paper search has no way to mark a result as useful
- **The paper services still fail from the cloud.** In the live example after the redeploy, Semantic Scholar answered HTTP 429 for one citation and the replacement search found no candidates, as in Session 8. The free API keys are still not added.
- **Paper search returned 4 papers when 20 were asked for.** On the live site, OpenAlex and Semantic Scholar did not answer (no API keys on shared cloud addresses), and the arXiv query required every one of the first six words of the description, including filler such as "working". The ranking also matched filler words ("now", "good").
- Filing error: the `tools/preflight.py` fix for result folders without a claim-level F1 (the E3 run) was left out of PR #38; it is added with this report.

## Challenges / blockers
- Recruiting 10 outside participants in one week and committing their raw evidence the same day. We have not yet run a single session on the live site, so the plan depends on every member finding two people.
- Reviewing the 80 real-citation labels: two teammates, at least 15 shared pairs for Cohen's kappa (target 0.6 or higher), before any real-citation number is reported.
- Speed of the new verifier on the site's 2 vCPUs, within the trial credit.
- Free Semantic Scholar and OpenAlex API keys are still not added to the site.

## Next week's goal
- **At least 10 outside participants use the live site**, now running the fine-tuned model, in a 15-20 minute session each between 2026-11-04 and 2026-11-09, with the task-test record, notes taken during the session and a dated screenshot committed the same day in `evidence/session10/`. The plan:
  - **Who**: people outside the team who read or cite papers: graduate students and research assistants in other groups, classmates outside our team, friends in research programmes. Each of the five members recruits two.
  - **Session**: the consent script from `evidence/templates/` and a participant code (P01-P10, no names), then three tasks: (T1) check a paragraph of their own writing with its references and say, for each verdict, whether it is right; (T2) find papers for their own research direction and say which are useful; (T3) answer "Would you check your citations with this before submitting? (1-5)" and why.
  - **What we record**: whether each task was completed and how long it took, the participant's judgement next to CiteCheck's verdict for every citation, the 1-5 answer and their main complaint, and the anonymised research export at the end of each day.
  - **Before the sessions (by 2026-11-05)**: the feedback fixes listed under "What did not work" (a 👎 saved on the first click, the right answer asked for, the model version stored with each check, a participant code, team accounts kept out) and the paper-search query fix are deployed. Sessions held before that rely on the facilitator's sheet.
  - **What we want to learn**: whether researchers agree with and act on the verdicts (which flagged citations they would change), and what would stop them from using CiteCheck.
  - **Roles**: Users & Research schedules the sessions and runs most of them; Product writes the task cards and closing questions and turns the findings into lean-canvas changes; Engineering ships the feedback fixes; Data & Evaluation reports agreement by verdict type; Operations checks that each session's evidence is committed the same day.

## Individual contributions
- Vyom (Product): writes the task cards and closing questions for the user sessions and applies the lean-canvas changes
- Sakshaat (Engineering): put the fine-tuned model on the site: the image now loads both fine-tuned models at build time, so a model that cannot load fails the build instead of the site silently falling back to the demo backend; rewrote the About page's "How well it does" and "Data and models" sections for the new model, with its caveats; reviewed and merged PR #40  (evidence: PR #41, PR #40)
- Sahil (Data&Eval): reviewed PR #39 (results, the tau-tuning leak guard, provenance) and merged it; re-scored the promoted model independently under the site's pinned versions; redeployed the site with the new model and checked it with the built-in example; checked feedback storage and paper search on the live site; this report and the preflight fix  (evidence: PR #39 review, PR #40, `docs/live_checks/2026-11-03_example_live_finetuned.md`)
- Ritika (Users&Research): next week, leads the user study: recruiting, scheduling and running the sessions, and committing the evidence the same day
- Hassan (Operations): fine-tuned verifiers (base and large) and the learned sentence selector, safety-capped tau tuning, evidence-unit experiments, the real-citation collector with draft labels, the citation-context gate, and the Colab notebook  (evidence: PR #39)

## Lean canvas changes (if any)
- Not applied to `lean-canvas.md` this week. Proposed for Product to apply:
  - **Solution**: a verifier fine-tuned on scientific claims, with a learned step that picks the evidence sentences (0.74 vs 0.60 macro-F1 on SciFact dev)
  - **Key metrics**: add a user-side number next to macro-F1: the share of flagged citations that users agree were real problems
  - **Cost structure**: still $0 per request (CPU only), but each citation now takes about 1.8 s to verify
  - **Key risk**: real citing sentences are harder than SciFact's rewritten claims (first, unreviewed look above)
