import json

import pytest

from src.config import load_config
from src.data_io import load_corpus
from src.evidence import LexicalSentenceScorer
from src.ingest import paper_from_text
from src.pipeline import CiteCheckPipeline, MAX_CLAIM_CHARS, build_pipeline
from src.retrieval import BM25Retriever
from src.schema import CONTRADICT, NEI, Paper, Probs, Reference, SUPPORT, Verifier


class Scripted:
    """Verifier that returns pre-set probabilities keyed by a word in the premise."""
    name = "scripted"

    def __init__(self, table, default=Probs(0.05, 0.9, 0.05)):
        self.table, self.default = table, default

    def predict_pairs(self, pairs):
        return [next((p for w, p in self.table.items() if w in prem.lower()), self.default) for prem, _ in pairs]


@pytest.fixture()
def corpus(fixture_dir):
    return load_corpus(fixture_dir / "corpus.jsonl")


def make(corpus, table, **kw):
    return CiteCheckPipeline(Scripted(table), BM25Retriever(corpus), LexicalSentenceScorer.from_docs(corpus), **kw)


def test_verify_claim_over_corpus(corpus):
    pipe = make(corpus, {"zorvex": Probs(0.93, 0.05, 0.02)}, k=3, tau=0.5, meta={"verifier": "scripted"})
    v = pipe.verify_claim("Zorvex supplementation increases bone density in mice.")
    assert v.label == SUPPORT and v.display_label == "SUPPORTS" and v.confidence == pytest.approx(0.93)
    assert v.evidence[0].title.startswith("Zorvex")                       # the paper that drove the decision comes first
    assert v.evidence[0].sentences == [corpus[0].sentences[i] for i in v.evidence[0].sentence_idxs]
    assert len(v.evidence) == 3 and v.evidence[0].retrieval_rank == 1 and v.backend == {"verifier": "scripted"}
    assert v.latency_ms > 0 and not v.abstained
    json.dumps(v.to_dict(), default=str)                                   # serialisable for logs / --json


def test_abstains_below_threshold(corpus):
    weak = Scripted({}, default=Probs(0.4, 0.4, 0.2))
    pipe = CiteCheckPipeline(weak, BM25Retriever(corpus), LexicalSentenceScorer.from_docs(corpus), tau=0.6)
    v = pipe.verify_claim("Zorvex supplementation increases bone density in mice.")
    assert v.label == NEI and v.abstained and "below threshold" in v.note


def test_verify_against_specific_paper_ignores_corpus(corpus):
    pipe = CiteCheckPipeline(Scripted({"vantrol": Probs(0.02, 0.08, 0.90)}))       # note: NO retriever at all
    paper = Paper("p", "Vantrol trial", "We tested vantrol. Vantrol did not lower LDL.", source="pasted")
    v = pipe.verify_against_paper("Vantrol lowers LDL cholesterol.", paper)
    assert v.label == CONTRADICT and len(v.evidence) == 1 and v.evidence[0].retrieval_rank is None
    with pytest.raises(ValueError, match="no abstract"):
        pipe.verify_against_paper("x", Paper("q", "T", ""))


def test_input_validation(corpus):
    pipe = CiteCheckPipeline(Scripted({}))
    with pytest.raises(ValueError, match="Enter a claim"):
        pipe.verify_claim("   ")
    with pytest.raises(ValueError, match="No paper corpus"):
        pipe.verify_claim("a claim")
    long = make(corpus, {}).verify_claim("zorvex " * 1000)
    assert len(long.claim) == MAX_CLAIM_CHARS and "truncated" in long.note


def test_audit_skips_and_cleans(corpus):
    pipe = CiteCheckPipeline(Scripted({"zorvex": Probs(0.9, 0.05, 0.05)}))
    ok = Reference(Paper("a", "Zorvex paper", "Zorvex helps bones."), context="Zorvex helps bones [4].")
    no_ctx = Reference(Paper("b", "B", "Some abstract."), context="")
    no_abs = Reference(Paper("c", "C", ""), context="A claim.")
    seen = []
    rows = pipe.audit([ok, no_ctx, no_abs], progress=lambda i, n: seen.append((i, n)))
    assert rows[0].verdict.label == SUPPORT and rows[0].verdict.claim == "Zorvex helps bones."   # marker stripped
    assert "no citing sentence" in rows[1].skipped_reason and "no abstract" in rows[2].skipped_reason
    assert seen == [(1, 3), (2, 3), (3, 3)] and len(pipe.audit([ok] * 5, max_items=2)) == 2


def test_protocols_are_satisfied(corpus):
    assert isinstance(Scripted({}), Verifier)


# ---- build_pipeline / config -----------------------------------------------------------------
def test_build_pipeline_from_env(monkeypatch, fixture_dir):
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(fixture_dir))
    pipe = build_pipeline()
    assert pipe.has_corpus and pipe.meta["demo_only"] and not pipe.meta["validated"]
    assert pipe.meta["overrides"] == ["CITECHECK_VERIFIER"]
    assert pipe.verify_claim("Meditation reduces cortisol in adults.").evidence[0].title.startswith("Mindfulness")


def test_missing_corpus_is_a_warning_not_a_crash(monkeypatch, tmp_path):
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(tmp_path))
    pipe = build_pipeline()
    assert not pipe.has_corpus and any("fetch_scifact" in w for w in pipe.warnings)
    v = pipe.verify_against_paper("Zorvex helps bones.", paper_from_text("t", "Zorvex helps bones in mice."))
    assert v.label in (SUPPORT, NEI, CONTRADICT)


def test_unloadable_nli_falls_back_loudly(monkeypatch, tmp_path):
    monkeypatch.setenv("CITECHECK_VERIFIER", "nli:" + str(tmp_path / "does-not-exist"))
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(tmp_path))
    pipe = build_pipeline()
    assert pipe.meta["demo_only"] and not pipe.meta["validated"] and any("could not be loaded" in w for w in pipe.warnings)
    with pytest.raises(Exception):
        build_pipeline(allow_fallback=False)


def test_deployed_config_marks_pipeline_validated(monkeypatch, tmp_path, fixture_dir):
    dep = tmp_path / "deployed_config.json"
    dep.write_text(json.dumps({"run_name": "zero_shot_nli", "retriever": "bm25", "verifier": "lexical", "k": 2,
                               "sentences_per_paper": 2, "tau": 0.7, "margin": 0.0, "dev_macro_f1": 0.61,
                               "dev_macro_f1_ci95": [0.55, 0.67], "dev_false_support_rate": 0.08}))
    for var in ("CITECHECK_VERIFIER", "CITECHECK_TAU", "CITECHECK_K", "CITECHECK_RETRIEVER"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(fixture_dir))
    cfg = load_config(dep)
    assert cfg.validated and (cfg.k, cfg.tau, cfg.verifier) == (2, 0.7, "lexical") and cfg.overrides == []
    pipe = build_pipeline(cfg)
    assert pipe.meta["validated"] and pipe.meta["deployed_run"] == "zero_shot_nli" and pipe.meta["dev_macro_f1"] == 0.61
    monkeypatch.setenv("CITECHECK_TAU", "0.3")                              # any override breaks the "validated" claim
    cfg2 = load_config(dep)
    assert not cfg2.validated and cfg2.overrides == ["CITECHECK_TAU"] and cfg2.tau == 0.3
