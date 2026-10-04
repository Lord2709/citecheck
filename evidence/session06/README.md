# Session 6 evidence (index): user tests run before the Oct 6 mid-semester presentation

Generated numbers live in `summary.md` / `summary.json` (`python -m tools.summarize_tasktests evidence/session06`).
Before committing: `python -m tools.check_evidence evidence/session06` must report no FAIL.

- dates of the sessions: <<FILL: e.g. 2026-10-04, 2026-10-05>>
- stimuli seed: <<FILL>>  (`python -m tools.pick_task_stimuli --seed <N> --split dev --out evidence/session06`)
- app configuration during tests (from the sidebar): <<FILL: e.g. Validated configuration `zero_shot_nli`>>
- participants: <<FILL: n>>  (codes in `roster.csv`; no names in this repo)
- what we changed because of these sessions: <<FILL: issue #N>>

| file | what it is | who/when |
|---|---|---|
| `roster.csv` | anonymized participants, consent recorded | <<FILL>> |
| `task_tests.csv` | one row per participant x task | <<FILL>> |
| `task_cards_PRINT.md`, `stimuli_key.csv` | what participants saw, and the answers | <<FILL>> |
| `usage_logs/P01.jsonl` | anonymized app log | <<FILL>> |
| `notes/P01.md` | notes taken during the session | <<FILL>> |
| `screenshots/…` | dated screenshot | <<FILL>> |
