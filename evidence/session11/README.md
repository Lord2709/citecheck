# Session 11 evidence: outside use of the live site (2026-11-16 and 2026-11-17)

Four people outside the team used the live site on their own work or on a test they built. Codes continue from
Session 10 (P04 onward). No names, e-mail addresses or account names are in these files: account names and the
signed-in e-mail were cropped or blanked out of the screenshots, the browser bar was cropped out of the recording and
the two file dialogs in it (which list file names from the participant's computer) were blurred, and the name was
removed from the written test and its file metadata. Each person agreed to their feedback being used without their
name.

| code | when (ET) | what they did | evidence | site version |
|---|---|---|---|---|
| P04 | 2026-11-16, about 20:16 | uploaded a paper as a PDF (refused: "longer than 60,000 characters"), then pasted a section with 4 citations | `P04_2026-11-16_pdf_upload_error.png`, `P04_feedback.md` | before the update |
| P05 | 2026-11-17, before 14:10 | built a 10-claim test on binary exploitation with true and planted false claims, and judged every verdict | `P05_written_test.md`, `P05_2026-11-17_results_1.png`, `P05_2026-11-17_results_2.png` | before the update |
| P06 | 2026-11-17, 12:41 (about 6 minutes) | uploaded their own draft on federated learning for IoT security as a PDF (the first 20 of its citations were checked), read the results and downloaded the report | `P06_session_recording.mp4` (screen only, no sound) | before the update |
| P07 | 2026-11-17, 13:03 to 14:37 | searched for papers four times (13:03, 13:04, 14:11, 14:36; 10 papers each), the last for "recent research papers related to Agentic AI Security"; both consent boxes ticked | `P07_2026-11-17_find_papers.png`, `P07_2026-11-17_history.png`, `P07_2026-11-17_account_consent.png` | page loaded before the update |

"The update" is PR #44, deployed on 2026-11-17 at about 14:10 ET. P07's Account page still shows the old version (no
study-code field, no "Delete my data"), so their browser tab was opened before the update.

## What happened

- **P04**: the PDF of a whole paper was refused because the site counted every page against the 60,000-character limit
  meant for pasted text. In the pasted section, none of the 4 cited papers had a free full text; 2 had no abstract in
  any free source and could not be checked; one citation that cites a number got "not enough evidence" from the
  abstract alone. P04's comments are in `P04_feedback.md`.
- **P05**: by P05's own judgement CiteCheck was right on 2 of 10 claims. None of the 3 planted false claims (#4, #6,
  #9) was labelled "Contradicted"; all three got "not enough evidence", two of them with confidence 0.99 or more. For
  #5 and #6 the reference was matched to a different, 2007 paper. #1, #2 and #7 cite web pages (Phrack, Microsoft
  Learn), which CiteCheck cannot read. No full text was read. P05 also wrote that "even when the verdict was incorrect,
  the evidence CiteCheck displayed was often relevant enough for me to spot the problem myself".
- **P06**: of the 20 citations checked, 1 was supported (#18, from the abstract), 1 contradicted (#14), 10 got "not
  enough evidence" and 8 could not be checked. The 8 include references to web pages, a dataset page and a framework
  that found no paper ("No Crossref match whose title matches the reference (best overlap 0.50 / 0.57)"). The one
  "Contradicted" was read from an open-access full text, but the sentences shown as conflicting (about the
  regularisation parameter and the tree ensemble model) do not, in our reading, contradict the sentence (XGBoost is an
  efficient gradient-boosting library); P06 did not say whether it was right. #11 (Gai et al.) was probably matched
  to a different paper ("Privacy-aware service placement for mobile edge computing via federated learning"). In the
  PDF text, a word split at a line end ("hon- eynets") and section headings ran into sentences ("XGBoost model Feature
  importance score B. Machine Learning models 1) Random Forest: ..."). For #16 the site suggested another paper that
  supports the sentence. The first 9 results, shown while the check was still running, were 0 supported, 6 "not enough
  evidence" and 3 could not be checked.
- **P07**: OpenAlex and Semantic Scholar did not answer the last search, so only arXiv results were shown (the site
  still has no API keys for them).

## Not in these files

- The site's own usage logs for these sessions (not exported this week).
- P04's pasted text and P06's PDF (unpublished work). The recording shows the sentences CiteCheck read from P06's PDF,
  shared with P06's agreement.
