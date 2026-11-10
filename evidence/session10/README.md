# Session 10 evidence: use of the live site (2026-11-04 to 2026-11-10)

Exported on 2026-11-10 from the site's own database (Supabase, schema `citecheck`) with read-only SQL queries.
These are the site's timestamped usage logs, not notes taken during a session.

## Who

| code | who | first sign-in (ET) | last activity (ET) | consent: research / keep text |
|---|---|---|---|---|
| U01 | team test account (not a participant) | 2026-10-26 14:43 | 2026-11-09 23:43 | yes / yes |
| U02 | person outside the team | 2026-11-04 18:08 | 2026-11-04 18:22 | yes / yes |
| U03 | person outside the team | 2026-11-10 14:26 | 2026-11-10 14:42 | yes / yes |

Codes are given in order of first sign-in. No names or e-mail addresses are stored in these files. All three
accounts ticked both consent boxes on the site ("Help us improve CiteCheck" and "Also keep the text I paste").
The sentences people pasted are left out of these files, because they may be unpublished work; paper titles are
public metadata. The only free-text comments are from the team account.

## Files

| file | one row per |
|---|---|
| `people.csv` | account: first and last activity, consent choices, number of checks and votes |
| `checks.csv` | citation checked (draft checks) or paper search (`kind` = `discovery`): verdict, confidence, whether the full text was read, the paper, seconds taken |
| `votes.csv` | 👍 (`agree`) or 👎 (`disagree`) on one citation, with the comment where one was written |
| `activity.csv` | page view or action (check started or finished, paper search, paper opened, feedback, filter, download) |

Times are US Eastern. `run` is the first 8 characters of the check's id; `cit` is the citation's number in that check.

## What each person did

- **U02 (2026-11-04, about 14 minutes):** pasted a paragraph on deep-learning vulnerability detection with its
  references. The first two checks finished in under a second with all 6 citations unresolved: the paragraph used
  plain-number citation markers, and a reference-list line ("IEEE Transactions on Software Engineering.") was read
  as a citing sentence. The third paste worked: of 5 citations, 1 supported, 1 not enough evidence (full text read
  for both) and 3 could not be checked, in 60 s. U02 marked all five 👍. Then three paper searches (10, 0 and 10
  papers) and opened the papers ranked 1 and 7.
- **U03 (2026-11-10, about 16 minutes):** checked a paragraph on LLM agents for network management with 6 citations
  to 3 papers, in 101 s, from the abstracts only: 4 not enough evidence, 1 supported (confidence 0.502, just above
  the 0.5 threshold) and 1 contradicted (0.99). No 👍/👎 given. Then two paper searches (0 and 10 papers).
- **U01 (team test account):** the deployment checks of 2026-10-26 and 2026-11-03 and a test paragraph on
  biological age with 8 citations (2026-11-03), where it gave two 👎 with comments about a sentence that cites two
  papers. Kept here because it is in the same export; it is not counted as user evidence.

## What the participants asked for

Told to the team after their sessions, not written down during them, so it is not in the files above:

- two input boxes, one for the text with its citations and one for the reference list, so they do not have to add a
  "References" line (without it the site cannot match citations to papers, as in U02's first two attempts)
- a way to mark each paper in "Find papers" as relevant or not to their research direction

## Limitations

- No notes or task-test records were taken during the two sessions, so the logs show what the participants did, not
  what they thought, apart from U02's 👍.
- A 👎 is saved only if the person also presses "Send", so missing 👎 cannot be ruled out.
- Both participants used the site after the 2026-11-03 redeploy, which runs the fine-tuned verifier
  (`docs/live_checks/2026-11-03_example_live_finetuned.md`).
