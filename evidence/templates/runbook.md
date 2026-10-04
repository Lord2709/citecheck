# Task-test runbook (20 minutes per participant)

**Before** (10 min, once per day)
- [ ] `git pull`; app runs: `streamlit run app/streamlit_app.py` (the sidebar must say **Validated configuration**. If it says DEMO or UNVALIDATED, stop: fix it or tell Sakshaat; those sessions do not count as testing our model).
- [ ] `python -m tools.pick_task_stimuli --seed <N> --split dev --out evidence/session06` (write the seed in `evidence/session06/README.md`)
- [ ] Set `CITECHECK_LOG=logs/usage.jsonl`. Open the app with `?p=P01` in the URL (participant code) or type it into the sidebar *Researcher panel*.
- [ ] Copy `templates/roster_TEMPLATE.csv` -> `session06/roster.csv`, `templates/task_tests_TEMPLATE.csv` -> `session06/task_tests.csv`, notes template -> `session06/notes/P01.md`.

**During** (participant drives; you observe and write notes AS IT HAPPENS)
1. Read the consent script. Ask about logging typed text; tick the box in the Researcher panel only if they say yes.
2. Give **T1-1, T1-2, T1-3** (cards from `task_cards_PRINT.md`). Press **▶ Start** in the Researcher panel when they begin, **✔ Done** or **✖ Gave up** when they finish.
3. **T2 (their own citation):** "Think of a claim you cited (or plan to cite) and the paper you cited for it. Check it with CiteCheck." Success = they got a verdict on a real citation of their own and tell you whether they agree with it.
4. Say only: "Please think aloud." Do **not** explain the UI. If they are stuck for more than 2 minutes, you may help: write `needed_help` as the outcome and note exactly what you said.
5. After each task ask: "Do you agree with the verdict?" (they can also click 👍/👎) and "What was confusing?". Write their words down verbatim.
6. Take a screenshot of the screen mid-task (dated file name; hide anything personal).

**After** (10 min, the SAME day)
- [ ] Fill `task_tests.csv`, one row per participant x task (seconds from the panel/log; outcome = `completed | gave_up | needed_help`).
- [ ] Anonymize the log into `evidence/session06/usage_logs/` (see `evidence/README.md`).
- [ ] `python -m tools.summarize_tasktests evidence/session06`, then read `summary.md`: fix any warning you can.
- [ ] `python -m tools.check_evidence evidence/session06` must end with `OK` (no FAIL) before you commit. Paste its output into the PR body.
- [ ] Commit on a branch, open a PR, ask a teammate to review it. Put the PR number in the weekly report.
- [ ] Write down **one change we should make because of this session** and open an issue for it: the report needs "what we changed as a result".
