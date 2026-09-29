"""Pre-submission check for a weekly report.   Owner: Engineering (Sakshaat) -- the "keep the repo honest" job.

    python -m tools.preflight --session 5                # local checks
    python -m tools.preflight --session 5 --gh           # + PR reviews, cited issues/PRs, branch protection (needs `gh auth login`)

Mirrors what the course grades (project/guidelines.md): the file is exactly reports/sessionNN.md on main, the front matter
follows the template, every claim points at evidence that EXISTS in the repo, numbers come from a real (non-synthetic)
evaluation run, PRs were reviewed by a teammate, everyone has visible work, and the last commit landed before 5:00pm
Eastern on the Tuesday deadline.  Exit code 1 if anything FAILs.  It cannot judge whether your writing is honest: that is on you.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

HATS = {"Product", "Engineering", "Data&Eval", "Users&Research", "Operations"}
SECTIONS = ["Shipped this week", "User evidence", "Metrics snapshot", "What did not work", "Challenges / blockers",
            "Next week's goal", "Individual contributions", "Lean canvas changes (if any)"]
PLACEHOLDER = re.compile(r"<<FILL|<your-|<name|<what |<NN>|<YYYY|<e\.g\.|<this week>|<last week>|<a negative result|<the one thing>|<path in this repo|<metric>|<value>")
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


@dataclass
class Check:
    name: str
    status: str  # PASS | WARN | FAIL
    detail: str = ""


def eastern_deadline(day: str, hour: int = 17) -> datetime:
    """5pm US Eastern on `day` (YYYY-MM-DD).  Uses zoneinfo when available, else EDT (-4) before Nov 1 / EST (-5)."""
    d = datetime.strptime(day, "%Y-%m-%d")
    try:
        from zoneinfo import ZoneInfo

        return datetime(d.year, d.month, d.day, hour, tzinfo=ZoneInfo("America/New_York"))
    except Exception:
        offset = -4 if (d.month, d.day) < (11, 1) and d.month >= 3 else -5
        return datetime(d.year, d.month, d.day, hour, tzinfo=timezone(timedelta(hours=offset)))


def git(root: Path, *args) -> str:
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def gh_runner(*args):
    """Returns (ok, parsed_json_or_text)."""
    try:
        r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return False, "gh CLI not installed"
    if r.returncode != 0:
        return False, (r.stderr or r.stdout).strip()
    try:
        return True, json.loads(r.stdout)
    except json.JSONDecodeError:
        return True, r.stdout


def _floats(text: str) -> list:
    return [float(x) for x in re.findall(r"(?<![\w.])\d+\.\d+|(?<![\w.])\d+(?![\w.])", text or "")]


def load_runs(root: Path) -> list:
    runs = []
    for p in sorted((root / "eval" / "results").glob("*/results.json")):
        try:
            runs.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            pass
    return runs


def run_checks(root: Path, session: int, use_gh: bool = False, deadline: datetime = None, gh=gh_runner, repo: str = None) -> list:
    checks = []
    add = lambda n, s, d="": checks.append(Check(n, s, d))  # noqa: E731
    rel = f"reports/session{session:02d}.md"
    path = root / rel

    # ---- 1. file name / location ---------------------------------------------------------------
    if not path.exists():
        wrong = [str(p.relative_to(root)) for p in root.rglob("*.md")
                 if re.search(rf"session0?{session}\b", p.name, re.I) and "reports" in p.parts and p != path]
        add("report file", "FAIL", f"{rel} not found" + (f"; found look-alikes that will NOT be graded: {wrong}" if wrong else ""))
        return checks
    add("report file", "PASS", rel)
    text = path.read_text(encoding="utf-8")

    # ---- 2. front matter -----------------------------------------------------------------------
    m = FRONT.match(text)
    fm = {}
    if not m:
        add("front matter", "FAIL", "file must start with a --- YAML block (copy reports/_TEMPLATE.md)")
    else:
        try:
            import yaml

            fm = yaml.safe_load(m.group(1)) or {}
            add("front matter", "PASS", "parses")
        except Exception as e:
            add("front matter", "FAIL", f"YAML error: {e}")
    if fm:
        problems = []
        if not fm.get("team") or PLACEHOLDER.search(str(fm.get("team"))):
            problems.append("team")
        if int(fm.get("session", -1)) != session:
            problems.append(f"session should be {session:02d}, is {fm.get('session')}")
        try:
            datetime.strptime(str(fm.get("date")), "%Y-%m-%d")
        except ValueError:
            problems.append("date must be YYYY-MM-DD")
        add("team/session/date", "FAIL" if problems else "PASS", "; ".join(problems))

        members = fm.get("members") or []
        mprob = []
        if not 4 <= len(members) <= 5:
            mprob.append(f"{len(members)} members (need 4 or 5)")
        hats = [mm.get("hat") for mm in members]
        for mm in members:
            if not mm.get("name") or not mm.get("github") or PLACEHOLDER.search(str(mm)):
                mprob.append(f"incomplete member entry {mm}")
            if mm.get("hat") not in HATS:
                mprob.append(f"hat '{mm.get('hat')}' not in {sorted(HATS)}")
        if len(set(hats)) != len(hats):
            mprob.append("two members share a hat")
        add("members / hats", "FAIL" if mprob else "PASS", "; ".join(mprob))

        ns = fm.get("north_star") or {}
        missing = [k for k in ("metric", "value", "previous") if not str(ns.get(k, "")).strip() or PLACEHOLDER.search(str(ns.get(k)))]
        add("north_star", "FAIL" if missing else "PASS", f"missing/placeholder: {missing}" if missing else f"{ns.get('metric')}: {ns.get('value')} (was {ns.get('previous')})")

    # ---- 3. placeholders and structure ----------------------------------------------------------
    left = sorted({x.group(0) for x in PLACEHOLDER.finditer(text)})
    add("no template placeholders left", "FAIL" if left else "PASS", f"still contains {left}" if left else "")
    heads = re.findall(r"^##\s+(.+?)\s*$", text, re.M)
    idx = [heads.index(s) if s in heads else -1 for s in SECTIONS]
    if -1 in idx:
        add("template sections", "FAIL", f"missing: {[s for s, i in zip(SECTIONS, idx) if i == -1]}")
    elif idx != sorted(idx):
        add("template sections", "WARN", "sections are out of the template's order")
    else:
        add("template sections", "PASS")

    def section(name):
        mm = re.search(rf"^##\s+{re.escape(name)}\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
        return mm.group(1).strip() if mm else ""

    # ---- 4. shipped bullets carry evidence -----------------------------------------------------
    shipped = [l for l in section("Shipped this week").splitlines() if l.strip().startswith("-")]
    unevidenced = [l.strip()[:60] for l in shipped if not re.search(r"evidence:.*(#\d+|[0-9a-f]{7,40}|https?://)", l, re.I)]
    add("shipped items link evidence", "FAIL" if (not shipped or unevidenced) else "PASS",
        "no bullets" if not shipped else f"no issue/PR/commit link on: {unevidenced}" if unevidenced else f"{len(shipped)} items")

    # ---- 5. user evidence exists in the repo ----------------------------------------------------
    ue = section("User evidence")
    arts = re.findall(r"\*\*Raw artifact\*\*:\s*(.+)", ue)
    if arts:
        paths = [t.strip("`*,;() ") for a in arts for t in re.split(r"[\s,;]+", a) if "/" in t or re.search(r"\.\w{2,4}$", t)]
        missing = [p for p in paths if not (root / p).exists()]
        empty = [p for p in paths if (root / p).is_file() and (root / p).stat().st_size == 0]
        ok = paths and not missing and not empty
        add("user evidence artifact committed", "PASS" if ok else "FAIL",
            f"{len(paths)} path(s) found" if ok else f"missing: {missing} empty: {empty}" if paths else "'Raw artifact' line has no file path")
        if ok:
            tracked = git(root, "ls-files", *paths)
            add("user evidence tracked by git", "PASS" if tracked else "WARN", "" if tracked else "artifact exists but is not `git add`ed")
    elif re.search(r"\bnone\b|no (running )?product|no user", ue, re.I):
        add("user evidence artifact committed", "WARN", "report honestly says there is none this week (scores low, but honesty is credited)")
    else:
        add("user evidence artifact committed", "FAIL", "no '**Raw artifact**:' line and no honest 'none this week'")

    # ---- 6. numbers come from a real run ---------------------------------------------------------
    runs = load_runs(root)
    real = [r for r in runs if not r["synthetic_fixture"] and not r["partial"]]
    if fm.get("north_star") and re.search(r"\d", str(fm["north_star"].get("value", ""))):
        vals = _floats(str(fm["north_star"]["value"]))
        def near(r):  # report may round to 2-3 decimals
            f1 = r["claim_level"]["macro_f1"]
            return any(abs(v - f1) <= 0.0051 or abs(v / 100 - f1) <= 0.0051 for v in vals)
        if any(near(r) for r in real):
            add("north_star value matches a real eval run", "PASS", next(r["name"] for r in real if near(r)))
        elif any(near(r) for r in runs):
            add("north_star value matches a real eval run", "FAIL", "the number comes from a SYNTHETIC or PARTIAL run")
        else:
            add("north_star value matches a real eval run", "FAIL", f"{vals} not found in any eval/results/*/results.json (commit the run that produced it)")
    else:
        add("north_star value matches a real eval run", "WARN", "no numeric north_star value (fine only if you honestly say 'not measured')")
    same = re.search(r"same model[^\n]*", section("Metrics snapshot"), re.I)
    if same and re.search(r"\byes\b", same.group(0), re.I) and not (root / "eval/results/deployed_config.json").exists():
        add("'same model as the product' is backed", "FAIL", "you answered yes but eval/results/deployed_config.json does not exist (run eval.run_eval --promote)")
    elif same:
        add("'same model as the product' is backed", "PASS")

    # ---- 7. honesty section ----------------------------------------------------------------------
    body = re.sub(r"^>.*$", "", section("What did not work"), flags=re.M).strip()
    add("'What did not work' is filled in", "PASS" if len(body) >= 60 else "WARN", "" if len(body) >= 60 else "very short: the guidelines credit specific negative results")

    # ---- 8. contributions ------------------------------------------------------------------------
    contrib = section("Individual contributions")
    lacking = [mm.get("name") for mm in (fm.get("members") or []) if not re.search(rf"{re.escape(str(mm.get('name')))}.*evidence:", contrib, re.I)]
    add("every member has evidenced work", "FAIL" if lacking else "PASS", f"no evidence link for: {lacking}" if lacking else "")

    # ---- 9. git state ----------------------------------------------------------------------------
    if git(root, "rev-parse", "--is-inside-work-tree") == "true":
        branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
        add("on main", "PASS" if branch == "main" else "WARN", f"currently on '{branch}': the grader reads `main`")
        dirty = git(root, "status", "--porcelain")
        add("working tree clean", "PASS" if not dirty else "WARN", "" if not dirty else f"{len(dirty.splitlines())} uncommitted change(s)")
        head, origin = git(root, "rev-parse", "HEAD"), git(root, "rev-parse", "origin/main")
        if origin:
            ahead = git(root, "rev-list", "--count", "origin/main..HEAD")
            add("pushed to origin/main", "PASS" if ahead == "0" else "FAIL", "" if ahead == "0" else f"{ahead} local commit(s) not on origin/main (run git fetch to refresh)")
        last = git(root, "log", "-1", "--format=%cI", "--", rel)
        if not last:
            add("report is committed", "FAIL", f"{rel} has no commit yet")
        else:
            t = datetime.fromisoformat(last)
            dl = deadline or eastern_deadline(str(fm.get("date", datetime.now().strftime("%Y-%m-%d"))))
            add("report committed before deadline", "PASS" if t <= dl else "FAIL", f"last commit {t.isoformat()} vs deadline {dl.isoformat()}")
    else:
        add("git repository", "WARN", "not a git checkout: cannot check commits/deadline")

    # ---- 10. GitHub (optional) -----------------------------------------------------------------
    if use_gh:
        repo_args = ["--repo", repo] if repo else []
        dl_ = deadline or eastern_deadline(str(fm.get("date", datetime.now().strftime("%Y-%m-%d"))))
        since_dt = dl_ - timedelta(days=7)
        ok, prs = gh("pr", "list", *repo_args, "--state", "merged", "--limit", "100", "--json", "number,title,author,mergedAt,reviews")
        if not ok:
            add("GitHub access", "WARN", f"could not query PRs: {str(prs)[:120]}")
        else:
            week = [p for p in prs if datetime.fromisoformat(p["mergedAt"].replace("Z", "+00:00")) >= since_dt]
            bad = []
            for p in week:
                approvers = {r["author"]["login"] for r in p.get("reviews", []) if r.get("state") == "APPROVED"} - {p["author"]["login"]}
                if not approvers:
                    bad.append(f"#{p['number']}")
            add("this week's merged PRs were approved by a teammate", "FAIL" if bad else "PASS" if week else "WARN",
                f"no approving review from someone else on {bad}" if bad else f"{len(week)} PR(s)" if week else "no merged PRs found this week")
            handles = {str(mm.get("github")).lower(): mm.get("name") for mm in (fm.get("members") or [])}
            authors = {p["author"]["login"].lower() for p in week}
            silent = [n for h, n in handles.items() if h not in authors]
            add("every member authored a merged PR this week", "WARN" if silent else "PASS", f"no merged PR from: {silent}" if silent else "")
        cited = sorted({int(n) for n in re.findall(r"(?:PR\s*)?#(\d+)", text)})
        gone = []
        for n in cited:
            ok, _ = gh("api", f"repos/{repo}/issues/{n}") if repo else gh("issue", "view", str(n), "--json", "number")
            if not ok:
                gone.append(f"#{n}")
        add("cited issues/PRs exist", "FAIL" if gone else "PASS" if cited else "WARN", f"not found: {gone}" if gone else f"{len(cited)} reference(s)" if cited else "the report cites no #numbers")
        if repo:
            ok, prot = gh("api", f"repos/{repo}/branches/main/protection")
            need = (prot or {}).get("required_pull_request_reviews", {}).get("required_approving_review_count", 0) if ok and isinstance(prot, dict) else None
            add("branch protection on main", "PASS" if need and need >= 1 else "WARN" if need is None else "FAIL",
                "cannot verify (admin token needed): check Settings > Branches" if need is None else f"required approvals: {need}")
    return checks


def render(checks: list) -> str:
    icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL"}
    w = max(len(c.name) for c in checks)
    lines = [f"{icon[c.status]}  {c.name.ljust(w)}  {c.detail}".rstrip() for c in checks]
    n = {s: sum(c.status == s for c in checks) for s in icon}
    lines.append(f"\n{n['PASS']} passed, {n['WARN']} warning(s), {n['FAIL']} FAILED")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--gh", action="store_true")
    ap.add_argument("--repo", default=None, help="owner/name (needed for --gh outside a clone)")
    ap.add_argument("--deadline", default=None, help="ISO time; default 5pm US Eastern on the report's date")
    a = ap.parse_args(argv)
    dl = datetime.fromisoformat(a.deadline) if a.deadline else None
    checks = run_checks(Path(a.root).resolve(), a.session, a.gh, dl, repo=a.repo)
    print(render(checks))
    return 1 if any(c.status == "FAIL" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
