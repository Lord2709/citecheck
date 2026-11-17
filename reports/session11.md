---
team: CiteCheck
session: 11
date: 2026-11-17
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
  previous: "0.736 (Session 10; the same deployed run)"
---

## Shipped this week
- **Every verdict now says what it was read from.** Each citation shows whether the full text was read, not found, refused by the publisher or not needed, and a "not enough evidence" from the abstract alone is labelled "Not in the abstract", with a box to paste the passage from the paper and check again. The summary counts how many verdicts rest on the abstract only. This is the disclaimer P04 asked for (below). Merged 2026-11-17 13:55 ET and live since about 14:10 ET  (evidence: PR #44, https://citecheck-877770798089.us-east4.run.app)
- **Whole-paper PDFs are read.** A PDF is no longer held to the 60,000-character limit for pasted text (up to 80 pages); running headers and footers are removed and words split at a line end are joined. When a draft has more than 20 citations, the site says that it checked the first 20  (evidence: PR #44)
- **More free full texts and abstracts are tried.** Repository copies (arXiv, PMC, university archives) before publisher PDFs, then OpenAlex, Semantic Scholar, and arXiv by title; Crossref and Europe PMC as extra abstract sources. When a publisher refuses the download, the citation links the free copy so the reader can open it  (evidence: PR #44)
- **The two requests from Session 10 and better feedback.** A separate box for the reference list; "relevant / not relevant" buttons on paper-search results; "Is this right?" on each verdict is saved at the first click and can be followed by what is right ("the paper contradicts it", "it read the wrong paper", ...) and a comment. Participants can enter a study code and delete their data from the Account page  (evidence: PR #44)
- **A measurement of which free sources have the cited papers**, run on the 18 DOIs cited on the live site so far  (evidence: commit 3e5dfe8, `docs/live_checks/2026-11-17_source_coverage.md`)
- **Built, not yet live: superscript citation numbers in PDFs.** After the update, a team test with a whole Communications Biology paper found 0 cited sentences, because its citations are superscript numbers that PDF text turns into plain digits glued to words. The fix reads them as citations when the reference list is numbered, and also removes the paper's own DOI and running headers that repeat with their parts in a different order. On the same paper: 37 cited sentences with 54 citations, all matched to its 52 references. Waiting for a teammate's review  (evidence: PR #45)

## User evidence
- Four people outside the team used the live site on 2026-11-16 and 2026-11-17, each on their own work or on a test they built: P04 (a whole paper as a PDF, then a pasted section), P05 (a 10-claim test with planted false claims, judging every verdict), P06 (their own draft as a PDF, recorded on screen for about 6 minutes) and P07 (four paper searches). All four used the site as it was before the update of 2026-11-17 14:10 ET.
- **Raw artifact**: `evidence/session11/README.md`, `evidence/session11/P04_feedback.md`, `evidence/session11/P04_2026-11-16_pdf_upload_error.png`, `evidence/session11/P05_written_test.md`, `evidence/session11/P05_2026-11-17_results_1.png`, `evidence/session11/P05_2026-11-17_results_2.png`, `evidence/session11/P06_session_recording.mp4`, `evidence/session11/P07_2026-11-17_find_papers.png`, `evidence/session11/P07_2026-11-17_history.png`, `evidence/session11/P07_2026-11-17_account_consent.png` (names, e-mail addresses and file names from participants' computers removed; P04's pasted text and P06's PDF are not included)
- What happened:
  - **P04** uploaded a whole paper as a PDF and was refused ("longer than 60,000 characters"), then pasted a section with 4 citations. None of the 4 papers had a free full text; 2 had no abstract in any free source and could not be checked; 1 was supported; 1 got "not enough evidence". P04 explained why: "in one reference I had cited a value for something, which would not be in the abstract", and asked for "some disclaimer if you could not access the entire reference and only used the abstract".
  - **P05** wrote 10 claims on binary exploitation with 5 references, including 3 claims they made false on purpose, and judged every verdict. By their judgement CiteCheck was right on **2 of 10**. None of the 3 false claims was labelled "Contradicted"; all got "not enough evidence", two at confidence 0.99 or more. A 1998 paper was matched to a different 2007 paper, and the 3 claims citing web pages (Phrack, Microsoft Learn) could not be checked although the URLs were given. No full text was read. Their priorities: "fixing contradiction detection and reference matching first". And: "even when the verdict was incorrect, the evidence CiteCheck displayed was often relevant enough for me to spot the problem myself".
  - **P06** uploaded their draft on federated learning for IoT security. Of the first 20 citations: 1 supported, 1 contradicted, 10 not enough evidence, 8 could not be checked (references to web pages, a dataset page and a software framework found no paper). The one "Contradicted" came from an open-access full text, but the sentences shown do not, in our reading, contradict the sentence; P06 did not say. One citation was probably matched to a different paper. The PDF text had a word split at a line end ("hon- eynets") and section headings running into sentences. P06 downloaded the report at the end.
  - **P07** searched for papers four times (10 results each). In the last search OpenAlex and Semantic Scholar did not answer, so only arXiv results were shown.
- What we changed as a result: P04's disclaimer and the refused PDF were fixed in PR #44 the next day; the PDF citation fix (PR #45) came from our own test after that. P05's two priorities, reference matching and contradiction detection, are not fixed yet; reference matching is next week's goal.

## Metrics snapshot
- Claim-level macro-F1: 0.736 (was 0.736), 95% bootstrap CI 0.684-0.784 (`eval/results/finetuned_nli_selector_v2_capped/results.json`). Unchanged: no new model this week
- False-SUPPORT rate (guardrail): 0.091 (was 0.091)
- Outside participants: **4** this week (2 in Session 10; target was 8 more)
- Citations checked by participants: 34 (P04 4, P05 10, P06 20). Supported 3, contradicted 1, not enough evidence 17, could not check 13
- Judged against a participant's own answer (P05 only): **2 of 10 right**; planted false claims labelled "Contradicted": **0 of 3**
- Citations read in full text: 2 of 34 (both P06's); P04 0 of 4, P05 0 of 10
- Free sources for the 18 DOIs cited on the live site (`docs/live_checks/2026-11-17_source_coverage.md`): abstract available for 16 (was 15 before PR #44), a free full text for 13 (was 12). Of those 13, 7 have a repository copy and 6 only a publisher PDF, which publishers often refuse to programs; 5 have no free full text at all
- PDF test (team, after the update): cited sentences found in a whole paper with superscript citations: 0 on the live site, 37 with PR #45
- Measured on: SciFact dev (300 claims) for the model; the participants' own results and P05's written judgements for the usage numbers
- Is this the same model that is running in the product? **Yes.** The update of 2026-11-17 changed how papers are found and read, not the model: still `nli:hassanedwan/citecheck-nli-ft-base-sel` at tau 0.5, the run in `eval/results/deployed_config.json`

## What did not work
- **Contradiction detection, on the first real test of it.** P05 planted 3 false claims whose cited papers say otherwise; CiteCheck called all three "not enough evidence", two at confidence 0.99 or more. The only "Contradicted" this week (P06) looks wrong to us. The model was tuned on biomedical claims (SciFact); these were security papers, and mostly abstracts.
- **Reference matching uses the title only.** P05's 1998 StackGuard paper was matched to a different 2007 paper because the titles overlap; the author and year were not checked. One of P06's citations was probably matched to the wrong paper the same way. A verdict on the wrong paper is worse than "could not check".
- **References to web pages, datasets and software cannot be checked.** 3 of P05's 10 citations and several of P06's 8 "could not check" were of this kind; CiteCheck looks only for papers, even when the URL is in the reference.
- **Almost everything still rests on the abstract.** Only 2 of 34 participant citations were read in full text. PR #44 now says so on each verdict, and reaches a few more full texts (12 to 13 of 18 cited DOIs), but 5 of those 18 papers have no free full text anywhere and 6 more only on publisher sites.
- **PDF reading broke in two new ways.** P04's whole-paper PDF was refused (fixed in PR #44, but P04 has not tried again yet); after that fix our own test of a paper with superscript citations found none (PR #45, not yet merged). P06's PDF showed words split at line ends and headings inside sentences; the first is handled since PR #44 but not re-checked on P06's file, the second is not handled.
- **Paper search still lacks two of its three sources** when they are busy: the free OpenAlex and Semantic Scholar keys are still not added to the site.
- **Fewer participants than planned**: 4 instead of 8, and only P05 judged every verdict. P04, P06 and P07 did not use "Is this right?", so for 24 of 34 citations we do not know whether the verdict was right.
- **Two of our own mistakes, caught before they reached the site**: the first source-coverage run was made without the e-mail address Unpaywall needs, which made a 12 to 13 gain in full texts look like 5 to 11; and the new arXiv search by title matched short, common titles ("Deep learning", 2015) to unrelated papers until we required at least 5 title words and a year within 3 years.

## Challenges / blockers
- Free full text is the ceiling: about a third of the cited papers have no free full text, or one that publishers do not let a program download. Pasting the passage (PR #44) is the workaround, and it asks work of the user.
- Contradiction detection needs test data from the participants' fields. P05's test is the first; a few more like it would let us measure it outside SciFact.
- Two weeks to Demo Day (2026-12-01); the changes next week have to be small and checked on the participants' own inputs.

## Next week's goal
- Check the first author and year before accepting a matched paper, and read web-page references from their URL; add the OpenAlex and Semantic Scholar keys. Then re-run P05's 10-claim test and P04's and P06's checks on the new version and report before and after (target: no claim matched to the wrong paper, and at least 5 of P05's 10 right). At least 3 more outside sessions in which the participant judges every verdict, committed in `evidence/session12/`.

## Individual contributions
- Vyom (Product): (evidence: none this week)
- Sakshaat (Engineering): built the update: abstract-only labels and passage re-check, whole-paper PDFs, more full-text and abstract sources, the reference-list box, relevance buttons, the new feedback, study code and data deletion (evidence: PR #44)
- Sahil (Data&Eval): measured free-source coverage of the cited papers, found and fixed the superscript-citation and running-header problems in PDFs, reviewed, merged and redeployed PR #44, collected and anonymised this week's evidence, and wrote this report (evidence: commit 3e5dfe8, PR #45, `evidence/session11/`)
- Ritika (Users&Research): brought in P05's written test (evidence: `evidence/session11/P05_written_test.md`)
- Hassan (Operations): (evidence: none this week)

## Lean canvas changes (if any)
- None applied. Two to agree on next week: the unique value proposition should say that CiteCheck **shows the sentences that decide each citation**, since P05 found that useful even when the verdict was wrong; and "share of citations read in full text" should sit next to F1 as a key metric, since on real writing most verdicts rest on the abstract. The key risk named in Session 9 is confirmed again: paywalls and reference matching, not only the model, limit what CiteCheck can verify.
