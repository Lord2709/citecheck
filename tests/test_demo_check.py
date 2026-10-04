"""Pre-demo check.  Owner: Engineering (Sakshaat).  Uses the fixture + word-overlap backend, so 'validated' must FAIL."""
import json

from src.data_io import load_corpus
from src.evidence import LexicalSentenceScorer
from src.ingest import paper_from_text
from src.nli import LexicalVerifier
from src.pipeline import CiteCheckPipeline
from tools import demo_check as dc


def make_pipe(fixture_dir, meta=None):
    corpus = load_corpus(fixture_dir / "corpus.jsonl")
    return CiteCheckPipeline(LexicalVerifier(), None, LexicalSentenceScorer.from_docs(corpus), tau=0.5,
                             meta=meta or {"verifier": "lexical", "demo_only": True})


def example(pipe, fixture_dir, doc_idx, claim, role="main", slot="X-1", verdict=None):
    doc = load_corpus(fixture_dir / "corpus.jsonl")[doc_idx]
    got = pipe.verify_against_paper(claim, paper_from_text(doc.title, doc.abstract)).label
    return {"slot": slot, "role": role, "claim_id": doc_idx, "claim": claim, "title": doc.title, "abstract": doc.abstract,
            "gold": got, "verdict": verdict or got}


def test_overrides_fail():
    assert dc.check_overrides({"CITECHECK_TAU": "0.9"})[1] == dc.FAIL
    assert dc.check_overrides({})[1] == dc.PASS


def test_backend_status():
    good = {"validated": True, "deployed_run": "zero_shot_nli", "dev_macro_f1": 0.6027, "dev_macro_f1_ci95": [0.545, 0.66],
            "dev_false_support_rate": 0.108, "verifier": "nli", "tau": 0.6}
    row = dc.check_backend(type("P", (), {"meta": good})())
    assert row[1] == dc.PASS and "zero_shot_nli" in row[2] and "0.60" in row[2]
    assert dc.check_backend(type("P", (), {"meta": {"demo_only": True}})())[1] == dc.FAIL
    assert dc.check_backend(type("P", (), {"meta": {"validated": False}})())[1] == dc.FAIL


def test_examples_main_mismatch_fails_backup_mismatch_warns(fixture_dir, tmp_path):
    pipe = make_pipe(fixture_dir)
    ok = example(pipe, fixture_dir, 0, "Zorvex supplementation increases bone density in mice.")
    bad_main = dict(ok, slot="X-2", verdict="CONTRADICT" if ok["verdict"] != "CONTRADICT" else "SUPPORT")
    bad_backup = dict(bad_main, slot="X-3", role="backup")
    rows = dc.check_examples(pipe, [ok, bad_main, bad_backup])
    assert [r[1] for r in rows] == [dc.PASS, dc.FAIL, dc.WARN]
    assert "ms" in rows[0][2]


def test_run_and_render_with_a_given_pipeline(fixture_dir, tmp_path):
    pipe = make_pipe(fixture_dir)
    ex = example(pipe, fixture_dir, 0, "Zorvex supplementation increases bone density in mice.")
    path = tmp_path / "demo.json"
    path.write_text(json.dumps({"examples": [ex], "failure": None}), encoding="utf-8")
    rows = dc.run(path, pipe=pipe, environ={})
    names = {r[0]: r[1] for r in rows}
    assert names["validated backend"] == dc.FAIL                  # word overlap must never pass as the demo model
    assert any(n.startswith("example X-1") and s == dc.PASS for n, s in names.items())
    md = dc.render(rows, online=False)
    assert "overall: **FAIL**" in md and "OFFLINE" in md
    missing = dc.run(tmp_path / "nope.json", pipe=pipe, environ={})
    assert ("demo examples", dc.FAIL) in [(r[0], r[1]) for r in missing]
