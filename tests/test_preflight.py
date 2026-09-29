import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools import preflight
from tools.preflight import eastern_deadline, run_checks

REPORT = """---
team: CiteCheck
session: 05
date: 2026-09-29
members:
  - name: Vyom
    github: vyom-1908
    hat: Product
  - name: Sakshaat
    github: SakshaatRaut
    hat: Engineering
  - name: Sahil
    github: Lord2709
    hat: Data&Eval
  - name: Ritika
    github: ritikakarande
    hat: Users&Research
north_star:
  metric: "Claim-level macro-F1 on SciFact dev"
  value: "0.58 (95% CI 0.52-0.64)"
  previous: "not measured"
---

## Shipped this week
- Pipeline and app merged  (evidence: PR #3, issue #2)
- Eval harness  (evidence: #4)

## User evidence
- Three outside people ran task tests.
- **Raw artifact**: `evidence/session05/task_tests.csv`
- Changed the wording of the abstain message (#5).

## Metrics snapshot
- Claim-level macro-F1: 0.58 (was: not measured)
- Is this the same model that is running in the product? yes, deployed_config.json

## What did not work
- The word-overlap baseline beat the neural model on the NOT ENOUGH EVIDENCE class, which we did not expect and are investigating.

## Challenges / blockers
- Small dev set.

## Next week's goal
- Oct 6 presentation.

## Individual contributions
- Vyom (Product): scope  (evidence: PR #3)
- Sakshaat (Engineering): app  (evidence: PR #3)
- Sahil (Data&Eval): eval  (evidence: #4)
- Ritika (Users&Research): tests  (evidence: #5)

## Lean canvas changes (if any)
- none
"""
DEADLINE = eastern_deadline("2026-09-29")
BEFORE = "2026-09-29T12:00:00-04:00"
AFTER = "2026-09-29T18:30:00-04:00"


def sh(root, *args, when=BEFORE):
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@x", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@x"}
    subprocess.run(["git", *args], cwd=root, env=env, check=True, capture_output=True)


def run(name, synthetic=False, partial=False, f1=0.58):
    return {"name": name, "synthetic_fixture": synthetic, "partial": partial, "claim_level": {"macro_f1": f1}}


def build(tmp_path, report=REPORT, runs=None, deployed=True, evidence=True, when=BEFORE, commit=True):
    root = tmp_path / "repo"
    (root / "reports").mkdir(parents=True)
    (root / "reports" / "session05.md").write_text(report, encoding="utf-8")
    if evidence:
        (root / "evidence" / "session05").mkdir(parents=True)
        (root / "evidence" / "session05" / "task_tests.csv").write_text("participant,task_id\nP01,T1-1\n")
    for r in (runs if runs is not None else [run("zero_shot_nli")]):
        d = root / "eval" / "results" / r["name"]
        d.mkdir(parents=True)
        (d / "results.json").write_text(json.dumps(r))
    if deployed:
        (root / "eval" / "results").mkdir(parents=True, exist_ok=True)
        (root / "eval" / "results" / "deployed_config.json").write_text("{}")
    subprocess.run(["git", "init", "-b", "main"], cwd=root, capture_output=True, check=True)
    if commit:
        sh(root, "add", "-A")
        sh(root, "commit", "-m", "report", when=when)
    return root


def status(checks):
    return {c.name: c.status for c in checks}


def test_a_good_report_has_no_failures(tmp_path):
    root = build(tmp_path)
    s = status(run_checks(root, 5, deadline=DEADLINE))
    assert "FAIL" not in s.values(), preflight.render(run_checks(root, 5, deadline=DEADLINE))
    assert s["north_star value matches a real eval run"] == "PASS" and s["report committed before deadline"] == "PASS"
    assert s["user evidence tracked by git"] == "PASS" and s["template sections"] == "PASS"


def test_wrong_filename_is_called_out(tmp_path):
    root = build(tmp_path)
    (root / "reports" / "session05.md").rename(root / "reports" / "session5.md")
    (c,) = run_checks(root, 5, deadline=DEADLINE)
    assert c.status == "FAIL" and "session5.md" in c.detail and "NOT be graded" in c.detail


@pytest.mark.parametrize("mutate,check", [
    (lambda t: t.replace("Three outside people ran task tests.", "<<FILL: who>>"), "no template placeholders left"),
    (lambda t: t.replace("session: 05", "session: 04"), "team/session/date"),
    (lambda t: t.replace("hat: Engineering", "hat: Product"), "members / hats"),
    (lambda t: t.replace("github: Lord2709", "github: "), "members / hats"),
    (lambda t: t.replace("  previous: \"not measured\"\n", ""), "north_star"),
    (lambda t: t.replace("## Metrics snapshot", "## Metrics"), "template sections"),
    (lambda t: t.replace("(evidence: PR #3, issue #2)", ""), "shipped items link evidence"),
    (lambda t: t.replace("`evidence/session05/task_tests.csv`", "`evidence/session05/missing.csv`"), "user evidence artifact committed"),
    (lambda t: t.replace("  (evidence: #5)", ""), "every member has evidenced work"),
])
def test_each_rule_can_fail(tmp_path, mutate, check):
    root = build(tmp_path, report=mutate(REPORT))
    assert status(run_checks(root, 5, deadline=DEADLINE))[check] == "FAIL"


