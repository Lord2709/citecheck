"""The CiteCheck agent.   Owner: Engineering.   Plan and diagrams: docs/agent_plan.md, Part 1.

    researcher input -> planner -> discovery path (research direction)  or  verification path (draft with citations)

Verification, per cited claim:
    extract claim + reference -> resolve to DOI/arXiv -> fetch the paper -> verify on the abstract
      -> unsure (abstained below tau)?  read the open-access full text, verify again          [decision 1]
      -> verdict below tau stays NOT ENOUGH EVIDENCE                                           [decision 2]
      -> contradicted or not enough evidence?  search for a replacement paper                  [decision 3]
      -> suggest a candidate only if it SUPPORTS with p >= tau_strict and no evidence contradicts [decision 4]
Every decision is written to the citation's `steps`, so the report shows why the agent did what it did.

The verdicts come from the SAME pipeline the app's single-claim check uses (src/pipeline.py), i.e. the evaluated
model.  The agent-level behaviour (escalation, suggestions) is NOT yet evaluated end to end; tau_strict is a placeholder
until the calibration work (docs/agent_plan.md, Part 2) tunes it on the calibration part of train.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Callable, Optional, Sequence

from .claims import parse_draft
from .evidence import LexicalSentenceScorer
from .ingest import IngestError
from .schema import CONTRADICT, NEI, SUPPORT, Doc, Paper

CHUNK_SENTENCES = 5          # full text is judged in passages of this many sentences
MAX_CHUNKS = 8               # ...the best-matching passages only (cost: one verifier call per passage)
DISCOVER_MAX_WORDS = 80      # input with no citation markers and at most this many words -> discovery


def default_tau_strict(tau: float) -> float:
    """PLACEHOLDER until tuned on the calibration part: clearly stricter than tau."""
    return round(min(0.95, max(0.85, tau + 0.2)), 2)


@dataclass
class Step:
    action: str
    detail: str
    ms: float = 0.0


@dataclass
class Suggestion:
    paper: Paper
    confidence: float
    sentences: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"paper": _paper_dict(self.paper), "confidence": round(self.confidence, 4), "sentences": list(self.sentences)}


@dataclass
class CitationResult:
    index: int
    sentence: str
    claim: str
    marker: str
    reference_text: str = ""
    identifier: Optional[str] = None
    status: str = "checked"          # checked | unresolved | not_found | no_abstract | error
    status_detail: str = ""
    paper: Optional[Paper] = None
    verdict: object = None           # src.schema.Verdict
    read_full_text: bool = False
    full_text_source: str = ""
    suggestions: list = field(default_factory=list)
    steps: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index": self.index, "sentence": self.sentence, "claim": self.claim, "marker": self.marker,
            "reference_text": self.reference_text, "identifier": self.identifier, "status": self.status,
            "status_detail": self.status_detail, "paper": _paper_dict(self.paper) if self.paper else None,
            "verdict": _verdict_dict(self.verdict) if self.verdict is not None else None,
            "read_full_text": self.read_full_text, "full_text_source": self.full_text_source,
            "suggestions": [s.to_dict() for s in self.suggestions], "steps": [asdict(s) for s in self.steps],
        }


@dataclass
class AgentReport:
    citations: list
    warnings: list
    backend: dict
    tau_strict: float
    style: str = "none"
    created_at: str = ""

    def to_dict(self) -> dict:
        return {"kind": "draft_check", "citations": [c.to_dict() for c in self.citations], "warnings": list(self.warnings),
                "backend": dict(self.backend), "tau_strict": self.tau_strict, "citation_style": self.style,
                "created_at": self.created_at}


@dataclass
class Plan:
    kind: str      # verify_draft | discover
    reason: str


def _paper_dict(p: Paper) -> dict:
    return {"paper_id": p.paper_id, "title": p.title, "year": p.year, "venue": p.venue, "doi": p.doi, "url": p.url,
            "source": p.source}


def _verdict_dict(v) -> dict:
    return {"label": v.label, "display_label": v.display_label, "confidence": round(v.confidence, 4),
            "abstained": v.abstained, "note": v.note,
            "evidence": [{"title": e.title, "sentences": list(e.sentences), "probs": e.probs.as_dict()} for e in v.evidence]}


def _same_paper(a: Paper, b: Paper) -> bool:
    if a.doi and b.doi:
        return a.doi.lower() == b.doi.lower()
    norm = lambda t: re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()  # noqa: E731
    return a.paper_id == b.paper_id or (bool(norm(a.title)) and norm(a.title) == norm(b.title))


def marker_text(cited_claim, key: str) -> str:
    """How the citation was written, for display: "[3]", or "(Smith et al., 2019)" for an author-year key."""
    if key.isdigit():
        return f"[{key}]"
    base = key.rstrip("+")
    m = re.match(r"([a-z]+)(\d{4})", base)
    if m:
        for mk in cited_claim.markers:
            if m.group(1) in re.sub(r"[^a-z]", "", mk.lower()) and m.group(2) in mk:
                return mk.strip()
    return base


def stub_paper(identifier: str, detail: str = "") -> Paper:
    """A paper we know only by its identifier (and the title the lookup reported), for the full-text route."""
    m = re.search(r"“(.+?)”", detail or "")
    title = m.group(1) if m else identifier
    if identifier.lower().startswith("arxiv:"):
        aid = identifier.split(":", 1)[1]
        return Paper(paper_id=f"arxiv:{aid}", title=title, url=f"https://arxiv.org/abs/{aid}", source="arxiv")
    doi = identifier.lower() if identifier.startswith("10.") else None
    return Paper(paper_id=f"doi:{doi}" if doi else identifier, title=title, doi=doi,
                 url=f"https://doi.org/{doi}" if doi else None, source="fulltext")


def chunk(sentences: Sequence, size: int = CHUNK_SENTENCES) -> list:
    return [list(sentences[i:i + size]) for i in range(0, len(sentences), size)]


def corpus_search(retriever) -> Callable:
    """Replacement search over the local SciFact corpus (offline; used by eval/agent_eval.py)."""
    def search(text: str, n: int) -> list:
        return [Paper(paper_id=f"scifact:{h.doc.doc_id}", title=h.doc.title, abstract=h.doc.abstract, url=h.doc.url,
                      source="scifact") for h in retriever.search(text, n)]
    return search


class CiteCheckAgent:
    def __init__(self, pipeline, fetcher=None, resolver=None, fulltext=None, search: Optional[Callable] = None,
                 discovery=None, tau_strict: Optional[float] = None, escalate: bool = True, suggest: bool = True,
                 max_candidates: int = 5, max_suggestions: int = 2, clock=time.perf_counter):
        self.pipe, self.fetcher, self.resolver, self.fulltext = pipeline, fetcher, resolver, fulltext
        self.search, self.discovery = search, discovery
        self.tau_strict = tau_strict if tau_strict is not None else default_tau_strict(pipeline.tau)
        self.escalate, self.suggest = escalate, suggest
        self.max_candidates, self.max_suggestions = max_candidates, max_suggestions
        self.clock = clock
        self.scorer = LexicalSentenceScorer()

    # ---- planner ---------------------------------------------------------------------------
    def plan(self, text: str) -> Plan:
        text = (text or "").strip()
        if not text:
            raise ValueError("Paste a research direction or a draft with citations.")
        parsed = parse_draft(text)
        if parsed.claims:
            return Plan("verify_draft", f"found {len(parsed.claims)} cited sentence(s) ({parsed.style} citations)")
        if len(text.split()) <= DISCOVER_MAX_WORDS:
            return Plan("discover", "no citations found and the text is short: treated as a research direction")
        return Plan("verify_draft", "no citation markers found; nothing to check (add [1] or (Author, year) markers)")

    # ---- one claim against one paper ---------------------------------------------------------
    def _timed(self, steps, action, fn):
        t0 = self.clock()
        out, detail = fn()
        steps.append(Step(action, detail, round(1000 * (self.clock() - t0), 1)))
        return out

    def _verify_full_text(self, claim: str, paper: Paper, sentences: Sequence):
        parts = chunk(sentences)
        if len(parts) > MAX_CHUNKS:
            scores = [max(self.scorer.score(claim, p) or [0.0]) for p in parts]
            keep = sorted(sorted(range(len(parts)), key=lambda i: -scores[i])[:MAX_CHUNKS])
            parts = [parts[i] for i in keep]
        docs = [Doc(doc_id=f"{paper.paper_id}#ft{i}", title=f"{paper.title} (full text)", sentences=tuple(p),
                    url=paper.url, source="fulltext") for i, p in enumerate(parts)]
        return self.pipe.verify_claim(claim, docs=docs)

    def check_claim(self, claim: str, paper: Paper, draft_year: Optional[int] = None, steps: Optional[list] = None):
        """Returns (verdict, read_full_text, full_text_source, suggestions, steps)."""
        steps = steps if steps is not None else []
        v = self._timed(steps, "verify abstract", lambda: (
            (r := self.pipe.verify_against_paper(claim, paper)),
            f"{r.display_label} (p={r.confidence:.2f}, tau={self.pipe.tau:.2f})"))
        read_ft, ft_source = False, ""
        if v.label == NEI and v.abstained:
            if not self.escalate or self.fulltext is None:
                steps.append(Step("read full text?", "unsure on the abstract, but full-text reading is off", 0.0))
            else:
                ft = self._timed(steps, "find open-access full text", lambda: (
                    (f := self.fulltext.find(paper)), self.fulltext.last_detail if f is None else f"found: {self.fulltext.last_detail}"))
                if ft is not None and ft.sentences:
                    v2 = self._timed(steps, "verify full text", lambda: (
                        (r := self._verify_full_text(claim, paper, ft.sentences)),
                        f"{r.display_label} (p={r.confidence:.2f}) from {ft.source}"))
                    v, read_ft, ft_source = v2, True, ft.source
        else:
            steps.append(Step("read full text?", f"not needed: confident on the abstract ({v.display_label})", 0.0))

        suggestions = []
        if v.label != SUPPORT and self.suggest and self.search is not None:
            suggestions = self._suggest(claim, paper, draft_year, steps)
        elif v.label != SUPPORT:
            steps.append(Step("look for a replacement?", "replacement search is off", 0.0))
        return v, read_ft, ft_source, suggestions, steps

    def _suggest(self, claim, failed: Paper, draft_year, steps) -> list:
        def run():
            try:
                found = list(self.search(claim, self.max_candidates + 3))
            except Exception as e:
                return [], f"search failed ({type(e).__name__})"
            pool = [p for p in found if p.abstract.strip() and not _same_paper(p, failed)
                    and not (draft_year and p.year and p.year > draft_year)][: self.max_candidates]
            out = []
            for p in pool:
                try:
                    cv = self.pipe.verify_against_paper(claim, p)
                except ValueError:
                    continue
                contradicts = any(e.probs.contradict >= self.pipe.tau for e in cv.evidence)
                if cv.label == SUPPORT and cv.confidence >= self.tau_strict and not contradicts:
                    out.append(Suggestion(p, cv.confidence, list(cv.evidence[0].sentences) if cv.evidence else []))
            out.sort(key=lambda s: -s.confidence)
            out = out[: self.max_suggestions]
            return out, (f"checked {len(pool)} candidate(s); {len(out)} support the claim with p >= {self.tau_strict:.2f}"
                         if pool else "no candidate papers with an abstract found")
        return self._timed(steps, "search for a replacement", run)

    # ---- a whole draft ------------------------------------------------------------------------
    def _fetch(self, identifier: str, cache: dict):
        if identifier in cache:
            return cache[identifier]
        try:
            paper = self.fetcher.fetch_paper(identifier)
            res = (paper, "checked", "")
        except IngestError as e:
            msg = str(e)
            res = (None, "no_abstract" if "abstract" in msg.lower() else "not_found", msg)
        except Exception as e:
            res = (None, "error", f"{type(e).__name__}: {str(e)[:120]}")
        cache[identifier] = res
        return res

    def check_draft(self, text: str, draft_year: Optional[int] = None, max_citations: int = 20,
                    progress: Optional[Callable] = None, on_result: Optional[Callable] = None) -> AgentReport:
        """progress(n, total) is called before each citation; on_result(CitationResult) after each one is finished
        (the web API uses it to stream results while the rest are still being checked)."""
        parsed = parse_draft(text)
        warnings = list(parsed.warnings)
        pairs = []  # (cited claim, marker, reference key or inline id, is_inline)
        for c in parsed.claims:
            for ident in c.inline_ids:
                pairs.append((c, ident, ident, True))
            for k in c.keys:
                pairs.append((c, marker_text(c, k), k, False))
        if not pairs:
            warnings.append("No citations found. Mark citations as [1] or (Author, year) and add a 'References' list.")
        if len(pairs) > max_citations:
            warnings.append(f"Checked the first {max_citations} of {len(pairs)} citations.")
            pairs = pairs[:max_citations]
        results, cache = [], {}

        def finish(r):
            results.append(r)
            if on_result:
                on_result(r)
        for n, (c, marker, key, inline) in enumerate(pairs, 1):
            if progress:
                progress(n, len(pairs))
            r = CitationResult(index=n, sentence=c.sentence, claim=c.claim, marker=marker)
            if inline:
                r.identifier = key
                r.steps.append(Step("resolve reference", f"identifier written in the sentence: {key}", 0.0))
            else:
                entry = parsed.entry(key)
                if entry is None:
                    r.status, r.status_detail = "unresolved", f"no entry for {marker} in the reference list"
                    r.steps.append(Step("resolve reference", r.status_detail, 0.0))
                    finish(r)
                    continue
                r.reference_text = entry.text
                if self.resolver is None:
                    r.status, r.status_detail = "unresolved", "reference resolution is not configured"
                    finish(r)
                    continue
                res = self._timed(r.steps, "resolve reference", lambda: ((x := self.resolver.resolve(entry.text)), x.detail))
                r.identifier = res.identifier
                if res.identifier is None:
                    r.status, r.status_detail = "unresolved", res.detail
                    finish(r)
                    continue
            if self.fetcher is None:
                r.status, r.status_detail = "not_found", "paper lookup is not configured"
                finish(r)
                continue
            paper, status, detail = self._timed(r.steps, "fetch paper", lambda: (
                (x := self._fetch(r.identifier, cache)), (x[0].title[:90] if x[0] else x[2])))
            r.paper, r.status, r.status_detail = paper, status, detail
            if paper is None and status == "no_abstract":
                self._check_without_abstract(r, c.claim, draft_year)   # try the open-access full text instead
            if r.paper is None or r.status != "checked":
                finish(r)
                continue
            if r.verdict is not None:                                  # already decided from the full text
                finish(r)
                continue
            try:
                v, read_ft, ft_src, sugg, _ = self.check_claim(c.claim, paper, draft_year, r.steps)
                r.verdict, r.read_full_text, r.full_text_source, r.suggestions = v, read_ft, ft_src, sugg
            except Exception as e:
                r.status, r.status_detail = "error", f"{type(e).__name__}: {str(e)[:120]}"
            finish(r)
        return AgentReport(results, warnings, dict(self.pipe.meta), self.tau_strict, parsed.style,
                           datetime.now().astimezone().isoformat(timespec="seconds"))

    def _check_without_abstract(self, r: "CitationResult", claim: str, draft_year: Optional[int]):
        """The paper exists but no open source gives its abstract (seen live: a Nature paper).  If full-text reading is
        on, look for a legal open-access copy and judge the claim on it; otherwise leave the citation unchecked."""
        if not (self.escalate and self.fulltext is not None and r.identifier):
            r.steps.append(Step("read full text?", "no abstract available and full-text reading is off", 0.0))
            return
        stub = stub_paper(r.identifier, r.status_detail)
        ft = self._timed(r.steps, "find open-access full text", lambda: (
            (f := self.fulltext.find(stub)), self.fulltext.last_detail if f is None else f"found: {self.fulltext.last_detail}"))
        if ft is None or not ft.sentences:
            r.status_detail += " No open-access full text was found either."
            return
        try:
            v = self._timed(r.steps, "verify full text", lambda: (
                (x := self._verify_full_text(claim, stub, ft.sentences)), f"{x.display_label} (p={x.confidence:.2f}) from {ft.source}"))
        except Exception as e:
            r.status, r.status_detail = "error", f"{type(e).__name__}: {str(e)[:120]}"
            return
        r.paper, r.status, r.status_detail = stub, "checked", ""
        r.verdict, r.read_full_text, r.full_text_source = v, True, ft.source
        if v.label != SUPPORT and self.suggest and self.search is not None:
            r.suggestions = self._suggest(claim, stub, draft_year, r.steps)

    def recheck_with_abstract(self, citation: dict, title: str, abstract: str, draft_year: Optional[int] = None) -> dict:
        """The researcher pasted the abstract for a citation we could not check.  Returns the updated citation dict
        (same shape as CitationResult.to_dict()), marked as checked against a pasted abstract."""
        from .ingest import paper_from_text

        title = (title or (citation.get("paper") or {}).get("title")
                 or stub_paper(citation.get("identifier") or "", citation.get("status_detail", "")).title or "Pasted abstract")
        paper = paper_from_text(title, abstract)
        steps = [Step(**s) for s in citation.get("steps") or []]
        steps.append(Step("abstract pasted", "the researcher pasted the abstract for this citation", 0.0))
        v, read_ft, ft_src, sugg, steps = self.check_claim(citation["claim"], paper, draft_year, steps)
        r = CitationResult(index=citation["index"], sentence=citation["sentence"], claim=citation["claim"],
                           marker=citation["marker"], reference_text=citation.get("reference_text", ""),
                           identifier=citation.get("identifier"), status="checked", paper=paper, verdict=v,
                           read_full_text=read_ft, full_text_source=ft_src, suggestions=sugg, steps=steps)
        d = r.to_dict()
        d["abstract_pasted"] = True
        return d

    # ---- discovery ------------------------------------------------------------------------------
    def discover(self, direction: str, k: int = 10):
        if self.discovery is None:
            raise ValueError("Paper search is not configured.")
        from .discovery import discover

        return discover(direction, self.discovery, k=k)


def build_agent(pipeline, fetcher, sources: Optional[Sequence] = None) -> CiteCheckAgent:
    """The agent as the app runs it.  CITECHECK_SEARCH_SOURCES=openalex,s2,arxiv,corpus picks the search sources."""
    from .discovery import PaperSearch
    from .fulltext import FullTextFinder
    from .resolve import ReferenceResolver

    if sources is None:
        sources = [s.strip() for s in os.environ.get("CITECHECK_SEARCH_SOURCES", "openalex,s2,arxiv").split(",") if s.strip()]
    search = PaperSearch(fetcher, sources=sources, retriever=pipeline.retriever if "corpus" in sources else None)
    return CiteCheckAgent(pipeline, fetcher=fetcher, resolver=ReferenceResolver(fetcher),
                          fulltext=FullTextFinder(fetcher), search=search.as_tool(), discovery=search)
