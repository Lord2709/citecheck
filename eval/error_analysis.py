"""Error analysis for one evaluation run.   Owner: Data & Evaluation (Sahil).

    python -m eval.error_analysis --run eval/results/zero_shot_nli --top 15

Writes  <run>/errors.md  and  <run>/errors.csv.  The automatic buckets tell you WHERE to look;
the "your category" column is for YOU: read at least 20 errors and name the real cause
(negation, numbers/units, coreference, needs full text, arguable gold label, retrieval miss, ...).
The guidelines credit an honest error analysis; the tool only prepares the ground.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.data_io import find_scifact_dir, load_claims, load_corpus

BUCKETS = {
    "FALSE_SUPPORT": "Predicted SUPPORT but gold is not SUPPORT (most harmful: false confidence)",
    "WRONG_DIRECTION": "SUPPORT <-> CONTRADICT flipped",
    "RETRIEVAL_MISS": "Gold paper was not among the k papers judged (retrieval failure, not the verifier's fault)",
    "MISSED_BY_VERIFIER": "Gold paper was retrieved but we answered NOT ENOUGH EVIDENCE (abstained or classified neutral)",
    "FALSE_CONTRADICT": "Predicted CONTRADICT but gold is NEI",
}


def bucket(rec: dict):
    g, p = rec["gold"], rec["pred"]
    if g == p:
        return None
    if p == "SUPPORT":
        return "FALSE_SUPPORT" if g != "CONTRADICT" else "WRONG_DIRECTION"
    if p == "CONTRADICT":
        return "WRONG_DIRECTION" if g == "SUPPORT" else "FALSE_CONTRADICT"
    # p == NEI, g in {SUPPORT, CONTRADICT}
    judged = {d["doc_id"] for d in rec["docs"]}
    return "MISSED_BY_VERIFIER" if judged & set(rec.get("gold_docs", [])) else "RETRIEVAL_MISS"


def _driver_label(rec: dict, driver, corpus: dict) -> str:
    """Which paper the shown sentences come from.  Before this, errors.md printed the rank-1 title next to sentences
    from the DRIVER paper, which may be a different one (RESULTS_session05.md, "Other small issues")."""
    if driver is None:
        return "(none)"
    title = corpus[driver["doc_id"]].title if driver["doc_id"] in corpus else driver["doc_id"]
    tag = "a gold evidence paper" if driver["doc_id"] in set(rec.get("gold_docs", [])) else "NOT a gold paper"
    if rec.get("driver_doc") is None:
        return f"none (abstained); showing rank-{driver.get('rank', 1)} paper: {title}"
    return f"rank {driver.get('rank', '?')}: {title} ({tag})"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="eval/results/<name>")
    ap.add_argument("--data-dir", default="data/scifact")
    ap.add_argument("--split", default=None)
    ap.add_argument("--top", type=int, default=15, help="examples per bucket (most confident first)")
    a = ap.parse_args(argv)

    run = Path(a.run)
    res = json.loads((run / "results.json").read_text(encoding="utf-8"))
    split = a.split or res["split"]
    data_dir = find_scifact_dir(a.data_dir if not res["synthetic_fixture"] else res["data"]["dir"])
    corpus = {d.doc_id: d for d in load_corpus(data_dir / "corpus.jsonl")}
    claims = {c.id: c for c in load_claims(data_dir / f"claims_{split}.jsonl")}
    recs = [json.loads(l) for l in (run / "predictions.jsonl").read_text(encoding="utf-8").splitlines()]

    by_bucket = defaultdict(list)
    for r in recs:
        b = bucket(r)
        if b:
            by_bucket[b].append(r)

    def sents(doc_id, idxs):
        d = corpus.get(str(doc_id))
        return [d.sentences[i] for i in idxs if d and i < len(d.sentences)]

    lines = [f"# Error analysis: `{res['name']}` ({split})", "",
             f"{sum(len(v) for v in by_bucket.values())} errors out of {len(recs)} claims.", "",
             "| bucket | count | meaning |", "|---|---|---|"]
    for b, why in BUCKETS.items():
        lines.append(f"| {b} | {len(by_bucket.get(b, []))} | {why} |")
    rows = []
    for b in BUCKETS:
        items = sorted(by_bucket.get(b, []), key=lambda r: -r["confidence"])[: a.top]
        if not items:
            continue
        lines += ["", f"## {b}", BUCKETS[b], ""]
        for r in items:
            c = claims[r["id"]]
            top = r["docs"][0] if r["docs"] else None
            driver = next((d for d in r["docs"] if d["doc_id"] == r["driver_doc"]), top)
            gold_titles = [corpus[d].title for d in r.get("gold_docs", []) if d in corpus]
            used = sents(driver["doc_id"], driver["sentence_idxs"]) if driver else []
            gold_sent = []
            for d in r.get("gold_docs", []):
                gold_sent += sents(d, c.rationale_sentence_idxs(d))
            lines += [
                f"**#{r['id']}** gold `{r['gold']}` -> pred `{r['pred']}` (conf {r['confidence']:.2f})  ",
                f"claim: {c.claim}  ",
                f"gold paper(s): {'; '.join(gold_titles) or '(none, NEI)'}  ",
                f"top retrieved (rank 1): {corpus[top['doc_id']].title if top else '(none)'}  ",
                f"paper that drove the verdict: {_driver_label(r, driver, corpus)}  ",
                f"sentences the verifier saw (from that paper): {' | '.join(used) or '-'}  ",
                f"gold rationale: {' | '.join(gold_sent) or '-'}  ",
                "your category: _______",
                "",
            ]
            rows.append({"bucket": b, "id": r["id"], "gold": r["gold"], "pred": r["pred"], "confidence": round(r["confidence"], 3),
                         "claim": c.claim, "sentences_seen": " | ".join(used), "gold_rationale": " | ".join(gold_sent),
                         "your_category": "", "notes": ""})
    lines += ["", "## Your taxonomy (fill in after reading >= 20 errors)", "",
              "| category | count | example ids | fix idea |", "|---|---|---|---|", "| | | | |"]
    (run / "errors.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(run / "errors.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["bucket"])
        w.writeheader()
        w.writerows(rows)
    print(Counter({b: len(v) for b, v in by_bucket.items()}))
    print(f"[saved] {run / 'errors.md'}  {run / 'errors.csv'}")


if __name__ == "__main__":
    main()
