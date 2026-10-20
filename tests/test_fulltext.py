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

    def _headers(self):
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
