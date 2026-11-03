"""Build and label the real-world citation set (experiment E4, docs/agent_plan.md).   Owner: Users & Research.

SciFact's claims are cleaned-up rewrites. This set uses REAL citing sentences from real papers in two fields, labelled
independently by two people (rules: docs/labelling_guide.md).

    # 1. candidates: citing sentences + the abstract of the cited paper, from Semantic Scholar (needs internet)
    python -m tools.realworld_set candidates --seeds data/realworld/seeds.csv --per-paper 6 --out data/cache/realworld/items.csv
    #    -> also writes labeller sheets items_A.csv and items_B.csv next to it (same items, label column empty)
    # 2. two people fill the `label` column of THEIR sheet, without talking about items, then:
    python -m tools.realworld_set kappa data/cache/realworld/items_A.csv data/cache/realworld/items_B.csv
    # 3. after resolving disagreements together (write the agreed label in `final_label` of sheet A):
    python -m tools.realworld_set merge data/cache/realworld/items_A.csv --out data/cache/realworld/gold_v1.jsonl \\
        --ids-out data/realworld/labels_v1.csv

seeds.csv columns: field,identifier   (e.g. biomed,10.1371/journal.pmed.0020124   cs,arXiv:2004.14974)
Labels: SUPPORT | CONTRADICT | NEI   (Unsure -> NEI; unusable item -> SKIP, excluded from scores).

Licensing: citing sentences and abstracts come from Semantic Scholar. Files with that TEXT stay under data/cache/
(git-ignored). The committed file (--ids-out) holds ids and labels only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

LABELS = ("SUPPORT", "CONTRADICT", "NEI")
SHEET_COLS = ["item_id", "field", "citing_identifier", "cited_identifier", "cited_title", "claim", "cited_abstract",
              "label", "note"]


def _read(path) -> list:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write(path, rows, cols):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def item_id(citing: str, cited: str, claim: str) -> str:
    return hashlib.sha1(f"{citing}|{cited}|{claim}".encode("utf-8")).hexdigest()[:12]


def cited_identifier(paper) -> str:
    """Something src.ingest.Fetcher.fetch_paper accepts: the DOI, else the Semantic Scholar URL."""
    return paper.doi or paper.url or paper.paper_id


def build_candidates(seeds: list, fetcher, per_paper: int = 6, seed: int = 0, min_words: int = 6) -> list:
    """seeds: [{"field", "identifier"}]. Returns sheet rows (label empty). Deterministic for a given seed."""
    from src.ingest import clean_context

    rng = random.Random(seed)
    rows, seen = [], set()
    for s in seeds:
        try:
            refs = fetcher.fetch_references(s["identifier"], limit=100)
        except Exception as e:
            print(f"  skip {s['identifier']}: {type(e).__name__}: {str(e)[:100]}")
            continue
        usable = []
        for r in refs:
            claim = clean_context(r.context)
            if len(claim.split()) >= min_words and r.cited.abstract.strip():
                usable.append((claim, r.cited))
        rng.shuffle(usable)
        for claim, cited in usable[:per_paper]:
            cid = cited_identifier(cited)
            iid = item_id(s["identifier"], cid, claim)
            if iid in seen:
                continue
            seen.add(iid)
            rows.append({"item_id": iid, "field": s["field"], "citing_identifier": s["identifier"],
                         "cited_identifier": cid, "cited_title": cited.title, "claim": claim,
                         "cited_abstract": cited.abstract, "label": "", "note": ""})
    rng.shuffle(rows)  # labellers should not see items grouped by paper
    return rows


def cohen_kappa(a: list, b: list, labels=LABELS) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def norm_label(x: str) -> str:
    x = (x or "").strip().upper()
    return {"S": "SUPPORT", "SUPPORTS": "SUPPORT", "C": "CONTRADICT", "CONTRADICTS": "CONTRADICT",
            "N": "NEI", "NOT ENOUGH EVIDENCE": "NEI", "UNSURE": "NEI"}.get(x, x)


def agreement(sheet_a: list, sheet_b: list) -> dict:
    b_by = {r["item_id"]: r for r in sheet_b}
    pairs, problems = [], []
    for r in sheet_a:
        o = b_by.get(r["item_id"])
        la, lb = norm_label(r.get("label")), norm_label(o.get("label") if o else "")
        if o is None:
            problems.append(f"{r['item_id']}: missing from sheet B")
        elif not la or not lb:
            problems.append(f"{r['item_id']}: unlabelled")
        elif "SKIP" in (la, lb):
            continue
        elif la not in LABELS or lb not in LABELS:
            problems.append(f"{r['item_id']}: unknown label {la!r}/{lb!r}")
        else:
            pairs.append((r["item_id"], la, lb))
    a = [p[1] for p in pairs]
    b = [p[2] for p in pairs]
    confusion = {la: {lb: sum(1 for x, y in zip(a, b) if x == la and y == lb) for lb in LABELS} for la in LABELS}
    return {"n": len(pairs), "kappa": round(cohen_kappa(a, b), 4) if pairs else None,
            "raw_agreement": round(sum(x == y for x, y in zip(a, b)) / len(pairs), 4) if pairs else None,
            "confusion_A_rows_B_cols": confusion, "disagreements": [p[0] for p in pairs if p[1] != p[2]],
            "problems": problems}


def merge(sheet: list) -> tuple:
    """Gold rows from the adjudicated sheet: `final_label` if present, else `label`.  SKIP rows are dropped."""
    gold, ids = [], []
    for r in sheet:
        lab = norm_label(r.get("final_label") or r.get("label"))
        if lab not in LABELS:
            continue
        gold.append({"item_id": r["item_id"], "field": r["field"], "claim": r["claim"],
                     "cited_identifier": r["cited_identifier"], "gold": lab})
        ids.append({"item_id": r["item_id"], "field": r["field"], "citing_identifier": r["citing_identifier"],
                    "cited_identifier": r["cited_identifier"], "gold": lab})
    return gold, ids


def main(argv=None):
    ap = argparse.ArgumentParser(description="Real-world citation set: candidates, agreement, merge.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("candidates")
    c.add_argument("--seeds", required=True)
    c.add_argument("--per-paper", type=int, default=6)
    c.add_argument("--seed", type=int, default=0)
    c.add_argument("--out", default="data/cache/realworld/items.csv")
    k = sub.add_parser("kappa")
    k.add_argument("sheet_a")
    k.add_argument("sheet_b")
    k.add_argument("--json", default=None, help="also write the agreement report here")
    m = sub.add_parser("merge")
    m.add_argument("sheet")
    m.add_argument("--out", default="data/cache/realworld/gold_v1.jsonl")
    m.add_argument("--ids-out", default="data/realworld/labels_v1.csv")
    a = ap.parse_args(argv)

    if a.cmd == "candidates":
        from src.ingest import Fetcher

        rows = build_candidates(_read(a.seeds), Fetcher(), a.per_paper, a.seed)
        out = Path(a.out)
        _write(out, rows, SHEET_COLS)
        for who in ("A", "B"):
            _write(out.with_name(f"{out.stem}_{who}{out.suffix}"), rows, SHEET_COLS)
        print(f"[written] {out} and labeller sheets _A/_B: {len(rows)} items, by field {dict(Counter(r['field'] for r in rows))}")
        return rows
    if a.cmd == "kappa":
        rep = agreement(_read(a.sheet_a), _read(a.sheet_b))
        print(f"items compared: {rep['n']}   Cohen's kappa: {rep['kappa']}   raw agreement: {rep['raw_agreement']}")
        print("confusion (rows = A, columns = B):")
        for la, row in rep["confusion_A_rows_B_cols"].items():
            print(f"  {la:<10} " + "  ".join(f"{lb[:3]} {v:>3}" for lb, v in row.items()))
        print(f"disagreements to discuss: {len(rep['disagreements'])}   problems: {len(rep['problems'])}")
        for p in rep["problems"][:20]:
            print("  !", p)
        if a.json:
            Path(a.json).parent.mkdir(parents=True, exist_ok=True)
            Path(a.json).write_text(json.dumps(rep, indent=2), encoding="utf-8")
        return rep
    gold, ids = merge(_read(a.sheet))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(g) + "\n" for g in gold), encoding="utf-8")
    _write(a.ids_out, ids, ["item_id", "field", "citing_identifier", "cited_identifier", "gold"])
    print(f"[written] {a.out} ({len(gold)} items, text: keep in data/cache) and {a.ids_out} (ids + labels: commit)")
    print(f"  labels: {dict(Counter(g['gold'] for g in gold))}")
    return gold


if __name__ == "__main__":
    main()
