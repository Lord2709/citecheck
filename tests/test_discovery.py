"""Discovery path (src/discovery.py): parsing, merging, ranking, failing sources.  Fake HTTP only."""
import pytest

from src import discovery as dsc
from src.data_io import load_corpus
from src.ingest import Fetcher
from src.retrieval import BM25Retriever
from src.schema import Paper

from test_ingest import Resp, Session

OA = {"results": [{"id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/A", "display_name": "Claim verification",
                   "publication_year": 2020, "abstract_inverted_index": {"We": [0], "verify": [1], "claims.": [2]},
                   "primary_location": {"source": {"display_name": "EMNLP"}}}]}
S2 = {"data": [{"paperId": "p1", "title": "Claim Verification", "abstract": "We verify scientific claims against abstracts.",
                "year": 2020, "externalIds": {"DOI": "10.1/a"}},
               {"paperId": "p2", "title": "Unrelated cooking", "abstract": "Pasta recipes.", "year": 2021, "externalIds": {}}]}
ATOM = """<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>http://arxiv.org/abs/2004.14974v2</id>
<title>Fact or Fiction</title><summary>Scientific claim verification with evidence.</summary>
<published>2020-04-30T00:00:00Z</published></entry></feed>"""


def fetcher(routes):
    return Fetcher(session=Session(routes), cache_dir=None, sleep=lambda s: None)


def test_build_query():
    assert dsc.build_query("Using NLP to verify the scientific claims, claims!") == "nlp verify scientific claims"


def test_parsers_and_merge_by_doi():
    oa, s2 = dsc.parse_openalex(OA), dsc.parse_s2(S2)
    assert oa[0].doi == "10.1/a" and oa[0].abstract == "We verify claims." and oa[0].venue == "EMNLP"
    ax = dsc.parse_arxiv(ATOM)
    assert ax[0].paper_id == "arxiv:2004.14974" and ax[0].year == 2020
    merged = dsc.merge([dsc.Candidate(oa[0], ["openalex"]), dsc.Candidate(s2[0], ["s2"]), dsc.Candidate(s2[1], ["s2"])])
    assert len(merged) == 2 and merged[0].sources == ["openalex", "s2"]
    assert merged[0].paper.abstract.startswith("We verify scientific")          # the longer abstract is kept
    assert dsc.parse_arxiv("not xml") == []


def test_search_survives_a_failing_source_and_ranks():
    f = fetcher([("api.openalex.org", Resp(200, OA)), ("semanticscholar.org", Resp(429)), ("export.arxiv.org", Resp(200, text=ATOM))])
    ps = dsc.PaperSearch(f, sources=("openalex", "s2", "arxiv"))
    rep = dsc.discover("verifying scientific claims", ps, k=5)
    assert "s2" in rep.errors and len(rep.results) == 2
    assert rep.results[0].score >= rep.results[1].score and rep.results[0].key_sentence
    d = rep.to_dict()
    assert d["kind"] == "discovery" and d["results"][0]["paper"]["title"]
    assert [p.title for p in ps.as_tool()("claims", 3)]
    with pytest.raises(ValueError):
        dsc.discover("  ", ps)


def test_corpus_source_offline(fixture_dir):
    docs = load_corpus(fixture_dir / "corpus.jsonl")
    ps = dsc.PaperSearch(None, sources=("corpus",), retriever=BM25Retriever(docs))
    res = ps.search(docs[0].title, 3)
    assert res.candidates and res.candidates[0].paper.source == "scifact" and not res.errors
    assert dsc.PaperSearch(None, sources=("openalex",)).search("x").errors   # no fetcher: reported, not raised


def test_explain_picks_best_sentence():
    p = Paper("x", "T", "Cooking is fun. Scientific claims need verification against evidence.")
    assert dsc.explain("verifying scientific claims", p).startswith("Scientific claims")
