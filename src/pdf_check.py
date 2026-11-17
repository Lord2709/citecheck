"""Decide at upload time whether a PDF has real text we can read, or is a scan we refuse.   Owner: Engineering.

Scope decision (docs/agent_plan.md): CiteCheck reads TEXT-BASED PDFs only.  We do not run OCR, so a scanned PDF is
refused up front with a message that offers a way forward (paste the text, or upload a text-based version).

How it decides, page by page:
  * a page is "text" when it has at least MIN_CHARS_PER_PAGE extracted characters AND most of its tokens look like
    words (READABLE_MIN), which catches PDFs whose fonts extract as garbage;
  * the file is "text" when at least TEXT_PAGE_SHARE of its pages are text pages, "mixed" when some are, "scanned"
    when none are, and "empty" when it has no pages.
A scan that already carries an OCR text layer counts as text (the text is there, possibly noisy): that is intended.

The thresholds are STARTING GUESSES, not tuned values.  Tune them on real PDFs (a few text papers, a few scans) and
record what you used; until then treat borderline results with care.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Sequence, Union

MIN_CHARS_PER_PAGE = 200   # a typical text page of a paper has 2,000-5,000 characters
READABLE_MIN = 0.6         # share of tokens that look like words
TEXT_PAGE_SHARE = 0.8      # share of pages that must be text pages for the whole file to count as "text"

_TOKEN = re.compile(r"\S+")
_WORDLIKE = re.compile(r"^[\(\[\"'“‘]*[A-Za-z][A-Za-z\-'’]*[A-Za-z]?[\)\]\"'”’.,;:!?%]*$")


class PdfRejected(Exception):
    """Message is safe and helpful to show to the user."""


@dataclass(frozen=True)
class PdfAssessment:
    kind: str                 # "text" | "mixed" | "scanned" | "empty"
    n_pages: int
    text_pages: tuple         # 0-based indices of pages we can read
    skipped_pages: tuple      # 0-based indices of pages we cannot read
    total_chars: int

    @property
    def accepted(self) -> bool:
        return self.kind in ("text", "mixed")

    def user_message(self) -> str:
        if self.kind == "text":
            return ""
        if self.kind == "mixed":
            pages = ", ".join(str(i + 1) for i in self.skipped_pages[:10]) + (" ..." if len(self.skipped_pages) > 10 else "")
            return (f"Some pages have no readable text and were skipped (page {pages}). "
                    "Citations on those pages will not be checked.")
        if self.kind == "empty":
            return "This PDF has no pages. Please upload a different file, or paste the text instead."
        return ("This PDF looks scanned, so we can't read its text. CiteCheck only reads text-based PDFs. "
                "Paste the paragraph you want checked instead, or upload a text-based version of the file.")


def readable_ratio(text: str) -> float:
    """Share of whitespace-separated tokens that look like ordinary words.  0.0 for empty text."""
    tokens = _TOKEN.findall(text or "")
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if _WORDLIKE.match(t)) / len(tokens)


def page_is_text(text: str) -> bool:
    text = (text or "").strip()
    return len(text) >= MIN_CHARS_PER_PAGE and readable_ratio(text) >= READABLE_MIN


def assess_pages(page_texts: Sequence) -> PdfAssessment:
    """Pure function over the extracted text of each page; the testable core of the check."""
    n = len(page_texts)
    good = tuple(i for i, t in enumerate(page_texts) if page_is_text(t))
    bad = tuple(i for i in range(n) if i not in set(good))
    total = sum(len((t or "").strip()) for t in page_texts)
    if n == 0:
        kind = "empty"
    elif not good:
        kind = "scanned"
    elif len(good) / n >= TEXT_PAGE_SHARE:
        kind = "text"
    else:
        kind = "mixed"
    return PdfAssessment(kind=kind, n_pages=n, text_pages=good, skipped_pages=bad, total_chars=total)


def extract_page_texts(pdf: Union[str, bytes, "io.BufferedIOBase"]) -> list:
    """Text of each page using pypdf (pure Python, no GPU).  Raises PdfRejected for files pypdf cannot open."""
    try:
        from pypdf import PdfReader
    except ImportError as e:  # pragma: no cover - dependency is in requirements.txt
        raise PdfRejected("PDF support is not installed on this server (missing pypdf).") from e
    try:
        source = io.BytesIO(pdf) if isinstance(pdf, (bytes, bytearray)) else pdf
        reader = PdfReader(source)
        if reader.is_encrypted:
            raise PdfRejected("This PDF is password-protected. Please upload an unprotected copy, or paste the text.")
        texts = []
        for page in reader.pages:
            try:
                texts.append(page.extract_text() or "")
            except Exception:  # one broken page should not sink the file
                texts.append("")
        return texts
    except PdfRejected:
        raise
    except Exception as e:
        raise PdfRejected("We could not open this file as a PDF. Please check the file, or paste the text instead.") from e


EDGE_LINES = 2              # lines at the top and bottom of a page where running headers and footers sit
REPEAT_SHARE = 0.5          # a line repeated at a page edge on at least this share of pages is a header or footer
PAGE_NUMBER = re.compile(r"^\s*(?:page\s*)?\d{1,4}(?:\s*(?:of|/)\s*\d{1,4})?\s*$", re.I)
HYPHEN_BREAK = re.compile(r"([A-Za-z]{2,})-\n([a-z]{2,})")
# Words that usually start a hyphenated compound: "self-\nsupervised" stays "self-supervised"; "evalu-\nation" is
# joined into one word.
COMPOUND_HEADS = frozenset("self non multi cross semi well state end high low large small real long short fine pre "
                           "post co anti inter intra over under sub".split())


def _join_hyphen(m) -> str:
    head, tail = m.group(1), m.group(2)
    return f"{head}-{tail}" if head.lower() in COMPOUND_HEADS else head + tail


CITATION_MARK = re.compile(r"\[\d")


def _edge_key(line: str) -> str:
    """A header seen on several pages differs only in its numbers ("Procedia 00 (2019) 123-130").  A line with a
    citation marker is body text, never a header."""
    if CITATION_MARK.search(line):
        return ""
    return re.sub(r"\d+", "#", line.strip().lower())


def clean_page_texts(page_texts: Sequence) -> list:
    """The pages' text without running headers, footers and page numbers, with words split across lines joined.

    A paper's running header ("Journal of X 12 (2019) 345-356", "Author et al.") would otherwise be read as part of
    the sentences around it, and "evalu-\nation" would never match the paper's "evaluation"."""
    pages = [(t or "").splitlines() for t in page_texts]
    n = len(pages)
    counts = {}
    if n >= 3:
        for lines in pages:
            edges = {_edge_key(x) for x in lines[:EDGE_LINES] + lines[-EDGE_LINES:] if x.strip()} - {""}
            for k in edges:
                counts[k] = counts.get(k, 0) + 1
    repeated = {k for k, c in counts.items() if c >= max(3, REPEAT_SHARE * n)}
    out = []
    for lines in pages:
        last = len(lines) - 1
        at_edge = lambda i: i < EDGE_LINES or i > last - EDGE_LINES  # noqa: E731
        kept = [x for i, x in enumerate(lines)
                if not (at_edge(i) and (_edge_key(x) in repeated or PAGE_NUMBER.match(x)))]
        out.append(HYPHEN_BREAK.sub(_join_hyphen, "\n".join(kept)))
    return out


def check_pdf(pdf) -> PdfAssessment:
    """Assess an uploaded PDF (path, bytes or file object).  Callers refuse it when `not result.accepted`."""
    return assess_pages(extract_page_texts(pdf))


if __name__ == "__main__":  # manual check:  python -m src.pdf_check some.pdf
    import sys

    for path in sys.argv[1:]:
        a = check_pdf(path)
        print(f"{path}: {a.kind} ({len(a.text_pages)}/{a.n_pages} text pages, {a.total_chars} chars) {a.user_message()}")
