"""Read a web page cited in a reference (documentation, a blog post, an online article).   Owner: Engineering.

Participants cite pages that no paper database knows: Phrack articles, Microsoft Learn, dataset pages (Session 11:
3 of P05's 10 citations and several of P06's could not be checked, although the URL was in the reference).  When a
reference has no DOI or arXiv id and Crossref finds no matching paper, the agent reads the page at the reference's
URL and checks the claim against its text, like a full text.

The site fetches the URL on the server, so the URL is checked first (server-side request forgery):
  * http or https only, on the standard ports;
  * every address the host name resolves to must be a public address (no private, loopback, link-local or cloud
    metadata addresses), and so must every redirect target, which is followed by hand (at most MAX_REDIRECTS);
  * at most MAX_BYTES are read, with a time limit, and only HTML or plain text is used.
Known limit: the address is resolved once for the check and again by the HTTP client, so a host that changes its
DNS answer in between (DNS rebinding) is not caught.  Cloud Run's metadata server, the sensitive address there,
answers only requests that carry a Metadata-Flavor header, which this code never sends.
"""
from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Callable, Optional
from urllib.parse import urljoin, urlsplit

from .text_utils import split_sentences

URL = re.compile(r"https?://[^\s<>\"'\]\)]+", re.I)
SKIP_HOSTS = ("doi.org", "dx.doi.org", "arxiv.org", "www.arxiv.org")   # identifiers: resolved as papers already
MAX_BYTES = 2_000_000
MAX_REDIRECTS = 3
TIMEOUT = 15
MAX_SENTENCES = 3000
MIN_WORDS = 40              # a page with less text than this (a login wall, a script-only page) is not read
USER_AGENT = "CiteCheck-course-project/0.2 (reads pages cited in a draft)"


class WebPageError(Exception):
    """Why a page could not be read, in words a researcher understands."""


@dataclass
class WebPage:
    url: str
    title: str
    sentences: list = field(default_factory=list)


def reference_url(entry: str) -> Optional[str]:
    """The first web address in a reference entry that is not a DOI or arXiv link (those are papers)."""
    for m in URL.finditer(entry or ""):
        url = m.group(0).rstrip(".,;:")
        host = (urlsplit(url).hostname or "").lower()
        if host and host not in SKIP_HOSTS:
            return url
    return None


def _public(host: str, resolve: Optional[Callable] = None) -> bool:
    try:
        infos = (resolve or socket.getaddrinfo)(host, None)
    except (OSError, UnicodeError):
        return False
    addrs = {info[4][0] for info in infos}
    if not addrs:
        return False
    for a in addrs:
        ip = ipaddress.ip_address(a.split("%")[0])
        if not ip.is_global or ip.is_multicast:
            return False
    return True


def check_url(url: str, resolve: Optional[Callable] = None) -> str:
    """The URL if it may be fetched; otherwise WebPageError."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise WebPageError("only http and https addresses are read")
    if parts.username or parts.password:
        raise WebPageError("addresses with a user name or password are not read")
    if parts.port not in (None, 80, 443):
        raise WebPageError("only standard web ports are read")
    host = (parts.hostname or "").lower()
    if not host or host == "localhost" or host.endswith((".local", ".internal")):
        raise WebPageError("that address is not a public web page")
    if not _public(host, resolve):
        raise WebPageError("that address is not a public web page")
    return url


BREAK = "\x00"              # a block boundary; line breaks inside a paragraph's source are only spaces


class _Text(HTMLParser):
    """The readable text of a page: paragraphs, list items, headings, table cells; no scripts, menus or footers."""

    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "button", "select",
            "template", "iframe"}
    BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "pre", "blockquote", "dd", "dt", "div",
             "section", "article", "br", "tr", "figcaption", "caption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.in_title, self.title, self.parts = 0, False, "", []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "title":
            self.in_title = True
        elif tag in self.BLOCK:
            self.parts.append(BREAK)

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in self.BLOCK:
            self.parts.append(BREAK)

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip:
            self.parts.append(data.replace(BREAK, " "))


def page_text(html: str):
    """(title, sentences) of an HTML page."""
    p = _Text()
    p.feed(html or "")
    p.close()
    blocks = [re.sub(r"\s+", " ", b).strip() for b in "".join(p.parts).split(BREAK)]
    sentences = []
    for b in blocks:
        if len(b.split()) >= 4:                       # menus and labels are a word or three
            sentences += split_sentences(b)
    return re.sub(r"\s+", " ", p.title).strip(), sentences[:MAX_SENTENCES]


def fetch_page(url: str, session, resolve: Optional[Callable] = None) -> WebPage:
    """Fetch and read a cited page, following redirects by hand so that each target is checked too."""
    current = check_url(url, resolve)
    for _ in range(MAX_REDIRECTS + 1):
        try:
            r = session.get(current, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain"},
                            timeout=TIMEOUT, allow_redirects=False, stream=True)
        except Exception as e:
            raise WebPageError(f"the page did not answer ({type(e).__name__})") from e
        if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
            r.close()
            current = check_url(urljoin(current, r.headers["location"]), resolve)
            continue
        if r.status_code >= 400:
            r.close()
            raise WebPageError(f"the page answered HTTP {r.status_code}")
        ctype = (r.headers.get("content-type") or "").lower()
        if "html" not in ctype and "text/plain" not in ctype:
            r.close()
            raise WebPageError(f"it is not a web page ({ctype.split(';')[0] or 'unknown type'})")
        body, size = [], 0
        for chunk in r.iter_content(65536):
            body.append(chunk)
            size += len(chunk)
            if size > MAX_BYTES:
                break
        r.close()
        raw = b"".join(body)[:MAX_BYTES]
        text = raw.decode(r.encoding or "utf-8", errors="replace")
        if "html" in ctype:
            title, sentences = page_text(text)
        else:
            title, sentences = "", split_sentences(text)[:MAX_SENTENCES]
        if sum(len(s.split()) for s in sentences) < MIN_WORDS:
            raise WebPageError("the page has too little readable text (it may need a sign-in or a browser)")
        return WebPage(current, title or current, sentences)
    raise WebPageError("the page redirects too many times")
