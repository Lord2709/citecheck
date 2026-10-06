"""
Owner: Users & Research (Ritika).

    python -m tools.check_evidence evidence/session06

The course rule is "a user claim goes into a doc only if a raw artifact is committed", and the privacy rules in
evidence/README.md are non-negotiable.  This turns both into checks a reviewer can run:

  structure   roster.csv, task_tests.csv, README.md, summary.md exist; one notes/Pxx.md per participant
  roster      participant codes look like P01; consent_participation is yes for everyone
  tests       every participant in task_tests.csv is in the roster; outcome is completed | gave_up | needed_help;
              seconds is a number; y/n columns are y, n or blank; validated_backend = y (else the session did not test
              our model); every file in evidence_files exists
  logs        usage_logs/<code>.jsonl only for roster codes; no typed text (claim/comment/...) for anyone who did not
              consent to text logging; no verify event on a DEMO/UNVALIDATED backend
  privacy     no e-mail address or phone number in any committed text file; nothing under raw_unredacted/ is tracked
  freshness   summary.md equals what tools/summarize_tasktests.py computes now (never hand-edited)

Exit code 1 if any check FAILs; WARNs are printed but do not fail.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

from src.text_utils import _EMAIL, _PHONE
from tools import summarize_tasktests

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
CODE = re.compile(r"^P\d{2,3}$")
OUTCOMES = {"completed", "gave_up", "needed_help"}
YN = {"", "y", "n"}
TEXT_KEYS = ("claim", "comment", "abstract", "direction", "identifier", "notes")
TEXT_SUFFIXES = {".md", ".csv", ".jsonl", ".json", ".txt"}


def _read_csv(path: Path) -> list:
    """utf-8-sig: Excel's "CSV UTF-8" starts the file with a byte-order mark, which otherwise renames the first column
    to '\ufeffparticipant' and every row looks empty (bug found in the Oct 4 full test)."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if "participant" not in (reader.fieldnames or []):
                raise ValueError(f"{Path(path).name}: no 'participant' column in the header {reader.fieldnames}; "
                                 "copy the header from evidence/templates/")
            return [r for r in reader if any((v or "").strip() for v in r.values())]
    except UnicodeDecodeError:
        raise ValueError(f"{Path(path).name} is not UTF-8: in Excel use 'Save as' -> 'CSV UTF-8 (Comma delimited)'")


def _yes(v) -> bool:
    return (v or "").strip().lower() in ("yes", "y", "true")


_DECIMAL = re.compile(r"\d*\.\d+")


def _fraction_digits(text: str, start: int) -> bool:
    """True when the match starts right after '<digit>.', i.e. it is the fractional part of a number like 0.6315789473
    (12/19 in summary.json was flagged as a phone number: Oct 4 full test)."""
    return start >= 2 and text[start - 1] == "." and text[start - 2].isdigit()


def personal_data(text: str) -> list:
    """E-mail addresses and phone numbers (a long decimal like 0.6666666666 is a number, not a phone)."""
    found = _EMAIL.findall(text)
    found += [m.group(0) for m in _PHONE.finditer(text)
              if not _DECIMAL.fullmatch(m.group(0).strip()) and not _fraction_digits(text, m.start())]
    return found


