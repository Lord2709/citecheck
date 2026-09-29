"""Small, dependency-light text helpers shared by retrieval, verification and ingest.

Owner: Engineering (Sakshaat).
"""
from __future__ import annotations

import re
from functools import lru_cache

try:  # nltk's Porter stemmer is pure rules: no corpus download needed
    from nltk.stem import PorterStemmer

    _PORTER = PorterStemmer()
except Exception:  # pragma: no cover - nltk missing
    _PORTER = None

STOPWORDS = frozenset(
    """a about above after again against all also am an and any are as at be because been
    before being below between both but by can could did do does doing down during each few
    for from further had has have having he her here hers him his how i if in into is it its
    just me more most my no nor not of off on once only or other our out over own same she
    should so some such than that the their them then there these they this those through to
    too under until up very was we were what when where which while who whom why will with
    would you your among may might within per via using used use based however thus
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")


@lru_cache(maxsize=500_000)
def _stem(word: str) -> str:
    return _PORTER.stem(word) if _PORTER is not None else word


def tokenize(text: str, stem: bool = True, drop_stopwords: bool = True) -> list:
    """Lower-case alphanumeric tokens, optionally stop-word filtered and stemmed."""
    toks = _TOKEN_RE.findall((text or "").lower())
    if drop_stopwords:
        toks = [t for t in toks if t not in STOPWORDS]
    if stem:
        toks = [_stem(t) for t in toks]
    return toks


# --------------------------------------------------------------------------- #
# Sentence splitting (for abstracts fetched from DOI/arXiv; SciFact is pre-split)
# --------------------------------------------------------------------------- #
_ABBREV = {
    "e.g", "i.e", "et al", "al", "fig", "figs", "vs", "cf", "approx", "no", "dr", "ca",
    "resp", "ref", "eq", "eqs", "st", "sp", "spp", "vol", "inc", "ltd", "co", "prof",
}
_BOUNDARY = re.compile(r"([.!?])([\"')\]]*)\s+(?=[A-Z0-9\"'(\[])")


def split_sentences(text: str) -> list:
    """Rule-based sentence splitter tuned for scientific abstracts."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if not text:
        return []
    sentences, start = [], 0
    for m in _BOUNDARY.finditer(text):
        if m.group(1) == ".":
            before = text[start : m.start()]
            last = re.search(r"([A-Za-z.]+)$", before)
            word = last.group(1).lower().rstrip(".") if last else ""
            if word in _ABBREV or (len(word) == 1 and word.isalpha()):
                continue  # "Fig.", "et al.", "J. Smith" are not sentence ends
        end = m.start() + 1 + len(m.group(2))
        piece = text[start:end].strip()
        if piece:
            sentences.append(piece)
        start = m.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


# --------------------------------------------------------------------------- #
# Misc
# --------------------------------------------------------------------------- #
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?\d[\s().-]{0,2}){9,14}\d(?!\d)")


def redact(text: str) -> str:
    """Mask e-mail addresses and phone numbers before anything is logged."""
    text = _EMAIL.sub("[email]", text or "")
    return _PHONE.sub("[phone]", text)


def truncate(text: str, n: int = 240) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"
