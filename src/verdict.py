"""Turn per-paper class probabilities into ONE claim-level verdict.  Owner: Data & Evaluation (Sahil).

Design choice (safety first): a false SUPPORTS is the most harmful error (it gives a researcher
unwarranted confidence), so the default is to ABSTAIN -- answer NOT ENOUGH EVIDENCE -- unless a
paper's evidence clears a confidence threshold tau.  tau is tuned on the TRAIN split (never on dev/test)
by eval/run_eval.py and then shipped in eval/results/deployed_config.json.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from .schema import CONTRADICT, NEI, SUPPORT, Probs


@dataclass
class Decision:
    label: str
    confidence: float
    doc_index: Optional[int]  # index (into the input list) of the paper that drove the decision
    abstained: bool
    note: str = ""


def decide(doc_probs: Sequence, tau: float = 0.5, margin: float = 0.0) -> Decision:
    """doc_probs: list[Probs], one per retrieved paper.

    * best_support / best_contradict = highest class probability over papers.
    * If neither reaches tau                    -> NEI (abstain, "below threshold").
    * If both reach tau and are within `margin` -> NEI (abstain, "conflicting evidence").
    * Otherwise the stronger of the two wins.
    NEI confidence is reported as 1 - (strongest non-neutral probability).
    """
    if not doc_probs:
        return Decision(NEI, 1.0, None, True, "no evidence retrieved")
    si = max(range(len(doc_probs)), key=lambda i: doc_probs[i].support)
    ci = max(range(len(doc_probs)), key=lambda i: doc_probs[i].contradict)
    s, c = doc_probs[si].support, doc_probs[ci].contradict
    top = max(s, c)
    if top < tau:
        return Decision(NEI, 1.0 - top, None, True, f"strongest evidence {top:.2f} is below threshold {tau:.2f}")
    if s >= tau and c >= tau and abs(s - c) < margin:
        return Decision(NEI, 1.0 - top, None, True, "papers disagree with similar strength")
    if s >= c:
        return Decision(SUPPORT, s, si, False)
    return Decision(CONTRADICT, c, ci, False)


def doc_level_labels(doc_probs: Sequence, tau: float = 0.5) -> list:
    """Per-paper label (SUPPORT / CONTRADICT) or None when the paper is not judged to be evidence."""
    out = []
    for p in doc_probs:
        top = max(p.support, p.contradict)
        out.append(None if top < tau else (SUPPORT if p.support >= p.contradict else CONTRADICT))
    return out
