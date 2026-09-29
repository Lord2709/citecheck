"""Evidence selection: pick the sentences of a retrieved paper that matter for a claim,
then have a verifier judge them.  Owner: Data & Evaluation (Sahil).

This module is the ONE place where "retrieved papers -> per-paper class probabilities"
is computed.  The eval harness (batched over all claims) and the product pipeline
(one claim at a time) both call score_claim_docs(), so the numbers we report come from
the same code path the user runs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from .schema import Hit, Probs
from .text_utils import tokenize


# --------------------------------------------------------------------------- #
# Sentence scorers
# --------------------------------------------------------------------------- #
class LexicalSentenceScorer:
    """Score of a sentence = share of the claim's IDF mass that the sentence covers (0..1)."""

    def __init__(self, idf: Optional[dict] = None):
        self.idf = idf or {}
        self._default = max(self.idf.values()) if self.idf else 1.0

    @classmethod
    def from_docs(cls, docs: Sequence) -> "LexicalSentenceScorer":
        df, n = {}, 0
        for d in docs:
            n += 1
            for t in set(tokenize(d.text)):
                df[t] = df.get(t, 0) + 1
        return cls({t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()})

    def _w(self, tok: str) -> float:
        return self.idf.get(tok, self._default)

    def score(self, claim: str, sentences: Sequence) -> list:
        q = set(tokenize(claim))
        total = sum(self._w(t) for t in q)
        if total == 0:
            return [0.0] * len(sentences)
        return [sum(self._w(t) for t in q & set(tokenize(s))) / total for s in sentences]


class DenseSentenceScorer:
    """Cosine similarity between claim and sentence embeddings (embedder: sentence-transformers style)."""

    def __init__(self, embedder):
        self.embedder = embedder

    def score(self, claim: str, sentences: Sequence) -> list:
        if not sentences:
            return []
        vecs = self.embedder.encode([claim, *sentences], normalize_embeddings=True, show_progress_bar=False)
        vecs = np.asarray(vecs)
        return (vecs[1:] @ vecs[0]).tolist()


def select_sentences(claim: str, sentences: Sequence, m: int = 3, scorer=None) -> list:
    """Indices (in reading order) of the m sentences most related to the claim."""
    if not sentences:
        return []
    scorer = scorer or LexicalSentenceScorer()
    scores = scorer.score(claim, sentences)
    order = sorted(range(len(sentences)), key=lambda i: (-scores[i], i))[:m]
    return sorted(order)


def build_premise(sentences: Sequence, idxs: Sequence) -> str:
    return " ".join(sentences[i] for i in idxs)


# --------------------------------------------------------------------------- #
# Retrieved papers -> class probabilities
# --------------------------------------------------------------------------- #
@dataclass
class DocScore:
    hit: Hit
    sentence_idxs: list
    premise: str
    probs: Probs


def score_claim_docs(items: Sequence, verifier, scorer=None, m: int = 3, gold_sentences: Optional[Sequence] = None) -> list:
    """Judge every (claim, retrieved paper) pair with one batched verifier call.

    items: [(claim_text, [Hit, ...]), ...]
    gold_sentences: optional, parallel to `items`; for each claim a {doc_id: [idx,...]} dict that
        overrides sentence selection (used ONLY for the oracle-rationale ablation).
    Returns: list (one per claim) of list[DocScore] in the order of the input hits.
    """
    scorer = scorer or LexicalSentenceScorer()
    pairs, index = [], []  # index[i] = (claim_no, doc_no)
    prepared = []
    for ci, (claim, hits) in enumerate(items):
        row = []
        for di, hit in enumerate(hits):
            sents = hit.doc.sentences
            override = gold_sentences[ci].get(hit.doc.doc_id) if gold_sentences is not None else None
            idxs = list(override) if override else select_sentences(claim, sents, m=m, scorer=scorer)
            premise = build_premise(sents, idxs) if idxs else hit.doc.title
            row.append((idxs, premise))
            pairs.append((premise, claim))
            index.append((ci, di))
        prepared.append(row)

    probs = verifier.predict_pairs(pairs) if pairs else []
    out = [[None] * len(hits) for _, hits in items]
    for (ci, di), p in zip(index, probs):
        idxs, premise = prepared[ci][di]
        out[ci][di] = DocScore(items[ci][1][di], idxs, premise, p)
    return out
