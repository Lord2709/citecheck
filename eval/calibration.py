"""How far the verifier's confidence can be trusted: a reliability table and expected calibration error (ECE).
Owner: Data & Evaluation.

    python -m eval.calibration eval/results/finetuned_nli_selector_v2_capped

Reads a run's predictions.jsonl (no model needed) and looks at the verdicts the site shows with a confidence:
SUPPORTS and CONTRADICTS.  For each confidence bin it compares the average confidence with the share that were right.
ECE is the bin-weighted gap; 0 would mean "0.9 confidence" is right 90% of the time.  Written to
<run>/calibration.json and <run>/calibration.md.  Analysis only: nothing here changes a verdict.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BINS = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0001)


def reliability(preds: list, bins=BINS) -> dict:
    rows = [(float(p["confidence"]), p["pred"] == p["gold"]) for p in preds
            if p.get("pred") in ("SUPPORT", "CONTRADICT") and p.get("confidence") is not None]
    table, ece, n = [], 0.0, len(rows)
    lo = 0.0
    for hi in bins:
        inb = [(c, ok) for c, ok in rows if lo <= c < hi]
        if inb:
            conf = sum(c for c, _ in inb) / len(inb)
            acc = sum(ok for _, ok in inb) / len(inb)
            ece += len(inb) / n * abs(conf - acc)
            table.append({"from": lo, "to": min(hi, 1.0), "n": len(inb), "mean_confidence": conf, "accuracy": acc})
        lo = hi
    over = sum(1 for c, ok in rows if c >= 0.99 and not ok)
    return {"n_judged": n, "ece": ece if n else None, "bins": table,
            "wrong_at_0_99_or_more": over, "share_at_0_99_or_more": (sum(c >= 0.99 for c, _ in rows) / n) if n else None}


def to_md(name: str, r: dict) -> str:
    lines = [f"# Calibration of `{name}` (SUPPORTS and CONTRADICTS verdicts, n={r['n_judged']})", "",
             f"- expected calibration error (ECE): **{r['ece']:.3f}**" if r["ece"] is not None else "- no verdicts",
             f"- verdicts at confidence ≥ 0.99: {r['share_at_0_99_or_more']:.0%} of all; {r['wrong_at_0_99_or_more']} of "
             "them wrong" if r["n_judged"] else "", "",
             "| confidence | n | mean confidence | share right |", "|---|---|---|---|"]
    lines += [f"| {b['from']:.2f}–{b['to']:.2f} | {b['n']} | {b['mean_confidence']:.3f} | {b['accuracy']:.3f} |"
              for b in r["bins"]]
    lines += ["", "> Analysis only. A gap between the two columns means the shown confidence should not be read as a "
              "probability of being right."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run", help="a results folder with predictions.jsonl, e.g. eval/results/finetuned_nli_selector_v2_capped")
    a = ap.parse_args(argv)
    run = Path(a.run)
    preds = [json.loads(line) for line in (run / "predictions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    r = reliability(preds)
    (run / "calibration.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    (run / "calibration.md").write_text(to_md(run.name, r), encoding="utf-8")
    print(to_md(run.name, r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
