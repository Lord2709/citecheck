"""Open-access full text (src/fulltext.py) with fake HTTP: no network."""
import pytest

pytest.importorskip("pypdf")

from src.fulltext import FullTextFinder, arxiv_id, clean_sentences, epmc_body_text  # noqa: E402
from src.schema import Paper  # noqa: E402

from test_ingest import Resp, Session  # noqa: E402
from test_pdf_check import make_pdf  # noqa: E402

BODY = ("Mice fed zorvex for twelve weeks showed a large increase in femoral bone density compared with controls. "
        "The increase was dose dependent across all three groups that we studied in this work. ")


class PdfResp(Resp):
    def __init__(self, content, status=200):
        super().__init__(status)
        self.content = content


class F:
    def __init__(self, routes, mailto=None):
        self.session, self.mailto, self.timeout = Session(routes), mailto, 5

    def _headers(self, url=""):
        return {}

    def _get(self, url, params=None):
        r = self.session.get(url, params=params)
        return None if r.status_code == 404 else r


def test_arxiv_id_and_cleaning():
    assert arxiv_id(Paper("arxiv:2004.14974")) == "2004.14974"
    assert arxiv_id(Paper("x", url="https://arxiv.org/abs/1706.03762")) == "1706.03762"
    assert arxiv_id(Paper("doi:10.1/x")) is None
    sents = clean_sentences(BODY + "\nReferences\n[1] Doe J. Something cited here, 2020. More text in the list.")
    assert len(sents) == 2 and all("Doe" not in s for s in sents)


def test_arxiv_pdf_path():
    f = F([("arxiv.org/pdf", PdfResp(make_pdf([BODY * 3])))])
    ft = FullTextFinder(f).find(Paper("arxiv:2004.14974", title="T"))
    assert ft is not None and ft.source == "arxiv" and len(ft.sentences) >= 2


def test_europepmc_path_and_unpaywall_skipped_without_email():
    xml = f"<article><front><p>Abstract text here only.</p></front><body><sec><p>{BODY}</p></sec></body></article>"
    f = F([("rest/search", Resp(200, {"resultList": {"result": [{"pmcid": "PMC1", "isOpenAccess": "Y"}]}})),
           ("fullTextXML", Resp(200, text=xml))])
    ft = FullTextFinder(f).find(Paper("doi:10.1/x", doi="10.1/x"))
    assert ft.source == "europepmc" and "femoral" in ft.sentences[0]
    assert "Abstract text" not in epmc_body_text(xml)
    g = F([("rest/search", Resp(200, {"resultList": {"result": []}}))])
    finder = FullTextFinder(g)
    assert finder.find(Paper("doi:10.1/x", doi="10.1/x")) is None
    assert "no open-access copy" in finder.last_detail and "no CITECHECK_MAILTO" in finder.last_detail


def test_unpaywall_landing_page_is_not_a_pdf():
    f = F([("rest/search", Resp(200, {"resultList": {"result": []}})),
           ("unpaywall.org", Resp(200, {"best_oa_location": {"url_for_pdf": "https://pub.example/x.pdf"}})),
           ("pub.example", PdfResp(b"<html>login</html>"))], mailto="me@umd.edu")
    finder = FullTextFinder(f)
    assert finder.find(Paper("doi:10.1/x", doi="10.1/x")) is None and "not a PDF" in finder.last_detail


def test_unpaywall_pdf_urls_checks_every_location():
    from src.fulltext import unpaywall_pdf_urls

    rec = {"best_oa_location": {"url": "https://journal/landing", "url_for_pdf": None},     # seen live on 2026-10-23
           "oa_locations": [{"url_for_pdf": None}, {"url_for_pdf": "https://repo/a.pdf"}, {"url_for_pdf": "https://repo/a.pdf"}]}
    assert unpaywall_pdf_urls(rec) == ["https://repo/a.pdf"]
    assert unpaywall_pdf_urls({}) == []


def test_unpaywall_uses_a_non_best_location():
    f = F([("rest/search", Resp(200, {"resultList": {"result": []}})),
           ("unpaywall.org", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": None},
                                        "oa_locations": [{"url_for_pdf": "https://repo.example/a.pdf"}]})),
           ("repo.example", PdfResp(make_pdf([BODY * 3])))], mailto="me@umd.edu")
    ft = FullTextFinder(f).find(Paper("doi:10.1/x", doi="10.1/x"))
    assert ft is not None and ft.source == "unpaywall" and ft.url == "https://repo.example/a.pdf"


def test_unpaywall_says_whether_a_paper_is_paywalled_or_only_a_web_page():
    closed = F([("unpaywall", Resp(200, {"is_oa": False, "best_oa_location": None, "oa_locations": []}))],
               mailto="me@umd.edu")
    finder = FullTextFinder(closed)
    assert finder.find(Paper("doi:10.1/x", doi="10.1/x")) is None
    assert "not open access (paywalled)" in finder.last_detail
    web = F([("unpaywall", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": None,
                                                                          "url_for_landing_page": "https://x"}}))],
            mailto="me@umd.edu")
    finder = FullTextFinder(web)
    assert finder.find(Paper("doi:10.1/x", doi="10.1/x")) is None and "only as a web page" in finder.last_detail


