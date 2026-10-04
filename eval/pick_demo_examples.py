"""Pick the live-demo examples by seed, with the DEPLOYED model, from data we never tuned on.
Owner: Data & Evaluation (Sahil).

    python -m eval.pick_demo_examples                      # dev split, seed 0, 2 examples per verdict (main + backup)
    python -m eval.pick_demo_examples --seed 1 --per-label 2 --include-failure

Why this exists (docs/midterm_oct6.md, pre-demo checklist): the three demo beats (a SUPPORTS, a CONTRADICTS, a NOT
ENOUGH EVIDENCE) must come "from data we did not tune on, and they behave".  Hand-picking claims until one works is
cherry-picking, and we would not know how often it fails.  This script makes the choice auditable:

  * claims come from SciFact **dev** (tau was tuned on train; dev is only ever used for reporting);
  * candidates are visited in a **seeded** random order, per gold label, and filtered only by what fits on a screen
    (one cited paper, short claim, short abstract);
  * each candidate goes through EXACTLY the app's path: paste the cited paper's title + abstract -> verify_against_paper;
  * the first `--per-label` candidates whose verdict equals the gold label are kept (main + backup), and we record how
    many candidates were tried to find them, so "it worked 2 out of 5 times" is written down, not hidden;
  * `--include-failure` also keeps the first candidate the model got WRONG, for an honest "what did not work" beat.

Writes  demo/demo_examples.json   (read by the app's demo selector and by tools/demo_check.py)
        demo/DEMO_SCRIPT.md       (presenter card: what to paste, what should appear, what to say if it does not)

The tried/kept counts are NOT a metric (tiny, filtered sample).  The metric is in eval/results/.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.data_io import find_scifact_dir, is_synthetic_fixture, load_claims, load_corpus
from src.ingest import paper_from_text
from src.schema import CONTRADICT, DISPLAY, NEI, SUPPORT

LABEL_ORDER = (SUPPORT, CONTRADICT, NEI)
OUT_JSON = Path("demo/demo_examples.json")
OUT_MD = Path("demo/DEMO_SCRIPT.md")


def _git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5).stdout.strip() or None
    except Exception:
        return None


def candidates(claims, corpus_by_id: dict, label: str, max_claim_chars: int = 140, max_sentences: int = 12) -> list:
    """Claims of one gold label that fit on a demo screen: exactly one cited paper, which we have, short enough to read.

    For SUPPORT / CONTRADICT the cited paper must be the annotated evidence paper (so the gold label is about THAT paper).
    For NEI, the cited paper is the one annotators read and found no evidence in: exactly the "paper I cite" setting.
    """
    out = []
    for c in claims:
        if c.gold_label != label or len(c.cited_doc_ids) != 1 or len(c.claim) > max_claim_chars:
            continue
        doc = corpus_by_id.get(c.cited_doc_ids[0])
        if doc is None or not doc.sentences or len(doc.sentences) > max_sentences:
            continue
        if label != NEI and doc.doc_id not in c.gold_docs:
            continue
        out.append((c, doc))
    return sorted(out, key=lambda cd: cd[0].id)


def run_one(pipe, claim, doc) -> dict:
    """Exactly what the app does when a presenter pastes the title + abstract."""
    paper = paper_from_text(doc.title, doc.abstract)
    v = pipe.verify_against_paper(claim.claim, paper)
    ev = v.evidence[0] if v.evidence else None
    return {
        "claim_id": claim.id, "claim": claim.claim, "gold": claim.gold_label, "doc_id": doc.doc_id,
        "title": doc.title, "abstract": doc.abstract,
        "verdict": v.label, "display": v.display_label, "confidence": round(float(v.confidence), 4),
        "abstained": bool(v.abstained), "note": v.note,
        "evidence_sentences": list(ev.sentences) if ev else [],
        "probs": ev.probs.as_dict() if ev else None,
        "latency_ms": round(v.latency_ms),
    }


def select(pipe, claims, corpus_by_id: dict, seed: int = 0, per_label: int = 2, max_tries: int = 40,
           include_failure: bool = False, **filters) -> dict:
    """Visit candidates in seeded order; keep the first `per_label` that the model gets right."""
    examples, tried, failure = [], {}, None
    for label in LABEL_ORDER:
        pool = candidates(claims, corpus_by_id, label, **filters)
        random.Random(f"{seed}:{label}").shuffle(pool)
        kept = n = 0
        for claim, doc in pool[:max_tries]:
            n += 1
            r = run_one(pipe, claim, doc)
            if r["verdict"] == label:
                kept += 1
                examples.append(dict(r, slot=f"{label}-{kept}", role="main" if kept == 1 else "backup", tried_before=n))
                if kept >= per_label:
                    break
            elif include_failure and failure is None:
                failure = dict(r, slot="FAILURE", role="honest failure")
        tried[label] = {"candidates": len(pool), "tried": n, "kept": kept}
    return {"examples": examples, "failure": failure, "tried": tried}


def render_script(payload: dict) -> str:
    lines = ["# Live demo script (generated by `python -m eval.pick_demo_examples`; do not edit by hand)", ""]
    if not payload.get("validated") or payload.get("synthetic_fixture"):
        lines += ["> **NOT FOR THE DEMO:** picked with an UNVALIDATED backend or the synthetic test fixture. "
                  "Re-run without overrides on real SciFact.", ""]
    lines += [f"Run `{payload['deployed_run']}` (verifier `{payload.get('verifier')}`, validated {payload.get('validated')}), "
             f"tau {payload['tau']}, picked from SciFact **{payload['split']}** "
             f"with seed {payload['seed']} at commit `{(payload['git_commit'] or 'unknown')[:7]}`.", "",
             "In the app: **Check a citation** -> pick the example in *Demo examples* (or choose *Paste an abstract* and paste the "
             "title and abstract below) -> **Check citation**.", "",
             "| verdict | candidates tried | kept |", "|---|---|---|"]
    for label, t in payload["tried"].items():
        lines.append(f"| {DISPLAY[label]} | {t['tried']} of {t['candidates']} | {t['kept']} |")
    lines += ["", "> The tried/kept counts are not a metric (small, filtered sample). If a main example misbehaves on the day, "
                  "use its backup and SAY so: \"this one did not behave on the laptop today; here is the backup\".", ""]
    items = payload["examples"] + ([payload["failure"]] if payload.get("failure") else [])
    for e in items:
        lines += [f"## {e['slot']} ({e['role']}): SciFact dev claim #{e['claim_id']}", "",
                  f"**Claim:** {e['claim']}", "",
                  f"**Paper:** {e['title']}", "",
                  f"**Expected on screen:** {e['display']} (confidence {e['confidence']:.2f}); SciFact label `{e['gold']}`", ""]
        if e["evidence_sentences"]:
            lines += ["**Evidence sentences shown:**", ""] + [f"> {s}" for s in e["evidence_sentences"]] + [""]
        if e["role"] == "honest failure":
            lines += ["**What to say:** the model answers "
                      f"{e['display']} but the annotators say `{e['gold']}`. This is the kind of error in "
                      "`eval/results/RESULTS_session05.md` section 4.", ""]
        lines += [f"<details><summary>Abstract to paste</summary>\n\n{e['abstract']}\n\n</details>", ""]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=None, help="default: the deployed config's data dir (data/scifact)")
    ap.add_argument("--split", default="dev", choices=["dev"], help="dev only: tau was tuned on train, test has no labels")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--per-label", type=int, default=2, help="1 main + backups")
    ap.add_argument("--max-tries", type=int, default=40)
    ap.add_argument("--max-claim-chars", type=int, default=140)
    ap.add_argument("--max-sentences", type=int, default=12)
    ap.add_argument("--include-failure", action="store_true")
    ap.add_argument("--allow-unvalidated", action="store_true", help="tests only: accept a non-deployed / demo backend")
    ap.add_argument("--out", default=str(OUT_JSON))
    ap.add_argument("--script-out", default=str(OUT_MD))
    a = ap.parse_args(argv)

    from src.config import load_config
    from src.pipeline import build_pipeline

    cfg = load_config()
    if a.data_dir:
        cfg.data_dir = a.data_dir
    pipe = build_pipeline(cfg, allow_fallback=a.allow_unvalidated)
    m = pipe.meta
    if not a.allow_unvalidated and (not m.get("validated") or m.get("demo_only")):
        raise SystemExit("The deployed, validated model is not what loaded (sidebar would say UNVALIDATED/DEMO). "
                         "Unset CITECHECK_* overrides and check eval/results/deployed_config.json. Refusing to pick demo examples.")
    d = find_scifact_dir(cfg.data_dir)
    if d is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    corpus_by_id = {x.doc_id: x for x in load_corpus(d / "corpus.jsonl")}
    claims = load_claims(d / f"claims_{a.split}.jsonl")

    sel = select(pipe, claims, corpus_by_id, seed=a.seed, per_label=a.per_label, max_tries=a.max_tries,
                 include_failure=a.include_failure, max_claim_chars=a.max_claim_chars, max_sentences=a.max_sentences)
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(), "split": a.split, "seed": a.seed,
        "synthetic_fixture": is_synthetic_fixture(d),
        "deployed_run": m.get("deployed_run"), "validated": bool(m.get("validated")), "verifier": m.get("verifier"),
        "tau": m.get("tau"), "k": m.get("k"),
        "how_chosen": "seeded order over dev claims with one cited paper; first per-label hits whose verdict equals the gold "
                      "label, run through the app's paste-an-abstract path",
        "data_licence": "SciFact claims CC BY 4.0, abstracts ODC-By 1.0 (https://github.com/allenai/scifact)",
        **sel,
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path(a.script_out).write_text(render_script(payload), encoding="utf-8")
    missing = [lab for lab in LABEL_ORDER if sel["tried"][lab]["kept"] == 0]
    print({lab: t for lab, t in sel["tried"].items()}, "->", out)
    if missing:
        print(f"WARNING: no candidate behaved for {missing} within --max-tries. Do NOT hand-pick one. Either raise "
              "--max-tries (and write down that you did) or demo that verdict as a failure and say so.")
    return payload


if __name__ == "__main__":
    main()
