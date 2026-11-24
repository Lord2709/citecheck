"""Turn the site's research export into the evidence files for a session (never type the numbers by hand).
Owner: Users & Research.

    python -m tools.summarize_export citecheck_research_export_2026-11-24.json --out evidence/session12 --since 2026-11-23
    python -m tools.summarize_export citecheck_research_export_2026-11-24.json --out evidence/session12 --codes P05,P06,P08

The export is the JSON from the Account page ("Download the export (JSON)", admins only). It already replaces
user ids with salted hashes and holds no free text (no drafts, no comments). This tool keeps only people outside
the team (team accounts are flagged in the export), names each person by their study code, and writes:

    citations.csv   one row per citation checked: the verdict and, if given, the person's own answer
    runs.csv        one row per check: when, how long it took, how many citations
    summary.md      per person and in total: verdicts, how many were judged, and how many the person said were right
    summary.json    the same numbers, machine-readable

"Right" means the person answered "Yes" to "Is this right?"; "wrong" means "No" (with the right answer when they
picked one); "not sure" is counted apart. A citation nobody judged is not counted as right or wrong.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

VERDICT_NAME = {"SUPPORT": "supported", "CONTRADICT": "contradicted", "NEI": "not enough evidence"}
RIGHT_ANSWER = {"SUPPORT": "the paper supports it", "CONTRADICT": "the paper contradicts it",
                "NEI": "the paper doesn't say", "WRONG_PAPER": "it read the wrong paper"}
COLUMNS = ["supported", "contradicted", "not enough evidence", "could not check"]


def _day(iso: str | None) -> str:
    return (iso or "")[:10]


def _when(iso: str | None):
    try:
        return datetime.fromisoformat((iso or "").replace("Z", "+00:00"))
    except ValueError:
        return None


def participants(export: dict, include_team: bool = False) -> dict:
    """user hash -> the name used in the evidence: the study code, or anon-<hash> when the person gave none."""
    out = {}
    for u in export.get("users") or []:
        if u.get("team") and not include_team:
            continue
        out[u["user"]] = (u.get("participant_code") or "").strip().upper() or f"anon-{u['user'][:6]}"
    return out


def outcome(c: dict) -> str:
    if c.get("status") != "checked" or not c.get("verdict"):
        return "could not check"
    return VERDICT_NAME.get(c["verdict"], c["verdict"].lower())


def answer(c: dict) -> str:
    """right | wrong | not sure | '' (not judged)."""
    if c.get("judgement_label") == "UNSURE":
        return "not sure"
    if c.get("judgement_agrees") is True:
        return "right"
    if c.get("judgement_agrees") is False:
        return "wrong"
    return ""


def select(export: dict, since: str | None = None, codes: list | None = None, include_team: bool = False):
    """(people, runs, citations) kept for this session."""
    people = participants(export, include_team)
    if codes:
        wanted = {c.strip().upper() for c in codes if c.strip()}
        people = {h: code for h, code in people.items() if code in wanted}
    start = _when(since) if since else None

    def keep(row):
        if row.get("user") not in people:
            return False
        if start is None:
            return True
        t = _when(row.get("created_at"))
        if t is None:
            return False
        if t.tzinfo is not None and start.tzinfo is None:
            t = t.replace(tzinfo=None)
        return t >= start

    runs = [r for r in export.get("runs") or [] if keep(r)]
    kept = {(r["user"], r["run"]) for r in runs}
    cits = [c for c in export.get("citations") or [] if (c.get("user"), c.get("run")) in kept]
    return people, runs, cits


def write_csvs(out: Path, people: dict, runs: list, cits: list) -> None:
    per_run = Counter(c["run"] for c in cits)
    with open(out / "runs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant", "run", "created_at", "kind", "status", "seconds", "input_chars", "citations"])
        for r in runs:
            w.writerow([people[r["user"]], r["run"], r.get("created_at"), r.get("kind"), r.get("status"),
                        r.get("seconds"), r.get("input_chars"), per_run.get(r["run"], 0)])
    with open(out / "citations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant", "run", "created_at", "citation", "result", "confidence", "read_full_text",
                    "their_answer", "right_answer_they_gave", "model"])
        for c in cits:
            label = c.get("judgement_label") or ""
            w.writerow([people[c["user"]], c["run"], c.get("created_at"), c.get("index"), outcome(c),
                        c.get("confidence"), "yes" if c.get("read_full_text") else "no", answer(c),
                        RIGHT_ANSWER.get(label, ""), c.get("model")])


def summarize(people: dict, runs: list, cits: list) -> dict:
    by = defaultdict(lambda: {"checks": 0, "citations": 0, **{k: 0 for k in COLUMNS}, "judged": 0, "right": 0,
                              "wrong": 0, "not sure": 0, "full_text": 0, "seconds": []})
    corrections = Counter()
    for r in runs:
        p = by[people[r["user"]]]
        p["checks"] += 1
        if r.get("seconds") is not None and r.get("kind") != "discover":
            p["seconds"].append(float(r["seconds"]))
    for c in cits:
        p = by[people[c["user"]]]
        p["citations"] += 1
        p[outcome(c)] += 1
        p["full_text"] += bool(c.get("read_full_text"))
        a = answer(c)
        if a:
            p["judged"] += 1
            p[a] += 1
        if a == "wrong" and c.get("judgement_label") in RIGHT_ANSWER:
            corrections[RIGHT_ANSWER[c["judgement_label"]]] += 1
    rows = {}
    for code in sorted(by):
        p = by[code]
        secs = p.pop("seconds")
        p["median_seconds_per_check"] = round(st.median(secs), 1) if secs else None
        rows[code] = p
    total = {k: sum(r[k] for r in rows.values()) for k in
             ["checks", "citations", *COLUMNS, "judged", "right", "wrong", "not sure", "full_text"]}
    return {"participants": rows, "total": total, "corrections": dict(corrections.most_common()),
            "n_participants": len(rows)}


def write_summary(out: Path, s: dict, since: str | None, source: str) -> None:
    t = s["total"]
    lines = [f"# Usage summary (generated by `python -m tools.summarize_export`; do not edit by hand)", "",
             f"Source: `{source}`" + (f", checks from {since} on" if since else "") +
             ". People outside the team only, named by study code.", "",
             "| participant | checks | citations | supported | contradicted | not enough evidence | could not check "
             "| read in full | judged | right | wrong | not sure | median s per check |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for code, p in s["participants"].items():
        lines.append(f"| {code} | {p['checks']} | {p['citations']} | {p['supported']} | {p['contradicted']} | "
                     f"{p['not enough evidence']} | {p['could not check']} | {p['full_text']} | {p['judged']} | "
                     f"{p['right']} | {p['wrong']} | {p['not sure']} | {p['median_seconds_per_check'] or '-'} |")
    lines.append(f"| **all ({s['n_participants']})** | {t['checks']} | {t['citations']} | {t['supported']} | "
                 f"{t['contradicted']} | {t['not enough evidence']} | {t['could not check']} | {t['full_text']} | "
                 f"{t['judged']} | {t['right']} | {t['wrong']} | {t['not sure']} | |")
    lines.append("")
    decided = t["right"] + t["wrong"]
    if decided:
        lines.append(f"Of the {decided} verdicts a participant judged right or wrong, **{t['right']} were right** "
                     f"({t['right'] / decided:.0%}) by their own answer; {t['judged']} of {t['citations']} citations "
                     "were judged at all.")
    else:
        lines.append("No verdict was judged right or wrong yet.")
    if s["corrections"]:
        lines += ["", "When a participant said a verdict was wrong, the right answer they picked:", ""]
        lines += [f"- {k}: {v}" for k, v in s["corrections"].items()]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", help="the JSON file downloaded from the Account page")
    ap.add_argument("--out", required=True, help="evidence folder, e.g. evidence/session12")
    ap.add_argument("--since", default=None, help="only checks from this date on (YYYY-MM-DD)")
    ap.add_argument("--codes", default="", help="only these study codes, comma-separated (e.g. P05,P06)")
    ap.add_argument("--include-team", action="store_true", help="keep team accounts (never counts as user evidence)")
    a = ap.parse_args(argv)
    export = json.loads(Path(a.export).read_text(encoding="utf-8-sig"))
    people, runs, cits = select(export, a.since, a.codes.split(",") if a.codes else None, a.include_team)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_csvs(out, people, runs, cits)
    s = summarize(people, runs, cits)
    write_summary(out, s, a.since, Path(a.export).name)
    t = s["total"]
    print(f"{s['n_participants']} participants, {t['checks']} checks, {t['citations']} citations, "
          f"{t['judged']} judged ({t['right']} right, {t['wrong']} wrong) -> {out}/summary.md")
    if any(code.startswith("anon-") for code in s["participants"]):
        print("Some people gave no study code; they appear as anon-<id>. Give them a code (P08, ...) and ask them to "
              "enter it on the Account page, or rename them in your notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
