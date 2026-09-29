import json

from src.data_io import (ClaimRecord, MIXED, find_scifact_dir, is_synthetic_fixture, label_distribution, load_claims,
                         load_corpus, sha256_file, split_has_labels)


def test_fixture_loads(fixture_dir):
    docs = load_corpus(fixture_dir / "corpus.jsonl")
    assert len(docs) == 10 and docs[0].doc_id == "1" and isinstance(docs[0].sentences, tuple)
    assert docs[0].text.startswith(docs[0].title)
    dev = load_claims(fixture_dir / "claims_dev.jsonl")
    assert label_distribution(dev) == {"SUPPORT": 4, "CONTRADICT": 3, "NEI": 3}
    c1 = dev[0]
    assert c1.gold_docs == ["1"] and c1.rationale_sets("1") == [[2]] and c1.cited_doc_ids == ["1"]


def test_test_split_has_no_labels(fixture_dir):
    assert split_has_labels(fixture_dir / "claims_dev.jsonl")
    assert not split_has_labels(fixture_dir / "claims_test.jsonl")
    (c,) = load_claims(fixture_dir / "claims_test.jsonl")
    assert c.evidence == {} and c.gold_label == "NEI"   # unlabeled != evaluable: run_eval refuses this split


def test_mixed_label_detected():
    c = ClaimRecord(1, "x", {"5": [{"label": "SUPPORT", "sentences": [0]}], "6": [{"label": "CONTRADICT", "sentences": [1]}]}, ["5", "6"])
    assert c.gold_label == MIXED
    assert c.gold_doc_labels == {"5": "SUPPORT", "6": "CONTRADICT"}


def test_find_dir_and_helpers(tmp_path, fixture_dir):
    assert find_scifact_dir(fixture_dir) == fixture_dir
    assert find_scifact_dir(tmp_path) is None
    nested = tmp_path / "data"
    nested.mkdir()
    (nested / "corpus.jsonl").write_text("")
    assert find_scifact_dir(tmp_path) == nested
    assert is_synthetic_fixture(fixture_dir) and not is_synthetic_fixture(tmp_path)
    assert len(sha256_file(fixture_dir / "corpus.jsonl")) == 64


def test_bad_json_names_the_line(tmp_path):
    p = tmp_path / "c.jsonl"
    p.write_text('{"id": 1, "claim": "a"}\nnot json\n')
    try:
        load_claims(p)
    except ValueError as e:
        assert "c.jsonl:2" in str(e)
    else:
        raise AssertionError("expected ValueError")
