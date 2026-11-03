"""Split SciFact TRAIN into a fit part and a calibration part.   Owner: Data & Evaluation.

    python -m eval.train_split --data-dir data/scifact --out data/splits/scifact_train_v1.json

Why (docs/agent_plan.md, Part 2): the fine-tuned verifier must not be calibrated, nor have the agent's thresholds
(tau, tau strict, the escalation rule) tuned, on the same claims it was trained on.  Otherwise it looks more confident
than it is, and the agent escalates too rarely.  So:

  * fit   (default 80%): the ONLY claims eval/finetune_nli.py trains on
  * calib (default 20%): temperature scaling and threshold tuning (eval/run_eval.py --tune-split-file ... --tune-part calib)
  * dev   : reporting only.  test: never (no public labels).

The split is stratified by the claim's gold label (SUPPORT / CONTRADICT / NEI / MIXED) and fully determined by the seed
and the train file, so anyone can regenerate it and get the same ids.  The output holds claim IDS ONLY (no SciFact
text), so it is safe to commit; commit it so every run uses the same split.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from src.data_io import find_scifact_dir, is_synthetic_fixture, load_claims, sha256_file

SPLIT_VERSION = 1
PARTS = ("fit", "calib")


def make_split(claims, calib_frac: float = 0.2, seed: int = 13) -> dict:
    """Stratified, deterministic split of claim ids.  Returns {"fit": [ids], "calib": [ids], "by_label": {...}}."""
    if not 0.0 < calib_frac < 1.0:
        raise ValueError("calib_frac must be between 0 and 1")
    by_label = defaultdict(list)
    for c in claims:
        by_label[c.gold_label].append(c.id)
    rng = random.Random(seed)
    fit, calib, counts = [], [], {}
    for label in sorted(by_label):
        ids = sorted(set(by_label[label]))
        rng.shuffle(ids)
        n_cal = int(round(len(ids) * calib_frac))
        if len(ids) >= 2:  # keep at least one claim of each label on each side when possible
            n_cal = min(max(n_cal, 1), len(ids) - 1)
        else:
            n_cal = 0
        calib += ids[:n_cal]
        fit += ids[n_cal:]
        counts[label] = {"fit": len(ids) - n_cal, "calib": n_cal}
    return {"fit": sorted(fit), "calib": sorted(calib), "by_label": counts}


def build_split_file(train_path, calib_frac: float = 0.2, seed: int = 13) -> dict:
    train_path = Path(train_path)
    if train_path.name != "claims_train.jsonl":
        raise SystemExit(f"Refusing to split {train_path.name}: only claims_train.jsonl may be split (dev/test are never used for fitting or tuning).")
    claims = load_claims(train_path)
    s = make_split(claims, calib_frac, seed)
    return {
        "version": SPLIT_VERSION,
        "source_file": "claims_train.jsonl",
        "source_sha256": sha256_file(train_path),
        "synthetic_fixture": is_synthetic_fixture(train_path),
        "seed": seed,
        "calib_frac": calib_frac,
        "n_claims": len(claims),
        "counts_by_label": s["by_label"],
        "fit": s["fit"],
        "calib": s["calib"],
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "rule": "fit = train the verifier; calib = calibrate and tune thresholds; dev = report only; test = never",
    }


def load_split(path) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [k for k in ("fit", "calib", "source_sha256") if k not in d]
    if missing:
        raise ValueError(f"{path}: not a train split file (missing {missing})")
    if set(d["fit"]) & set(d["calib"]):
        raise ValueError(f"{path}: fit and calib overlap")
    return d


def select_part(claims, split: dict, part: str, train_path=None) -> list:
    """Claims whose id is in `part` of the split.  If `train_path` is given, refuses a split made from another file."""
    if part not in PARTS:
        raise ValueError(f"part must be one of {PARTS}")
    if train_path is not None and sha256_file(train_path) != split["source_sha256"]:
        raise ValueError("this split was made from a different claims_train.jsonl (sha256 differs); regenerate it")
    keep = set(split[part])
    return [c for c in claims if c.id in keep]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Split SciFact train into fit / calib parts (claim ids only).")
    ap.add_argument("--data-dir", default="data/scifact")
    ap.add_argument("--out", default="data/splits/scifact_train_v1.json")
    ap.add_argument("--calib-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=13)
    a = ap.parse_args(argv)
    d = find_scifact_dir(a.data_dir)
    if d is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    out = build_split_file(d / "claims_train.jsonl", a.calib_frac, a.seed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[written] {a.out}: {len(out['fit'])} fit / {len(out['calib'])} calib of {out['n_claims']} train claims")
    for label, c in sorted(out["counts_by_label"].items()):
        print(f"  {label:<11} fit {c['fit']:>4}   calib {c['calib']:>4}")
    if out["synthetic_fixture"]:
        print("  NOTE: made from the SYNTHETIC test fixture; do not commit this file as the real split.")
    return out


if __name__ == "__main__":
    main()