def check(folder) -> list:
    d = Path(folder)
    rows = []
    add = lambda name, status, detail="": rows.append((name, status, detail))  # noqa: E731

    # ---- structure ------------------------------------------------------------------------------------------
    missing = [f for f in ("roster.csv", "task_tests.csv", "README.md", "summary.md") if not (d / f).exists()]
    if missing:
        add("required files", FAIL, "missing: " + ", ".join(missing))
    else:
        add("required files", PASS)
    if not (d / "roster.csv").exists() or not (d / "task_tests.csv").exists():
        return rows

    try:
        roster = {r["participant"].strip(): r for r in _read_csv(d / "roster.csv")}
        tests = [r for r in _read_csv(d / "task_tests.csv") if (r.get("participant") or "").strip()]
    except ValueError as e:
        add("CSV format", FAIL, str(e))
        return rows

    # ---- roster ---------------------------------------------------------------------------------------------
    bad_codes = [c for c in roster if not CODE.match(c)]
    add("participant codes", FAIL if bad_codes else PASS,
        f"not a code (use P01, P02...): {bad_codes}" if bad_codes else f"{len(roster)} participant(s): {', '.join(roster)}")
    no_consent = [c for c, r in roster.items() if not _yes(r.get("consent_participation"))]
    add("consent to participate", FAIL if no_consent else PASS, f"no recorded consent: {no_consent}" if no_consent else "")
    if len(roster) < 3:
        add("number of participants", WARN, f"{len(roster)} (the plan targets at least 3 outside users); report n honestly")

    # ---- task tests -----------------------------------------------------------------------------------------
    problems = []
    for i, r in enumerate(tests, 2):  # line 1 is the header
        p = r["participant"].strip()
        if p not in roster:
            problems.append(f"line {i}: {p} is not in roster.csv")
        if (r.get("outcome") or "").strip() not in OUTCOMES:
            problems.append(f"line {i}: outcome '{r.get('outcome')}' not in {sorted(OUTCOMES)}")
        sec = (r.get("seconds") or "").strip()
        if sec:
            try:
                float(sec)
            except ValueError:
                problems.append(f"line {i}: seconds '{sec}' is not a number")
        for col in ("participant_agrees", "participant_correct", "validated_backend"):
            if (r.get(col) or "").strip().lower() not in YN:
                problems.append(f"line {i}: {col} must be y, n or blank")
    add("task_tests.csv rows", FAIL if problems else PASS, "; ".join(problems[:8]) or f"{len(tests)} row(s)")
    if not tests:
        add("task_tests.csv rows", FAIL, "no task attempts recorded")
    unvalidated = [f"{r['participant']}:{r['task_id']}" for r in tests if (r.get("validated_backend") or "").strip().lower() == "n"]
    if unvalidated:
        add("validated backend during tests", WARN, f"not our evaluated model: {unvalidated} (do not count these as tests of it)")
    missing_files = []
    for r in tests:
        for f in filter(None, (x.strip() for x in (r.get("evidence_files") or "").split(";"))):
            if not (d / f).exists():
                missing_files.append(f"{r['participant']}:{f}")
    add("evidence_files exist", FAIL if missing_files else PASS, ", ".join(missing_files[:8]))
    tested = sorted({r["participant"].strip() for r in tests})
    no_notes = [p for p in tested if not (d / "notes" / f"{p}.md").exists()]
    add("notes per participant", FAIL if no_notes else PASS,
        f"missing notes/{{code}}.md for {no_notes}" if no_notes else f"{len(tested)} file(s)")

    # ---- logs -----------------------------------------------------------------------------------------------
    log_dir = d / "usage_logs"
    logs = sorted(log_dir.glob("*.jsonl")) if log_dir.exists() else []
    if not logs:
        add("usage logs", WARN, "no usage_logs/*.jsonl: add anonymized logs as second evidence (tools/anonymize_log.py)")
    for lp in logs:
        code = lp.stem
        if code != "unassigned" and code not in roster:
            add(f"log {lp.name}", FAIL, "file name is not a roster code")
            continue
        texty, demo, n = [], 0, 0
        for line in lp.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e, n = json.loads(line), n + 1
            if any(k in e for k in TEXT_KEYS):
                texty.append(e.get("event"))
            if e.get("event") == "verify" and (not e.get("validated") or str(e.get("verifier", "")).startswith(("lexical", "majority"))):
                demo += 1
        consented = _yes((roster.get(code) or {}).get("consent_text_logging"))
        if texty and not consented:
            add(f"log {lp.name}", FAIL, f"contains typed text ({sorted(set(texty))}) but no consent_text_logging: re-run anonymize_log without --keep-text")
        elif demo:
            add(f"log {lp.name}", WARN, f"{demo} verify event(s) on a DEMO/UNVALIDATED backend")
        else:
            add(f"log {lp.name}", PASS, f"{n} event(s)")

    # ---- privacy --------------------------------------------------------------------------------------------
    leaks = []
    for f in sorted(d.rglob("*")):
        if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES and "raw_unredacted" not in f.parts:
            if personal_data(f.read_text(encoding="utf-8", errors="replace")):
                leaks.append(str(f.relative_to(d)))
    add("no e-mails / phone numbers", FAIL if leaks else PASS, ", ".join(leaks))
    try:
        tracked = subprocess.run(["git", "ls-files", str(d)], capture_output=True, text=True, timeout=10).stdout.split()
    except Exception:
        tracked = []
    raw = [t for t in tracked if "raw_unredacted" in t]
    add("raw_unredacted not tracked", FAIL if raw else PASS, ", ".join(raw[:5]))

    # ---- freshness ------------------------------------------------------------------------------------------
    if (d / "summary.md").exists():
        try:
            now = summarize_tasktests.render(summarize_tasktests.summarize(
                summarize_tasktests.load_tests(d / "task_tests.csv"), summarize_tasktests.log_flags(log_dir)))
        except (ValueError, KeyError) as e:
            add("summary.md is current", FAIL, f"cannot recompute it ({type(e).__name__}: {e}); fix task_tests.csv first")
            return rows
        same = (d / "summary.md").read_text(encoding="utf-8").replace("\r\n", "\n") == now
        add("summary.md is current", PASS if same else FAIL,
            "" if same else f"re-run: python -m tools.summarize_tasktests {d.as_posix()}")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="e.g. evidence/session06")
    a = ap.parse_args(argv)
    rows = check(a.folder)
    width = max(len(r[0]) for r in rows)
    for name, status, detail in rows:
        print(f"{status:4}  {name:<{width}}  {detail}")
    failed = sum(r[1] == FAIL for r in rows)
    print(f"\n{'FAIL' if failed else 'OK'}: {failed} failing check(s), {sum(r[1] == WARN for r in rows)} warning(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
