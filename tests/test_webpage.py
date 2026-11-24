"""src/webpage.py and the agent's web-page fallback (no network)."""
import pytest

from src import webpage as wp
from src.agent import CiteCheckAgent
from src.resolve import ReferenceResolver
from src.schema import SUPPORT

from agent_fakes import FakeFetcher, make_pipeline

PUBLIC = "93.184.216.34"


def resolver(table):
    def resolve(host, port):
        if host not in table:
            raise OSError("no such host")
        return [(2, 1, 6, "", (table[host], 0))]
    return resolve


HOSTS = resolver({"phrack.org": PUBLIC, "learn.microsoft.com": PUBLIC, "evil.example": "10.0.0.5",
                  "meta.example": "169.254.169.254", "loop.example": "127.0.0.1"})

PAGE = """<html><head><title>Data Execution Prevention</title><script>var x = 'not text';</script></head>
<body><nav>Home Docs Sign in</nav>
<p>Data Execution Prevention (DEP) is a system-level memory protection feature that marks memory pages as
non-executable. DEP prevents code from being run from data pages such as the default heap, stacks and memory pools.
If an application attempts to run code from a data page that is protected, a memory access violation exception
occurs.</p><footer>Privacy Terms</footer></body></html>"""


class Resp:
    def __init__(self, status=200, body=b"", headers=None):
        self.status_code, self._body, self.headers, self.encoding = status, body, headers or {}, "utf-8"

    def iter_content(self, n):
        yield self._body

    def close(self):
        pass


class Session:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, **kw):
        self.calls.append((url, kw))
        assert kw.get("allow_redirects") is False                  # redirects are followed by hand, and checked
        return self.routes[url]


HTML = {"content-type": "text/html; charset=utf-8"}


def test_reference_url_skips_doi_and_arxiv_links():
    assert wp.reference_url("Aleph One. Smashing the Stack. Phrack 1996. https://phrack.org/issues/49/14.") \
        == "https://phrack.org/issues/49/14"
    assert wp.reference_url("Doe. Title. https://doi.org/10.1/x") is None
    assert wp.reference_url("Doe. Title. 2020.") is None


@pytest.mark.parametrize("url", ["ftp://phrack.org/x", "http://phrack.org:8080/x", "http://localhost/x",
                                 "http://evil.example/x", "http://meta.example/latest", "http://loop.example/",
                                 "http://user:pw@phrack.org/", "http://nowhere.example/", "http://db.internal/"])
def test_only_public_web_addresses_are_read(url):
    with pytest.raises(wp.WebPageError):
        wp.check_url(url, HOSTS)


def test_page_text_keeps_paragraphs_and_drops_scripts_and_menus():
    title, sentences = wp.page_text(PAGE)
    assert title == "Data Execution Prevention"
    assert sentences[0].startswith("Data Execution Prevention (DEP) is a system-level")
    assert not any("Sign in" in s or "not text" in s or "Privacy" in s for s in sentences)


def test_fetch_follows_a_checked_redirect_and_refuses_one_to_a_private_address():
    url = "https://learn.microsoft.com/dep"
    ok = Session({url: Resp(301, headers={"location": "/en-us/dep"}),
                  "https://learn.microsoft.com/en-us/dep": Resp(200, PAGE.encode(), HTML)})
    page = wp.fetch_page(url, ok, HOSTS)
    assert page.url.endswith("/en-us/dep") and len(page.sentences) == 3
    bad = Session({url: Resp(302, headers={"location": "http://meta.example/latest"})})
    with pytest.raises(wp.WebPageError, match="not a public"):
        wp.fetch_page(url, bad, HOSTS)


def test_fetch_refuses_files_errors_and_empty_pages():
    url = "https://phrack.org/x"
    for resp, why in [(Resp(200, b"%PDF", {"content-type": "application/pdf"}), "not a web page"),
                      (Resp(403), "HTTP 403"),
                      (Resp(200, b"<html><p>Please sign in</p></html>", HTML), "too little readable text")]:
        with pytest.raises(wp.WebPageError, match=why):
            wp.fetch_page(url, Session({url: resp}), HOSTS)


def test_the_agent_reads_a_cited_web_page_when_no_paper_matches(monkeypatch):
    monkeypatch.setattr(wp.socket, "getaddrinfo", HOSTS)
    fetcher = FakeFetcher({})
    url = "https://learn.microsoft.com/dep"
    fetcher.session = Session({url: Resp(200, PAGE.encode(), HTML)})
    agent = CiteCheckAgent(make_pipeline(), fetcher=fetcher, resolver=ReferenceResolver(None), suggest=False)
    text = ("DEP marks memory pages as non-executable to prevent code from being run from data pages [1].\n\n"
            "References\n[1] Microsoft. Data Execution Prevention. Microsoft Learn. " + url)
    c = agent.check_draft(text).citations[0]
    assert c.status == "checked" and c.full_text_source == "web page" and c.read_full_text
    assert c.paper.source == "web" and c.paper.title == "Data Execution Prevention"
    assert c.verdict.label == SUPPORT
    assert [s.action for s in c.steps][-2:] == ["read web page", "verify web page"]


def test_an_unreadable_page_says_why_and_full_text_off_skips_it(monkeypatch):
    monkeypatch.setattr(wp.socket, "getaddrinfo", HOSTS)
    fetcher = FakeFetcher({})
    fetcher.session = Session({"https://phrack.org/x": Resp(403)})
    text = "Stack smashing overwrites the saved return address [1].\n\nReferences\n[1] Aleph One. Phrack. https://phrack.org/x"
    c = CiteCheckAgent(make_pipeline(), fetcher=fetcher, resolver=ReferenceResolver(None), suggest=False) \
        .check_draft(text).citations[0]
    assert c.status == "unresolved" and "web page in the reference could not be read (the page answered HTTP 403)" in c.status_detail
    off = CiteCheckAgent(make_pipeline(), fetcher=fetcher, resolver=ReferenceResolver(None), suggest=False, escalate=False)
    c2 = off.check_draft(text).citations[0]
    assert c2.status == "unresolved" and "web page" not in c2.status_detail
