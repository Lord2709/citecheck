"""Apply the pivot-or-persevere rules to COMMITTED files, and record every number we quote with its source.
Owner: Product (Vyom).

    python -m tools.midterm_decision                                 # evidence from evidence/session06
    python -m tools.midterm_decision --evidence evidence/session06 --out docs/midterm_numbers.md

Inputs (nothing is typed by hand):
  docs/decision_rules.json                 thresholds (set before the results they decide; see its honesty_note)
  eval/results/deployed_config.json        which run is the product
  eval/results/<run>/results.json          macro-F1 + CI, paired comparisons, false-SUPPORT, timing, oracle ablation
  <evidence>/summary.json                  user-test numbers (tools/summarize_tasktests.py)   [optional]
  demo/demo_examples.json                  how many demo candidates were tried / kept          [optional]

Writes docs/midterm_numbers.md: a table of every number we quote with the file it came from, the three rules with
PASS / FAIL / NOT MEASURED, and the decision those rules produce (thresholds in docs/decision_rules.json).
Rule of the house: a number that is not in this file is not quoted, in the presentation or in a report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PASS, FAIL, NOT_MEASURED = "PASS", "FAIL", "NOT MEASURED"


def _load(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _f(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def _ci(ci, nd=3):
    return "n/a" if not ci else f"[{ci[0]:.{nd}f}, {ci[1]:.{nd}f}]"


def _signed_ci(ci):
    return "n/a" if not ci else f"[{ci[0]:+.3f}, {ci[1]:+.3f}]"


def comparison(results: dict, vs: str):
    return next((c for c in results.get("paired_comparisons") or [] if c.get("vs") == vs), None)


# ---------------------------------------------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------------------------------------------
def rule_model(dep: dict, rules: dict) -> tuple:
    if dep is None:
        return NOT_MEASURED, "deployed run's results.json not found"
    parts, ok = [], True
    for b in rules["model"]["baselines"]:
        c = comparison(dep, b)
        if c is None:
            return NOT_MEASURED, f"no paired comparison vs {b} in {dep.get('name')}/results.json (run with --compare-with)"
        above = c["ci95"][0] > 0
        ok &= above
        parts.append(f"vs {b} {c['diff']:+.3f} CI {_signed_ci(c['ci95'])} ({'above 0' if above else 'includes or below 0'})")
    return (PASS if ok else FAIL), "; ".join(parts)


def rule_safety(dep: dict, rules: dict) -> tuple:
    if dep is None:
        return NOT_MEASURED, "deployed run's results.json not found"
    fs, cap = dep["claim_level"]["false_support_rate"], rules["safety"]["false_support_max"]
    return (PASS if fs <= cap else FAIL), f"false-SUPPORT {fs:.3f} vs ceiling {cap:.3f}"


def rule_users(summary, rules: dict) -> tuple:
    u = rules["users"]
    if not summary or not summary.get("n_participants"):
        return NOT_MEASURED, "no user-test summary.json with participants: we cannot claim user validation"
    n, ok_t1, misled = summary["n_participants"], summary.get("t1_success_participants"), summary.get("misled")
    if ok_t1 is None or misled is None:
        return NOT_MEASURED, "summary.json lacks t1_success_participants / misled (re-run tools.summarize_tasktests)"
    checks = [n >= u["min_participants"], ok_t1 >= u["min_t1_success_participants"], misled <= u["max_misled"]]
    detail = (f"{n} participant(s) (need >= {u['min_participants']}); {ok_t1} of {summary.get('t1_participants')} got every T1 "
              f"task right without help (need >= {u['min_t1_success_participants']}); misled {misled} time(s) "
              f"(allowed <= {u['max_misled']})")
    return (PASS if all(checks) else FAIL), detail


def decide(model: str, safety: str, users: str) -> tuple:
    """Returns (headline, list of actions): the pivot / persevere consequences agreed with docs/decision_rules.json."""
    actions = []
    if model == FAIL:
        actions.append("PIVOT to evidence finding: drop the verdict, show the most relevant sentences and let the user judge.")
    if users == FAIL:
        actions.append("PIVOT the user or the job before the model: reviewers/editors checking manuscripts, "
                       "or 'find the sentence that supports my claim'.")
    if safety == FAIL and model != FAIL:
        actions.append("PERSEVERE in abstain-first mode: raise tau and report the coverage it costs.")
    if model == NOT_MEASURED or safety == NOT_MEASURED:
        return "NO DECISION: a model rule could not be measured", actions + ["Fix the missing results first."]
    if model == FAIL or users == FAIL:
        return "PIVOT", actions
    if users == NOT_MEASURED:
        return "PERSEVERE (provisional: the user rule was not measured)", actions + [
            "Say plainly that no outside user has validated the product yet; the next week's job is user tests."]
    return ("PERSEVERE" + (" (abstain-first)" if safety == FAIL else "")), actions or ["Keep the product and the user; "
                                                                                       "improve the verifier (the measured bottleneck)."]


# ---------------------------------------------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------------------------------------------
def build(results_root: Path, rules: dict, evidence: Path, demo_path: Path) -> dict:
    deployed = _load(results_root / "deployed_config.json") or {}
    run = deployed.get("run_name")
    dep = _load(results_root / run / "results.json") if run else None
    summary = _load(evidence / "summary.json")
    demo = _load(demo_path)
    numbers = []  # (what, value, source)

    def add(what, value, source):
        numbers.append((what, value, source))

    if dep:
        src = f"eval/results/{run}/results.json"
        cl = dep["claim_level"]
        add(f"Deployed run (the model in the demo)", f"`{run}`", "eval/results/deployed_config.json")
        add("Dev macro-F1 [95% CI], n claims", f"{_f(cl['macro_f1'])} {_ci(cl['macro_f1_ci95'])}, n={cl['n']}", src)
        add("False-SUPPORT rate", _f(cl["false_support_rate"]), src)
        add("SUPPORT precision / coverage", f"{_f(cl['support_precision'])} / {_f(cl['coverage'])}", src)
        add("tau (tuned on)", f"{dep['config']['tau']} (on {dep['tau_tuning']['split']}, n={dep['tau_tuning']['n_claims']}, "
                              f"leak={dep['tau_tuning']['leak']})", src)
        for b in rules["model"]["baselines"]:
            br = _load(results_root / b / "results.json")
            if br:
                add(f"Baseline `{b}` macro-F1 [95% CI]", f"{_f(br['claim_level']['macro_f1'])} {_ci(br['claim_level']['macro_f1_ci95'])}",
                    f"eval/results/{b}/results.json")
                add(f"Baseline `{b}` false-SUPPORT", _f(br["claim_level"]["false_support_rate"]), f"eval/results/{b}/results.json")
            c = comparison(dep, b)
            if c:
                add(f"Paired difference vs `{b}` [95% CI]", f"{c['diff']:+.3f} {_signed_ci(c['ci95'])}", src)
        ea = dep.get("error_attribution") or {}
        if ea:
            add("Oracle: gold paper given (closest to 'the paper I cite')", _f(ea.get("oracle_doc")), src)
            add("Oracle: gold paper + gold sentences (verifier ceiling)", _f(ea.get("oracle_rationale")), src)
        t = dep.get("timing") or {}
        add("Latency per claim (retrieval + verification, ms)",
            f"{t.get('retrieval_ms_per_claim', 0):.0f} + {t.get('verify_ms_per_claim', 0):.0f} on {t.get('device', '?')} "
            f"({(dep.get('provenance') or {}).get('versions', {}).get('platform', '?')})", src)
    for other in sorted(p.parent.name for p in results_root.glob("*/results.json")):
        if other in (run, *rules["model"]["baselines"]):
            continue
        orr = _load(results_root / other / "results.json")
        c = comparison(orr, run) if run else None
        add(f"Not promoted: `{other}` macro-F1 / false-SUPPORT",
            f"{_f(orr['claim_level']['macro_f1'])} / {_f(orr['claim_level']['false_support_rate'])}"
            + (f"; vs `{run}` {c['diff']:+.3f} {_signed_ci(c['ci95'])}" if c else ""), f"eval/results/{other}/results.json")
    if summary and summary.get("n_participants"):
        es = f"{evidence.as_posix()}/summary.json"
        pct = lambda x: "n/a" if x is None else f"{100 * x:.0f}%"  # noqa: E731
        add("User tests: participants / task attempts", f"{summary['n_participants']} / {summary['n_attempts']}", es)
        add("User tests: task success rate", pct(summary.get("success_rate")), es)
        add("User tests: every T1 task right without help", f"{summary.get('t1_success_participants')} of {summary.get('t1_participants')}", es)
        add("User tests: agreed with a wrong verdict (misled)", str(summary.get("misled")), es)
        add("User tests: agreed with the verdict", pct(summary.get("agree_rate")), es)
        med = summary.get("median_seconds")
        add("User tests: median seconds per completed task", "n/a" if med is None else f"{med:.0f}", es)
    else:
        add("User tests", "none committed", f"{evidence.as_posix()}/summary.json (missing)")
    if demo:
        tried = "; ".join(f"{k}: kept {v['kept']} of {v['tried']} tried" for k, v in (demo.get("tried") or {}).items())
        add("Demo examples (seeded, dev; not a metric)", tried or "n/a", demo_path.as_posix())

    m, s, u = rule_model(dep, rules), rule_safety(dep, rules), rule_users(summary, rules)
    headline, actions = decide(m[0], s[0], u[0])
    return {"numbers": numbers, "rules": [("1. Model beats both baselines", *m), ("2. Safety: false-SUPPORT ceiling", *s),
                                          ("3. Users", *u)],
            "decision": headline, "actions": actions, "rules_meta": rules}


def render(r: dict) -> str:
    meta = r["rules_meta"]
    lines = ["# Mid-semester numbers and decision (generated by `python -m tools.midterm_decision`; do not edit by hand)", "",
             "Every number we quote must appear here, with the file it came from.", "",
             "| what | value | source |", "|---|---|---|"]
    lines += [f"| {w} | {v} | `{s}` |" for w, v, s in r["numbers"]]
    lines += ["", f"## Rules (`docs/decision_rules.json`, set {meta.get('set_on')})", "",
              f"> {meta.get('honesty_note', '')}", "", "| rule | result | detail |", "|---|---|---|"]
    lines += [f"| {n} | **{st}** | {d} |" for n, st, d in r["rules"]]
    lines += ["", f"## Decision: **{r['decision']}**", ""] + [f"- {a}" for a in r["actions"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", default="docs/decision_rules.json")
    ap.add_argument("--results", default="eval/results")
    ap.add_argument("--evidence", default="evidence/session06")
    ap.add_argument("--demo", default="demo/demo_examples.json")
    ap.add_argument("--out", default="docs/midterm_numbers.md")
    a = ap.parse_args(argv)
    rules = _load(Path(a.rules))
    if rules is None:
        raise SystemExit(f"{a.rules} not found or not JSON")
    r = build(Path(a.results), rules, Path(a.evidence), Path(a.demo))
    text = render(r)
    Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return r


if __name__ == "__main__":
    main()
