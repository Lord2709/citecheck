---
team: CiteCheck
session: 12
date: 2026-11-24
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
  previous: "0.736 (Session 11; the same deployed run)"
---

## Shipped this week
- **A paper found by its title is used only if its authors and year agree with the reference.** In Session 11, P05's 1998 StackGuard reference was matched to an unrelated 2007 paper and the claim was judged against it. A Crossref match now also needs one of its first five authors named in the reference and a year within one year of the reference's; otherwise the citation says the closest match is a different paper and is not judged (evidence: PR #47)
- **PDF headings and figure labels no longer run into cited sentences, and the PDF library is pinned.** P06's recording showed "XGBoost model Feature importance score B. Machine Learning models 1) Random Forest: ..." as one cited sentence. While testing the fix we found that pypdf 6, which any fresh image build installs because we only required `>=4.2`, reads superscript citation numbers with a space before them: on our PDF test paper it finds 14 cited sentences instead of 37. pypdf is now pinned below 6 (evidence: PR #50, commit aca39dc)
- **Citations of web pages can be checked.** 3 of P05's 10 citations (Phrack, Microsoft Learn) and several of P06's could not be checked although the reference gave the URL. When no paper matches and the reference has a web address, the site now reads that page and judges the claim against its text; only public http(s) addresses are fetched, every redirect is checked again, and at most 2 MB of HTML or plain text is read (evidence: https://github.com/Lord2709/citecheck/blob/main/src/webpage.py)
- **The paper-search keys can be checked on the live site.** `/api/health` says whether the OpenAlex and Semantic Scholar keys are set (never the keys), and the deploy guide has the steps to add them, after P07's search fell back to arXiv only (evidence: PR #49)
- **The source-coverage measurement is on main.** The Session 11 report cited its results before the PR was merged; it is merged now (evidence: PR #52, commit 3e5dfe8)
- **A training option that weighs contradictions more,** for the next model; nothing is trained with it yet (evidence: PR #48)
- **A tool that turns the site's research export into session evidence,** keeping only people outside the team and naming them by study code, with a guide for running sessions on the live site (evidence: PR #51)

## User evidence
- None this week. No one outside the team used the site between 2026-11-18 and 2026-11-24 that we have a record of;
  we spent the week on the fixes that Session 11's four participants asked for (`evidence/session11/`), and the
  sessions on the updated site, including P05 re-running their 10-claim test, are not done yet.
- What this week's changes answer, from Session 11's evidence: the wrong-paper match (P05), web pages that could not
  be checked (P05, P06), headings inside sentences (P06), and paper search without OpenAlex and Semantic Scholar
  (P07). P05's top request, catching false claims, is not answered yet: the training option above is the fix we will
  try, not a result.

## Metrics snapshot
- Claim-level macro-F1: 0.736 (was 0.736), 95% bootstrap CI 0.684-0.784
  (`eval/results/finetuned_nli_selector_v2_capped/results.json`). Unchanged: no new model this week
- False-SUPPORT rate (guardrail): 0.091 (was 0.091)
- Outside participants: **0** this week (4 in Session 11)
- PDF test paper (team, Communications Biology, used for PR #45): cited sentences found **14** with pypdf 6, **37**
  with pypdf 5.9 and with this week's pin (PR #50)
- Free sources for the 18 DOIs cited on the live site (`docs/live_checks/2026-11-17_source_coverage.md`, now on
  main): abstract available for 16, a free full text for 13 (7 with a repository copy, 6 publisher-only), none for 5
- Contradiction detection outside biomedicine: **not measured yet** (the computer-science test set is not merged)
- Measured on: SciFact dev (300 claims) for the model; our own PDF test for the PDF number
- Is this the same model that is running in the product? **Yes.** `nli:hassanedwan/citecheck-nli-ft-base-sel` at tau
  0.5 (`eval/results/deployed_config.json`); this week changed how references are matched, how PDFs and web pages
  are read, not the model

## What did not work
- **No outside sessions this week.** We built the fixes from Session 11 but did not put the updated site in front of
  anyone, so nothing this week shows whether the fixes help a real user; P05's re-run of their test is still to do.
- **We had broken PDF reading without noticing.** `requirements.txt` allowed any pypdf from 4.2 on; our tests ran on
  5.9, but a fresh image build installs 6.x, which finds 14 of the 37 cited sentences in our test paper. We have not
  checked which version the image deployed on 2026-11-17 contains; the next redeploy with the pin settles it.
- **Our Session 11 report cited a file that was not on main** (`docs/live_checks/2026-11-17_source_coverage.md`): the
  PR was opened only this week. The repo did not match the report for a week.
- **The computer-science test set is built but not merged.** 76 arXiv abstracts and 76 drafted claims (26 meant to be
  supported, 25 planted false, 25 not in the abstract) are ready, but the PR was not opened this week, so there is
  still no measurement of contradiction detection outside biomedicine.
- **Contradiction detection is unchanged on the site.** The plan to add written contradicting claims to the training
  data was dropped; the next model uses a heavier loss weight on contradictions instead (PR #48), which needs no new
  data. Neither it nor a separate threshold for "Contradicted" has been run yet.
- **The web-page fallback is tested only without network access;** it has not been tried on the live site yet.
- **Faster checks dropped.** P06's 20-citation check took most of a 6-minute session, but the site does not record
  time per step, so we could not show where the time goes and did not change the order of work.
- **The paper-search keys are not on the site yet**: the code and steps are merged, the Semantic Scholar key needs an
  approval that can take days.

## Challenges / blockers
- One week to the final submission (2026-12-01, 5pm), with Thanksgiving on Nov 26 and 27.
- Training and evaluating the next model needs a Colab GPU; the run, the scores on SciFact dev and on the
  computer-science set, and the decision to ship or not must all fit Nov 27 to 29.
- The computer-science test set must be merged and labelled by two people before any model can be scored on it.

## Next week's goal
- Final submission on 2026-12-01: merge and label the computer-science test set; run the separate "Contradicted"
  threshold and the next model on Colab and ship one only if it keeps SciFact dev macro-F1 (no significant drop from
  0.736), keeps false-SUPPORT at or below 0.10, and labels more planted false claims "Contradicted" on the
  computer-science set; at least 3 outside sessions on the updated site with a judgement on every verdict, including
  P05's re-run; and `reports/final/` with the report, slides and a recorded demo.

## Individual contributions
- Vyom (Product): (evidence: none this week)
- Sakshaat (Engineering): kept PDF headings out of cited sentences, found and pinned the pypdf regression, made web-page citations checkable, reviewed and merged #47, #48 and #49 (evidence: PR #50, https://github.com/Lord2709/citecheck/blob/main/src/webpage.py)
- Sahil (Data&Eval): author-and-year reference matching, the search-key health check and deploy steps, the contradiction training option, the source-coverage measurement (evidence: PR #47, PR #48, PR #49, PR #52)
- Ritika (Users&Research): the research-export summary tool and the guide for sessions on the live site (evidence: PR #51)
- Hassan (Operations): (evidence: none this week)

## Lean canvas changes (if any)
- None this week.
