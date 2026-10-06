# Session 6 evidence (index): no user tests were run before the Oct 6 presentation

**Status: no outside participant has used CiteCheck yet.** No user-test session was run for Session 6, so this folder
has no roster, task tests, usage logs, notes or screenshots, and `python -m tools.midterm_decision` reports the user rule
as NOT MEASURED (`docs/midterm_numbers.md`). We report that instead of counting teammates or reactions to a demo, which
do not count as user evidence.

What is ready for the first sessions (on `main`):
- protocol and consent script: `evidence/templates/runbook.md`, `evidence/templates/consent_script.md`
- seeded task cards: `python -m tools.pick_task_stimuli --seed <N> --split dev --out evidence/session07`
- the app's Researcher panel (participant code, text-logging consent switch, task timer) and the usage log
- anonymiser, summariser and checker: `tools/anonymize_log.py`, `tools/summarize_tasktests.py`, `tools/check_evidence.py`
  (they read Excel "CSV UTF-8" files since the `fix/evidence-csv-bom` fix)

Plan: at least 3 outside participants (not teammates) use the running app on the task cards; the raw evidence is
committed to `evidence/session07/` in the same week it is collected, before the Session 7 report (Tuesday Oct 20).
