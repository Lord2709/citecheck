#Evidence-folder checker.  Owner: Users & Research - Ritika
import csv
import json

import pytest

from tools import check_evidence as ce, summarize_tasktests

FIELDS = ["participant", "task_id", "started_at", "ended_at", "seconds", "outcome", "verdict_shown", "participant_agrees",
          "gold_label", "participant_correct", "validated_backend", "needed_help_notes", "evidence_files"]
ROSTER = ["participant", "role", "field", "how_recruited", "consent_participation", "consent_text_logging",
          "consent_screen_recording", "consent_date", "session_date", "notes"]


def write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


@pytest.fixture()
def good(tmp_path):
    d = tmp_path / "session06"
    write(d / "roster.csv", ROSTER, [
        {"participant": p, "role": "grad student", "consent_participation": "yes", "consent_text_logging": "no"}
        for p in ("P01", "P02", "P03")])
    rows = []
    for p in ("P01", "P02", "P03"):
        rows.append({"participant": p, "task_id": "T1-1", "seconds": "120", "outcome": "completed", "verdict_shown": "SUPPORTS",
                     "participant_agrees": "y", "gold_label": "SUPPORT", "participant_correct": "y", "validated_backend": "y",
                     "evidence_files": f"notes/{p}.md"})
        (d / "notes").mkdir(exist_ok=True)
        (d / "notes" / f"{p}.md").write_text(f"# Session notes: {p}\n\"I would use this before submitting.\"\n", encoding="utf-8")
    write(d / "task_tests.csv", FIELDS, rows)
    (d / "usage_logs").mkdir()
    (d / "usage_logs" / "P01.jsonl").write_text(json.dumps(
        {"event": "verify", "participant": "P01", "claim_len": 40, "validated": True, "verifier": "nli:x", "confidence": 0.912}) + "\n",
        encoding="utf-8")
    (d / "README.md").write_text("# Session 6 evidence\n", encoding="utf-8")
    summarize_tasktests.main([str(d)])
    return d


def status(rows, name):
    return next(s for n, s, _ in rows if n == name)


def test_good_folder_passes(good):
    rows = ce.check(good)
    assert not [r for r in rows if r[1] == ce.FAIL], rows
    assert ce.main([str(good)]) == 0


def test_missing_files_and_unknown_participant(good):
    (good / "notes" / "P02.md").unlink()
    with open(good / "task_tests.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["P09", "T1-1", "", "", "abc", "finished"] + [""] * 7)
    rows = ce.check(good)
    assert status(rows, "notes per participant") == ce.FAIL
    assert status(rows, "evidence_files exist") == ce.FAIL
    detail = next(d for n, s, d in rows if n == "task_tests.csv rows")
    assert "P09 is not in roster.csv" in detail and "outcome 'finished'" in detail and "not a number" in detail
    assert ce.main([str(good)]) == 1


def test_privacy_leaks_are_caught(good):
    (good / "notes" / "P01.md").write_text("Reach me at someone@umd.edu or 301 555 0100\n", encoding="utf-8")
    assert status(ce.check(good), "no e-mails / phone numbers") == ce.FAIL
    assert ce.personal_data("macro-F1 0.6666666666666666 and 0.9123456789") == []


def test_text_in_log_without_consent_fails(good):
    (good / "usage_logs" / "P02.jsonl").write_text(json.dumps({"event": "verify", "claim": "my secret claim"}) + "\n", encoding="utf-8")
    assert status(ce.check(good), "log P02.jsonl") == ce.FAIL
    (good / "usage_logs" / "P99.jsonl").write_text("{}\n", encoding="utf-8")
    assert status(ce.check(good), "log P99.jsonl") == ce.FAIL


def test_bad_codes_consent_and_stale_summary(good):
    write(good / "roster.csv", ROSTER, [{"participant": "Alice", "consent_participation": "no"},
                                        {"participant": "P01", "consent_participation": "yes"}])
    rows = ce.check(good)
    assert status(rows, "participant codes") == ce.FAIL and status(rows, "consent to participate") == ce.FAIL
    assert status(rows, "number of participants") == ce.WARN
    (good / "summary.md").write_text("# edited by hand\n", encoding="utf-8")
    assert status(ce.check(good), "summary.md is current") == ce.FAIL


def test_summary_counts_misled_and_t1(tmp_path):
    d = tmp_path / "s"
    write(d / "task_tests.csv", FIELDS, [
        {"participant": "P01", "task_id": "T1-1", "outcome": "completed", "verdict_shown": "SUPPORTS", "gold_label": "NEI",
         "participant_agrees": "y", "participant_correct": "n"},                                   # misled
        {"participant": "P02", "task_id": "T1-1", "outcome": "completed", "verdict_shown": "NOT ENOUGH EVIDENCE",
         "gold_label": "NEI", "participant_agrees": "y", "participant_correct": "y"},
        {"participant": "P02", "task_id": "T1-2", "outcome": "completed", "verdict_shown": "CONTRADICTS",
         "gold_label": "SUPPORT", "participant_agrees": "n", "participant_correct": "y"},          # caught the error: not misled
        {"participant": "P03", "task_id": "T2", "outcome": "completed"},
    ])
    s = summarize_tasktests.main([str(d)])
    assert s["misled"] == 1 and s["misled_rows"] == ["P01:T1-1"]
    assert (s["t1_participants"], s["t1_success_participants"]) == (2, 1)
    j = json.loads((d / "summary.json").read_text(encoding="utf-8"))
    assert j["misled"] == 1 and j["n_participants"] == 3


def test_excel_bom_csvs_are_read(tmp_path):
    """Excel 'CSV UTF-8' writes a byte-order mark; it used to give 0 participants and a KeyError (Oct 4 full test)."""
    d = tmp_path / "s"
    d.mkdir()
    for name, fields, rows in (("roster.csv", ROSTER, [{"participant": "P01", "consent_participation": "yes"}]),
                               ("task_tests.csv", FIELDS, [{"participant": "P01", "task_id": "T1-1", "outcome": "completed",
                                                            "seconds": "60", "evidence_files": "notes/P01.md"}])):
        with open(d / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in fields})
    (d / "notes").mkdir()
    (d / "notes" / "P01.md").write_text("# notes\n", encoding="utf-8")
    (d / "README.md").write_text("# index\n", encoding="utf-8")
    s = summarize_tasktests.main([str(d)])
    assert s["n_participants"] == 1 and s["n_attempts"] == 1
    rows = ce.check(d)
    assert status(rows, "participant codes") == ce.PASS and status(rows, "task_tests.csv rows") == ce.PASS


def test_wrong_header_is_a_clear_failure_not_a_crash(tmp_path):
    d = tmp_path / "s"
    d.mkdir()
    (d / "roster.csv").write_text("name,consent\nP01,yes\n", encoding="utf-8")
    (d / "task_tests.csv").write_text("who,task\nP01,T1\n", encoding="utf-8")
    assert status(ce.check(d), "CSV format") == ce.FAIL
    with pytest.raises(SystemExit, match="participant"):
        summarize_tasktests.main([str(d)])


def test_decimals_are_not_phone_numbers_but_phones_are():
    fractions = [n / q for q in range(2, 101) for n in range(1, q)]
    assert ce.personal_data(json.dumps({"rates": fractions})) == []          # 12/19 = 0.631578947368421 used to be flagged
    for phone in ("301 555 0100", "301.555.0100", "+1 (301) 555-0100", "Reach me at 3015550100."):
        assert ce.personal_data(phone), phone
