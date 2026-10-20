"""Real-world set tooling (tools/realworld_set.py) and the session log export.  No network."""
import csv

import pytest

from src.schema import Paper, Reference
from src.usage_log import UsageLogger
from tools import realworld_set as rw


def sheet(rows):
    return [{"item_id": i, "label": l, "field": "cs", "claim": "c", "cited_identifier": "10.1/x", "citing_identifier": "s"}
            for i, l in rows]


def test_kappa_matches_sklearn():
    sk = pytest.importorskip("sklearn.metrics")
    a = ["SUPPORT", "NEI", "CONTRADICT", "SUPPORT", "NEI", "SUPPORT"]
    b = ["SUPPORT", "SUPPORT", "CONTRADICT", "SUPPORT", "NEI", "NEI"]
    assert abs(rw.cohen_kappa(a, b) - sk.cohen_kappa_score(a, b)) < 1e-9


def test_agreement_handles_skips_blanks_and_aliases():
    a = sheet([("1", "S"), ("2", "nei"), ("3", "SKIP"), ("4", ""), ("5", "CONTRADICTS")])
    b = sheet([("1", "SUPPORT"), ("2", "SUPPORT"), ("3", "NEI"), ("4", "NEI"), ("5", "C")])
    rep = rw.agreement(a, b)
    assert rep["n"] == 3 and rep["disagreements"] == ["2"] and rep["problems"] == ["4: unlabelled"]
    assert rep["confusion_A_rows_B_cols"]["NEI"]["SUPPORT"] == 1


def test_merge_prefers_final_label_and_drops_skips():
    rows = sheet([("1", "SUPPORT"), ("2", "NEI"), ("3", "SKIP")])
    rows[1]["final_label"] = "CONTRADICT"
    gold, ids = rw.merge(rows)
    assert [g["gold"] for g in gold] == ["SUPPORT", "CONTRADICT"] and "claim" not in ids[0]


def test_candidates_with_fake_fetcher_and_cli_merge(tmp_path):
    cited = Paper("s2:abc", "Cited paper", "An abstract about sleep.", doi="10.1/c", url="https://www.semanticscholar.org/paper/abc")
    no_abs = Paper("s2:def", "No abstract", "")

    class F:
        def fetch_references(self, ident, limit=100):
            return [Reference(cited, "Exercise improves sleep quality in older adults [12]."),
                    Reference(no_abs, "Another claim with plenty of words in it [3]."),
                    Reference(cited, "Too short [4].")]
    rows = rw.build_candidates([{"field": "biomed", "identifier": "10.1/seed"}], F(), per_paper=5, seed=1)
    assert len(rows) == 1 and rows[0]["claim"] == "Exercise improves sleep quality in older adults."
    assert rows[0]["cited_identifier"] == "10.1/c" and rows[0]["label"] == ""
    p = tmp_path / "A.csv"
    rows[0]["label"] = "SUPPORT"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rw.SHEET_COLS)
        w.writeheader()
        w.writerows(rows)
    gold = rw.main(["merge", str(p), "--out", str(tmp_path / "gold.jsonl"), "--ids-out", str(tmp_path / "ids.csv")])
    assert gold[0]["gold"] == "SUPPORT" and (tmp_path / "ids.csv").exists()
    rep = rw.main(["kappa", str(p), str(p), "--json", str(tmp_path / "k.json")])
    assert rep["kappa"] == 1.0


def test_session_log_export_only_has_this_session(tmp_path):
    path = tmp_path / "usage.jsonl"
    a = UsageLogger(path, participant="P01")
    b = UsageLogger(path, participant="P02")
    a.log("session_start")
    b.log("session_start")
    a.log("draft_check", draft="secret text", n_citations=3)
    ev = a.session_events()
    assert [e["event"] for e in ev] == ["session_start", "draft_check"] and all(e["participant"] == "P01" for e in ev)
    assert "secret text" not in a.session_jsonl() and ev[1]["draft_len"] == len("secret text")
    assert UsageLogger(tmp_path / "none.jsonl").session_events() == []
