"""tools/source_coverage.py: which free source has the abstract and the full text, without the network."""
from tools import source_coverage as sc

LONG = " ".join(["word"] * 40)


class Resp:
    def __init__(self, status, payload=None):
        self.status_code, self._payload = status, payload

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class Session:
    """Answers by URL substring; records every call (url, params, headers)."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append((url, params or {}, headers or {}))
        for key, resp in self.routes:
            if key in url:
                return resp
        return Resp(404)


def routes_for(paywalled=False):
    inv = {w: [i] for i, w in enumerate(f"w{i}" for i in range(40))}
    return [
        ("api.openalex.org", Resp(200, {"abstract_inverted_index": None if paywalled else inv, "publication_year": 2005,
                                        "open_access": {"oa_status": "closed"}, "locations": [{"pdf_url": None}],
                                        "primary_location": {"source": {"host_organization_name": "Elsevier BV"}}})),
        ("api.semanticscholar.org", Resp(429)),
        ("api.crossref.org", Resp(200, {"message": {"abstract": f"<jats:p>{LONG}</jats:p>"}})),
        ("europepmc", Resp(200, {"resultList": {"result": []}})),
        ("api.unpaywall.org", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": None,
                                                                             "url_for_landing_page": "https://x"}})),
    ]


def test_read_dois_from_a_csv_export():
    text = 'doi\n10.1016/j.adhoc.2005.01.004\n"10.1109/MNET.2006.1637927",x\n10.1016/j.adhoc.2005.01.004\nnot a doi\n'
    assert sc.read_dois(text) == ["10.1016/j.adhoc.2005.01.004", "10.1109/mnet.2006.1637927"]


def test_probe_finds_what_each_source_has():
    http = sc.Http(session=Session(routes_for(paywalled=True)), mailto="team@example.edu", sleep=lambda s: None)
    row = sc.probe("10.1016/j.adhoc.2005.01.004", http, mailto="team@example.edu")
    assert row["openalex"] is False and row["crossref"] is True and row["s2"] == "error 429"
    assert row["abstract_before"] is False and row["abstract_after"] is True        # Crossref adds it
    assert row["unpaywall_pdf"] is False and row["unpaywall_landing_only"] is True
    assert row["fulltext_any"] is False and row["core"].startswith("skipped")
    assert row["publisher"] == "Elsevier BV" and row["year"] == 2005


def test_keys_go_only_to_their_own_service():
    session = Session(routes_for())
    http = sc.Http(session=session, mailto="team@example.edu", s2_key="S2SECRET", core_key="CORESECRET",
                   sleep=lambda s: None)
    report = sc.run(["10.1/abc"], http=http, env={"CITECHECK_MAILTO": "team@example.edu", "CORE_API_KEY": "CORESECRET",
                                                  "S2_API_KEY": "S2SECRET"}, pause=lambda: None)
    for url, params, headers in session.calls:
        assert ("x-api-key" in headers) == ("semanticscholar" in url)
        assert ("Authorization" in headers) == ("core.ac.uk" in url)
    out = sc.to_markdown(report) + str(report)
    assert "S2SECRET" not in out and "CORESECRET" not in out and "S2_API_KEY" in report["keys_used"]


def test_summary_counts_what_sources_add_beyond_the_product():
    rows = [
        {"openalex": True, "s2": False, "crossref": True, "europepmc": False, "unpaywall_pdf": False,
         "europepmc_oa": False, "s2_oa_pdf": True, "openalex_pdf": False, "core": False},
        {"openalex": False, "s2": False, "crossref": True, "europepmc": False, "unpaywall_pdf": True,
         "europepmc_oa": False, "s2_oa_pdf": True, "openalex_pdf": True, "core": False},
    ]
    for r in rows:
        for what, sources in (("abstract", sc.ABSTRACT_SOURCES), ("fulltext", sc.FULLTEXT_SOURCES)):
            r[f"{what}_before"] = any(r[k] for k in sc.BEFORE[what])
            r[f"{what}_after"] = any(r[k] for k in sc.AFTER[what])
            r[f"{what}_any"] = any(r[k] for k in sources)
    s = sc.summarize(rows)
    assert (s["abstract_before"], s["abstract_after"], s["abstract_any"]) == (1, 2, 2)
    assert s["adds_beyond_before"]["crossref"] == 1 and s["adds_beyond_before"]["s2_oa_pdf"] == 1
    assert (s["fulltext_before"], s["fulltext_after"], s["fulltext_any"]) == (1, 2, 2)
    assert "| abstract available | 1/2 (50%) | 2/2 (100%) | 2/2 (100%) |" in sc.to_markdown(
        {"date": "2026-11-17", "platform": "test", "keys_used": [], "rows": [dict(r, doi="10.1/x") for r in rows],
         "summary": s})


def test_a_run_without_the_contact_email_says_it_is_incomplete():
    http = sc.Http(session=Session(routes_for()), sleep=lambda s: None)
    report = sc.run(["10.1/abc"], http=http, env={}, pause=lambda: None)
    md = sc.to_markdown(report)
    assert report["summary"]["by_source"]["unpaywall_pdf"]["skipped"] == 1
    assert "Incomplete run: unpaywall_pdf, core skipped" in md
