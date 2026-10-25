"""E3 hand-check sheet (eval/e3_review.py) on the SYNTHETIC fixture."""
import csv
import json

from eval import agent_eval, e3_review


def test_sheet_and_score(fixture_dir, tmp_path):
    agent_eval.main(["swap", "--name", "fx", "--data-dir", str(fixture_dir), "--verifier", "lexical", "--tau", "0.5",
                     "--out", str(tmp_path)])
    run = tmp_path / "fx"
    preds = [json.loads(l) for l in (run / "predictions.jsonl").read_text().splitlines()]
    preds[0]["suggested"], preds[0]["suggested_gold"], preds[0]["verdict_on_wrong"] = ["X1", "G1"], ["G1"], "SUPPORT"
    (run / "predictions.jsonl").write_text("".join(json.dumps(p) + "\n" for p in preds))
    res = json.loads((run / "results.json").read_text())
    res["metrics"]["bad_replacement_upper"]["n"], res["metrics"]["n_claims"] = 4, 10
    (run / "results.json").write_text(json.dumps(res))
    rows = e3_review.main([str(run), "--data-dir", str(fixture_dir)])
    kinds = [r["kind"] for r in rows]
    assert kinds.count("non_gold_suggestion") >= 1 and kinds.count("wrong_citation_kept") >= 1
    with open(run / "review_sheet.csv", newline="", encoding="utf-8") as f:
        sheet = list(csv.DictReader(f))
    for r in sheet:
        r["supports"] = "y" if r["kind"] == "non_gold_suggestion" else "n"
    with open(run / "review_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=e3_review.COLS)
        w.writeheader()
        w.writerows(sheet)
    out = e3_review.main([str(run), "--score"])
    n_non_gold = kinds.count("non_gold_suggestion")
    assert out["bad_replacement_after_review"]["k"] == 0 and out["bad_replacement_after_review"]["n"] == 4
    assert out["false_keep_after_review"]["k"] == kinds.count("wrong_citation_kept") and n_non_gold >= 1
    assert (run / "review_summary.json").exists()
