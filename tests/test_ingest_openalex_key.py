"""OpenAlex API key handling (OpenAlex meters usage since 2026; the key goes in the `api_key` query parameter)."""
from src.ingest import Fetcher

from test_ingest import OPENALEX, Resp, Session, fetcher


def test_key_and_mailto_are_sent_to_openalex(tmp_path):
    f = fetcher([("openalex.org", Resp(200, OPENALEX))], tmp_path, mailto="me@umd.edu", openalex_api_key="k123")
    f.fetch_paper("10.1000/xyz")
    url, params, headers = f.session.calls[0]
    assert "openalex.org" in url and params == {"api_key": "k123", "mailto": "me@umd.edu"}
    assert "x-api-key" not in headers  # that header is the Semantic Scholar key, not OpenAlex


def test_key_from_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENALEX_API_KEY", "fromenv")
    f = fetcher([("openalex.org", Resp(200, OPENALEX))], tmp_path)
    f.fetch_paper("10.1000/xyz")
    assert f.session.calls[0][1] == {"api_key": "fromenv"}


def test_no_key_no_mailto_sends_no_params(tmp_path):
    f = fetcher([("openalex.org", Resp(200, OPENALEX))], tmp_path)
    f.fetch_paper("10.1000/xyz")
    assert f.session.calls[0][1] is None


def test_key_is_not_sent_to_other_services(tmp_path):
    f = fetcher([("export.arxiv.org", Resp(404))], tmp_path, openalex_api_key="k123")
    try:
        f.fetch_paper("arXiv:2004.14974")
    except Exception:
        pass
    for url, params, _ in f.session.calls:
        assert "k123" not in str(params) and "k123" not in url


def test_openalex_key_is_used_for_search(monkeypatch):
    """Discovery (src/discovery.py) searches OpenAlex with the same key."""
    from src.discovery import PaperSearch
    from test_discovery import OA

    monkeypatch.setenv("OPENALEX_API_KEY", "k1")
    f = Fetcher(session=Session([("api.openalex.org", Resp(200, OA))]), cache_dir=None, sleep=lambda s: None)
    PaperSearch(f, sources=("openalex",)).search("claims")
    assert f.session.calls[0][1]["api_key"] == "k1" and f.session.calls[0][1]["search"] == "claims"
