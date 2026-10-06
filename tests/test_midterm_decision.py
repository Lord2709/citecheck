"""Pivot-or-persevere rules.  Owner: Product (Vyom)."""
import json

import pytest

from tools import midterm_decision as md

RULES = {"set_on": "2026-10-04", "honesty_note": "set late",
         "model": {"baselines": ["majority", "lexical"]}, "safety": {"false_support_max": 0.15},
         "users": {"min_participants": 3, "min_t1_success_participants": 2, "max_misled": 0}}


def results(name, f1, fs, comps=()):
    return {"name": name, "claim_level": {"n": 300, "macro_f1": f1, "macro_f1_ci95": [f1 - 0.05, f1 + 0.05],
                                          "false_support_rate": fs, "support_precision": 0.8, "coverage": 0.5},
            "config": {"tau": 0.6}, "tau_tuning": {"split": "train", "n_claims": 200, "leak": False},
            "paired_comparisons": [{"vs": v, "diff": d, "ci95": [lo, hi]} for v, d, lo, hi in comps],
            "timing": {"retrieval_ms_per_claim": 25, "verify_ms_per_claim": 450, "device": "cpu"},
            "error_attribution": {"oracle_doc": 0.65, "oracle_rationale": 0.64}}


@pytest.fixture()
def tree(tmp_path):
    root = tmp_path / "results"
    for name, r in {"majority": results("majority", 0.18, 0.0), "lexical": results("lexical", 0.52, 0.22),
                    "zs": results("zs", 0.60, 0.108, [("majority", 0.42, 0.36, 0.48), ("lexical", 0.08, 0.01, 0.16)])}.items():
        (root / name).mkdir(parents=True)
        (root / name / "results.json").write_text(json.dumps(r), encoding="utf-8")
    (root / "deployed_config.json").write_text(json.dumps({"run_name": "zs"}), encoding="utf-8")
    return tmp_path


def users(n=3, ok=2, t1=3, misled=0):
    return {"n_participants": n, "n_attempts": 9, "success_rate": 0.7, "t1_participants": t1,
            "t1_success_participants": ok, "misled": misled, "agree_rate": 0.8, "median_seconds": 95}


def run(tree, summary=None, rules=RULES):
    ev = tree / "ev"
    ev.mkdir(exist_ok=True)
    if summary is not None:
        (ev / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return md.build(tree / "results", rules, ev, tree / "none.json")


def test_all_pass_is_persevere(tree):
    r = run(tree, users())
    assert [x[1] for x in r["rules"]] == [md.PASS, md.PASS, md.PASS] and r["decision"] == "PERSEVERE"
    text = md.render(r)
    assert "0.600 [0.550, 0.650]" in text and "eval/results/zs/results.json" in text and "set late" in text


def test_no_user_evidence_is_provisional_not_a_pass(tree):
    r = run(tree)
    assert r["rules"][2][1] == md.NOT_MEASURED and r["decision"].startswith("PERSEVERE (provisional")
    assert any("none committed" in v for _, v, _ in r["numbers"])


def test_model_ci_touching_zero_pivots_to_evidence_finding(tree):
    zs = results("zs", 0.60, 0.108, [("majority", 0.42, 0.36, 0.48), ("lexical", 0.03, -0.01, 0.08)])
    (tree / "results" / "zs" / "results.json").write_text(json.dumps(zs), encoding="utf-8")
    r = run(tree, users())
    assert r["rules"][0][1] == md.FAIL and r["decision"] == "PIVOT" and "evidence finding" in r["actions"][0]


def test_safety_fail_is_abstain_first(tree):
    rules = dict(RULES, safety={"false_support_max": 0.10})
    r = run(tree, users(), rules)
    assert r["rules"][1][1] == md.FAIL and r["decision"] == "PERSEVERE (abstain-first)"


@pytest.mark.parametrize("summary", [users(n=2), users(ok=1), users(misled=1)])
def test_user_rule_failures_pivot_the_user(tree, summary):
    r = run(tree, summary)
    assert r["rules"][2][1] == md.FAIL and r["decision"] == "PIVOT" and any("user or the job" in a for a in r["actions"])


def test_missing_comparison_is_not_measured(tree):
    zs = results("zs", 0.60, 0.108, [("majority", 0.42, 0.36, 0.48)])
    (tree / "results" / "zs" / "results.json").write_text(json.dumps(zs), encoding="utf-8")
    r = run(tree, users())
    assert r["rules"][0][1] == md.NOT_MEASURED and r["decision"].startswith("NO DECISION")


def test_committed_rules_file_is_complete():
    rules = json.loads(open("docs/decision_rules.json", encoding="utf-8").read())
    assert rules["set_on"] and rules["honesty_note"] and rules["model"]["baselines"] == ["majority", "lexical"]
    assert 0 < rules["safety"]["false_support_max"] < 1 and rules["users"]["min_participants"] >= 3
