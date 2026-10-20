"""Find every cited claim in a draft and link it to its reference entry.   Owner: Engineering.

Input: plain text (pasted, or extracted from a text-based PDF), optionally ending with a reference list.
Output: one CitedClaim per sentence that carries a citation, with the reference entries it points to.

Citation styles handled (rule-based; covers the common cases, not every style guide):
  numeric      ... reduces infection [3].   [3, 5]   [4-6]   [4–6]
  author-year  ... reduces infection (Smith et al., 2019; Lee and Park, 2020).   Smith et al. (2019) showed ...
  inline id    ... (doi:10.1038/nature14539)   arXiv:2004.14974
Reference list: everything after a heading line "References", "Bibliography", "Works cited" or "Literature cited".
Entries: "[1] ...", "1. ...", "1) ..." (numeric), or one entry per line / paragraph (author-year).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .ingest import clean_context, parse_identifier
from .text_utils import split_sentences

REF_HEADING = re.compile(r"^\s*(?:\d+\.?\s*)?(references|bibliography|works cited|literature cited|reference list)\s*:?\s*$",
                         re.I | re.M)
NUMERIC = re.compile(r"\[\s*(\d+(?:\s*[,–—-]\s*\d+)*)\s*\]")
PAREN = re.compile(r"\(([^()]*?\b(?:19|20)\d{2}[a-z]?\b[^()]*)\)")
NARRATIVE = re.compile(r"\b([A-Z][A-Za-z\-'’]+)(?:\s+et\s+al\.?|\s+(?:and|&)\s+[A-Z][A-Za-z\-'’]+)?\s+\(((?:19|20)\d{2}[a-z]?)\)")
YEAR = re.compile(r"\b((?:19|20)\d{2})[a-z]?\b")
NUM_ENTRY = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.)])\s+(.*)$")
MAX_RANGE = 30


@dataclass
class RefEntry:
    key: str            # "3" for numeric entries, "smith2019" for author-year entries
    text: str


@dataclass
class CitedClaim:
    index: int           # 1-based position among cited sentences
    sentence: str        # the sentence as written
    claim: str           # the sentence with citation markers removed: what we verify
    markers: list = field(default_factory=list)       # the markers as written, e.g. ["[3]", "(Smith et al., 2019)"]
    keys: list = field(default_factory=list)          # reference keys they point to, in order
    inline_ids: list = field(default_factory=list)    # DOIs / arXiv ids written in the sentence itself


@dataclass
class DraftParse:
    claims: list
    references: dict     # key -> RefEntry
    style: str           # numeric | author-year | mixed | none
    warnings: list = field(default_factory=list)

    def entry(self, key: str) -> Optional[RefEntry]:
        return self.references.get(key)


def _surname_key(surname: str, year: str) -> str:
    return re.sub(r"[^a-z]", "", surname.lower()) + year


def split_body_and_references(text: str):
    """(body, reference_block).  The LAST matching heading wins (a paper may mention 'references' earlier)."""
    matches = list(REF_HEADING.finditer(text or ""))
    if not matches:
        return text or "", ""
    m = matches[-1]
    return text[: m.start()], text[m.end():]


def parse_reference_list(block: str) -> dict:
    """key -> RefEntry.  Numeric entries keyed by number; others by first-author surname + year."""
    lines = [l.rstrip() for l in (block or "").splitlines()]
    refs, current = {}, None
    numbered = any(NUM_ENTRY.match(l) for l in lines)
    entries = []
    for l in lines:
        if not l.strip():
            current = None if not numbered else current
            continue
        m = NUM_ENTRY.match(l) if numbered else None
        if m:
            current = [m.group(1) or m.group(2), m.group(3).strip()]
            entries.append(current)
        elif current is not None and (numbered or l[:1].isspace() or l[:1].islower()):
            current[1] += " " + l.strip()          # continuation line
        elif not numbered:
            current = [None, l.strip()]
            entries.append(current)
    for num, txt in entries:
        if num is not None:
            refs[num] = RefEntry(num, txt)
            continue
        first = re.match(r"\s*([A-Z][A-Za-z\-'’]+)", txt)
        year = YEAR.search(txt)
        if first and year:
            key = _surname_key(first.group(1), year.group(1))
            while key in refs:                     # Smith 2019a / 2019b: keep both, suffix the second
                key += "+"
            refs[key] = RefEntry(key, txt)
    return refs


def _expand_numeric(group: str) -> list:
    keys = []
    for part in re.split(r"\s*,\s*", group):
        rng = re.split(r"\s*[–—-]\s*", part)
        if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit():
            a, b = int(rng[0]), int(rng[1])
            if a <= b and b - a <= MAX_RANGE:
                keys += [str(i) for i in range(a, b + 1)]
                continue
        if part.isdigit():
            keys.append(part)
    return keys


def _author_year_keys(inner: str) -> list:
    keys = []
    for part in inner.split(";"):
        y = YEAR.search(part)
        s = re.search(r"([A-Z][A-Za-z\-'’]+)", part)
        if y and s:
            keys.append(_surname_key(s.group(1), y.group(1)))
    return keys


def find_markers(sentence: str):
    """(markers as written, reference keys, inline identifiers)."""
    markers, keys, ids = [], [], []
    for m in NUMERIC.finditer(sentence):
        markers.append(m.group(0))
        keys += _expand_numeric(m.group(1))
    for m in PAREN.finditer(sentence):
        inner = m.group(1)
        if re.search(r"\bdoi\b|10\.\d{4,9}/|arxiv", inner, re.I):
            continue                                   # handled as an inline identifier below
        k = _author_year_keys(inner)
        if k:
            markers.append(m.group(0))
            keys += k
    for m in NARRATIVE.finditer(sentence):
        markers.append(m.group(0))
        keys.append(_surname_key(m.group(1), m.group(2)[:4]))
    for chunk in re.findall(r"(?:doi:?\s*)?10\.\d{4,9}/[^\s\"<>)\]]+|arXiv:\s*\d{4}\.\d{4,5}(?:v\d+)?", sentence, re.I):
        pid = parse_identifier(chunk.replace(" ", ""))
        if pid:
            markers.append(chunk)
            ids.append(f"{pid.kind}:{pid.value}" if pid.kind != "doi" else pid.value)
    seen = set()
    keys = [k for k in keys if not (k in seen or seen.add(k))]
    return markers, keys, ids


def _strip_markers(sentence: str, markers: list) -> str:
    s = sentence
    for m in markers:
        if NARRATIVE.fullmatch(m):
            s = s.replace(m, re.sub(r"\s*\((?:19|20)\d{2}[a-z]?\)", "", m))
        else:
            s = s.replace(m, "")
    s = re.sub(r"\(\s*(?:doi:?)?\s*\)", "", s, flags=re.I)
    return clean_context(s)


def resolve_key(key: str, refs: dict) -> Optional[str]:
    """Exact key, else the same surname+year with a/b suffix variants."""
    if key in refs:
        return key
    for k in refs:
        if k.rstrip("+") == key:
            return k
    return None


def parse_draft(text: str, max_claims: int = 200) -> DraftParse:
    body, ref_block = split_body_and_references(text or "")
    refs = parse_reference_list(ref_block)
    warnings, claims = [], []
    numeric_seen = author_seen = False
    for sent in split_sentences(body):
        markers, keys, ids = find_markers(sent)
        if not markers:
            continue
        numeric_seen |= any(k.isdigit() for k in keys)
        author_seen |= any(not k.isdigit() for k in keys)
        resolved = [resolve_key(k, refs) or k for k in keys]
        claim = _strip_markers(sent, markers)
        if len(claim.split()) < 3:
            warnings.append(f"Skipped a citation with too little text to check: “{sent[:80]}”")
            continue
        claims.append(CitedClaim(len(claims) + 1, sent, claim, markers, resolved, ids))
        if len(claims) >= max_claims:
            warnings.append(f"Only the first {max_claims} cited sentences were read.")
            break
    if claims and not refs and not all(c.inline_ids for c in claims):
        warnings.append("No reference list found (add a 'References' heading followed by the entries), so citations "
                        "can only be checked when the sentence itself contains a DOI or arXiv id.")
    style = "mixed" if numeric_seen and author_seen else "numeric" if numeric_seen else "author-year" if author_seen else "none"
    return DraftParse(claims, refs, style, warnings)
