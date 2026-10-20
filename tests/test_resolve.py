"""Reference entry -> identifier (src/resolve.py)."""
from src.resolve import ReferenceResolver, title_overlap

from test_ingest import Resp, Session


class F:
    def __init__(self, routes, mailto="me@umd.edu"):
        self.session, self.mailto = Session(routes), mailto

    def _get(self, url, params=None):
        r = self.session.get(url, params=params)
        if r.status_code == 404:
            return None
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code}")
        return r


CR = {"message": {"items": [{"DOI": "10.18653/V1/2020.EMNLP-MAIN.609",
                             "title": ["Fact or Fiction: Verifying Scientific Claims"]}]}}


def test_identifier_in_reference_needs_no_network():
    r = ReferenceResolver(fetcher=None)
    assert r.resolve("Doe J. Zorvex. 2021. doi:10.1000/ZORVEX.").identifier == "10.1000/zorvex"
    assert r.resolve("Wadden et al. arXiv:2004.14974").identifier == "arXiv:2004.14974"
    assert r.resolve("Doe J. Zorvex. 2021.").identifier is None


def test_crossref_match_accepted_and_cached():
    f = F([("crossref.org", Resp(200, CR))])
    r = ReferenceResolver(f)
    res = r.resolve("Wadden D, et al. Fact or fiction: verifying scientific claims. EMNLP 2020.")
    assert res.identifier == "10.18653/v1/2020.emnlp-main.609" and res.method == "crossref"
    assert f.session.calls[0][1]["mailto"] == "me@umd.edu"
    r.resolve("Wadden D, et al. Fact or fiction: verifying scientific claims. EMNLP 2020.")
    assert len(f.session.calls) == 1


def test_crossref_wrong_title_rejected_and_failure_not_cached():
    f = F([("crossref.org", Resp(200, CR))])
    res = ReferenceResolver(f).resolve("Roe A. Statins and cholesterol in adults. Lancet 2019.")
    assert res.identifier is None and "no Crossref match" in res.detail
    g = F([("crossref.org", [Resp(500), Resp(200, CR)])])
    rr = ReferenceResolver(g)
    assert rr.resolve("Fact or fiction verifying scientific claims").identifier is None
    assert rr.resolve("Fact or fiction verifying scientific claims").identifier is not None   # retried, not cached


def test_title_overlap():
    assert title_overlap("Fact or Fiction", "fact or fiction: verifying") == 1.0
    assert title_overlap("", "x") == 0.0
