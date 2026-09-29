## Folder layout (one folder per session)

```
evidence/
  README.md                   this file
  templates/                  copy these, never edit them
  session05/
    README.md                 index: who/when/what + list of files (fill in)
    roster.csv                anonymized participants (codes, not names)
    task_tests.csv            one row per participant x task
    task_cards_PRINT.md       what we showed participants (from tools/pick_task_stimuli.py)
    stimuli_key.csv           gold answers for those tasks (committed so the choice is auditable)
    usage_logs/P01.jsonl      anonymized app logs (tools/anonymize_log.py)
    notes/P01.md              notes taken DURING the session
    screenshots/P01_2026-09-29.png
    summary.md                generated: python -m tools.summarize_tasktests evidence/session05
    raw_unredacted/           GIT-IGNORED: recordings, names, anything identifying. Never commit.
```

## Privacy rules (non-negotiable)

1. Participants get a **code** (P01, P02...). Names, e-mails and the code-to-name key live only in `raw_unredacted/` (git-ignored) or off-repo.
2. Read `templates/consent_script.md` aloud and get a **yes** before anything is recorded or the text they type is logged.
3. Recordings show the *screen* only (no face, no voice) and are committed only if small (<25 MB) and the participant agreed;
   otherwise keep them in `raw_unredacted/` and commit the log + notes + a screenshot instead.
4. Run `python -m tools.anonymize_log logs/usage.jsonl --out evidence/session05/usage_logs --scrub "Name1,Name2"` before committing any log.
5. Do not test with teammates. Do not count a participant who was coached.

## Who can be a participant

Outside people who read or cite papers: UMD grad students and RAs in other groups, labmates, friends in research programs.
Not on our team. Aim for **3 in Session 5**, more later. The lean canvas key assumption is *researchers find evidence-grounded verdicts useful*;
that is what these sessions test.
