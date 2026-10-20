"""Find a LEGAL open-access full text for a paper, as sentences.   Owner: Engineering.

Used only when the verifier is unsure on the abstract (docs/agent_plan.md, "Read the full text?").  Order:
  1. arXiv            the paper is an arXiv preprint: https://arxiv.org/pdf/<id>
  2. Europe PMC       a DOI with an open-access PMC copy: full text as XML (no PDF parsing needed)
  3. Unpaywall        a DOI with a legal open-access PDF somewhere (needs a contact e-mail: CITECHECK_MAILTO)
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
MIN_SENT, MAX_SENT = 25, 600
_REF_TAIL = re.compile(r"\n\s*(references|bibliography|literature cited)\s*\n", re.I)


@dataclass
class FullText:
    source: str                 # arxiv | europepmc | unpaywall
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

    def _pdf_sentences(self, url: str) -> list:
        r = self.fetcher.session.get(url, headers=self.fetcher._headers(), timeout=self.fetcher.timeout)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        content = getattr(r, "content", b"") or b""
        if len(content) > self.max_bytes:
            raise RuntimeError("PDF too large")
        if not content.startswith(b"%PDF"):
            raise RuntimeError("not a PDF (probably a landing page)")
        return clean_sentences("\n".join(extract_page_texts(content)))

    def find(self, paper: Paper) -> Optional[FullText]:
        tried = []
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
                    best = ((r.json() if r is not None else {}) or {}).get("best_oa_location") or {}
                    pdf = best.get("url_for_pdf")
                    if pdf:
                        sents = self._pdf_sentences(pdf)
                        if sents:
                            self.last_detail = f"Unpaywall open-access PDF, {len(sents)} sentences"
                            return FullText("unpaywall", pdf, sents)
                        tried.append("Unpaywall: PDF has no text")
                    else:
                        tried.append("Unpaywall: no open-access PDF")
                except Exception as e:
                    tried.append(f"Unpaywall: {str(e)[:60]}")
            else:
                tried.append("Unpaywall: skipped (no CITECHECK_MAILTO)")
        self.last_detail = "; ".join(tried) or "no DOI or arXiv id"
        return None
