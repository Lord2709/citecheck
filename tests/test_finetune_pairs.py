"""Training-pair builder for the NLI fine-tune (SYNTHETIC fixture: plumbing only, no torch)."""
from eval import finetune_nli
from src.data_io import MIXED, load_claims, load_corpus
from src.evidence import LexicalSentenceScorer, build_premise, select_sentences
from src.retrieval import BM25Retriever
from src.schema import NEI, SUPPORT


def _load(fixture_dir):
    corpus = load_corpus(fixture_dir / "corpus.jsonl")
    claims = load_claims(fixture_dir / "claims_train.jsonl")
    return claims, corpus, {d.doc_id: d for d in corpus}, LexicalSentenceScorer.from_docs(corpus)


def _source_docs(premise, claim, corpus, scorer, m=3):
    """Ids of the papers whose selected-sentence premise for this claim is exactly `premise`."""
    return {d.doc_id for d in corpus
            if d.sentences and build_premise(d.sentences, select_sentences(claim, d.sentences, m, scorer)) == premise}


def test_positive_pairs_are_gold_rationales_with_the_paper_label(fixture_dir):
    claims, _, by_id, scorer = _load(fixture_dir)
    pairs = finetune_nli.build_training_pairs(claims, by_id, None, scorer, neg_per_claim=0)
    got = set(pairs)
    for c in claims:
        for doc_id, lab in c.gold_doc_labels.items():
            if lab == MIXED:
                continue
            cls = "support" if lab == SUPPORT else "contradict"
            for rset in c.rationale_sets(doc_id):
                premise = " ".join(by_id[doc_id].sentences[i] for i in rset)
                assert (premise, c.claim, cls) in got
    # with no retriever, every neutral pair comes from an NEI claim's cited paper
    nei_claims = {c.claim for c in claims if c.gold_label == NEI}
    assert all(claim in nei_claims for _, claim, lab in pairs if lab == "neutral")
    assert {lab for _, _, lab in pairs} <= {"support", "neutral", "contradict"}


def test_hard_negatives_never_use_a_gold_paper(fixture_dir):
    claims, corpus, by_id, scorer = _load(fixture_dir)
    pairs = finetune_nli.build_training_pairs(claims, by_id, BM25Retriever(corpus), scorer, neg_per_claim=1)
    base = finetune_nli.build_training_pairs(claims, by_id, None, scorer, neg_per_claim=0)
    extra = [p for p in pairs if p not in base]
    assert extra and all(lab == "neutral" for _, _, lab in extra)
    by_claim = {c.claim: c for c in claims}
    for premise, claim, _ in extra:
        src = _source_docs(premise, claim, corpus, scorer)
        assert src, "a hard negative must be the selector's premise for some paper"
        assert not src <= set(by_claim[claim].gold_docs)


def test_selected_positives_are_opt_in_and_hold_real_evidence(fixture_dir):
    claims, corpus, by_id, scorer = _load(fixture_dir)
    off = finetune_nli.build_training_pairs(claims, by_id, None, scorer, neg_per_claim=0)
    on = finetune_nli.build_training_pairs(claims, by_id, None, scorer, neg_per_claim=0, selected_positives=True)
    assert set(off) <= set(on)
    added = [p for p in on if p not in off]
    assert len(added) == len(set(added))                       # the flag adds no duplicates
    by_claim = {c.claim: c for c in claims}
    for premise, claim, lab in added:
        c = by_claim[claim]
        gold_src = [d for d in _source_docs(premise, claim, corpus, scorer) if d in c.gold_doc_labels]
        assert gold_src, "an added pair must be the selector's premise for a gold paper"
        doc_id = gold_src[0]
        sel = select_sentences(claim, by_id[doc_id].sentences, 3, scorer)
        assert set(sel) & set(c.rationale_sentence_idxs(doc_id))
        assert lab == ("support" if c.gold_doc_labels[doc_id] == SUPPORT else "contradict")


def test_pairs_hash_is_stable_and_order_sensitive():
    a = [("p1", "c1", "support"), ("p2", "c2", "neutral")]
    assert finetune_nli.pairs_sha256(a) == finetune_nli.pairs_sha256(list(a))
    assert finetune_nli.pairs_sha256(a) != finetune_nli.pairs_sha256(a[::-1])
    assert len(finetune_nli.pairs_sha256(a)) == 64


def test_pairs_only_cli_reports_hash_and_flag(fixture_dir):
    off = finetune_nli.main(["--data-dir", str(fixture_dir), "--pairs-only"])
    on = finetune_nli.main(["--data-dir", str(fixture_dir), "--pairs-only", "--selected-positives"])
    assert off["selected_positives"] is False and on["selected_positives"] is True
    assert len(off["pairs_sha256"]) == 64 and on["n_pairs"] >= off["n_pairs"]


def test_provenance_never_raises():
    prov = finetune_nli.run_provenance()
    assert {"git_commit", "git_dirty", "torch", "transformers", "numpy"} <= set(prov)
