"""Is this paper relevant to MY research direction?  Owner: Engineering (Sakshaat), with Product.

Deliberately modest: a transparent score plus the matched terms, and an explicit "uncalibrated" note.
It is a SECONDARY feature (citation support is the MVP).  There is no labelled relevance data yet;
Users & Research collect "do you agree?" clicks in the app, which is what will let us calibrate the bands.

Two methods:
  * dense  : cosine similarity of sentence embeddings (needs an embedder; used when available)
  * lexical: share of the direction's (IDF-weighted) content words that occur in the paper's title+abstract
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from .schema import Paper, RelevanceResult
from .text_utils import _stem, tokenize

BANDS = {  # (likely_at_least, maybe_at_least)  -- PLACEHOLDERS until calibrated on user data
    "lexical": (0.60, 0.30),
    "dense": (0.50, 0.30),
}
UNCALIBRATED = "Bands are uncalibrated placeholders: treat this as a hint for skimming, not a judgement."


class RelevanceScorer:
    def __init__(self, embedder=None, idf: Optional[dict] = None):
        self.embedder = embedder
        self.idf = idf or {}

    def _w(self, tok: str) -> float:
        return self.idf.get(tok, 1.0)

    def score(self, direction: str, paper: Paper) -> RelevanceResult:
        if not (direction or "").strip():
            raise ValueError("Describe your research direction first.")
        text = f"{paper.title} {paper.abstract}"
        surface = tokenize(direction, stem=False)
        stems = [_stem(w) for w in surface]
        paper_stems = set(tokenize(text))
        matched = sorted({w for w, s in zip(surface, stems) if s in paper_stems})

        if self.embedder is not None:
            v = np.asarray(self.embedder.encode([direction, text], normalize_embeddings=True, show_progress_bar=False))
            cos = float(v[0] @ v[1])
            score, method = max(0.0, min(1.0, cos)), "dense"
        else:
            total = sum(self._w(s) for s in set(stems))
            hit = sum(self._w(s) for s in set(stems) if s in paper_stems)
            score, method = (hit / total if total else 0.0), "lexical"

        likely, maybe = BANDS[method]
        band = "likely relevant" if score >= likely else "maybe relevant" if score >= maybe else "likely not relevant"
        return RelevanceResult(score=score, band=band, matched_terms=matched, method=method, note=UNCALIBRATED)
