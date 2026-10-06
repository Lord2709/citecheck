"""Demo-example picker: seeded, app-path, honest about what was tried.  Owner: Data & Evaluation (Sahil).
A scripted verifier stands in for the NLI model, so these tests check the selection logic, not model quality."""
import json

import pytest

from eval import pick_demo_examples as pde
from src.data_io import load_claims, load_corpus
from src.evidence import LexicalSentenceScorer
from src.pipeline import CiteCheckPipeline
from src.schema import CONTRADICT, NEI, SUPPORT, Probs


class Scripted:
    """SUPPORT for papers mentioning `sup`, CONTRADICT for `con`, neutral otherwise."""
    name = "scripted"

    def __init__(self, sup=("zorvex", "quillon", "meditation"), con=("glimmerine", "vantrol")):
        self.sup, self.con = sup, con

    def predict_pairs(self, pairs):
        out = []
        for prem, claim in pairs:
            p = prem.lower() + " " + claim.lower()
            if any(w in p for w in self.con):
                out.append(Probs(0.02, 0.08, 0.90))
            elif any(w in p for w in self.sup) and "memory" not in claim.lower() and "kidney" not in claim.lower():
                out.append(Probs(0.90, 0.08, 0.02))
            else:
                out.append(Probs(0.05, 0.90, 0.05))
        return out


@pytest.fixture()
def data(fixture_dir):
    corpus = load_corpus(fixture_dir / "corpus.jsonl")
    return load_claims(fixture_dir / "claims_dev.jsonl"), {d.doc_id: d for d in corpus}, corpus


def pipe(corpus, verifier=None):
    return CiteCheckPipeline(verifier or Scripted(), None, LexicalSentenceScorer.from_docs(corpus), k=3, tau=0.6,
                             meta={"verifier": "scripted"})


def test_candidates_respect_label_and_cited_paper(data):
    claims, by_id, _ = data
    sup = pde.candidates(claims, by_id, SUPPORT)
    assert sup and all(c.gold_label == SUPPORT and d.doc_id in c.gold_docs for c, d in sup)
    nei = pde.candidates(claims, by_id, NEI)
    assert {c.id for c, _ in nei} == {6, 7, 8}
    assert pde.candidates(claims, by_id, SUPPORT, max_claim_chars=10) == []        # screen-size filter applies


def test_select_keeps_only_correct_verdicts_and_counts_tries(data):
    claims, by_id, corpus = data
    sel = pde.select(pipe(corpus), claims, by_id, seed=0, per_label=2, include_failure=True)
    for e in sel["examples"]:
        assert e["verdict"] == e["gold"] and e["slot"].startswith(e["gold"])
        assert e["evidence_sentences"] and e["abstract"] and e["tried_before"] >= 1
    labels = [e["gold"] for e in sel["examples"]]
    assert labels.count(SUPPORT) == 2 and labels.count(CONTRADICT) == 2 and labels.count(NEI) == 2
    assert [e["role"] for e in sel["examples"] if e["gold"] == SUPPORT] == ["main", "backup"]
    # nalbrix (claims 9, 10) is neutral for the scripted model: it is tried, fails, and becomes the honest failure
    assert sel["failure"] is not None and sel["failure"]["verdict"] != sel["failure"]["gold"]
    assert all(t["tried"] >= t["kept"] for t in sel["tried"].values())


def test_select_is_seeded(data):
    claims, by_id, corpus = data
    a = pde.select(pipe(corpus), claims, by_id, seed=3, per_label=1)
    b = pde.select(pipe(corpus), claims, by_id, seed=3, per_label=1)
    assert [e["claim_id"] for e in a["examples"]] == [e["claim_id"] for e in b["examples"]]
    seen = {tuple(e["claim_id"] for e in pde.select(pipe(corpus), claims, by_id, seed=s, per_label=1)["examples"])
            for s in range(10)}
    assert len(seen) > 1


def test_nothing_behaves_is_reported_not_hidden(data):
    claims, by_id, corpus = data
    never = Scripted(sup=(), con=())
    sel = pde.select(pipe(corpus, never), claims, by_id, seed=0, per_label=1)
    assert sel["tried"][SUPPORT]["kept"] == 0 and sel["tried"][SUPPORT]["tried"] > 0
    assert all(e["gold"] == NEI for e in sel["examples"])


def test_cli_writes_json_and_script(fixture_dir, tmp_path, monkeypatch):
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.chdir(tmp_path)                                   # no deployed_config.json here -> unvalidated
    with pytest.raises(SystemExit):
        pde.main(["--data-dir", str(fixture_dir), "--out", "x.json", "--script-out", "x.md"])
    out = pde.main(["--data-dir", str(fixture_dir), "--allow-unvalidated", "--include-failure",
                    "--out", "demo/demo_examples.json", "--script-out", "demo/DEMO_SCRIPT.md"])
    j = json.loads((tmp_path / "demo" / "demo_examples.json").read_text(encoding="utf-8"))
    assert j["split"] == "dev" and j["synthetic_fixture"] is True and j["validated"] is False
    assert j["examples"] == out["examples"] and "tried" in j
    md = (tmp_path / "demo" / "DEMO_SCRIPT.md").read_text(encoding="utf-8")
    assert "seed 0" in md and "not a metric" in md and "NOT FOR THE DEMO" in md
