"""tools/summarize_export.py: the research export -> evidence files."""
import csv
import json

from tools import summarize_export as se

EXPORT = {
    "users": [
        {"user": "aaaaaaaaaaaa", "participant_code": "p05", "team": False},
        {"user": "bbbbbbbbbbbb", "participant_code": "", "team": False},
        {"user": "cccccccccccc", "participant_code": "T01", "team": True},
    ],
    "runs": [
        {"user": "aaaaaaaaaaaa", "run": "r1", "kind": "draft", "created_at": "2026-11-23T15:00:00+00:00",
         "status": "done", "seconds": 40.0, "input_chars": 900},
        {"user": "aaaaaaaaaaaa", "run": "r0", "kind": "draft", "created_at": "2026-11-16T15:00:00+00:00",
         "status": "done", "seconds": 50.0, "input_chars": 900},
        {"user": "bbbbbbbbbbbb", "run": "r2", "kind": "pdf", "created_at": "2026-11-23T16:00:00+00:00",
         "status": "done", "seconds": 120.0, "input_chars": 30000},
        {"user": "cccccccccccc", "run": "r3", "kind": "draft", "created_at": "2026-11-23T17:00:00+00:00",
         "status": "done", "seconds": 10.0, "input_chars": 100},
    ],
    "citations": [
        {"user": "aaaaaaaaaaaa", "run": "r1", "index": 1, "status": "checked", "verdict": "SUPPORT",
         "confidence": 0.9, "read_full_text": True, "judgement_agrees": True, "judgement_label": "AGREE"},
        {"user": "aaaaaaaaaaaa", "run": "r1", "index": 2, "status": "checked", "verdict": "NEI",
         "confidence": 0.99, "read_full_text": False, "judgement_agrees": False, "judgement_label": "CONTRADICT"},
        {"user": "aaaaaaaaaaaa", "run": "r1", "index": 3, "status": "unresolved", "verdict": None,
         "judgement_agrees": None, "judgement_label": "UNSURE"},
        {"user": "aaaaaaaaaaaa", "run": "r0", "index": 1, "status": "checked", "verdict": "SUPPORT",
         "judgement_agrees": True, "judgement_label": "AGREE"},
        {"user": "bbbbbbbbbbbb", "run": "r2", "index": 1, "status": "checked", "verdict": "CONTRADICT",
         "judgement_agrees": False, "judgement_label": "WRONG_PAPER"},
        {"user": "bbbbbbbbbbbb", "run": "r2", "index": 2, "status": "checked", "verdict": "NEI",
         "judgement_agrees": None, "judgement_label": None},
        {"user": "cccccccccccc", "run": "r3", "index": 1, "status": "checked", "verdict": "SUPPORT",
         "judgement_agrees": True, "judgement_label": "AGREE"},
    ],
}


def test_team_left_out_codes_used_and_date_filter(tmp_path):
    people, runs, cits = se.select(EXPORT, since="2026-11-23")
    assert set(people.values()) == {"P05", "anon-bbbbbb"}
    assert {r["run"] for r in runs} == {"r1", "r2"} and len(cits) == 5


def test_numbers_and_files(tmp_path):
    src = tmp_path / "export.json"
    src.write_text(json.dumps(EXPORT))
    assert se.main([str(src), "--out", str(tmp_path / "ev"), "--since", "2026-11-23"]) == 0
    s = json.loads((tmp_path / "ev" / "summary.json").read_text())
    p05 = s["participants"]["P05"]
    assert (p05["citations"], p05["supported"], p05["not enough evidence"], p05["could not check"]) == (3, 1, 1, 1)
    assert (p05["judged"], p05["right"], p05["wrong"], p05["not sure"]) == (3, 1, 1, 1)
    assert s["total"]["right"] == 1 and s["total"]["wrong"] == 2
    assert s["corrections"] == {"the paper contradicts it": 1, "it read the wrong paper": 1}
    md = (tmp_path / "ev" / "summary.md").read_text()
    assert "**1 were right** (33%)" in md and "T01" not in md
    rows = list(csv.DictReader(open(tmp_path / "ev" / "citations.csv")))
    assert [r["their_answer"] for r in rows if r["participant"] == "P05"] == ["right", "wrong", "not sure"]
    assert rows[1]["right_answer_they_gave"] == "the paper contradicts it"


def test_only_chosen_codes(tmp_path):
    people, runs, cits = se.select(EXPORT, codes=["P05"])
    assert list(people.values()) == ["P05"] and {r["run"] for r in runs} == {"r0", "r1"} and len(cits) == 4
