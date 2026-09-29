"""Metrics.  Owner: Data & Evaluation (Sahil).  Pure functions, unit-tested against scikit-learn.

Three families:

1. Claim-level classification (our product-facing metric): 3-class macro-F1 over
   SUPPORT / CONTRADICT / NEI, plus the SAFETY metrics false-SUPPORT rate and SUPPORT precision.
2. Retrieval: Recall@k, Precision@k, MRR, nDCG@k against the gold evidence papers.
   NOTE: SciFact claims average ~1 gold paper, so Precision@k is capped at 1/k.  Recall@k and MRR
   are the informative numbers; we report Precision@k too because the lean canvas promised it.
3. Abstract-level P/R/F1 in the style of the SciFact leaderboard (label-only and label+rationale) so
   our numbers can be read next to published ones.  (Not the official scorer: see eval/README.md.)
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Sequence

import numpy as np

LABELS = ("SUPPORT", "CONTRADICT", "NEI")


# --------------------------------------------------------------------------- #
# 1. Classification
# --------------------------------------------------------------------------- #
def confusion_matrix(y_true: Sequence, y_pred: Sequence, labels: Sequence = LABELS) -> list:
    """Rows = gold, columns = predicted, in `labels` order."""
    idx = {l: i for i, l in enumerate(labels)}
    m = [[0] * len(labels) for _ in labels]
    for t, p in zip(y_true, y_pred):
        if t in idx and p in idx:
            m[idx[t]][idx[p]] += 1
    return m


def prf_per_class(y_true: Sequence, y_pred: Sequence, labels: Sequence = LABELS) -> Dict[str, dict]:
    cm = confusion_matrix(y_true, y_pred, labels)
    out = {}
    for i, l in enumerate(labels):
        tp = cm[i][i]
        fp = sum(cm[j][i] for j in range(len(labels))) - tp
        fn = sum(cm[i]) - tp
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        out[l] = {"precision": p, "recall": r, "f1": f, "support": tp + fn}
    return out


def macro_f1(y_true: Sequence, y_pred: Sequence, labels: Sequence = LABELS) -> float:
    per = prf_per_class(y_true, y_pred, labels)
    return sum(v["f1"] for v in per.values()) / len(labels)


def accuracy(y_true: Sequence, y_pred: Sequence) -> float:
    n = len(y_true)
    return sum(t == p for t, p in zip(y_true, y_pred)) / n if n else 0.0


def false_support_rate(y_true: Sequence, y_pred: Sequence) -> float:
    """Of the claims whose gold label is NOT SUPPORT, the share we wrongly called SUPPORT."""
    neg = [(t, p) for t, p in zip(y_true, y_pred) if t != "SUPPORT"]
    return sum(p == "SUPPORT" for _, p in neg) / len(neg) if neg else 0.0


def support_precision(y_true: Sequence, y_pred: Sequence) -> float:
    """Of the claims we called SUPPORT, the share that really are."""
    called = [(t, p) for t, p in zip(y_true, y_pred) if p == "SUPPORT"]
    return sum(t == "SUPPORT" for t, _ in called) / len(called) if called else 0.0


def coverage(y_pred: Sequence) -> float:
    """Share of claims on which the system committed to SUPPORT/CONTRADICT (did not abstain)."""
    return sum(p != "NEI" for p in y_pred) / len(y_pred) if y_pred else 0.0


def bootstrap_ci(
    y_true: Sequence, y_pred: Sequence, fn: Callable = macro_f1, n_boot: int = 1000, seed: int = 0, alpha: float = 0.05
) -> tuple:
    """Percentile bootstrap CI over claims.  With ~300 dev claims expect roughly +-4-5 F1 points."""
    rng = np.random.default_rng(seed)
    yt, yp = np.asarray(y_true, dtype=object), np.asarray(y_pred, dtype=object)
    n = len(yt)
    if n == 0:
        return (0.0, 0.0)
    vals = []
    for _ in range(n_boot):
        s = rng.integers(0, n, n)
        vals.append(fn(list(yt[s]), list(yp[s])))
    return (float(np.percentile(vals, 100 * alpha / 2)), float(np.percentile(vals, 100 * (1 - alpha / 2))))


def paired_bootstrap_diff(
    y_true: Sequence, pred_a: Sequence, pred_b: Sequence, fn: Callable = macro_f1, n_boot: int = 1000, seed: int = 0
) -> dict:
    """Is system A really better than B?  Resample claims jointly; report the F1 difference (A-B)."""
    rng = np.random.default_rng(seed)
    yt, a, b = (np.asarray(x, dtype=object) for x in (y_true, pred_a, pred_b))
    n = len(yt)
    diffs = []
    for _ in range(n_boot):
        s = rng.integers(0, n, n)
        diffs.append(fn(list(yt[s]), list(a[s])) - fn(list(yt[s]), list(b[s])))
    diffs = np.asarray(diffs)
    return {
        "diff": float(fn(list(yt), list(a)) - fn(list(yt), list(b))),
        "ci95": (float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))),
        "p_a_better": float((diffs > 0).mean()),
    }


# --------------------------------------------------------------------------- #
# 2. Retrieval
# --------------------------------------------------------------------------- #
def recall_at_k(ranked: Sequence, gold: set, k: int) -> float:
    return len(set(ranked[:k]) & gold) / len(gold) if gold else 0.0


def hit_at_k(ranked: Sequence, gold: set, k: int) -> float:
    return 1.0 if set(ranked[:k]) & gold else 0.0


def precision_at_k(ranked: Sequence, gold: set, k: int) -> float:
    return len(set(ranked[:k]) & gold) / k if k else 0.0


def reciprocal_rank(ranked: Sequence, gold: set) -> float:
    for i, d in enumerate(ranked, 1):
        if d in gold:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked: Sequence, gold: set, k: int = 10) -> float:
    dcg = sum(1.0 / math.log2(i + 1) for i, d in enumerate(ranked[:k], 1) if d in gold)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(gold), k) + 1))
    return dcg / ideal if ideal else 0.0


def retrieval_report(rankings: dict, gold: dict, ks: Sequence = (1, 3, 5, 10, 20)) -> dict:
    """rankings: {claim_id: [doc_id, ...]}, gold: {claim_id: set(doc_id)}.  Claims without gold docs are skipped."""
    ids = [c for c in gold if gold[c]]
    n = len(ids)
    rep = {"n_claims": n}
    for k in ks:
        rep[f"recall@{k}"] = sum(recall_at_k(rankings[c], gold[c], k) for c in ids) / n if n else 0.0
        rep[f"hit@{k}"] = sum(hit_at_k(rankings[c], gold[c], k) for c in ids) / n if n else 0.0
        rep[f"precision@{k}"] = sum(precision_at_k(rankings[c], gold[c], k) for c in ids) / n if n else 0.0
    rep["mrr"] = sum(reciprocal_rank(rankings[c], gold[c]) for c in ids) / n if n else 0.0
    rep["ndcg@10"] = sum(ndcg_at_k(rankings[c], gold[c], 10) for c in ids) / n if n else 0.0
    rep["avg_gold_docs_per_claim"] = sum(len(gold[c]) for c in ids) / n if n else 0.0
    return rep


# --------------------------------------------------------------------------- #
# 3. Abstract-level (SciFact-leaderboard style)
# --------------------------------------------------------------------------- #
def abstract_level_prf(pred: dict, gold: dict, require_rationale: bool = False, max_pred_sentences: int = 3) -> dict:
    """
    pred: {claim_id: {doc_id: {"label": "SUPPORT"|"CONTRADICT", "sentences": [int, ...]}}}
    gold: {claim_id: {doc_id: {"label": ..., "rationales": [[int, ...], ...]}}}

    A predicted abstract is correct if it is a gold abstract, its label matches, and (when
    require_rationale) some gold rationale set is contained in the first `max_pred_sentences`
    predicted sentences.  Precision = correct/predicted, recall = correct/gold, over ALL claims
    (so predicting evidence for a claim that has none costs precision).
    """
    n_pred = n_gold = n_correct = 0
    for cid, gdocs in gold.items():
        n_gold += len(gdocs)
        pdocs = pred.get(cid, {})
        n_pred += len(pdocs)
        for doc_id, p in pdocs.items():
            g = gdocs.get(doc_id)
            if g is None or g["label"] != p["label"]:
                continue
            if require_rationale:
                chosen = set(p.get("sentences", [])[:max_pred_sentences])
                if not any(set(r) <= chosen for r in g["rationales"]):
                    continue
            n_correct += 1
    prec = n_correct / n_pred if n_pred else 0.0
    rec = n_correct / n_gold if n_gold else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "n_pred": n_pred, "n_gold": n_gold, "n_correct": n_correct}
