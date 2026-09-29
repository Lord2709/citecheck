# Mid-semester presentation: Tuesday October 6 (Session 6)

Owner: Product (Vyom).  Worth 5% of the course grade.  **5 minutes + 2 minutes of questions. There is no written report that week.**

## What the guidelines require (all five, or lose points)
1. **Demo the MVP running.** Not slides about it running.
2. **Show what a real user did with it** and the evidence captured at the time.
3. **Report the metric against the baseline.**
4. **State a decision: pivot or persevere, and why.**
5. **Rotate the presenter** so it is not the same person on demo day.

> "An honest 'this did not work, and here is what we learned' scores better than a claim you cannot show."

## Run of show (5:00)

| time | beat | what is on screen | who/what backs it |
|---|---|---|---|
| 0:00-0:30 | **Problem and one-sentence pitch**: "We help researchers check whether the paper they cite supports their claim, faster than re-reading it and more trustworthy than a chatbot." | Slide 1 | lean canvas |
| 0:30-2:00 | **Live demo, 3 beats**: (1) a SUPPORTS with the evidence sentences, (2) a CONTRADICTS, (3) a claim the paper does not address -> NOT ENOUGH EVIDENCE | the running app, sidebar visible ("Validated configuration") | app from `main`; recorded backup |
| 2:00-3:00 | **Metric vs baseline**: one chart, macro-F1 for majority / word-overlap / zero-shot with CIs, then ONE sentence on the false-SUPPORT rate | `eval/results/figures/f1_by_run.png` | `eval/results/*/results.json` |
| 3:00-4:00 | **What a real user did**: n participants, task success, one verbatim quote, the one thing we changed because of them | screenshot from `evidence/session05/` | `summary.md`, notes |
| 4:00-4:40 | **What did not work + the decision**: apply the rules below, say pivot or persevere and why | Slide 5 | this file |
| 4:40-5:00 | **Next 3 weeks** | Slide 6 | `docs/roadmap_to_demo_day.md` |

Slides (6): title/pitch, (demo: no slide, switch to the app), metric chart, user evidence, what did not work + decision, next steps.
Submit/present from the repo. Keep one backup: a screen recording of the demo path and a PDF of the slides.

## Decision rules (write the thresholds BEFORE you see the results; then apply them honestly)

**Persevere** only if all three hold:

1. **Model:** the zero-shot (or better) system beats both baselines: paired-bootstrap 95% CI of the macro-F1 difference is above 0. (`eval.run_eval --compare-with`)
2. **Safety:** false-SUPPORT rate is at or below `<<TBD: set in docs/north_star.md>>`.
3. **Users:** `<<TBD, e.g. at least 2 of 3>>` participants completed T1 correctly without help, and none reported that the verdict misled them.

**If rule 1 fails** -> pivot to *evidence finding*: drop the verdict, show the most relevant sentences and let the user judge
(keeps the retrieval work, removes the risky claim). **If rule 2 fails** -> persevere in *abstain-first* mode: raise tau and report the coverage cost.
**If rule 3 fails** -> change the user or the job before changing the model: reviewers/editors checking manuscripts, or "find the sentence that supports my claim".
Whatever happens, say it plainly. A pivot backed by data beats a persevere backed by hope.

## Presenter rotation
Proposal: **Vyom presents Oct 6**; the demo-day presenter must be someone else (decide by Session 11 when slots are assigned).
Everyone rehearses their part twice; the presenter runs the demo, the rest of the team owns the answers about their hat.

## Likely questions (prepare an answer that quotes a measured number)

| question | honest answer skeleton |
|---|---|
| Why not just ask ChatGPT? | Ungrounded chat can invent support. We show the exact sentences and abstain below a tuned threshold; our false-SUPPORT rate is `<<FILL>>`. We can also compare directly if we run that baseline. |
| How do you know it works? | SciFact dev, n=300 claims, macro-F1 `<<FILL>>` with 95% CI `<<FILL>>`, vs majority `<<FILL>>` and word-overlap `<<FILL>>`; tau tuned on train only. |
| Does it work outside biomedicine? | We do not know; SciFact is biomedical. Our user tests with `<<FILL>>` are the first look at the gap. |
| Only 3 users? | Yes. It shows what happened in those sessions; we are recruiting more each week. |
| What did users change about the product? | `<<FILL: the concrete change, issue #>>` |
| What happens when the model is wrong? | We show evidence, abstain when unsure, and log agree/disagree; the worst case is a false SUPPORTS and we track that rate. |
| What does a request cost? | Local model, $0 marginal; `<<FILL>>` ms per claim on `<<FILL: hardware>>`. |
| Is the number you show the model in the demo? | Yes: the sidebar shows the deployed run `<<FILL>>` from `deployed_config.json`. |

## Pre-demo checklist (Monday Oct 5)
- [ ] `git pull` on the presenting laptop; `streamlit run app/streamlit_app.py` shows **Validated configuration**
- [ ] The three demo examples are picked (a SUPPORTS, a CONTRADICTS, a NEI) **from data we did not tune on**, and they behave; write down what happens if they do not
- [ ] Wi-Fi off: the paste-an-abstract path still works
- [ ] Backup screen recording + slide PDF on the laptop and in the repo
- [ ] Timed rehearsal under 5:00, twice; a teammate runs the clock
- [ ] Every number on a slide can be traced to a file in `eval/results/` or `evidence/`
