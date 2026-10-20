"""Fit / calibration split of SciFact train (SYNTHETIC fixture: plumbing only)."""
import json

import pytest

from eval import finetune_nli, run_eval, train_split
from src.data_io import load_claims


def test_split_is_stratified_disjoint_complete_and_deterministic(fixture_dir):
    claims = load_claims(fixture_dir / "claims_train.jsonl")
    a = train_split.make_split(claims, calib_frac=0.25, seed=13)
    b = train_split.make_split(claims, calib_frac=0.25, seed=13)
    assert a == b
    assert not set(a["fit"]) & set(a["calib"])
    assert sorted(a["fit"] + a["calib"]) == sorted(c.id for c in claims)
    for label, c in a["by_label"].items():
        n = sum(1 for x in claims if x.gold_label == label)
        assert c["fit"] + c["calib"] == n
        if n >= 2:
            assert c["fit"] >= 1 and c["calib"] >= 1
    other = train_split.make_split(claims, calib_frac=0.25, seed=99)
    assert sorted(other["fit"] + other["calib"]) == sorted(a["fit"] + a["calib"])


def test_bad_fraction_and_refuses_dev(fixture_dir):
    claims = load_claims(fixture_dir / "claims_train.jsonl")
    for bad in (0, 1, 1.5):
        with pytest.raises(ValueError):
            train_split.make_split(claims, calib_frac=bad)
    with pytest.raises(SystemExit, match="only claims_train"):
        train_split.build_split_file(fixture_dir / "claims_dev.jsonl")


def test_cli_writes_ids_only_and_marks_fixture(fixture_dir, tmp_path):
    out = tmp_path / "split.json"
    d = train_split.main(["--data-dir", str(fixture_dir), "--out", str(out), "--calib-frac", "0.25"])
    saved = json.loads(out.read_text())
    assert saved["fit"] == d["fit"] and saved["synthetic_fixture"] is True
    assert all(isinstance(i, int) for i in saved["fit"] + saved["calib"])          # ids only, no SciFact text
    loaded = train_split.load_split(out)
    claims = load_claims(fixture_dir / "claims_train.jsonl")
    part = train_split.select_part(claims, loaded, "calib", train_path=fixture_dir / "claims_train.jsonl")
    assert {c.id for c in part} == set(loaded["calib"])
    with pytest.raises(ValueError, match="different claims_train"):
        train_split.select_part(claims, loaded, "fit", train_path=fixture_dir / "claims_dev.jsonl")
    with pytest.raises(ValueError):
        train_split.select_part(claims, loaded, "dev")


def test_load_split_rejects_overlap(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"fit": [1, 2], "calib": [2], "source_sha256": "x"}))
    with pytest.raises(ValueError, match="overlap"):
        train_split.load_split(p)


def test_finetune_pairs_only_uses_fit_part(fixture_dir, tmp_path):
    split = tmp_path / "split.json"
    train_split.main(["--data-dir", str(fixture_dir), "--out", str(split), "--calib-frac", "0.25"])
    full = finetune_nli.main(["--data-dir", str(fixture_dir), "--pairs-only"])
    fit = finetune_nli.main(["--data-dir", str(fixture_dir), "--pairs-only", "--split-file", str(split),
                             "--export-pairs", str(tmp_path / "pairs.jsonl")])
    n_fit = len(json.loads(split.read_text())["fit"])
    assert fit["n_claims"] == n_fit and full["n_claims"] == 8 and fit["n_claims"] < full["n_claims"]
    assert 0 < fit["n_pairs"] <= full["n_pairs"]
    rows = [json.loads(l) for l in (tmp_path / "pairs.jsonl").read_text().splitlines()]
    assert len(rows) == fit["n_pairs"] and {r["label"] for r in rows} <= {"support", "neutral", "contradict"}


def test_run_eval_tunes_tau_on_calib_part_only(fixture_dir, tmp_path):
    split = tmp_path / "split.json"
    train_split.main(["--data-dir", str(fixture_dir), "--out", str(split), "--calib-frac", "0.25"])
    res = run_eval.main(["--name", "calib", "--data-dir", str(fixture_dir), "--out", str(tmp_path / "r"),
                         "--retriever", "bm25", "--verifier", "lexical", "--no-cache", "--n-boot", "20",
                         "--tune-split-file", str(split)])
    t = res["tau_tuning"]
    assert t["split"] == "train" and t["part"] == "calib" and t["leak"] is False
    assert t["n_claims"] == len(json.loads(split.read_text())["calib"])
