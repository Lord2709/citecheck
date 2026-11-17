"""Find a LEGAL open-access full text for a paper, as sentences.   Owner: Engineering.

Used only when the verifier is unsure on the abstract (docs/agent_plan.md, "Read the full text?").  Order:
  1. arXiv            the paper is an arXiv preprint: https://arxiv.org/pdf/<id>
  2. Europe PMC       a DOI with an open-access PMC copy: full text as XML (no PDF parsing needed)
  3. Unpaywall        a DOI with a legal open-access PDF somewhere (needs a contact e-mail: CITECHECK_MAILTO)
  4. OpenAlex         the PDF links of its open-access locations (for example the ACL Anthology)
  5. Semantic Scholar the open-access PDF it lists for the DOI (author copies and repositories Unpaywall can miss);
                      after OpenAlex, because without an API key it often answers HTTP 429 from shared cloud addresses
  6. arXiv by title   an arXiv version that no DOI record links to, accepted only when the title matches
Within each route, repository copies are tried before the publisher's: publisher sites often refuse programs.
On the DOIs users cited up to 2026-11-17, routes 4 and 5 raised the share of papers with a free full text from 5 to
13 of 18 (docs/live_checks/2026-11-17_source_coverage.md).
Paywalled papers have no legal full text: the agent then says it only read the abstract.
PDFs are read with pypdf (src/pdf_check.py); scanned PDFs yield no text and are skipped.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

from .pdf_check import PdfRejected, extract_page_texts
from .schema import Paper
from .text_utils import split_sentences

EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
UNPAYWALL = "https://api.unpaywall.org/v2/{doi}"
MAX_PDF_BYTES = 20_000_000
MAX_UNPAYWALL_PDFS = 3       # PDF links tried per source (repository copies first, then the publisher's)
# Repositories let programs download their PDFs; publisher sites often refuse them (seen live on 2026-11-10: the ACM
# Digital Library answered HTTP 403 for two open-access papers), so their copies are tried first.
REPOSITORY_HOSTS = ("arxiv.org", "europepmc.org", "ncbi.nlm.nih.gov", "biorxiv.org", "medrxiv.org", "hal.science",
                    "zenodo.org", "osf.io", "core.ac.uk", "aclanthology.org", "openreview.net", ".edu/")
MIN_TITLE_MATCH = 0.85       # an arXiv copy found by title must have (almost) the same title,
MIN_TITLE_WORDS = 5          # a title specific enough ("Deep learning" matches many unrelated arXiv papers),
ARXIV_YEARS = (-3, 1)        # and a year close to the paper's (a preprint comes before, or soon after, the paper)
MIN_SENT, MAX_SENT = 25, 600
_REF_TAIL = re.compile(r"\n\s*(references|bibliography|literature cited)\s*\n", re.I)


@dataclass
class FullText:
    source: str                 # arxiv | europepmc | unpaywall | s2 | openalex
    url: str
    sentences: list = field(default_factory=list)


def clean_sentences(text: str) -> list:
    """Body text -> sentences: drop the reference list, very short fragments and run-on garbage."""
    m = list(_REF_TAIL.finditer(text or ""))
    if m:
        text = text[: m[-1].start()]
    text = re.sub(r"-\n(?=[a-z])", "", text or "")          # re-join hyphenated line breaks
    return [s for s in split_sentences(text) if MIN_SENT <= len(s) <= MAX_SENT]


def arxiv_id(paper: Paper) -> Optional[str]:
    for s in (paper.paper_id or "", paper.url or ""):
        m = re.search(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})", s, re.I)
        if m:
            return m.group(1)
    return None


def is_repository(url: str, kind: str = "") -> bool:
    return kind == "repository" or any(h in (url or "").lower() for h in REPOSITORY_HOSTS)


def repository_first(pairs) -> list:
    """URLs from (url, kind) pairs without duplicates: repository copies first, each group in its original order."""
    seen, repo, other = set(), [], []
    for url, kind in pairs:
        if url and url not in seen:
            seen.add(url)
            (repo if is_repository(url, kind) else other).append(url)
    return repo + other


def unpaywall_pdf_urls(record: dict) -> list:
    """Every PDF link in an Unpaywall record, repository copies first, without duplicates.
    Seen live on 2026-10-23: a paper can be open access with no PDF link in its best location (only a landing page)."""
    locs = [record.get("best_oa_location") or {}] + list(record.get("oa_locations") or [])
    return repository_first(((loc or {}).get("url_for_pdf"), (loc or {}).get("host_type", "")) for loc in locs)


def title_tokens(title: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (title or "").lower())) - {"a", "an", "the", "of", "and", "for", "in", "on", "with"}


def same_title(a: str, b: str) -> bool:
    ta, tb = title_tokens(a), title_tokens(b)
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= MIN_TITLE_MATCH


def arxiv_match(entries: list, title: str, year=None):
    """The arXiv id of the entry that is this paper, or None.  Seen on 2026-11-17: by title alone, Nature's "Deep
    learning" (2015) and CACM's "Security in wireless sensor networks" (2004) matched unrelated arXiv papers."""
    if len(title_tokens(title)) < MIN_TITLE_WORDS:
        return None
    for aid, t, y in entries:
        if not same_title(t, title):
            continue
        if year and y and not (year + ARXIV_YEARS[0] <= y <= year + ARXIV_YEARS[1]):
            continue
        return aid
    return None


