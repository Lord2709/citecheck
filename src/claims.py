"""Find every cited claim in a draft and link it to its reference entry.   Owner: Engineering.

Input: plain text (pasted, or extracted from a text-based PDF), optionally ending with a reference list.
Output: one CitedClaim per sentence that carries a citation, with the reference entries it points to.

Citation styles handled (rule-based; covers the common cases, not every style guide):
  numeric      ... reduces infection [3].   [3, 5]   [4-6]   [4–6]
  author-year  ... reduces infection (Smith et al., 2019; Lee and Park, 2020).   Smith et al. (2019) showed ...
  inline id    ... (doi:10.1038/nature14539)   arXiv:2004.14974
Reference list: everything after a heading line "References", "Bibliography", "Works cited" or "Literature cited";
without a heading, a run of lines at the end of the text that look like reference entries; or the website's separate
reference-list box (`join_references`).
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
# Superscript citations ("…mortality risk3,12." in Nature-style papers) lose their formatting when text is copied or
# read from a PDF: the numbers end up glued to the word or punctuation before them.  Only a lower-case letter, a closing
# bracket or quote, or punctuation may come before them (not "0.778", not "ResNet50"), and only spaces, punctuation or the
# end may follow.
SUPERSCRIPT = re.compile(r"(?<=[a-z)\]’”'.,;:])(?<!\d[.,])(\d{1,3}(?:\s?[,–—-]\s?\d{1,3})*)(?=[\s.,;:)]|$)")
MIN_SUPERSCRIPTS = 3        # fewer glued numbers than this are more likely ordinary numbers than a citation style
# Author and affiliation lines carry superscript numbers too ("Jordan Bortz1,2", "Imperial College London, UK.6"): a
# line that looks like one is skipped.
AFFILIATION = re.compile(r"\b(?:Department|University|Universit[àé]|Institute|College|School|Faculty|Centre|Center|"
                         r"Hospital|Laborator(?:y|ies)|Inc|Ltd|GmbH|Email|e-mail|Correspondence)\b|@|✉")
PAREN = re.compile(r"\(([^()]*?\b(?:19|20)\d{2}[a-z]?\b[^()]*)\)")
NARRATIVE = re.compile(r"\b([A-Z][A-Za-z\-'’]+)(?:\s+et\s+al\.?|\s+(?:and|&)\s+[A-Z][A-Za-z\-'’]+)?\s+\(((?:19|20)\d{2}[a-z]?)\)")
YEAR = re.compile(r"\b((?:19|20)\d{2})[a-z]?\b")
NUM_ENTRY = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)[.)])\s+(.*)$")
MAX_RANGE = 30
# An author-year entry starts "Surname, A." / "Surname, Anne" / "Surname A," and contains a year.
AUTHOR_ENTRY = re.compile(r"^\s*[A-Z][A-Za-z\-'’]+,?\s+(?:[A-Z]\.|[A-Z][a-z]+,|[A-Z]{1,3}[,.])")
ID_IN_LINE = re.compile(r"\b10\.\d{4,9}/|arxiv:?\s*\d{4}\.\d{4,5}|https?://", re.I)
MIN_TAIL_ENTRIES = 2


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


def _looks_like_entry(line: str) -> bool:
    t = line.strip()
    if not t or NUMERIC.search(t[3:]):            # a citing sentence carries markers after its start
        return False
    if NUM_ENTRY.match(t):
        return True
    return bool((AUTHOR_ENTRY.match(t) and YEAR.search(t)) or (ID_IN_LINE.search(t) and YEAR.search(t)))


def _unlabelled_tail(text: str):
    """Start offset of a reference list pasted without a heading: entry-like lines at the end of the text (with up to
    two wrapped continuation lines between them), at least MIN_TAIL_ENTRIES of them.  None if there is none."""
    lines = text.splitlines(keepends=True)
    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)
    start, entries, run = None, 0, 0
    for i in reversed(range(len(lines))):
        line = lines[i].strip()
        if not line:
            continue
        if _looks_like_entry(line):
            entries, start, run = entries + 1, offsets[i], 0
            continue
        run += 1
        if run > 2 or NUMERIC.search(line) or len(line.split()) > 40:
            break                                   # body text: a citing sentence or a paragraph
    return start if entries >= MIN_TAIL_ENTRIES and start else None


def split_body_and_references(text: str):
    """(body, reference_block).  The LAST matching heading wins (a paper may mention 'references' earlier); without a
    heading, an entry-like block at the end of the text is taken as the reference list."""
    text = text or ""
    matches = list(REF_HEADING.finditer(text))
    if matches:
        m = matches[-1]
        return text[: m.start()], text[m.end():]
    tail = _unlabelled_tail(text)
    if tail is not None:
        return text[:tail], text[tail:]
    return text, ""


def join_references(text: str, references: str) -> str:
    """The draft as one text when the reference list comes from its own box.  If the text already has a reference
    list after a heading, the box's entries are added to it; otherwise a heading is added."""
    references = (references or "").strip()
    if not references:
        return text or ""
    text = (text or "").rstrip()
    if REF_HEADING.search(text):
        return f"{text}\n{references}\n"
    return f"{text}\n\nReferences\n{references}\n"


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


def superscripts_to_brackets(body: str, n_refs: int) -> tuple:
    """(body with superscript citations written as [n], how many were found).  Used only when the reference list is
    numbered and the text has no bracketed citations: every number must be an entry of the list (1..n_refs)."""
    if n_refs <= 0 or NUMERIC.search(body):
        return body, 0

    def numbers(group: str) -> list:
        out = []
        for part in group.split(","):
            a, _, b = part.replace("–", "-").replace("—", "-").partition("-")
            out += [int(a)] + ([int(b)] if b else [])
        return out

    def line_of(m) -> str:
        return body[body.rfind("\n", 0, m.start()) + 1: (body.find("\n", m.end()) + 1 or len(body) + 1) - 1]

    hits = [m for m in SUPERSCRIPT.finditer(body)
            if all(1 <= n <= n_refs for n in numbers(m.group(1))) and not AFFILIATION.search(line_of(m))]
    if len(hits) < MIN_SUPERSCRIPTS:
        return body, 0
    out, last = [], 0
    for m in hits:
        out += [body[last:m.start()], f" [{m.group(1)}]"]
        last = m.end()
    return "".join(out + [body[last:]]), len(hits)


def parse_draft(text: str, max_claims: int = 200) -> DraftParse:
    body, ref_block = split_body_and_references(text or "")
    refs = parse_reference_list(ref_block)
    warnings, claims = [], []
    if refs and all(k.isdigit() for k in refs):
        body, n_sup = superscripts_to_brackets(body, max(int(k) for k in refs))
        if n_sup:
            warnings.append(f"Read {n_sup} superscript citation numbers (for example “…risk3,12.”) as citations.")
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
        warnings.append("No reference list found. Paste it in the reference-list box (or after a line that says "
                        "'References'), so citations can be matched to papers; until then only a citation with a DOI "
                        "or arXiv id in the sentence itself can be checked.")
    style = "mixed" if numeric_seen and author_seen else "numeric" if numeric_seen else "author-year" if author_seen else "none"
    return DraftParse(claims, refs, style, warnings)
