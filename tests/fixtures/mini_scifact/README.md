# SYNTHETIC test fixture

Everything in this folder is **invented** (fictional compounds, made-up abstracts) and follows the
SciFact file format so unit tests can run offline and fast.

**Never report metrics computed on this folder.** `eval/run_eval.py` marks any run whose data path
contains `fixtures` as `synthetic_fixture: true`, and `tools/preflight.py` refuses to accept such a
run as the source of a number in a weekly report.
