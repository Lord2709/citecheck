import pytest

from src.nli import LexicalVerifier, MajorityVerifier, build_verifier, resolve_label_indices
from src.schema import Probs

ORDERS = [
    {0: "entailment", 1: "neutral", 2: "contradiction"},          # MoritzLaurer DeBERTa-v3 style
    {0: "contradiction", 1: "entailment", 2: "neutral"},          # cross-encoder/nli-* style
    {0: "CONTRADICTION", 1: "NEUTRAL", 2: "ENTAILMENT"},          # facebook/bart-large-mnli style
]


@pytest.mark.parametrize("id2label", ORDERS)
def test_label_mapping_is_by_name_not_position(id2label):
    idx = resolve_label_indices(id2label)
    assert id2label[idx["support"]].lower().startswith("entail")
    assert id2label[idx["contradict"]].lower().startswith("contra")
    assert id2label[idx["neutral"]].lower().startswith("neutral")


def test_label_mapping_rejects_unknown_scheme():
    with pytest.raises(ValueError):
        resolve_label_indices({0: "LABEL_0", 1: "LABEL_1", 2: "LABEL_2"})


def test_majority_and_lexical():
    assert MajorityVerifier().predict_pairs([("a", "b")])[0].label == "NEI"
    lex = LexicalVerifier()
    sup, con, neu = lex.predict_pairs([
        ("Zorvex significantly increased bone density in mice.", "Zorvex increases bone density in mice."),
        ("Vantrol did not lower LDL cholesterol compared with placebo.", "Vantrol lowers LDL cholesterol."),
        ("Coral bleaching intensity rose in warm seas.", "Zorvex increases bone density in mice."),
    ])
    assert (sup.label, con.label, neu.label) == ("SUPPORT", "CONTRADICT", "NEI")
    for p in (sup, con, neu):
        assert abs(p.support + p.neutral + p.contradict - 1.0) < 1e-9


def test_build_verifier():
    assert build_verifier("majority").name == "majority" and build_verifier("lexical").name == "lexical"
    assert build_verifier("nli:some/model").model_name == "some/model"     # lazy: nothing is loaded yet
    with pytest.raises(ValueError):
        build_verifier("gpt")


@pytest.mark.parametrize("id2label", ORDERS[:2])
def test_real_transformer_plumbing_with_tiny_model(tmp_path, id2label):
    pytest.importorskip("torch")
    pytest.importorskip("transformers")
    import torch

    from src.nli import NLIVerifier
    from tests.tiny_model import make_tiny_nli

    path = make_tiny_nli(tmp_path / "m", id2label)
    pairs = [("zorvex increased bone density in mice", "zorvex increases bone density"),
             ("vantrol did not lower ldl cholesterol", "vantrol lowers cholesterol"),
             ("coral bleaching rose", "glimmerine reduced pressure")] * 3
    v = NLIVerifier(path, device="cpu", batch_size=4)
    out = v.predict_pairs(pairs)
    assert len(out) == len(pairs) and all(isinstance(p, Probs) for p in out)
    assert all(abs(p.support + p.neutral + p.contradict - 1) < 1e-5 for p in out)
    # order must be preserved when the verifier sorts by length internally: different batch size -> same answers
    out2 = NLIVerifier(path, device="cpu", batch_size=1).predict_pairs(pairs)
    assert [round(p.support, 5) for p in out] == [round(p.support, 5) for p in out2]
    # and the probability we call `support` must be the model's 'entailment' logit, whatever its position
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok, model = AutoTokenizer.from_pretrained(path), AutoModelForSequenceClassification.from_pretrained(path).eval()
    enc = tok(pairs[0][0], pairs[0][1], return_tensors="pt", truncation="only_first")
    with torch.no_grad():
        probs = torch.softmax(model(**enc).logits, -1)[0]
    ent = [i for i, n in id2label.items() if n.startswith("entail")][0]
    assert out[0].support == pytest.approx(float(probs[ent]), abs=1e-5)
    assert v.n_params > 0 and v.predict_pairs([]) == []


def test_lexical_polarity_read_from_best_sentence_not_whole_premise():
    """Regression: 'loss'/'unchanged' in OTHER sentences used to flip the polarity of the whole premise."""
    lex = LexicalVerifier()
    premise = ("Bone loss is a major concern. Zorvex significantly increased femoral bone density. "
               "Body weight was unchanged.")
    assert lex.predict_pairs([(premise, "Zorvex increases bone density.")])[0].label == "SUPPORT"
    premise2 = "We tested vantrol in 180 adults. After twelve weeks vantrol did not lower LDL cholesterol. HDL was unchanged."
    assert lex.predict_pairs([(premise2, "Vantrol lowers LDL cholesterol.")])[0].label == "CONTRADICT"
