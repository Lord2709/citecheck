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


# P05's reference [3] (Session 11): Crossref's top hit was a different, 2007 paper whose short title's words all
# appear in the entry, so the title check alone accepted it.  The records below are made up for the test.
STACKGUARD = ("Cowan et al. StackGuard: Automatic Adaptive Detection and Prevention of Buffer-Overflow Attacks. "
              "USENIX Security 1998.")
WRONG_2007 = {"DOI": "10.1000/WRONG.2007", "title": ["Automatic Detection of Buffer-Overflow Attacks"],
              "author": [{"family": "Lee", "given": "A."}, {"family": "Park", "given": "B."}],
              "issued": {"date-parts": [[2007, 5]]}}
RIGHT_1998 = {"DOI": "10.1000/STACKGUARD", "title": ["StackGuard: Automatic Adaptive Detection and Prevention of "
                                                     "Buffer-Overflow Attacks"],
              "author": [{"family": "Cowan", "given": "C."}, {"family": "Pu", "given": "C."}],
              "issued": {"date-parts": [[1998]]}}


def _cr(*items):
    return {"message": {"items": list(items)}}


def test_wrong_year_and_authors_are_rejected():
    f = F([("crossref.org", Resp(200, _cr(WRONG_2007)))])
    res = ReferenceResolver(f).resolve(STACKGUARD)
    assert res.identifier is None and res.method == "none"
    assert "different paper" in res.detail and "2007" in res.detail and "1998" in res.detail


def test_the_candidate_that_passes_every_check_is_used():
    f = F([("crossref.org", Resp(200, _cr(WRONG_2007, RIGHT_1998)))])
    res = ReferenceResolver(f).resolve(STACKGUARD)
    assert res.identifier == "10.1000/stackguard"
    assert "first author Cowan and year 1998 match the reference" in res.detail
    assert f.session.calls[0][1]["rows"] == 5


def test_right_author_wrong_year_is_rejected():
    item = dict(RIGHT_1998, issued={"date-parts": [[2007]]}, created={"date-parts": [[2007]]})
    res = ReferenceResolver(F([("crossref.org", Resp(200, _cr(item)))])).resolve(STACKGUARD)
    assert res.identifier is None and "its year (2007)" in res.detail


def test_a_year_apart_is_allowed_and_accents_do_not_matter():
    item = {"DOI": "10.1000/X", "title": ["Federated learning for intrusion detection in smart homes"],
            "author": [{"family": "Müller", "given": "J."}], "issued": {"date-parts": [[2021]]},
            "published-online": {"date-parts": [[2020, 12]]}}
    entry = "J. Muller, Federated learning for intrusion detection in smart homes, IEEE IoT Journal, 2020."
    res = ReferenceResolver(F([("crossref.org", Resp(200, _cr(item)))])).resolve(entry)
    assert res.identifier == "10.1000/x"


def test_missing_year_or_authors_are_not_held_against_a_match():
    item = {"DOI": "10.1000/Y", "title": ["Federated learning for intrusion detection in smart homes"]}
    entry = "Federated learning for intrusion detection in smart homes. IEEE IoT Journal."
    res = ReferenceResolver(F([("crossref.org", Resp(200, _cr(item)))])).resolve(entry)
    assert res.identifier == "10.1000/y" and "no author or year to compare" in res.detail


def test_years_inside_urls_and_dois_are_not_reference_years():
    from src.resolve import entry_years
    assert entry_years("Smith J. Title. 2019. https://example.org/2004/x doi:10.1145/2007.123") == {2019}
    assert entry_years("Microsoft. Data Execution Prevention. https://learn.microsoft.com/en-us/x") == set()


def test_author_named_uses_the_longest_part_of_a_family_name():
    from src.resolve import author_named
    assert author_named(["van der Berg"], "A. van der Berg and B. Smith (2020) A title")
    assert not author_named(["Lee", "Park"], STACKGUARD)
