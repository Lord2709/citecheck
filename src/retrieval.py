"""Retrieval over a document collection.  Owner: Data & Evaluation (Sahil).

Replaces the Session-4 BM25 script (same algorithm, now behind a common interface):

    BM25Retriever      lexical baseline (rank_bm25, stemmed + stop-word filtered)
    DenseRetriever     bi-encoder embeddings (sentence-transformers), cached on disk
    HybridRetriever    Reciprocal Rank Fusion of several retrievers
    CrossEncoderReranker  re-scores the top-N of any retriever with a cross-encoder

Every retriever exposes  .search(query, k) -> list[Hit]  and .name  so the eval
harness and the app can swap them freely.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from .schema import Doc, Hit
from .text_utils import tokenize


def _top_k(scores: np.ndarray, k: int) -> np.ndarray:
    k = min(k, len(scores))
    if k <= 0:
        return np.array([], dtype=int)
    idx = np.argpartition(-scores, k - 1)[:k]
    return idx[np.argsort(-scores[idx], kind="stable")]


class BM25Retriever:
    name = "bm25"

    def __init__(self, docs: Sequence, k1: float = 1.5, b: float = 0.75):
        from rank_bm25 import BM25Okapi

        self.docs = list(docs)
        self._bm25 = BM25Okapi([tokenize(d.text) for d in self.docs], k1=k1, b=b)

    def scores(self, query: str) -> np.ndarray:
        q = tokenize(query)
        if not q:
            return np.zeros(len(self.docs))
        return np.asarray(self._bm25.get_scores(q), dtype=float)

    def search(self, query: str, k: int = 10) -> list:
        s = self.scores(query)
        return [Hit(self.docs[i], float(s[i]), r + 1) for r, i in enumerate(_top_k(s, k))]


class DenseRetriever:
    """Bi-encoder retrieval.  `embedder` must expose encode(list[str], ...) -> ndarray."""

    def __init__(
        self,
        docs: Sequence,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        embedder=None,
        batch_size: int = 64,
        cache_dir: Optional[str] = "data/cache/embeddings",
        max_seq_length: int = 256,
    ):
        self.docs = list(docs)
        self.model_name = model_name
        self.name = "dense"
        self._embedder = embedder
        self._batch = batch_size
        self._max_len = max_seq_length
        self._cache_dir = Path(cache_dir) if cache_dir else None
        self._emb = self._load_or_embed()

    def _get_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(self.model_name)
            self._embedder.max_seq_length = self._max_len
        return self._embedder

    def _encode(self, texts):
        vecs = self._get_embedder().encode(
            list(texts), batch_size=self._batch, normalize_embeddings=True, show_progress_bar=False
        )
        return np.asarray(vecs, dtype=np.float32)

    def _cache_path(self) -> Optional[Path]:
        if self._cache_dir is None:
            return None
        h = hashlib.sha1()
        h.update(self.model_name.encode())
        for d in self.docs:
            h.update(d.doc_id.encode())
            h.update(str(len(d.text)).encode())
        return self._cache_dir / f"emb_{h.hexdigest()[:16]}.npy"

    def _load_or_embed(self) -> np.ndarray:
        path = self._cache_path()
        if path is not None and path.exists():
            return np.load(path)
        emb = self._encode([d.text for d in self.docs])
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            np.save(path, emb)
        return emb

    def scores(self, query: str) -> np.ndarray:
        q = self._encode([query])[0]
        return self._emb @ q

    def search(self, query: str, k: int = 10) -> list:
        s = self.scores(query)
        return [Hit(self.docs[i], float(s[i]), r + 1) for r, i in enumerate(_top_k(s, k))]


class HybridRetriever:
    """Reciprocal Rank Fusion:  score(d) = sum_i  w_i / (rrf_k + rank_i(d))."""

    def __init__(self, retrievers: Sequence, weights: Optional[Sequence] = None, rrf_k: int = 60, depth: int = 100):
        self.retrievers = list(retrievers)
        self.weights = list(weights) if weights else [1.0] * len(self.retrievers)
        self.rrf_k, self.depth = rrf_k, depth
        self.name = "hybrid(" + "+".join(r.name for r in self.retrievers) + ")"

    def search(self, query: str, k: int = 10) -> list:
        fused, docs = {}, {}
        for w, r in zip(self.weights, self.retrievers):
            for h in r.search(query, self.depth):
                fused[h.doc.doc_id] = fused.get(h.doc.doc_id, 0.0) + w / (self.rrf_k + h.rank)
                docs[h.doc.doc_id] = h.doc
        ranked = sorted(fused.items(), key=lambda kv: -kv[1])[:k]
        return [Hit(docs[i], float(s), r + 1) for r, (i, s) in enumerate(ranked)]


class CrossEncoderReranker:
    """Re-scores the top `depth` hits of `base` with a cross-encoder (query, doc text)."""

    def __init__(self, base, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", depth: int = 30, scorer=None):
        self.base, self.depth, self.model_name = base, depth, model_name
        self._scorer = scorer
        self.name = f"{base.name}+rerank"

    def _get_scorer(self):
        if self._scorer is None:
            from sentence_transformers import CrossEncoder

            self._scorer = CrossEncoder(self.model_name, max_length=384)
        return self._scorer

    def search(self, query: str, k: int = 10) -> list:
        cands = self.base.search(query, max(self.depth, k))
        if not cands:
            return []
        s = np.asarray(self._get_scorer().predict([(query, h.doc.text) for h in cands]), dtype=float)
        order = np.argsort(-s, kind="stable")[:k]
        return [Hit(cands[i].doc, float(s[i]), r + 1) for r, i in enumerate(order)]


def build_retriever(name: str, docs: Sequence, **kw):
    """name: bm25 | dense | hybrid | hybrid+rerank | bm25+rerank."""
    name = name.lower()
    if name == "bm25":
        return BM25Retriever(docs)
    if name == "dense":
        return DenseRetriever(docs, **kw)
    if name == "hybrid":
        return HybridRetriever([BM25Retriever(docs), DenseRetriever(docs, **kw)])
    if name == "hybrid+rerank":
        return CrossEncoderReranker(HybridRetriever([BM25Retriever(docs), DenseRetriever(docs, **kw)]))
    if name == "bm25+rerank":
        return CrossEncoderReranker(BM25Retriever(docs))
    raise ValueError(f"unknown retriever '{name}' (bm25 | dense | hybrid | hybrid+rerank | bm25+rerank)")
