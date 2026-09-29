import csv
import json

import pytest

from tools import anonymize_log, pick_task_stimuli, summarize_tasktests

FIELDS = ["participant", "task_id", "started_at", "ended_at", "seconds", "outcome", "verdict_shown", "participant_agrees",
          "gold_label", "participant_correct", "validated_backend", "needed_help_notes", "evidence_files"]


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})


def test_stimuli_are_seeded_balanced_and_key_matches(fixture_dir, tmp_path):
    a = tmp_path / "a"
    pick_task_stimuli.main(["--data-dir", str(fixture_dir), "--seed", "3", "--out", str(a)])
    key = list(csv.DictReader(open(a / "stimuli_key.csv", encoding="utf-8")))
    assert sorted(r["gold_label"] for r in key) == ["CONTRADICT", "NEI", "SUPPORT"]
    cards = (a / "task_cards_PRINT.md").read_text(encoding="utf-8")
    assert "seed 3" in cards and all(r["claim"] in cards for r in key)
    assert "SUPPORT" not in cards.replace("supports, contradicts", "")            # the answers are not on the participant's card
    b = tmp_path / "b"
    pick_task_stimuli.main(["--data-dir", str(fixture_dir), "--seed", "3", "--out", str(b)])
    assert (a / "stimuli_key.csv").read_text() == (b / "stimuli_key.csv").read_text()       # same seed -> same stimuli
    c = tmp_path / "c"
    seeds = {tuple(r["claim_id"] for r in csv.DictReader(open(_run(fixture_dir, c, s) / "stimuli_key.csv"))) for s in range(8)}
    assert len(seeds) > 1                                                                  # different seeds do differ


def _run(fixture_dir, base, seed):
    out = base / str(seed)
    pick_task_stimuli.main(["--data-dir", str(fixture_dir), "--seed", str(seed), "--out", str(out)])
    return out


def test_anonymize_drops_text_masks_names_and_splits(tmp_path):
    raw = tmp_path / "usage.jsonl"
    recs = [{"ts": "t", "session_id": "abc", "participant": "P01", "event": "verify", "claim": "Jane Doe's idea, mail jane@umd.edu", "claim_len": 30},
            {"ts": "t", "session_id": "abc", "participant": "P02", "event": "comment", "comment": "call Jane Doe +1 301 555 0100"},
            {"ts": "t", "session_id": "zzz", "participant": None, "event": "session_start"}]
    raw.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    out = tmp_path / "out"
    anonymize_log.main([str(raw), "--out", str(out)])
    assert {p.name for p in out.iterdir()} == {"P01.jsonl", "P02.jsonl", "unassigned.jsonl"}
    p1 = json.loads((out / "P01.jsonl").read_text())
    assert "claim" not in p1 and p1["claim_len"] == 30 and p1["session_id"] != "abc" and len(p1["session_id"]) == 12
    out2 = tmp_path / "out2"
    anonymize_log.main([str(raw), "--out", str(out2), "--keep-text", "--scrub", "Jane Doe"])
    p2 = (out2 / "P02.jsonl").read_text()
    assert "Jane" not in p2 and "[name]" in p2 and "[phone]" in p2
    assert "@" not in "".join(p.read_text() for p in out2.iterdir())


def test_anonymize_refuses_leftover_email(tmp_path):
    raw = tmp_path / "u.jsonl"
    raw.write_text(json.dumps({"participant": "P01", "event": "x", "weird_field": "leak@umd.edu"}) + "\n")
    with pytest.raises(SystemExit, match="'@'"):
        anonymize_log.main([str(raw), "--out", str(tmp_path / "o")])


def test_summary_numbers(tmp_path):
    d = tmp_path / "session05"
    (d / "usage_logs").mkdir(parents=True)
    write_csv(d / "task_tests.csv", [
        {"participant": "P01", "task_id": "T1-1", "seconds": "100", "outcome": "completed", "participant_agrees": "y", "gold_label": "SUPPORT", "participant_correct": "y"},
        {"participant": "P01", "task_id": "T1-2", "seconds": "200", "outcome": "completed", "participant_agrees": "n", "gold_label": "NEI", "participant_correct": "n"},
        {"participant": "P02", "task_id": "T1-1", "seconds": "300", "outcome": "needed_help", "participant_agrees": "", "gold_label": "SUPPORT", "participant_correct": ""},
        {"participant": "P02", "task_id": "T2", "seconds": "60", "outcome": "completed", "participant_agrees": "y"},
        {"participant": "", "task_id": "T9"},                                                     # blank rows ignored
    ])
    (d / "usage_logs" / "P01.jsonl").write_text(
        json.dumps({"event": "verify", "validated": True, "verifier": "nli:x"}) + "\n" +
        json.dumps({"event": "verify", "validated": False, "verifier": "lexical"}) + "\n" +
        json.dumps({"event": "feedback", "agrees": True}) + "\n")
    s = summarize_tasktests.main([str(d)])
    assert (s["n_participants"], s["n_attempts"], s["completed"]) == (2, 4, 3)
    assert s["success_rate"] == pytest.approx(2 / 4)         # P01 T1-2 completed but WRONG; P02 T1-1 needed help
    assert s["median_seconds"] == 100                         # median of completed tasks: 60, 100, 200
    assert s["agree_rate"] == pytest.approx(2 / 3) and s["correct_rate"] == pytest.approx(1 / 2)
    md = (d / "summary.md").read_text()
    assert "task success rate: 50%" in md and "1 verify event(s) ran on a DEMO or UNVALIDATED backend" in md
    assert "only 2 participant(s)" in md
