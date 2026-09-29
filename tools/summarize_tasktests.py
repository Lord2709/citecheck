"""Compute the user-evidence numbers from the RAW records (never type them by hand).
Owner: Users & Research (Ritika).

    python -m tools.summarize_tasktests evidence/session05

Reads   task_tests.csv                 (one row per participant x task; see evidence/templates/)
        usage_logs/*.jsonl  [optional] (anonymized app logs; used to cross-check times and to flag demo/unvalidated backends)
Writes  summary.md                     (paste the headline numbers into reports/sessionNN.md)
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

DONE = "completed"


def load_tests(path: Path) -> list:
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if (r.get("participant") or "").strip()]
    for r in rows:
        r["seconds"] = float(r["seconds"]) if (r.get("seconds") or "").strip() else None
    return rows


def success(r: dict) -> bool:
    """Completed without help, and (when there is a gold answer) got it right."""
    if (r.get("outcome") or "").strip() != DONE:
        return False
    return (r.get("participant_correct") or "").strip().lower() != "n"


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
    }


def render(s: dict) -> str:
    pct = lambda x: "n/a" if x is None else f"{100 * x:.0f}%"  # noqa: E731
    med = "n/a" if s["median_seconds"] is None else "%.0f s" % s["median_seconds"]
    lines = ["# User evidence summary (computed from raw records; do not edit by hand)", "",
             f"- participants: **{s['n_participants']}** ({', '.join(s['participants'])}); task attempts: **{s['n_attempts']}**",
             f"- **task success rate: {pct(s['success_rate'])}** (completed without help and, where a gold answer exists, correct)",
             f"- median time to finish a completed task: {med}",
             f"- participants who agreed with the tool's verdict: {pct(s['agree_rate'])}",
             f"- participant's final answer matched the gold label: {pct(s['correct_rate'])}", "",
             "| task | attempts | success | median s |", "|---|---|---|---|"]
    for t, v in s["per_task"].items():
        lines.append(f"| {t} | {v['n']} | {pct(v['success'])} | {v['median_s']:.0f} |")
    f = s["flags"]
    lines += ["", f"App logs: {f['logs']} file(s), {f['n_events']} events, {f['verify_events']} verify events, "
                  f"feedback agree/disagree {f['agree']}/{f['disagree']}."]
    warns = []
    if s["n_participants"] < 3:
        warns.append(f"only {s['n_participants']} participant(s): the Session 5 plan targeted 3 outside users")
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
    rows = load_tests(d / "task_tests.csv")
    s = summarize(rows, log_flags(d / "usage_logs"))
    (d / "summary.md").write_text(render(s), encoding="utf-8")
    print(render(s))
    return s


if __name__ == "__main__":
    main()
