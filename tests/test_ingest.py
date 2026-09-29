"""Ingest tests use hand-written responses shaped like the OpenAlex / arXiv / Semantic Scholar docs.
They prove OUR parsing and retry logic; they do NOT prove the live APIs still answer this way."""
import json

import pytest

from src.ingest import (Fetcher, IngestError, ParsedId, abstract_from_inverted_index, clean_context, paper_from_text,
                        parse_identifier)


@pytest.mark.parametrize("text,expected", [
    ("10.1038/nature14539", ParsedId("doi", "10.1038/nature14539")),
    ("https://doi.org/10.1038/NATURE14539.", ParsedId("doi", "10.1038/nature14539")),
    ("see (doi: 10.1145/3292500.3330701).", ParsedId("doi", "10.1145/3292500.3330701")),
    ("arXiv:2004.14974v2", ParsedId("arxiv", "2004.14974")),
    ("https://arxiv.org/abs/2004.14974", ParsedId("arxiv", "2004.14974")),
    ("2004.14974", ParsedId("arxiv", "2004.14974")),
    ("arXiv:cs/0112017", ParsedId("arxiv", "cs/0112017")),
    ("https://www.semanticscholar.org/paper/Some-Title/" + "a" * 40, ParsedId("s2", "a" * 40)),
])
def test_parse_identifier(text, expected):
    assert parse_identifier(text) == expected


@pytest.mark.parametrize("bad", ["", "   ", "hello world", "12345", "10.12/short"])
def test_parse_identifier_rejects(bad):
    assert parse_identifier(bad) is None


def test_inverted_index_and_context_cleaning():
    inv = {"Zorvex": [0], "increases": [1], "bone": [2, 5], "density.": [3], "Mice": [4]}
    assert abstract_from_inverted_index(inv) == "Zorvex increases bone density. Mice bone"
    assert abstract_from_inverted_index(None) == ""
    assert clean_context("Vaccines reduce infection [12, 13] as shown before (Smith et al., 2019; Lee, 2020) in trials .") \
        == "Vaccines reduce infection as shown before in trials."
    assert clean_context("Range cite [5-7] here") == "Range cite here"


class Resp:
    def __init__(self, status=200, data=None, text=""):
        self.status_code, self._data, self.text = status, data, text

    def json(self):
        return self._data


class Session:
    """routes: list of (url-fragment, Resp | [Resp,...]); a list is consumed one response per call."""
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params, headers))
        for frag, resp in self.routes:
            if frag in url:
                return resp.pop(0) if isinstance(resp, list) else resp
        return Resp(404)


OPENALEX = {"display_name": "Zorvex and bone", "publication_year": 2021,
            "abstract_inverted_index": {"Zorvex": [0], "helps": [1], "bones.": [2]},
            "primary_location": {"source": {"display_name": "Journal of Invented Results"}}}


def fetcher(routes, tmp_path, **kw):
    return Fetcher(session=Session(routes), cache_dir=str(tmp_path / "cache"), sleep=lambda s: None, **kw)


def test_fetch_by_doi_openalex_and_cache(tmp_path):
    f = fetcher([("openalex.org", Resp(200, OPENALEX))], tmp_path, mailto="me@umd.edu")
    p = f.fetch_paper("https://doi.org/10.1000/xyz")
    assert (p.title, p.year, p.venue, p.doi, p.source) == ("Zorvex and bone", 2021, "Journal of Invented Results", "10.1000/xyz", "openalex")
    assert p.abstract == "Zorvex helps bones." and p.to_doc().sentences == ("Zorvex helps bones.",)
    url, params, headers = f.session.calls[0]
    assert url.endswith("/works/https://doi.org/10.1000/xyz") and params == {"mailto": "me@umd.edu"} and "mailto:me@umd.edu" in headers["User-Agent"]
    n = len(f.session.calls)
    assert f.fetch_paper("10.1000/xyz").title == "Zorvex and bone" and len(f.session.calls) == n   # served from cache


def test_openalex_without_abstract_falls_back_to_s2(tmp_path):
    no_abs = dict(OPENALEX, abstract_inverted_index=None)
    s2 = {"paperId": "abc", "title": "Zorvex and bone", "abstract": "Zorvex helps bones a lot.", "year": 2021,
          "venue": "J", "externalIds": {"DOI": "10.1000/XYZ"}, "url": "https://www.semanticscholar.org/paper/abc"}
    f = fetcher([("openalex.org", Resp(200, no_abs)), ("semanticscholar.org", Resp(200, s2))], tmp_path)
    p = f.fetch_paper("10.1000/xyz")
    assert p.source == "s2" and p.abstract == "Zorvex helps bones a lot." and p.doi == "10.1000/xyz"


