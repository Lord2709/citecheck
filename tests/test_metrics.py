import random

import pytest

from eval import metrics as M


def test_macro_f1_matches_sklearn():
    sk = pytest.importorskip("sklearn.metrics")
    rng = random.Random(0)
    labels = list(M.LABELS)
    for _ in range(20):
        yt = [rng.choice(labels) for _ in range(60)]
        yp = [rng.choice(labels) for _ in range(60)]
        assert M.macro_f1(yt, yp) == pytest.approx(sk.f1_score(yt, yp, labels=labels, average="macro", zero_division=0))
        cm = sk.confusion_matrix(yt, yp, labels=labels).tolist()
        assert M.confusion_matrix(yt, yp) == cm


def test_false_support_and_precision():
    yt = ["SUPPORT", "CONTRADICT", "NEI", "NEI"]
    yp = ["SUPPORT", "SUPPORT", "SUPPORT", "NEI"]
    assert M.false_support_rate(yt, yp) == pytest.approx(2 / 3)   # 2 of the 3 non-support claims
    assert M.support_precision(yt, yp) == pytest.approx(1 / 3)    # 1 of the 3 SUPPORT calls
    assert M.coverage(yp) == pytest.approx(0.75)
    assert M.false_support_rate(["SUPPORT"], ["SUPPORT"]) == 0.0  # no negatives -> 0, not a crash


def test_all_nei_predictor_scores_low():
    yt = ["SUPPORT"] * 4 + ["CONTRADICT"] * 3 + ["NEI"] * 3
    yp = ["NEI"] * 10
    assert M.macro_f1(yt, yp) == pytest.approx((0 + 0 + 2 * 0.3 / 1.3) / 3)


def test_retrieval_metrics():
    ranked, gold = ["a", "b", "c", "d"], {"c", "z"}
    assert M.recall_at_k(ranked, gold, 3) == 0.5
    assert M.precision_at_k(ranked, gold, 3) == pytest.approx(1 / 3)
    assert M.hit_at_k(ranked, gold, 2) == 0.0 and M.hit_at_k(ranked, gold, 3) == 1.0
    assert M.reciprocal_rank(ranked, gold) == pytest.approx(1 / 3)
    assert M.ndcg_at_k(["c", "x"], {"c"}, 10) == pytest.approx(1.0)
    rep = M.retrieval_report({1: ranked, 2: ["q"]}, {1: gold, 2: set()}, ks=(3,))
    assert rep["n_claims"] == 1 and rep["recall@3"] == 0.5   # claims without gold are skipped


def test_abstract_level_matches_scifact_docs_example():
    """Worked example from allenai/scifact doc/evaluation.md: label+rationale P=R=F1=1/2."""
    gold = {52: {"11": {"label": "SUPPORT", "rationales": [[0, 1], [11]]}, "15": {"label": "SUPPORT", "rationales": [[4]]}}}
    pred = {52: {"11": {"label": "SUPPORT", "sentences": [1, 11, 13]}, "16": {"label": "CONTRADICT", "sentences": [18, 20]}}}
    r = M.abstract_level_prf(pred, gold, require_rationale=True)
    assert (r["precision"], r["recall"], r["f1"]) == (0.5, 0.5, 0.5)
    # label-only: doc 11 is right regardless of rationale
    assert M.abstract_level_prf(pred, gold, require_rationale=False)["n_correct"] == 1
    # rationale must be inside the first 3 predicted sentences
    late = {52: {"11": {"label": "SUPPORT", "sentences": [1, 2, 3, 11]}}}
    assert M.abstract_level_prf(late, gold, require_rationale=True)["n_correct"] == 0
    # evidence for a claim that has none costs precision
    gold2 = {1: {}, 2: {"9": {"label": "SUPPORT", "rationales": [[0]]}}}
    pred2 = {1: {"5": {"label": "SUPPORT", "sentences": [0]}}, 2: {"9": {"label": "SUPPORT", "sentences": [0]}}}
    r2 = M.abstract_level_prf(pred2, gold2)
    assert r2["precision"] == 0.5 and r2["recall"] == 1.0


def test_bootstrap_and_paired():
    yt = ["SUPPORT", "CONTRADICT", "NEI"] * 20
    assert M.bootstrap_ci(yt, yt, n_boot=50) == (1.0, 1.0)
    bad = ["NEI"] * len(yt)
    d = M.paired_bootstrap_diff(yt, yt, bad, n_boot=200)
    assert d["diff"] > 0.5 and d["p_a_better"] == 1.0 and d["ci95"][0] > 0
    same = M.paired_bootstrap_diff(yt, yt, yt, n_boot=50)
    assert same["diff"] == 0 and same["p_a_better"] == 0.0
