"""tools/live_sources_check.py against FAKE responses: proves the bookkeeping (no crash on failures, no secrets in the
output), NOT that the live services answer.  The live run is the tool's whole point and must be done by a person."""
import json
from datetime import datetime, timezone

from src.ingest import Fetcher
from tools import live_sources_check as lsc

from test_ingest import OPENALEX, Resp, Session

ATOM = """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>A preprint</title>
<summary>We study claims. Results hold.</summary><published>2020-04-30T00:00:00Z</published></entry></feed>"""


def ticking():
    t = [0.0]

    def clock():
        t[0] += 0.5
        return t[0]
    return clock


def fake_session():
    return Session([
        ("api.openalex.org/works/https://doi.org/10.1056", Resp(500)),          # NEJM: server error every time
        ("api.openalex.org/works/https://doi.org", Resp(200, OPENALEX)),
        ("export.arxiv.org", Resp(200, text=ATOM)),
        ("/references", Resp(200, {"data": [{"citedPaper": {"paperId": "x", "title": "T"}, "contexts": ["ctx [1]"]},
                                             {"citedPaper": {"paperId": "y", "title": "U"}, "contexts": []}]})),
        ("semanticscholar.org/graph/v1/paper/search", Resp(200, {"data": [{"title": "a"}]})),
        ("api.semanticscholar.org", Resp(404)),
        ("api.crossref.org", Resp(200, {"message": {"items": [{"DOI": "10.18653/V1/2020.EMNLP-MAIN.609"}]}})),
        ("europepmc", Resp(200, {"hitCount": 1, "resultList": {"result": [{"isOpenAccess": "Y"}]}})),
        ("api.openalex.org/works", Resp(429)),
        ("unpaywall", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": "https://x/y.pdf"}})),
    ])


def make(monkeypatch, mailto=None, key=None):
    for k, v in (("CITECHECK_MAILTO", mailto), ("OPENALEX_API_KEY", key)):
        if v:
            monkeypatch.setenv(k, v)
    s = fake_session()
    f = Fetcher(session=s, cache_dir=None, retries=1, sleep=lambda x: None)
    return lsc.run(fetcher=f, session=s, clock=ticking(), now=datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)), s


def test_records_successes_and_failures_without_crashing(monkeypatch):
    rep, _ = make(monkeypatch)
    by = {r["probe"]: r for r in rep["papers"]}
    assert len(rep["papers"]) == len(lsc.PAPER_PROBES)
    assert by["doi-cs-nature"]["ok"] and by["doi-cs-nature"]["source"] == "openalex"
    assert by["doi-biomed-nejm"]["ok"] is False and by["doi-biomed-nejm"]["error"]
    assert by["arxiv-new"]["ok"] and by["arxiv-new"]["source"] == "arxiv"
    assert all(r["seconds"] > 0 for r in rep["papers"])
    assert rep["references"]["n_references"] == 2 and rep["references"]["n_with_citing_sentence"] == 1
    planned = {r["probe"]: r for r in rep["planned"]}
    assert planned["crossref-resolve"]["ok"]                                  # DOI compared case-insensitively
    assert planned["openalex-search"]["ok"] is False and planned["openalex-search"]["http"] == 429
    assert "unpaywall-oa" not in planned                                     # needs an e-mail address
    md = lsc.to_markdown(rep)
    assert "Unpaywall was not checked" in md and "not a reliability measurement" in md


def test_unpaywall_runs_with_mailto_and_secrets_never_reach_output(monkeypatch, tmp_path):
    rep, s = make(monkeypatch, mailto="tester@umd.edu", key="SECRETKEY123")
    planned = {r["probe"]: r for r in rep["planned"]}
    assert planned["unpaywall-oa"]["ok"] and "pdf=yes" in planned["unpaywall-oa"]["detail"]
    assert any(p and p.get("api_key") == "SECRETKEY123" for _, p, _ in s.calls)   # the key IS sent...
    text = json.dumps(rep) + lsc.to_markdown(rep)
    assert "SECRETKEY123" not in text and "tester@umd.edu" not in text           # ...but never written down
    assert rep["keys"] == {"openalex": True, "s2": False, "mailto": True}


def test_redact():
    assert lsc.redact("a KEY b", ["KEY", None, ""]) == "a <redacted> b"
