"""Turn a reference-list entry into an identifier we can fetch (DOI or arXiv id).   Owner: Engineering.

  1. The entry already contains a DOI or an arXiv id: use it.
  2. Otherwise ask Crossref's bibliographic search (free; a contact e-mail puts us in the faster "polite pool") and
     accept its top match ONLY if most words of the returned title appear in the entry.  A wrong match would make us
     judge the claim against the wrong paper, which is worse than saying "reference not found".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .ingest import parse_identifier
from .text_utils import tokenize

CROSSREF = "https://api.crossref.org/works"
MIN_TITLE_OVERLAP = 0.7


@dataclass
class Resolution:
    identifier: Optional[str]   # "10.xxxx/..." or "arXiv:NNNN.NNNNN", None when not resolved
    method: str                 # in_reference | crossref | none
    detail: str = ""


def title_overlap(title: str, entry: str) -> float:
    """Share of the title's content words that appear in the reference entry (0..1)."""
    t = set(tokenize(title or ""))
    if not t:
        return 0.0
    return len(t & set(tokenize(entry or ""))) / len(t)


class ReferenceResolver:
    def __init__(self, fetcher=None, use_crossref: bool = True, min_overlap: float = MIN_TITLE_OVERLAP):
        self.fetcher, self.use_crossref, self.min_overlap = fetcher, use_crossref, min_overlap
        self._cache = {}

    def resolve(self, entry_text: str) -> Resolution:
        entry_text = (entry_text or "").strip()
        if not entry_text:
            return Resolution(None, "none", "empty reference entry")
        pid = parse_identifier(entry_text)
        if pid is not None and pid.kind in ("doi", "arxiv"):
            ident = pid.value if pid.kind == "doi" else f"arXiv:{pid.value}"
            return Resolution(ident, "in_reference", f"identifier written in the reference: {ident}")
        if not (self.use_crossref and self.fetcher is not None):
            return Resolution(None, "none", "no DOI or arXiv id in the reference, and Crossref lookup is off")
        if entry_text in self._cache:
            return self._cache[entry_text]
        params = {"query.bibliographic": entry_text[:400], "rows": 3}
        if getattr(self.fetcher, "mailto", None):
            params["mailto"] = self.fetcher.mailto
        try:
            r = self.fetcher._get(CROSSREF, params)
            items = (((r.json() if r is not None else {}) or {}).get("message") or {}).get("items") or []
        except Exception as e:
            res = Resolution(None, "none", f"Crossref did not answer ({type(e).__name__})")
            return res  # not cached: a transient failure may succeed later
        best, best_ov = None, 0.0
        for it in items:
            title = " ".join(it.get("title") or [])
            ov = title_overlap(title, entry_text)
            if ov > best_ov:
                best, best_ov = it, ov
        if best is not None and best.get("DOI") and best_ov >= self.min_overlap:
            doi = best["DOI"].lower()
            res = Resolution(doi, "crossref", f"Crossref match {doi} (title overlap {best_ov:.2f})")
        else:
            res = Resolution(None, "none", "no Crossref match whose title matches the reference"
                             + (f" (best overlap {best_ov:.2f})" if items else ""))
        self._cache[entry_text] = res
        return res