def test_semantic_scholar_open_access_pdf_is_the_last_route():
    f = F([("unpaywall", Resp(200, {"is_oa": False})),
           ("semanticscholar.org", Resp(200, {"openAccessPdf": {"url": "https://author.example/copy.pdf"}})),
           ("author.example", PdfResp(make_pdf([BODY * 3])))], mailto="me@umd.edu")
    ft = FullTextFinder(f).find(Paper("doi:10.1/x", doi="10.1/x"))
    assert ft is not None and ft.source == "s2" and ft.url == "https://author.example/copy.pdf"


def test_openalex_pdf_locations_are_tried_before_semantic_scholar():
    oa = {"best_oa_location": {"pdf_url": None}, "locations": [{"pdf_url": "https://aclanthology.example/a.pdf"}]}
    f = F([("unpaywall", Resp(200, {"is_oa": False})), ("semanticscholar.org", Resp(200, {"openAccessPdf": None})),
           ("api.openalex.org", Resp(200, oa)), ("aclanthology.example", PdfResp(make_pdf([BODY * 3])))],
          mailto="me@umd.edu")
    finder = FullTextFinder(f)
    ft = finder.find(Paper("doi:10.18653/x", doi="10.18653/x"))
    assert ft is not None and ft.source == "openalex"
    assert not any("semanticscholar" in call[0] for call in f.session.calls)   # often HTTP 429 without a key: last


def test_repository_copies_are_tried_before_the_publisher():
    from src.fulltext import unpaywall_pdf_urls

    rec = {"best_oa_location": {"url_for_pdf": "https://dl.acm.org/doi/pdf/10.1145/x", "host_type": "publisher"},
           "oa_locations": [{"url_for_pdf": "https://dl.acm.org/doi/pdf/10.1145/x", "host_type": "publisher"},
                            {"url_for_pdf": "https://eprints.uni.example/x.pdf", "host_type": "repository"},
                            {"url_for_pdf": "https://arxiv.org/pdf/2501.00001", "host_type": ""}]}
    assert unpaywall_pdf_urls(rec) == ["https://eprints.uni.example/x.pdf", "https://arxiv.org/pdf/2501.00001",
                                       "https://dl.acm.org/doi/pdf/10.1145/x"]


def test_a_refused_download_names_the_site_and_an_arxiv_version_is_found_by_title():
    atom = ('<feed xmlns="http://www.w3.org/2005/Atom">'
            '<entry><id>http://arxiv.org/abs/2502.01234v2</id><title>MeshAgent: Enabling Reliable Network\n'
            '  Management with Large Language Models</title></entry></feed>')
    f = F([("unpaywall", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": "https://dl.acm.org/doi/pdf/1"}})),
           ("dl.acm.org", PdfResp(b"", status=403)), ("export.arxiv.org", Resp(200, text=atom)),
           ("arxiv.org/pdf/2502.01234", PdfResp(make_pdf([BODY * 3])))], mailto="me@umd.edu")
    finder = FullTextFinder(f)
    ft = finder.find(Paper("doi:10.1145/1", doi="10.1145/1",
                           title="MeshAgent: Enabling Reliable Network Management with Large Language Models"))
    assert ft is not None and ft.url == "https://arxiv.org/pdf/2502.01234" and "found by title" in finder.last_detail
    other = FullTextFinder(f)                       # a different paper with a similar topic is not accepted
    assert other.find(Paper("doi:10.1145/2", doi="10.1145/2", title="Reliable LLM agents for traffic analysis")) is None
    assert "dl.acm.org refused the download (HTTP 403)" in other.last_detail
    assert "arXiv: no version with this title" in other.last_detail


def test_an_arxiv_title_match_needs_a_specific_title_and_a_close_year():
    from src.fulltext import arxiv_match

    entries = [("1801.00001", "Deep Learning", 2018), ("1509.01234", "Security in Wireless Sensor Networks", 2015),
               ("2502.01234", "MeshAgent: Enabling Reliable Network Management with Large Language Models", 2025)]
    assert arxiv_match(entries, "Deep learning", 2015) is None                          # too short to trust
    assert arxiv_match(entries, "Security in wireless sensor networks", 2004) is None    # same words, wrong paper
    assert arxiv_match(entries, "MeshAgent: Enabling reliable network management with large language models",
                       2025) == "2502.01234"


def test_a_free_copy_whose_site_refuses_us_is_remembered_for_the_researcher():
    f = F([("unpaywall", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": "https://dl.acm.org/doi/pdf/9"}})),
           ("dl.acm.org", PdfResp(b"", status=403))], mailto="me@umd.edu")
    finder = FullTextFinder(f)
    assert finder.find(Paper("doi:10.1145/9", doi="10.1145/9", title="Short")) is None
    assert finder.last_free_url == "https://dl.acm.org/doi/pdf/9"
    web = F([("unpaywall", Resp(200, {"is_oa": True, "best_oa_location": {"url_for_pdf": None,
                                                                          "url_for_landing_page": "https://j.example/a"}}))],
            mailto="me@umd.edu")
    finder = FullTextFinder(web)
    assert finder.find(Paper("doi:10.1/a", doi="10.1/a")) is None and finder.last_free_url == "https://j.example/a"
