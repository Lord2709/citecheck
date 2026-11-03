"""Agent evaluation harness (eval/agent_eval.py) on the SYNTHETIC fixture and fakes: plumbing only."""
import json

import pytest

from eval import agent_eval as ae
from src.agent import CiteCheckAgent
from src.fulltext import FullText

from agent_fakes import make_pipeline, paper


def test_wilson_and_rate():
    assert ae.wilson(0, 0) is None
    lo, hi = ae.wilson(5, 10)
    assert lo < 0.5 < hi and 0 <= lo and hi <= 1
    assert ae.rate(3, 4)["rate"] == 0.75


def test_macro_f1_matches_sklearn():
    sk = pytest.importorskip("sklearn.metrics")
    g = ["SUPPORT", "NEI", "CONTRADICT", "SUPPORT", "NEI"]
    p = ["SUPPORT", "SUPPORT", "CONTRADICT", "NEI", "NEI"]
    assert abs(ae.macro_f1(g, p) - sk.f1_score(g, p, average="macro", labels=["SUPPORT", "CONTRADICT", "NEI"])) < 1e-4


def test_swap_cli_on_fixture(fixture_dir, tmp_path):
    res = ae.main(["swap", "--name", "swap_fx", "--data-dir", str(fixture_dir), "--verifier", "lexical",
                   "--tau", "0.5", "--out", str(tmp_path)])
    m = res["metrics"]
    assert res["synthetic_fixture"] is True and m["n_claims"] >= 1
    for key in ("flagged_rate", "suggestion_rate", "control_kept_rate"):
        assert m[key]["n"] == m["n_claims"] and 0 <= m[key]["rate"] <= 1
    d = tmp_path / "swap_fx"
    assert {p.name for p in d.iterdir()} == {"results.json", "predictions.jsonl", "summary.md"}
    assert "SYNTHETIC" in (d / "summary.md").read_text()
    assert json.loads((d / "results.json").read_text())["experiment"] == "E3 swap test"


def test_escalation_eval_with_fakes():
    vague = paper("p1", "Vague", "We describe a cohort of patients. Methods are reported in full.")

    class FT:
        last_detail = ""

        def find(self, p):
            return FullText("fake", "u", ["Exercise improves sleep quality in older adults strongly."])

    pipe = make_pipeline()
    off = CiteCheckAgent(pipe, escalate=False, suggest=False)
    on = CiteCheckAgent(pipe, fulltext=FT(), escalate=True, suggest=False)
    items = [{"item_id": "a", "claim": "Exercise improves sleep quality in older adults.", "cited_identifier": "p1", "gold": "SUPPORT"},
             {"item_id": "b", "claim": "x y z w", "cited_identifier": "missing", "gold": "NEI"}]

    def fetch(i):
        if i != "p1":
            raise KeyError(i)
        return vague
    m, rows = ae.escalation_eval(items, off, on, fetch)
    assert m["n_scored"] == 1 and m["n_skipped"] == 1 and m["escalated"] == 1
    assert m["accuracy_off"]["rate"] == 0.0 and m["accuracy_on"]["rate"] == 1.0
    assert m["unsure_resolved_correctly"]["rate"] == 1.0
