---
team: CiteCheck
session: 07
date: 2026-10-20
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
    github: "not yet added to the repository"
    hat: Operations
north_star:
  metric: "Claim-level macro-F1 on SciFact dev, end-to-end (retrieve, then verify); tau tuned on train"
  value: "0.603 (95% CI 0.545-0.660), from eval/results/zero_shot_nli (verifier unchanged this week)"
  previous: "0.603 (Session 5; the same deployed run)"
---

## Shipped this week
- CiteCheck is now an agent. Paste a draft with its reference list (or upload a text-based PDF) and it finds every cited sentence, resolves each reference to a DOI or arXiv id (Crossref when the entry has none, accepted only if the titles match), fetches the paper, verifies the sentence against the abstract with the evaluated verifier, reads the legal open-access full text when the verifier is unsure (arXiv, Europe PMC, Unpaywall), and suggests a paper that supports the sentence when a citation fails; every decision is shown with its reason  (evidence: PR #28)
- Discovery: describe a research direction and get ranked papers from OpenAlex, Semantic Scholar and arXiv, each with the sentence that makes it relevant; draft checks and paper lists download as a Markdown report  (evidence: PR #28)
- Scanned PDFs are refused at upload with a message offering to paste the text instead; OpenAlex API-key support; a live source checker; a Dockerfile and deployment guide for a free Hugging Face Space (not deployed yet)  (evidence: PR #28)
- Experiment targets for the agent and the fine-tuned verifier, committed before any agent evaluation run  (evidence: PR #30, `docs/north_star.md`)
- Agent evaluation harness: the E3 swap test on SciFact (offline) and the E2 escalation harness for the real-world set; fit/calibration split of SciFact train so a fine-tuned model is never calibrated on its own training claims (code merged; the split file is generated next week)  (evidence: PR #30)
- Post-midterm plan with both flowcharts, the agent's four decisions, experiments E1-E5, owners by hat and build order; lean canvas updated in place  (evidence: PR #29, `docs/agent_plan.md`)
- Real-world citation set tooling (real citing sentences from Semantic Scholar, labeller sheets, Cohen's kappa, merge) and a labelling guide; per-session log export used by the app's download button for hosted user tests  (evidence: PR #27)

## User evidence
- None this week: no outside participant used the running product. We did not schedule any sessions in time for this report. This is the third report without user evidence (Session 5, the midterm, Session 7).
- What we changed as a result: the app can now export each session's log from the browser, so sessions can run on a hosted copy over a video call (PR #27, PR #28), and the deployment guide is merged (PR #28). Deploying it and running at least three outside sessions is next week's goal.

## Metrics snapshot
- Claim-level macro-F1: 0.603 (was 0.603), 95% bootstrap CI 0.545-0.660 (`eval/results/zero_shot_nli/results.json`). Unchanged: the verifier is the same zero-shot model; fine-tuning starts next week.
- False-SUPPORT rate (guardrail): 0.108 (was 0.108)
- Agent-level metrics (E3 swap test, E2 escalation): not measured yet. The harness is merged (PR #30); the first E3 run on SciFact dev is planned for next week.
- User tests: none run this week
- Measured on: SciFact dev (300 claims); tau tuned on train claims, never on dev
- Is this the same model that is running in the product? Yes for the verifier (`eval/results/deployed_config.json`, run `zero_shot_nli`). The agent's own behaviour (full-text reading, suggested papers) is new and not yet evaluated; the app says so in its sidebar, and its strict suggestion threshold is a placeholder until it is tuned on the calibration part of train.

## What did not work
- A flaw in our own evaluation: `eval/run_eval.py` tuned tau on random train claims. Fine for a zero-shot model, but a model fine-tuned on train would have tau tuned on claims it was trained on. Fixed before any fine-tuning run with a fit/calibration split (PR #30).
- No user tests again (see User evidence).
- We did not run the agent evaluation (E3) or the live source check before the deadline, so the agent's network paths (OpenAlex, Semantic Scholar, arXiv, Crossref, Europe PMC, Unpaywall) are so far tested only against recorded responses, and the agent has no measured accuracy yet.
- The deployment files are merged but the app is not deployed yet.
- Scope cut: no OCR before Dec 1; scanned PDFs are refused at upload.

## Challenges / blockers
- The agent's suggestion threshold and escalation rule are not tuned yet; they need the calibration work planned for next week.
- Free-tier limits: OpenAlex meters searches with a daily budget, so the agent must cache results and spread searches across sources.
- Full text exists only for open-access papers; for the rest the agent reads only the abstract and says so.
- A hosted app wipes its log on restart, so each session's log must be downloaded right after the session.

## Next week's goal
- Deploy the agent and have at least 3 outside participants use it on a paragraph with real citations, with the raw evidence committed the same day.

## Individual contributions
- Vyom (Product): post-midterm plan and flowcharts, lean canvas update  (evidence: PR #29)
- Sakshaat (Engineering): agent loop, claim extraction, reference resolution, full-text reading, discovery path, report export, app tabs, PDF check, live source checker, deployment files  (evidence: PR #28)
- Sahil (Data&Eval): Session 7 targets, agent evaluation harness (E3, E2), fit/calibration split, the evaluation flaw above  (evidence: PR #30)
- Ritika (Users&Research): real-world set tooling and labelling guide, session log export for hosted user tests  (evidence: PR #27)
- Hassan (Operations): joined the team this week; not yet added to the repository, so no visible work this week; starts on fine-tuning next week  (evidence: none this week)

## Lean canvas changes (if any)
- Applied to `lean-canvas.md` this week (PR #29; every change and why in `docs/lean_canvas_session07_changes.md`): the solution becomes an agent with two jobs (find papers, check every citation in a draft); value proposition, unfair advantage (own fine-tuned verifier, full-text escalation), metrics, cost (free resources only), ethics (text-based PDFs only, open-access full text only, suggested papers are to read, not to paste) and risks (free-tier limits, full-text availability) changed. The key assumption is still untested.
