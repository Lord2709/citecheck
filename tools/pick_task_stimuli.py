"""Pick the claims participants will check, by seed, so nobody can cherry-pick easy ones.
Owner: Users & Research (Ritika).

    python -m tools.pick_task_stimuli --seed 1 --split dev --out evidence/session05

Draws one SUPPORT, one CONTRADICT and one NEI claim at random (seeded) from SciFact and writes
  task_cards_PRINT.md   what you hand/show the participant (claim + the abstracts of the paper(s) it cites; NO answer)
  stimuli_key.csv       the gold answers (researcher-only while testing; commit afterwards so the choice is auditable)
The participant pastes the abstract into CiteCheck ("Paste an abstract") or searches the corpus, so no internet is needed.
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

from src.data_io import find_scifact_dir, load_claims, load_corpus


def pick(claims, seed: int, per_label: int = 1):
    rng = random.Random(seed)
    chosen = []
    for label in ("SUPPORT", "CONTRADICT", "NEI"):
        pool = sorted((c for c in claims if c.gold_label == label), key=lambda c: c.id)
        chosen += rng.sample(pool, min(per_label, len(pool)))
    rng.shuffle(chosen)  # do not always present them in the same label order
    return chosen


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="data/scifact")
    ap.add_argument("--split", default="dev", choices=["dev", "train"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--per-label", type=int, default=1)
    ap.add_argument("--out", default="evidence/session05")
    a = ap.parse_args(argv)

    d = find_scifact_dir(a.data_dir)
    if d is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    corpus = {x.doc_id: x for x in load_corpus(d / "corpus.jsonl")}
    picked = pick(load_claims(d / f"claims_{a.split}.jsonl"), a.seed, a.per_label)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cards = ["# Task cards (hand these to the participant; the answers are in stimuli_key.csv)", "",
             f"_Stimuli drawn with seed {a.seed} from SciFact {a.split}._", ""]
    key = []
    for n, c in enumerate(picked, 1):
        doc_id = (c.gold_docs or c.cited_doc_ids or [None])[0]
        doc = corpus.get(doc_id)
        cards += [f"## Task T1-{n}", "",
                  "**Claim:** " + c.claim, "",
                  f"**The paper someone cited for this claim:** {doc.title if doc else '(missing)'}", "",
                  "**Abstract:** " + (doc.abstract if doc else ""), "",
                  "**Your task:** using CiteCheck, decide whether this paper supports the claim, contradicts it, or does not "
                  "say enough to tell. Tell us which sentence(s) made you decide.", ""]
        key.append({"task": f"T1-{n}", "claim_id": c.id, "gold_label": c.gold_label, "doc_id": doc_id,
                    "doc_title": doc.title if doc else "", "claim": c.claim})
    (out / "task_cards_PRINT.md").write_text("\n".join(cards), encoding="utf-8")
    with open(out / "stimuli_key.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(key[0].keys()))
        w.writeheader()
        w.writerows(key)
    print(f"wrote {out / 'task_cards_PRINT.md'} and {out / 'stimuli_key.csv'}: {[(k['task'], k['gold_label']) for k in key]}")


if __name__ == "__main__":
    main()