def test_numbers_must_come_from_a_real_run(tmp_path):
    synthetic = build(tmp_path / "a", runs=[run("fixture_run", synthetic=True)])
    r = {c.name: c for c in run_checks(synthetic, 5, deadline=DEADLINE)}["north_star value matches a real eval run"]
    assert r.status == "FAIL" and "SYNTHETIC" in r.detail
    partial = build(tmp_path / "b", runs=[run("smoke", partial=True)])
    assert status(run_checks(partial, 5, deadline=DEADLINE))["north_star value matches a real eval run"] == "FAIL"
    other = build(tmp_path / "c", runs=[run("zero_shot_nli", f1=0.71)])
    assert status(run_checks(other, 5, deadline=DEADLINE))["north_star value matches a real eval run"] == "FAIL"
    none = build(tmp_path / "d", runs=[])
    assert status(run_checks(none, 5, deadline=DEADLINE))["north_star value matches a real eval run"] == "FAIL"


def test_same_model_claim_needs_a_deployed_config(tmp_path):
    root = build(tmp_path, deployed=False)
    assert status(run_checks(root, 5, deadline=DEADLINE))["'same model as the product' is backed"] == "FAIL"


def test_honest_none_is_a_warning_not_a_failure(tmp_path):
    text = REPORT.replace("- Three outside people ran task tests.\n- **Raw artifact**: `evidence/session05/task_tests.csv`\n"
                          "- Changed the wording of the abstain message (#5).",
                          "None this week: the app was not runnable until Tuesday afternoon.")
    root = build(tmp_path, report=text, evidence=False)
    assert status(run_checks(root, 5, deadline=DEADLINE))["user evidence artifact committed"] == "WARN"


def test_late_commit_fails_the_deadline(tmp_path):
    root = build(tmp_path, when=AFTER)
    assert status(run_checks(root, 5, deadline=DEADLINE))["report committed before deadline"] == "FAIL"


def test_uncommitted_report_fails(tmp_path):
    root = build(tmp_path, commit=False)
    assert status(run_checks(root, 5, deadline=DEADLINE))["report is committed"] == "FAIL"


def test_eastern_deadline_is_5pm_eastern():
    dl = eastern_deadline("2026-09-29")
    assert dl.utcoffset() == timedelta(hours=-4) and dl.hour == 17          # EDT in September
    assert datetime.fromisoformat(BEFORE) <= dl < datetime.fromisoformat(AFTER)


# ---- GitHub checks with a fake `gh` -----------------------------------------------------------------
def fake_gh(prs, existing=(3, 2, 4, 5), protection=1):
    def gh(*args):
        if args[:2] == ("pr", "list"):
            return True, prs
        if args[0] == "api" and "protection" in args[1]:
            return (True, {"required_pull_request_reviews": {"required_approving_review_count": protection}}) if protection is not None else (False, "403")
        if args[0] == "api":
            n = int(args[1].rsplit("/", 1)[1])
            return (n in existing), {}
        return False, "unexpected"
    return gh


def pr(n, author, approver=None, merged="2026-09-28T15:00:00Z"):
    return {"number": n, "title": "t", "author": {"login": author}, "mergedAt": merged,
            "reviews": [{"author": {"login": approver}, "state": "APPROVED"}] if approver else []}


def test_gh_all_good(tmp_path):
    root = build(tmp_path)
    prs = [pr(3, "vyom-1908", "SakshaatRaut"), pr(4, "Lord2709", "vyom-1908"), pr(5, "ritikakarande", "Lord2709"), pr(6, "SakshaatRaut", "ritikakarande")]
    s = status(run_checks(root, 5, True, DEADLINE, gh=fake_gh(prs), repo="o/r"))
    assert s["this week's merged PRs were approved by a teammate"] == "PASS"
    assert s["every member authored a merged PR this week"] == "PASS" and s["cited issues/PRs exist"] == "PASS"
    assert s["branch protection on main"] == "PASS"


def test_gh_flags_self_merge_missing_refs_and_no_protection(tmp_path):
    root = build(tmp_path)
    prs = [pr(3, "vyom-1908", None), pr(4, "Lord2709", "Lord2709"), pr(9, "old", None, merged="2026-08-01T00:00:00Z")]
    s = status(run_checks(root, 5, True, DEADLINE, gh=fake_gh(prs, existing=(3, 2), protection=0), repo="o/r"))
    assert s["this week's merged PRs were approved by a teammate"] == "FAIL"        # #3 unreviewed, #4 self-approved; old #9 ignored
    assert s["every member authored a merged PR this week"] == "WARN"
    assert s["cited issues/PRs exist"] == "FAIL" and s["branch protection on main"] == "FAIL"
    unknown = status(run_checks(root, 5, True, DEADLINE, gh=fake_gh([], protection=None), repo="o/r"))
    assert unknown["branch protection on main"] == "WARN"


def test_main_exit_code(tmp_path, capsys):
    root = build(tmp_path)
    assert preflight.main(["--session", "5", "--root", str(root), "--deadline", DEADLINE.isoformat()]) == 0
    (root / "reports" / "session05.md").write_text("no front matter")
    assert preflight.main(["--session", "5", "--root", str(root), "--deadline", DEADLINE.isoformat()]) == 1
    assert "FAILED" in capsys.readouterr().out