def test_no_abstract_anywhere_tells_user_to_paste(tmp_path):
    no_abs = dict(OPENALEX, abstract_inverted_index=None)
    f = fetcher([("openalex.org", Resp(200, no_abs)), ("semanticscholar.org", Resp(404))], tmp_path)
    with pytest.raises(IngestError, match="Paste the abstract"):
        f.fetch_paper("10.1000/xyz")


def test_not_found_and_bad_input(tmp_path):
    f = fetcher([], tmp_path)
    with pytest.raises(IngestError, match="No paper found"):
        f.fetch_paper("10.1000/missing")
    with pytest.raises(IngestError, match="could not find a DOI"):
        f.fetch_paper("please check my paper")


def test_retries_then_succeeds_and_rate_limit_message(tmp_path):
    f = fetcher([("openalex.org", [Resp(429), Resp(503), Resp(200, OPENALEX)])], tmp_path)
    assert f.fetch_paper("10.1000/a").title == "Zorvex and bone" and len(f.session.calls) == 3
    g = fetcher([("openalex.org", Resp(429)), ("semanticscholar.org", Resp(429))], tmp_path)
    with pytest.raises(IngestError, match="paste the abstract"):
        g.fetch_paper("10.1000/b")


def test_network_error_is_wrapped(tmp_path):
    class Boom:
        def get(self, *a, **k):
            raise ConnectionError("dns")

    f = Fetcher(session=Boom(), cache_dir=None, sleep=lambda s: None)
    with pytest.raises(IngestError, match="not responding"):
        f.fetch_paper("10.1000/c")


ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>Fact or Fiction:
  Verifying Scientific Claims</title><summary>  We introduce scientific claim verification.
 A new task.  </summary><published>2020-04-30T17:00:00Z</published></entry></feed>"""


def test_fetch_arxiv_atom(tmp_path):
    f = fetcher([("export.arxiv.org", Resp(200, text=ATOM))], tmp_path)
    p = f.fetch_paper("arXiv:2004.14974v1")
    assert p.title == "Fact or Fiction: Verifying Scientific Claims" and p.year == 2020 and p.venue == "arXiv"
    assert p.abstract == "We introduce scientific claim verification. A new task."
    assert f.session.calls[0][1] == {"id_list": "2004.14974"}


def test_fetch_references_with_contexts(tmp_path):
    payload = {"data": [
        {"contexts": ["Zorvex helps bones [3]."], "intents": ["result"],
         "citedPaper": {"paperId": "p1", "title": "Zorvex trial", "abstract": "Zorvex helps.", "year": 2019, "externalIds": {"DOI": "10.1/A"}}},
        {"contexts": [], "intents": [], "citedPaper": {"paperId": "p2", "title": "No context paper", "abstract": None}},
        {"contexts": ["ignored"], "citedPaper": {"paperId": "p3", "title": None}},
    ]}
    f = fetcher([("/references", Resp(200, payload))], tmp_path, s2_api_key="KEY")
    refs = f.fetch_references("10.1000/xyz", limit=5)
    assert [r.cited.title for r in refs] == ["Zorvex trial", "No context paper"]        # nameless rows dropped
    assert refs[0].context == "Zorvex helps bones [3]." and refs[0].cited.doi == "10.1/a" and refs[0].intents == ("result",)
    assert refs[1].context == "" and refs[1].cited.abstract == ""
    url, params, headers = f.session.calls[0]
    assert "DOI:10.1000/xyz/references" in url and params["limit"] == 5 and headers["x-api-key"] == "KEY"
    assert "citedPaper.abstract" in params["fields"] and "contexts" in params["fields"]


def test_paper_from_text():
    p = paper_from_text("T", "Sentence one. Sentence two.")
    assert p.source == "pasted" and p.paper_id.startswith("pasted-") and len(p.to_doc().sentences) == 2
    assert paper_from_text("", "x").title == "Pasted abstract"
    with pytest.raises(IngestError):
        paper_from_text("t", "   ")