def arxiv_entries(xml_text: str) -> list:
    """(arXiv id, title, year first published) of each entry in an arXiv API answer."""
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out = []
    for e in root.findall("a:entry", ns):
        m = re.search(r"arxiv\.org/abs/([^\s]+?)(?:v\d+)?$", e.findtext("a:id", default="", namespaces=ns) or "")
        if m:
            published = e.findtext("a:published", default="", namespaces=ns) or ""
            out.append((m.group(1), re.sub(r"\s+", " ", e.findtext("a:title", default="", namespaces=ns)).strip(),
                        int(published[:4]) if published[:4].isdigit() else None))
    return out


def epmc_body_text(xml_text: str) -> str:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return ""
    body = root.find(".//body")
    if body is None:
        return ""
    paras = [" ".join("".join(p.itertext()).split()) for p in body.iter("p")]
    return "\n".join(p for p in paras if p)


class FullTextFinder:
    def __init__(self, fetcher, mailto: Optional[str] = None, max_bytes: int = MAX_PDF_BYTES):
        self.fetcher = fetcher
        self.mailto = mailto or getattr(fetcher, "mailto", None)
        self.max_bytes = max_bytes
        self.last_detail = ""
        self.last_free_url = ""

    def _pdf_sentences(self, url: str) -> list:
        r = self.fetcher.session.get(url, headers=self.fetcher._headers(url), timeout=self.fetcher.timeout)
        if r.status_code in (401, 403):
            host = re.sub(r"^https?://([^/]+).*$", r"\1", url)
            self.last_free_url = self.last_free_url or url       # free to read in a browser, not by a program
            raise RuntimeError(f"{host} refused the download (HTTP {r.status_code})")
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        content = getattr(r, "content", b"") or b""
        if len(content) > self.max_bytes:
            raise RuntimeError("PDF too large")
        if not content.startswith(b"%PDF"):
            raise RuntimeError("not a PDF (probably a landing page)")
        return clean_sentences("\n".join(extract_page_texts(content)))

    def find(self, paper: Paper) -> Optional[FullText]:
        """The full text as sentences, or None.  When None, `last_detail` says what was tried and `last_free_url` is a
        free copy a person can open in a browser (a PDF whose site refused our download, or an open-access web page),
        or "" when there is none."""
        tried = []
        self.last_free_url = ""
        aid = arxiv_id(paper)
        if aid:
            url = f"https://arxiv.org/pdf/{aid}"
            try:
                sents = self._pdf_sentences(url)
                if sents:
                    self.last_detail = f"arXiv PDF, {len(sents)} sentences"
                    return FullText("arxiv", url, sents)
                tried.append("arXiv: no text")
            except (PdfRejected, Exception) as e:
                tried.append(f"arXiv: {str(e)[:60]}")
        doi = (paper.doi or "").lower() or None
        if doi:
            try:
                r = self.fetcher._get(EPMC_SEARCH, {"query": f'DOI:"{doi}"', "format": "json", "resultType": "lite"})
                res = ((r.json() if r is not None else {}).get("resultList") or {}).get("result") or []
                hit = next((x for x in res if x.get("pmcid") and x.get("isOpenAccess") == "Y"), None)
                if hit:
                    url = EPMC_FULLTEXT.format(pmcid=hit["pmcid"])
                    r2 = self.fetcher._get(url)
                    sents = clean_sentences(epmc_body_text(r2.text)) if r2 is not None else []
                    if sents:
                        self.last_detail = f"Europe PMC {hit['pmcid']}, {len(sents)} sentences"
                        return FullText("europepmc", url, sents)
                    tried.append("Europe PMC: no body text")
                else:
                    tried.append("Europe PMC: no open-access copy")
            except Exception as e:
                tried.append(f"Europe PMC: {type(e).__name__}")
            if self.mailto:
                try:
                    r = self.fetcher._get(UNPAYWALL.format(doi=doi), {"email": self.mailto})
                    record = (r.json() if r is not None else {}) or {}
                    pdfs = unpaywall_pdf_urls(record)
                    if not pdfs:
                        tried.append("Unpaywall: open access, but only as a web page (no PDF)" if record.get("is_oa")
                                     else "Unpaywall: not open access (paywalled)")
                        if record.get("is_oa"):
                            best = record.get("best_oa_location") or {}
                            self.last_free_url = self.last_free_url or best.get("url_for_landing_page") or best.get("url") or ""
                    for pdf in pdfs[:MAX_UNPAYWALL_PDFS]:
                        try:
                            sents = self._pdf_sentences(pdf)
                        except Exception as e:
                            tried.append(f"Unpaywall PDF: {str(e)[:50]}")
                            continue
                        if sents:
                            self.last_detail = f"Unpaywall open-access PDF, {len(sents)} sentences"
                            return FullText("unpaywall", pdf, sents)
                        tried.append("Unpaywall PDF: no text")
                except Exception as e:
                    tried.append(f"Unpaywall: {str(e)[:60]}")
            else:
                tried.append("Unpaywall: skipped (no CITECHECK_MAILTO)")
            try:
                params = getattr(self.fetcher, "_openalex_params", lambda: None)()
                r = self.fetcher._get(f"https://api.openalex.org/works/https://doi.org/{doi}", params)
                j = (r.json() if r is not None else {}) or {}
                locs = [j.get("best_oa_location") or {}] + list(j.get("locations") or [])
                urls = repository_first(((loc or {}).get("pdf_url"), ((loc or {}).get("source") or {}).get("type", ""))
                                        for loc in locs)
                if not urls:
                    tried.append("OpenAlex: no open-access PDF")
                for u in urls[:MAX_UNPAYWALL_PDFS]:
                    try:
                        sents = self._pdf_sentences(u)
                    except Exception as e:
                        tried.append(f"OpenAlex PDF: {str(e)[:50]}")
                        continue
                    if sents:
                        self.last_detail = f"OpenAlex open-access PDF, {len(sents)} sentences"
                        return FullText("openalex", u, sents)
                    tried.append("OpenAlex PDF: no text")
            except Exception as e:
                tried.append(f"OpenAlex: {str(e)[:60]}")
            try:
                r = self.fetcher._get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                                      {"fields": "openAccessPdf"})
                pdf = (((r.json() if r is not None else {}) or {}).get("openAccessPdf") or {}).get("url")
                if not pdf:
                    tried.append("Semantic Scholar: no open-access PDF")
                else:
                    sents = self._pdf_sentences(pdf)
                    if sents:
                        self.last_detail = f"Semantic Scholar open-access PDF, {len(sents)} sentences"
                        return FullText("s2", pdf, sents)
                    tried.append("Semantic Scholar PDF: no text")
            except Exception as e:
                tried.append(f"Semantic Scholar: {str(e)[:60]}")
        if not aid and paper.title:
            ft = self._arxiv_by_title(paper.title, paper.year, tried)
            if ft is not None:
                return ft
        self.last_detail = "; ".join(tried) or "no DOI or arXiv id"
        return None

    def _arxiv_by_title(self, title: str, year, tried: list) -> Optional["FullText"]:
        """Many computer-science papers have an arXiv version that no DOI record links to: look it up by title, and
        accept it only when the titles (almost) match."""
        if len(title_tokens(title)) < MIN_TITLE_WORDS:
            tried.append("arXiv: title too short to search by")
            return None
        try:
            q = re.sub(r"[^\w\s-]", " ", title)
            r = self.fetcher._get("http://export.arxiv.org/api/query", {"search_query": f'ti:"{q.strip()}"', "max_results": 3})
            hit = arxiv_match(arxiv_entries(r.text if r is not None else ""), title, year)
            if hit is None:
                tried.append("arXiv: no version with this title")
                return None
            url = f"https://arxiv.org/pdf/{hit}"
            sents = self._pdf_sentences(url)
            if sents:
                self.last_detail = f"arXiv version {hit} (found by title), {len(sents)} sentences"
                return FullText("arxiv", url, sents)
            tried.append("arXiv version: no text")
        except Exception as e:
            tried.append(f"arXiv by title: {str(e)[:60]}")
        return None
