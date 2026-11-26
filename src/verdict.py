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


def decide(doc_probs: Sequence, tau: float = 0.5, margin: float = 0.0,
           tau_contradict: Optional[float] = None) -> Decision:
    """doc_probs: list[Probs], one per retrieved paper.

    * best_support / best_contradict = highest class probability over papers.
    * SUPPORT needs best_support >= tau; CONTRADICT needs best_contradict >= tau_contradict (default: tau) AND
      best_contradict > best_support.  A lower tau_contradict catches more contradictions without ever turning a
      verdict into SUPPORT, so the false-SUPPORT rate cannot rise.
    * If neither qualifies                      -> NEI (abstain, "below threshold").
    * If both qualify and are within `margin`   -> NEI (abstain, "conflicting evidence").
    * Otherwise the stronger of the two wins.
    NEI confidence is reported as 1 - (strongest non-neutral probability); the site shows the strongest probability
    itself, so a "not enough evidence" verdict never reads as "0.99 sure".
    """
    if not doc_probs:
        return Decision(NEI, 1.0, None, True, "no evidence retrieved")
    tc = tau if tau_contradict is None else tau_contradict
    si = max(range(len(doc_probs)), key=lambda i: doc_probs[i].support)
    ci = max(range(len(doc_probs)), key=lambda i: doc_probs[i].contradict)
    s, c = doc_probs[si].support, doc_probs[ci].contradict
    top = max(s, c)
    s_ok, c_ok = s >= tau, c >= tc and c > s
    if not (s_ok or c_ok):
        limit = f"{tau:.2f}" if tc == tau else f"{tau:.2f} (support) / {tc:.2f} (contradiction)"
        return Decision(NEI, 1.0 - top, None, True, f"strongest evidence {top:.2f} is below threshold {limit}")
    if s >= tau and c >= tc and abs(s - c) < margin:
        return Decision(NEI, 1.0 - top, None, True, "papers disagree with similar strength")
    if c_ok:
        return Decision(CONTRADICT, c, ci, False)
    return Decision(SUPPORT, s, si, False)


def doc_level_labels(doc_probs: Sequence, tau: float = 0.5) -> list:
    """Per-paper label (SUPPORT / CONTRADICT) or None when the paper is not judged to be evidence."""
    out = []
    for p in doc_probs:
        top = max(p.support, p.contradict)
        out.append(None if top < tau else (SUPPORT if p.support >= p.contradict else CONTRADICT))
    return out
