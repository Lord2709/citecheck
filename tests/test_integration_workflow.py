"""The whole team workflow on synthetic data, end to end:
   fetch tarball -> run eval (tiny random NLI model) -> promote -> the app loads exactly that run and says so.
Numbers are meaningless (random weights, synthetic data); this proves the wiring, not the science."""
import io
import json
import shutil
import tarfile
from pathlib import Path

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
st = pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from data import fetch_scifact  # noqa: E402
from eval import run_eval  # noqa: E402
from src.config import load_config  # noqa: E402
from src.pipeline import build_pipeline  # noqa: E402
from tests.tiny_model import FIXTURE, make_tiny_nli  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")


def make_tarball(path):
    with tarfile.open(path, "w:gz") as tf:
        for name in ("corpus.jsonl", "claims_train.jsonl", "claims_dev.jsonl", "claims_test.jsonl"):
            tf.add(FIXTURE / name, arcname=f"data/{name}")
        evil = tarfile.TarInfo("../evil.txt")
        evil.size = 4
        tf.addfile(evil, io.BytesIO(b"evil"))


def test_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for var in ("CITECHECK_VERIFIER", "CITECHECK_TAU", "CITECHECK_K", "CITECHECK_RETRIEVER", "CITECHECK_DATA_DIR"):
        monkeypatch.delenv(var, raising=False)

    # 1. fetch: extracts only the four whitelisted files, writes a manifest, ignores the traversal member
    make_tarball(tmp_path / "data.tar.gz")
    fetch_scifact.main(["--tar", str(tmp_path / "data.tar.gz"), "--out", "data/scifact"])
    assert sorted(p.name for p in (tmp_path / "data" / "scifact").iterdir()) == [
        "MANIFEST.json", "claims_dev.jsonl", "claims_test.jsonl", "claims_train.jsonl", "corpus.jsonl"]
    assert not (tmp_path / "evil.txt").exists() and not (tmp_path.parent / "evil.txt").exists()
    manifest = json.loads((tmp_path / "data" / "scifact" / "MANIFEST.json").read_text())
    assert manifest["files"]["claims_dev.jsonl"]["n_rows"] == 10 and manifest["license"]["claims_and_evidence_annotations"] == "CC BY 4.0"

    # 2. evaluate with a (random, tiny) NLI checkpoint; path has no 'fixtures' so it counts as real data for the plumbing
    tiny = make_tiny_nli(tmp_path / "tiny")
    res = run_eval.main(["--name", "zero_shot_nli", "--data-dir", "data/scifact", "--verifier", "nli", "--model", tiny,
                         "--device", "cpu", "--n-boot", "30", "--oracle", "--promote"])
    assert res["synthetic_fixture"] is False and res["config"]["verifier"].startswith("nli:")
    dep = json.loads((tmp_path / "eval" / "results" / "deployed_config.json").read_text())
    assert dep["run_name"] == "zero_shot_nli" and dep["dev_macro_f1"] == res["claim_level"]["macro_f1"]

    # 3. the pipeline loads exactly that configuration and knows it is validated
    cfg = load_config()
    assert cfg.validated and cfg.verifier == f"nli:{tiny}" and cfg.tau == dep["tau"]
    pipe = build_pipeline(cfg)
    assert pipe.meta["validated"] and not pipe.meta["demo_only"] and pipe.meta["dev_macro_f1"] == dep["dev_macro_f1"]
    v = pipe.verify_claim("Zorvex supplementation increases bone density in mice.")
    assert v.label in ("SUPPORT", "CONTRADICT", "NEI") and v.evidence and v.backend["validated"] is True

    # 4. the app tells the user which run it is and what that run scored (and does not say DEMO)
    st.cache_resource.clear()
    monkeypatch.setenv("CITECHECK_LOG", str(tmp_path / "usage.jsonl"))
    at = AppTest.from_file(APP, default_timeout=120)
    at.run()
    assert not at.exception, at.exception
    ok = " ".join(e.value for e in at.sidebar.success)
    assert "Validated configuration `zero_shot_nli`" in ok and f"{dep['dev_macro_f1']:.2f}" in ok
    assert not at.sidebar.error
    at.text_area(key="claim").set_value("Meditation reduces cortisol in adults.").run()
    at.radio(key="chk_src").set_value("Search the SciFact corpus").run()
    at.button(key="btn_check").click().run()
    assert not at.exception and not at.error
    verify = [json.loads(l) for l in (tmp_path / "usage.jsonl").read_text().splitlines() if '"verify"' in l][0]
    assert verify["validated"] is True and verify["mode"] == "corpus"
    st.cache_resource.clear()

    # 5. any override drops the validated claim (the banner must not keep boasting about a different setup)
    monkeypatch.setenv("CITECHECK_TAU", "0.9")
    assert not load_config().validated
