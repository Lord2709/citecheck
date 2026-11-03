"""Hand-check sheet for the E3 swap test.   Owner: Data & Evaluation.

    python -m eval.e3_review eval/results/agent_swap_dev

SciFact labels only the papers each claim cites, so two E3 numbers are upper bounds until a person reads the papers:
  * "suggestions that are not gold": a suggested paper outside SciFact's labels may still support the claim;
  * "wrong citation kept as supports": the "wrong" paper (best non-gold BM25 hit) may in fact support the claim.
This writes review_sheet.csv next to the results: one row per such case, with the claim, the paper's title and abstract,
and an empty `supports` column (y / n / unsure) and `note`.  After filling it in:

    python -m eval.e3_review eval/results/agent_swap_dev --score

prints the corrected rates (rows marked y no longer count as bad) and writes review_summary.json.
SciFact claims are CC BY 4.0 and abstracts ODC-By 1.0 (data/README.md), so the sheet may be committed.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.data_io import find_scifact_dir, load_claims, load_corpus

COLS = ["kind", "claim_id", "claim", "doc_id", "title", "abstract", "supports", "note"]


def build_rows(preds: list, claims_by_id: dict, corpus_by_id: dict) -> list:
    rows = []
    for p in preds:
        c = claims_by_id.get(p["id"])
        if c is None:
            continue
        for d in p.get("suggested", []):
            if d not in p.get("suggested_gold", []):
                rows.append(("non_gold_suggestion", c, d))
        if p.get("verdict_on_wrong") == "SUPPORT":
            rows.append(("wrong_citation_kept", c, p["wrong_doc"]))
    out = []
    for kind, c, d in rows:
        doc = corpus_by_id.get(str(d))
        out.append({"kind": kind, "claim_id": c.id, "claim": c.claim, "doc_id": d,
                    "title": doc.title if doc else "", "abstract": doc.abstract if doc else "", "supports": "", "note": ""})
    return out


def score(sheet: list, results: dict) -> dict:
    m = results["metrics"]
    judged = {"y": 0, "n": 0, "unsure": 0, "blank": 0}
    by_kind = {}
    for r in sheet:
        j = (r.get("supports") or "").strip().lower()
        j = j if j in ("y", "n", "unsure") else "blank"
        judged[j] += 1
        by_kind.setdefault(r["kind"], {"y": 0, "n": 0, "unsure": 0, "blank": 0})[j] += 1
    sug = by_kind.get("non_gold_suggestion", {})
    kept = by_kind.get("wrong_citation_kept", {})
    n_sugg = m["bad_replacement_upper"]["n"]
    n_claims = m["n_claims"]
    bad_sugg = sug.get("n", 0) + sug.get("unsure", 0) + sug.get("blank", 0)    # unsure / unjudged stay counted as bad
    false_keep = kept.get("n", 0) + kept.get("unsure", 0) + kept.get("blank", 0)
    return {"judgements": judged, "by_kind": by_kind,
            "bad_replacement_after_review": {"k": bad_sugg, "n": n_sugg, "rate": round(bad_sugg / n_sugg, 4) if n_sugg else None},
            "false_keep_after_review": {"k": false_keep, "n": n_claims, "rate": round(false_keep / n_claims, 4) if n_claims else None},
            "rule": "rows judged 'y' (the paper does support the claim) are not counted as errors; 'n', 'unsure' and blank are"}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Hand-check sheet for the E3 swap test.")
    ap.add_argument("run_dir", help="e.g. eval/results/agent_swap_dev")
    ap.add_argument("--data-dir", default="data/scifact")
    ap.add_argument("--score", action="store_true", help="read the filled-in sheet and print corrected rates")
    a = ap.parse_args(argv)
    run = Path(a.run_dir)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    sheet_path = run / "review_sheet.csv"
    if a.score:
        with open(sheet_path, encoding="utf-8-sig", newline="") as f:
            sheet = list(csv.DictReader(f))
        out = score(sheet, results)
        (run / "review_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
        b, k = out["bad_replacement_after_review"], out["false_keep_after_review"]
        print(f"judged: {out['judgements']}")
        print(f"bad replacements after review: {b['k']}/{b['n']} = {b['rate']}  (upper bound was "
              f"{results['metrics']['bad_replacement_upper']['rate']})")
        print(f"wrong citations kept as 'supports' after review: {k['k']}/{k['n']} = {k['rate']}  (before review "
              f"{results['metrics']['false_keep_rate']['rate']})")
        print(f"[written] {run / 'review_summary.json'}")
        return out
    d = find_scifact_dir(a.data_dir)
    if d is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    split = results.get("split", "dev")
    claims = {c.id: c for c in load_claims(d / f"claims_{split}.jsonl")}
    corpus = {x.doc_id: x for x in load_corpus(d / "corpus.jsonl")}
    preds = [json.loads(l) for l in (run / "predictions.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = build_rows(preds, claims, corpus)
    with open(sheet_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(f"[written] {sheet_path}: {len(rows)} rows {kinds}. Fill `supports` with y / n / unsure, then run with --score.")
    return rows


if __name__ == "__main__":
    main()
