import pytest

from src.data_io import load_corpus
from src.evidence import LexicalSentenceScorer, build_premise, score_claim_docs, select_sentences
from src.nli import LexicalVerifier, MajorityVerifier
from src.schema import CONTRADICT, Hit, NEI, Probs, SUPPORT
from src.verdict import decide, doc_level_labels


def P(s, n, c):
    return Probs(s, n, c)


def test_decide_thresholding_and_direction():
    assert decide([P(0.9, 0.05, 0.05)], tau=0.5).label == SUPPORT
    assert decide([P(0.05, 0.05, 0.9)], tau=0.5).label == CONTRADICT
    weak = decide([P(0.4, 0.4, 0.2)], tau=0.5)
    assert weak.label == NEI and weak.abstained and "below threshold" in weak.note
    # best evidence may come from a later paper
    d = decide([P(0.1, 0.8, 0.1), P(0.8, 0.1, 0.1)], tau=0.5)
    assert d.label == SUPPORT and d.doc_index == 1
    # stronger of support/contradict wins
    assert decide([P(0.6, 0.0, 0.4), P(0.1, 0.0, 0.9)], tau=0.5).label == CONTRADICT
    assert decide([], tau=0.5).label == NEI


def test_decide_conflict_margin():
    both = [P(0.8, 0.1, 0.1), P(0.1, 0.1, 0.8)]
    assert decide(both, tau=0.5, margin=0.0).label == SUPPORT           # tie goes to support only w/o margin
    d = decide(both, tau=0.5, margin=0.1)
    assert d.label == NEI and "disagree" in d.note


def test_doc_level_labels():
    assert doc_level_labels([P(0.9, 0.05, 0.05), P(0.1, 0.8, 0.1), P(0.2, 0.1, 0.7)], 0.5) == [SUPPORT, None, CONTRADICT]


def test_sentence_selection_prefers_claim_words(fixture_dir):
    docs = load_corpus(fixture_dir / "corpus.jsonl")
    scorer = LexicalSentenceScorer.from_docs(docs)
    d1 = docs[0]
    idxs = select_sentences("Zorvex supplementation increases bone density in mice.", d1.sentences, m=1, scorer=scorer)
    assert idxs == [2]                                    # "Zorvex supplementation significantly increased femoral bone density..."
    idxs3 = select_sentences("zorvex bone density", d1.sentences, m=3, scorer=scorer)
    assert idxs3 == sorted(idxs3) and len(idxs3) == 3     # reading order preserved
    assert build_premise(d1.sentences, [0, 2]) == d1.sentences[0] + " " + d1.sentences[2]
    assert select_sentences("anything", [], m=3) == []


def test_score_claim_docs_batches_and_overrides(fixture_dir):
    docs = load_corpus(fixture_dir / "corpus.jsonl")
    scorer = LexicalSentenceScorer.from_docs(docs)
    items = [("Zorvex supplementation increases bone density in mice.", [Hit(docs[0], 1.0, 1), Hit(docs[1], 0.5, 2)]),
             ("Glimmerine raises systolic blood pressure.", [Hit(docs[1], 1.0, 1)])]
    out = score_claim_docs(items, LexicalVerifier(), scorer, m=2)
    assert [len(r) for r in out] == [2, 1]
    assert out[0][0].probs.label == SUPPORT               # claim words all in the top sentences, same polarity
    assert out[0][1].probs.label == NEI                   # unrelated paper
    assert out[1][0].probs.label == CONTRADICT            # "reduced" vs "raises": direction flip
    forced = score_claim_docs(items[:1], MajorityVerifier(), scorer, gold_sentences=[{docs[0].doc_id: [4]}])
    assert forced[0][0].sentence_idxs == [4]              # oracle override is honoured


def test_a_separate_contradict_threshold():
    weak_c = [P(0.2, 0.45, 0.35)]
    assert decide(weak_c, tau=0.5).label == NEI
    d = decide(weak_c, tau=0.5, tau_contradict=0.3)
    assert d.label == CONTRADICT and d.confidence == 0.35
    # never CONTRADICT when support is the stronger reading, and never more SUPPORT
    assert decide([P(0.45, 0.2, 0.35)], tau=0.5, tau_contradict=0.3).label == NEI
    assert decide([P(0.6, 0.0, 0.4)], tau=0.5, tau_contradict=0.3).label == SUPPORT
    # with tau_contradict == tau (or None) every decision is the same as before
    import itertools
    grid = [i / 10 for i in range(11)]
    for s, c in itertools.product(grid, grid):
        if s + c <= 1:
            p = [P(s, 1 - s - c, c)]
            assert decide(p, 0.5).label == decide(p, 0.5, tau_contradict=0.5).label
    assert "0.30 (contradiction)" in decide([P(0.1, 0.8, 0.1)], tau=0.5, tau_contradict=0.3).note


def test_the_contradict_threshold_comes_from_the_deployed_config(tmp_path, monkeypatch):
    import json

    from src.config import load_config

    monkeypatch.delenv("CITECHECK_TAU_CONTRADICT", raising=False)
    dep = tmp_path / "deployed_config.json"
    dep.write_text(json.dumps({"verifier": "lexical", "tau": 0.5, "tau_contradict": 0.3}))
    assert load_config(dep).tau_contradict == 0.3
    dep.write_text(json.dumps({"verifier": "lexical", "tau": 0.5}))
    assert load_config(dep).tau_contradict is None
    monkeypatch.setenv("CITECHECK_TAU_CONTRADICT", "0.35")
    cfg = load_config(dep)
    assert cfg.tau_contradict == 0.35 and "CITECHECK_TAU_CONTRADICT" in cfg.overrides
