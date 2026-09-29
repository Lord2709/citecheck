import zlib

import numpy as np
import pytest

from src.data_io import load_claims, load_corpus
from src.retrieval import BM25Retriever, CrossEncoderReranker, DenseRetriever, HybridRetriever, build_retriever
from src.schema import Doc, Hit


@pytest.fixture()
def docs(fixture_dir):
    return load_corpus(fixture_dir / "corpus.jsonl")


def test_bm25_finds_the_gold_paper_for_every_evidence_claim(fixture_dir, docs):
    r = BM25Retriever(docs)
    hits = r.search("zorvex bone density mice", k=3)
    assert hits[0].doc.doc_id == "1" and [h.rank for h in hits] == [1, 2, 3]
    assert hits[0].score >= hits[1].score >= hits[2].score
    for c in load_claims(fixture_dir / "claims_dev.jsonl"):
        if c.gold_docs:
            assert c.gold_docs[0] in [h.doc.doc_id for h in r.search(c.claim, k=3)], c.claim


def test_bm25_edge_cases(docs):
    r = BM25Retriever(docs)
    assert len(r.search("the of and", k=5)) == 5          # all stop-words -> zero scores, still returns k docs
    assert len(r.search("zorvex", k=100)) == len(docs)    # k larger than corpus


class FakeEmbedder:
    """Deterministic hashed bag-of-words embedder (no model download)."""
    def __init__(self, dim=64):
        self.dim, self.calls = dim, 0

    def encode(self, texts, batch_size=32, normalize_embeddings=True, show_progress_bar=False):
        self.calls += 1
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for w in t.lower().split():
                out[i, zlib.crc32(w.strip(".,").encode()) % self.dim] += 1
        n = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(n, 1e-9)


def test_dense_retriever_and_cache(docs, tmp_path):
    emb = FakeEmbedder()
    r1 = DenseRetriever(docs, embedder=emb, cache_dir=str(tmp_path))
    assert r1.search("zorvex supplementation bone density", k=1)[0].doc.doc_id == "1"
    calls = emb.calls
    r2 = DenseRetriever(docs, embedder=emb, cache_dir=str(tmp_path))       # second build must reuse the .npy cache
    assert list(tmp_path.glob("emb_*.npy")) and emb.calls == calls
    assert r2.search("nalbrix vaccine influenza", k=1)[0].doc.doc_id == "6"


class Stub:
    def __init__(self, name, order, docs):
        self.name, self._order, self._docs = name, order, {d.doc_id: d for d in docs}

    def search(self, q, k=10):
        return [Hit(self._docs[i], 0.0, r + 1) for r, i in enumerate(self._order[:k])]


def test_rrf_fusion_arithmetic(docs):
    a = Stub("a", ["1", "2", "3"], docs)
    b = Stub("b", ["2", "3", "1"], docs)
    h = HybridRetriever([a, b], rrf_k=60).search("q", 3)
    # doc2: ranks (2,1) -> 1/62+1/61 ; doc1: ranks (1,3) -> 1/61+1/63 ; doc3: ranks (3,2) -> 1/63+1/62
    assert [x.doc.doc_id for x in h] == ["2", "1", "3"]
    assert h[0].score == pytest.approx(1 / 62 + 1 / 61)
    assert h[1].score == pytest.approx(1 / 61 + 1 / 63)
    w = HybridRetriever([a, b], weights=[5.0, 1.0], rrf_k=60).search("q", 3)
    assert w[0].doc.doc_id == "1"                          # weighting retriever `a` shifts the winner


def test_reranker_reorders(docs):
    base = Stub("base", ["1", "2", "3"], docs)

    class Scorer:
        def predict(self, pairs):
            return [0.1 if "zorvex" in d.lower() else 0.9 if "glimmerine" in d.lower() else 0.5 for _, d in pairs]

    rr = CrossEncoderReranker(base, scorer=Scorer(), depth=3)
    assert [h.doc.doc_id for h in rr.search("q", 3)] == ["2", "3", "1"] and rr.name == "base+rerank"


def test_build_retriever_names(docs):
    assert build_retriever("bm25", docs).name == "bm25"
    with pytest.raises(ValueError):
        build_retriever("nope", docs)


def test_real_sentence_transformers_paths_with_tiny_models(docs, tmp_path):
    """Exercises the REAL SentenceTransformer / CrossEncoder code paths (encode kwargs, lazy load, cache, predict)
    with tiny random models. Retrieval quality is meaningless here; this only proves the plumbing works with the
    installed sentence-transformers version."""
    pytest.importorskip("torch")
    pytest.importorskip("sentence_transformers")
    from tests.tiny_model import make_tiny_nli, make_tiny_sentence_transformer

    st_path = make_tiny_sentence_transformer(tmp_path / "st")
    dense = DenseRetriever(docs, model_name=st_path, cache_dir=str(tmp_path / "cache"), max_seq_length=64)
    hits = dense.search("zorvex bone density", k=3)
    assert len(hits) == 3 and [h.rank for h in hits] == [1, 2, 3] and all(isinstance(h.score, float) for h in hits)
    again = DenseRetriever(docs, model_name=st_path, cache_dir=str(tmp_path / "cache"), max_seq_length=64)
    assert [h.doc.doc_id for h in again.search("zorvex bone density", 3)] == [h.doc.doc_id for h in hits]   # cached embeddings identical

    hybrid = HybridRetriever([BM25Retriever(docs), dense]).search("zorvex bone density", 3)
    assert len(hybrid) == 3

    ce_path = make_tiny_nli(tmp_path / "ce", num_labels=1)
    rr = CrossEncoderReranker(BM25Retriever(docs), model_name=ce_path, depth=5)
    out = rr.search("zorvex bone density", 3)
    assert len(out) == 3 and [h.rank for h in out] == [1, 2, 3] and out[0].score >= out[1].score >= out[2].score
