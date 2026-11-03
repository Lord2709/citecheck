"""Discovery: "here is my research direction, which papers should I read?"   Owner: Engineering, with Product.

    direction -> search queries -> search open sources -> merge duplicates -> rank -> explain each paper

Sources (all free; see docs/agent_plan.md):
  openalex : https://api.openalex.org/works?search=...      (metered: a free key gives ~1,000 searches/day)
  s2       : https://api.semanticscholar.org/graph/v1/paper/search
  arxiv    : http://export.arxiv.org/api/query
  corpus   : the local SciFact corpus with BM25 (offline; used by the evaluation and when the internet is down)

Ranking reuses src/relevance.py (transparent score + matched terms); the explanation is the paper sentence that best
matches the direction.  Scores are NOT calibrated (no labelled relevance data yet): they order results, they do not
certify relevance.  The agent also uses PaperSearch to look for replacement papers when a citation fails.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence

from .evidence import LexicalSentenceScorer
from .ingest import IngestError, abstract_from_inverted_index, looks_like_citation
from .relevance import RelevanceScorer
from .schema import Paper
from .text_utils import split_sentences, tokenize

DEFAULT_SOURCES = ("openalex", "s2", "arxiv")
MAX_QUERY_TERMS = 8


# ----------------------------------------------------------------------------------------------
# Queries
# ----------------------------------------------------------------------------------------------
def build_query(text: str, max_terms: int = MAX_QUERY_TERMS) -> str:
    """Content words of the direction (or claim), in order, without duplicates or stopwords."""
    seen, words = set(), []
    for w in tokenize(text or "", stem=False):
        if len(w) > 1 and w not in seen:
            seen.add(w)
            words.append(w)
    return " ".join(words[:max_terms])


# ----------------------------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------------------------
@dataclass
class Candidate:
    paper: Paper
    sources: list = field(default_factory=list)
    score: float = 0.0
    band: str = ""
    matched_terms: list = field(default_factory=list)
    key_sentence: str = ""

    def to_dict(self) -> dict:
        p = self.paper
        return {"paper": {"paper_id": p.paper_id, "title": p.title, "year": p.year, "venue": p.venue, "doi": p.doi,
                          "url": p.url, "source": p.source, "has_abstract": bool(p.abstract.strip())},
                "sources": list(self.sources), "score": round(self.score, 4), "band": self.band,
                "matched_terms": list(self.matched_terms), "key_sentence": self.key_sentence}


@dataclass
class SearchResult:
    query: str
    candidates: list = field(default_factory=list)  # list[Candidate], merged, in source order
    errors: dict = field(default_factory=dict)       # source -> message (a source that failed does not stop the others)


@dataclass
class DiscoveryReport:
    direction: str
    query: str
    results: list = field(default_factory=list)      # list[Candidate], ranked
    errors: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"kind": "discovery", "direction": self.direction, "query": self.query,
                "results": [c.to_dict() for c in self.results], "errors": dict(self.errors),
                "note": "Scores order the results; they are not calibrated (no labelled relevance data yet)."}


def _norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def dedupe_key(p: Paper) -> str:
    return f"doi:{p.doi.lower()}" if p.doi else f"title:{_norm_title(p.title)}"


def merge(candidates: Sequence) -> list:
    """Merge the same paper found by several sources (by DOI, else by normalised title); keep the longest abstract."""
    out, index = [], {}
    for c in candidates:
        if not c.paper.title.strip():
            continue
        k = dedupe_key(c.paper)
        if k not in index:
            index[k] = len(out)
            out.append(Candidate(c.paper, list(c.sources)))
            continue
        cur = out[index[k]]
        cur.sources += [s for s in c.sources if s not in cur.sources]
        if len(c.paper.abstract) > len(cur.paper.abstract):
            cur.paper = c.paper
    return out


# ----------------------------------------------------------------------------------------------
# Sources
# ----------------------------------------------------------------------------------------------
def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def parse_openalex(j: dict) -> list:
    out = []
    for w in (j or {}).get("results") or []:
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
        abstract = abstract_from_inverted_index(w.get("abstract_inverted_index"))
        if looks_like_citation(abstract):
            abstract = ""
        loc = w.get("primary_location") or {}
        out.append(Paper(paper_id=f"doi:{doi}" if doi else f"openalex:{(w.get('id') or '').rsplit('/', 1)[-1]}",
                         title=_clean(w.get("display_name") or w.get("title")), abstract=abstract,
                         year=w.get("publication_year"), venue=(loc.get("source") or {}).get("display_name"),
                         doi=doi, url=f"https://doi.org/{doi}" if doi else w.get("id"), source="openalex"))
    return out


def parse_s2(j: dict) -> list:
    out = []
    for r in (j or {}).get("data") or []:
        ext = r.get("externalIds") or {}
        doi = (ext.get("DOI") or "").lower() or None
        arxiv = ext.get("ArXiv")
        pid = f"doi:{doi}" if doi else f"arxiv:{arxiv}" if arxiv else f"s2:{r.get('paperId')}"
        out.append(Paper(paper_id=pid, title=_clean(r.get("title")), abstract=_clean(r.get("abstract")),
                         year=r.get("year"), venue=r.get("venue") or None, doi=doi,
                         url=r.get("url") or (f"https://arxiv.org/abs/{arxiv}" if arxiv else None), source="s2"))
    return out


def parse_arxiv(xml_text: str) -> list:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(xml_text or "")
    except ET.ParseError:
        return []
    out = []
    for e in root.findall("a:entry", ns):
        url = _clean(e.findtext("a:id", default="", namespaces=ns))
        m = re.search(r"arxiv\.org/abs/(.+?)(?:v\d+)?$", url)
        if not m:
            continue
        aid = m.group(1)
        published = _clean(e.findtext("a:published", default="", namespaces=ns))
        out.append(Paper(paper_id=f"arxiv:{aid}", title=_clean(e.findtext("a:title", default="", namespaces=ns)),
                         abstract=_clean(e.findtext("a:summary", default="", namespaces=ns)),
                         year=int(published[:4]) if published[:4].isdigit() else None, venue="arXiv",
                         url=f"https://arxiv.org/abs/{aid}", source="arxiv"))
    return out


def corpus_papers(retriever, query: str, n: int) -> list:
    """Local SciFact corpus as a search source (offline)."""
    return [Paper(paper_id=f"scifact:{h.doc.doc_id}", title=h.doc.title, abstract=h.doc.abstract, url=h.doc.url,
                  source="scifact") for h in retriever.search(query, n)]


class PaperSearch:
    """Searches several sources and merges the results.  `fetcher` is a src.ingest.Fetcher (retries, polite headers)."""

    def __init__(self, fetcher=None, sources: Sequence = DEFAULT_SOURCES, retriever=None, per_source: int = 10):
        self.fetcher, self.retriever, self.per_source = fetcher, retriever, per_source
        self.sources = [s for s in sources if s != "corpus" or retriever is not None]

    def _one(self, source: str, query: str, n: int) -> list:
        f = self.fetcher
        if source == "corpus":
            return corpus_papers(self.retriever, query, n)
        if f is None:
            raise IngestError("no network fetcher configured")
        if source == "openalex":
            key_params = getattr(f, "_openalex_params", lambda: None)() or {}   # API key + contact e-mail, if set
            params = dict(key_params, search=query, per_page=n)
            r = f._get("https://api.openalex.org/works", params)
            return parse_openalex(r.json()) if r is not None else []
        if source == "s2":
            r = f._get("https://api.semanticscholar.org/graph/v1/paper/search",
                       {"query": query, "limit": n, "fields": "title,abstract,year,venue,externalIds,url"})
            return parse_s2(r.json()) if r is not None else []
        if source == "arxiv":
            terms = query.split()[:6]
            r = f._get("http://export.arxiv.org/api/query",
                       {"search_query": " AND ".join(f"all:{t}" for t in terms), "max_results": n})
            return parse_arxiv(r.text) if r is not None else []
        raise ValueError(f"unknown source '{source}'")

    def search(self, text: str, n: Optional[int] = None) -> SearchResult:
        n = n or self.per_source
        query = build_query(text) or (text or "").strip()[:200]
        res = SearchResult(query=query)
        found = []
        for s in self.sources:
            try:
                found += [Candidate(p, [s]) for p in self._one(s, query, n)]
            except Exception as e:  # one source failing (rate limit, outage) must not stop the others
                res.errors[s] = f"{type(e).__name__}: {str(e)[:160]}"
        res.candidates = merge(found)
        return res

    def as_tool(self) -> Callable:
        """The callable the agent uses for replacement search: (text, n) -> list[Paper]."""
        return lambda text, n: [c.paper for c in self.search(text, n).candidates]


# ----------------------------------------------------------------------------------------------
# Ranking and explanation
# ----------------------------------------------------------------------------------------------
def explain(direction: str, paper: Paper, scorer=None) -> str:
    """The abstract sentence that best matches the direction (the 'why should I read this')."""
    sents = split_sentences(paper.abstract)
    if not sents:
        return ""
    scores = (scorer or LexicalSentenceScorer()).score(direction, sents)
    best = max(range(len(sents)), key=lambda i: (scores[i], -i))
    return sents[best] if scores[best] > 0 else ""


def rank(direction: str, candidates: Sequence, relevance: Optional[RelevanceScorer] = None, k: int = 10) -> list:
    relevance = relevance or RelevanceScorer()
    for c in candidates:
        r = relevance.score(direction, c.paper)
        boost = 0.02 * (len(c.sources) - 1)  # found by several sources: a small, transparent tie-breaker
        c.score, c.band, c.matched_terms = min(1.0, r.score + boost), r.band, r.matched_terms
        c.key_sentence = explain(direction, c.paper)
    return sorted(candidates, key=lambda c: (-c.score, -(c.paper.year or 0), c.paper.title))[:k]


def discover(direction: str, search: PaperSearch, k: int = 10, relevance: Optional[RelevanceScorer] = None) -> DiscoveryReport:
    if not (direction or "").strip():
        raise ValueError("Describe your research direction first (one or two sentences).")
    res = search.search(direction, max(k, search.per_source))
    return DiscoveryReport(direction=direction.strip(), query=res.query,
                           results=rank(direction, res.candidates, relevance, k), errors=res.errors)
