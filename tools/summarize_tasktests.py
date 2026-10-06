"""Compute the user-evidence numbers from the RAW records (never type them by hand).
Owner: Users & Research (Ritika).

    python -m tools.summarize_tasktests evidence/session05

Reads   task_tests.csv                 (one row per participant x task; see evidence/templates/)
        usage_logs/*.jsonl  [optional] (anonymized app logs; used to cross-check times and to flag demo/unvalidated backends)
Writes  summary.md                     (paste the headline numbers into reports/sessionNN.md)
        summary.json                   (the same numbers, machine-readable: tools/midterm_decision.py reads it)
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

DONE = "completed"
# verdict_shown is written as the app displays it; gold_label in SciFact's vocabulary
TO_INTERNAL = {"SUPPORTS": "SUPPORT", "CONTRADICTS": "CONTRADICT", "NOT ENOUGH EVIDENCE": "NEI",
               "SUPPORT": "SUPPORT", "CONTRADICT": "CONTRADICT", "NEI": "NEI"}


def load_tests(path: Path) -> list:
    # utf-8-sig: Excel's "CSV UTF-8" adds a byte-order mark that silently hid every row (0 participants; Oct 4 full test)
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "participant" not in (reader.fieldnames or []):
            raise ValueError(f"{Path(path).name}: no 'participant' column in the header {reader.fieldnames}; "
                             "copy the header from evidence/templates/task_tests_TEMPLATE.csv")
        rows = [r for r in reader if (r.get("participant") or "").strip()]
    for r in rows:
        r["seconds"] = float(r["seconds"]) if (r.get("seconds") or "").strip() else None
    return rows


def success(r: dict) -> bool:
    """Completed without help, and (when there is a gold answer) got it right."""
    if (r.get("outcome") or "").strip() != DONE:
        return False
    return (r.get("participant_correct") or "").strip().lower() != "n"


def misled(r: dict) -> bool:
    """The tool showed a WRONG verdict and the participant agreed with it: the harm our guardrail exists to prevent."""
    shown = TO_INTERNAL.get((r.get("verdict_shown") or "").strip().upper())
    gold = TO_INTERNAL.get((r.get("gold_label") or "").strip().upper())
    return bool(shown and gold and shown != gold and (r.get("participant_agrees") or "").strip().lower() == "y")


def t1_by_participant(rows: list) -> dict:
    """participant -> True if every T1 attempt (T1, T1-1, T1-2...) was a success.  Only participants who did T1."""
    out = {}
    for r in rows:
        if (r.get("task_id") or "").strip().upper().startswith("T1"):
            out[r["participant"]] = out.get(r["participant"], True) and success(r)
    return out


def log_flags(log_dir: Path) -> dict:
    flags = {"n_events": 0, "verify_events": 0, "demo_or_unvalidated": 0, "agree": 0, "disagree": 0, "logs": 0}
    if not log_dir.exists():
        return flags
    for p in sorted(log_dir.glob("*.jsonl")):
        flags["logs"] += 1
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            flags["n_events"] += 1
            if e.get("event") == "verify":
                flags["verify_events"] += 1
                if not e.get("validated") or str(e.get("verifier", "")).startswith(("lexical", "majority")):
                    flags["demo_or_unvalidated"] += 1
            if e.get("event") == "feedback":
                flags["agree" if e.get("agrees") else "disagree"] += 1
    return flags


def summarize(rows: list, flags: dict) -> dict:
    people = sorted({r["participant"] for r in rows})
    times = [r["seconds"] for r in rows if r["seconds"] is not None and (r.get("outcome") or "").strip() == DONE]
    per_task = defaultdict(list)
    for r in rows:
        per_task[r["task_id"]].append(r)
    agree = [r for r in rows if (r.get("participant_agrees") or "").strip().lower() in ("y", "n")]
    gold = [r for r in rows if (r.get("participant_correct") or "").strip().lower() in ("y", "n")]
    return {
        "n_participants": len(people), "n_attempts": len(rows), "participants": people,
        "success_rate": sum(success(r) for r in rows) / len(rows) if rows else None,
        "completed": sum((r.get("outcome") or "").strip() == DONE for r in rows),
        "median_seconds": st.median(times) if times else None,
        "agree_rate": sum((r["participant_agrees"].strip().lower() == "y") for r in agree) / len(agree) if agree else None,
        "correct_rate": sum((r["participant_correct"].strip().lower() == "y") for r in gold) / len(gold) if gold else None,
        "per_task": {t: {"n": len(v), "success": sum(success(r) for r in v) / len(v),
                         "median_s": st.median([r["seconds"] for r in v if r["seconds"] is not None] or [float("nan")])}
                     for t, v in sorted(per_task.items())},
        "flags": flags,
        "t1_participants": len(t1_by_participant(rows)),
        "t1_success_participants": sum(t1_by_participant(rows).values()),
        "misled": sum(misled(r) for r in rows),
        "misled_rows": [f"{r['participant']}:{r['task_id']}" for r in rows if misled(r)],
    }


def render(s: dict) -> str:
    pct = lambda x: "n/a" if x is None else f"{100 * x:.0f}%"  # noqa: E731
    med = "n/a" if s["median_seconds"] is None else "%.0f s" % s["median_seconds"]
    lines = ["# User evidence summary (computed from raw records; do not edit by hand)", "",
             f"- participants: **{s['n_participants']}** ({', '.join(s['participants'])}); task attempts: **{s['n_attempts']}**",
             f"- **task success rate: {pct(s['success_rate'])}** (completed without help and, where a gold answer exists, correct)",
             f"- median time to finish a completed task: {med}",
             f"- participants who agreed with the tool's verdict: {pct(s['agree_rate'])}",
             f"- participant's final answer matched the gold label: {pct(s['correct_rate'])}",
             f"- participants who got every T1 task right without help: **{s['t1_success_participants']} of {s['t1_participants']}**",
             f"- times a participant agreed with a WRONG verdict (misled): **{s['misled']}**"
             + (f" ({', '.join(s['misled_rows'])})" if s["misled_rows"] else ""), "",
             "| task | attempts | success | median s |", "|---|---|---|---|"]
    for t, v in s["per_task"].items():
        lines.append(f"| {t} | {v['n']} | {pct(v['success'])} | {v['median_s']:.0f} |")
    f = s["flags"]
    lines += ["", f"App logs: {f['logs']} file(s), {f['n_events']} events, {f['verify_events']} verify events, "
                  f"feedback agree/disagree {f['agree']}/{f['disagree']}."]
    warns = []
    if s["n_participants"] < 3:
        warns.append(f"only {s['n_participants']} participant(s): the plan targets at least 3 outside users")
    if f["demo_or_unvalidated"]:
        warns.append(f"{f['demo_or_unvalidated']} verify event(s) ran on a DEMO or UNVALIDATED backend: those sessions do not evaluate our real model")
    if s["n_attempts"] and not f["logs"]:
        warns.append("no usage logs found next to task_tests.csv: add anonymized logs as second evidence")
    lines += ["", "## Warnings"] + ([f"- {w}" for w in warns] or ["- none"])
    lines += ["", "> n is tiny. Report these as what happened in these sessions, not as a rate for all researchers."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="e.g. evidence/session05")
    a = ap.parse_args(argv)
    d = Path(a.folder)
    try:
        rows = load_tests(d / "task_tests.csv")
    except (ValueError, UnicodeDecodeError) as e:
        raise SystemExit(f"ERROR: {e}")
    s = summarize(rows, log_flags(d / "usage_logs"))
    (d / "summary.md").write_text(render(s), encoding="utf-8")
    (d / "summary.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")
    print(render(s))
    return s


if __name__ == "__main__":
    main()
