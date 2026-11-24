"""Turn a reference-list entry into an identifier we can fetch (DOI or arXiv id).   Owner: Engineering.

  1. The entry already contains a DOI or an arXiv id: use it.
  2. Otherwise ask Crossref's bibliographic search (free; a contact e-mail puts us in the faster "polite pool") and
     accept a match ONLY if most words of the returned title appear in the entry AND, when the entry gives them, one
     of the paper's first authors is named in the entry and its year is within YEAR_TOLERANCE of the entry's year.
     A wrong match would make us judge the claim against the wrong paper, which is worse than saying "reference not
     found": a title check alone matched "StackGuard ... Buffer-Overflow Attacks (Cowan et al., 1998)" to an
     unrelated 2007 paper whose short title's words all appear in that entry.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from .ingest import parse_identifier
from .text_utils import tokenize

CROSSREF = "https://api.crossref.org/works"
MIN_TITLE_OVERLAP = 0.7
YEAR_TOLERANCE = 1          # a preprint or online-first version is often dated a year before the printed one
AUTHORS_CHECKED = 5         # one of the paper's first authors must be named in the entry
CANDIDATES = 5              # Crossref results examined; the best one that passes every check is used
YEAR = re.compile(r"(?<![\d./-])((?:19|20)\d{2})(?![\d/])")
URLISH = re.compile(r"(?:https?://|doi:|10\.\d{4,9}/)\S+", re.I)


@dataclass
class Resolution:
    identifier: Optional[str]   # "10.xxxx/..." or "arXiv:NNNN.NNNNN", None when not resolved
    method: str                 # in_reference | crossref | none
    detail: str = ""


def _plain(text: str) -> str:
    """Lower case without accents: "Müller" and "Muller" compare equal."""
    text = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in text if not unicodedata.combining(ch)).lower()


def entry_years(entry: str) -> set:
    """The years written in a reference entry (not the digits inside a URL or DOI)."""
    return {int(y) for y in YEAR.findall(URLISH.sub(" ", entry or ""))}


def item_years(item: dict) -> set:
    """Every year Crossref gives for a record: issued, online, print and created dates can differ by a year."""
    years = set()
    for k in ("issued", "published", "published-online", "published-print", "created"):
        for part in ((item.get(k) or {}).get("date-parts") or []):
            if part and isinstance(part[0], int):
                years.add(part[0])
    return years


def item_surnames(item: dict) -> list:
    """Family names of the record's first authors, as written (an organisation's name when there is no family name)."""
    out = []
    for a in (item.get("author") or [])[:AUTHORS_CHECKED]:
        name = (a.get("family") or a.get("name") or "").strip()
        if name:
            out.append(name)
    return out


def author_named(surnames: list, entry: str) -> bool:
    """True when one of the surnames appears as a word in the entry ("van der Berg": its longest part is enough)."""
    words = set(re.findall(r"[a-z]+", _plain(entry)))
    for name in surnames:
        parts = re.findall(r"[a-z]+", _plain(name))
        if parts and max(parts, key=len) in words and len(max(parts, key=len)) >= 2:
            return True
    return False


def check_match(item: dict, entry: str):
    """(ok, why) for a Crossref record against the reference entry.  Each check runs only when both sides give the
    information: an entry without a year is not checked on the year, a record without authors not on authors."""
    years, ref_years = item_years(item), entry_years(entry)
    surnames = item_surnames(item)
    first = surnames[0] if surnames else ""
    year = min(years) if years else None
    year_checked, author_checked = bool(years and ref_years), bool(surnames)
    if year_checked and not any(abs(a - b) <= YEAR_TOLERANCE for a in years for b in ref_years):
        return False, (f"its year ({year}) does not match the reference "
                       f"({', '.join(str(y) for y in sorted(ref_years))})")
    if author_checked and not author_named(surnames, entry):
        return False, f"its first author ({first}) is not named in the reference"
    agreed = ([f"first author {first}"] if author_checked else []) + ([f"year {year}"] if year_checked else [])
    if not agreed:
        return True, "no author or year to compare"
    return True, " and ".join(agreed) + (" match" if len(agreed) > 1 else " matches") + " the reference"


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
        params = {"query.bibliographic": entry_text[:400], "rows": CANDIDATES}
        if getattr(self.fetcher, "mailto", None):
            params["mailto"] = self.fetcher.mailto
        try:
            r = self.fetcher._get(CROSSREF, params)
            items = (((r.json() if r is not None else {}) or {}).get("message") or {}).get("items") or []
        except Exception as e:
            res = Resolution(None, "none", f"Crossref did not answer ({type(e).__name__})")
            return res  # not cached: a transient failure may succeed later
        scored = sorted(((title_overlap(" ".join(it.get("title") or []), entry_text), n, it)
                         for n, it in enumerate(items) if it.get("DOI")), key=lambda t: (-t[0], t[1]))
        best_ov = scored[0][0] if scored else 0.0
        rejected = []
        res = None
        for ov, _, it in scored:
            if ov < self.min_overlap:
                break
            ok, why = check_match(it, entry_text)
            doi = it["DOI"].lower()
            if ok:
                res = Resolution(doi, "crossref", f"Crossref match {doi} (title overlap {ov:.2f}; {why})")
                break
            rejected.append(f"{doi}: {why}")
        if res is None and rejected:
            res = Resolution(None, "none", "Crossref's closest match is a different paper, so it was not used ("
                             + "; ".join(rejected[:2]) + ")")
        elif res is None:
            res = Resolution(None, "none", "no Crossref match whose title matches the reference"
                             + (f" (best overlap {best_ov:.2f})" if items else ""))
        self._cache[entry_text] = res
        return res
