"""Which free source has the abstract, and which has the full text, for the papers our users actually cite.
Owner: Data & Evaluation.

    python -m tools.source_coverage dois.txt                 # writes docs/live_checks/<today>_source_coverage.{json,md}
    python -m tools.source_coverage dois.txt --no-write      # print only

Why: in the user sessions of 2026-11-04 to 2026-11-16 most verdicts came from the abstract alone, and some citations
could not be checked at all because no open source returned an abstract (for example an Elsevier 2005 paper and a
Springer 2009 chapter). Before adding sources to the product we measure, on the DOIs people cited, what each free
source would add.

Input: a text file with DOIs, one per line (anything else on a line is ignored; lines without a DOI are skipped). The
query at the end of this docstring lists them from the site's database.

Per DOI it asks, once each:
  abstract   OpenAlex (in the product), Semantic Scholar (in the product, fallback), Crossref, Europe PMC
  full text  Unpaywall PDF link and Europe PMC open access (both in the product), Semantic Scholar's open-access PDF,
             OpenAlex PDF locations, an arXiv version found by title, CORE (only with CORE_API_KEY)
It also records which sites host the PDF links and whether one of them is a repository (arXiv, a university, PMC...):
publisher sites often refuse downloads by programs (the ACM Digital Library answered HTTP 403 on 2026-11-10).
It records whether each source answered and what it had; it does not download any PDF.

Optional environment variables (never written to the output files):
  CITECHECK_MAILTO   contact e-mail: Crossref and OpenAlex "polite pool"; required by Unpaywall
  OPENALEX_API_KEY   free OpenAlex key
  S2_API_KEY         free Semantic Scholar key (without it, expect some HTTP 429 answers)
  CORE_API_KEY       free CORE key (core.ac.uk/services/api)

To list the DOIs cited on the live site (Supabase, SQL Editor; export the result as CSV and pass that file):

    select distinct lower(coalesce(c->'paper'->>'doi',
                                   substring(c->>'identifier' from '(10\\.[0-9]{4,9}/[^[:space:]]+)'))) as doi
    from citecheck.runs r, json_array_elements(r.report->'citations') c
    where r.kind in ('draft_check', 'claim_check')
      and coalesce(c->'paper'->>'doi', substring(c->>'identifier' from '(10\\.[0-9]{4,9}/[^[:space:]]+)')) is not null
    order by 1;
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote, urlparse
import xml.etree.ElementTree as ET

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"',;]+)", re.I)
TAG_RE = re.compile(r"<[^>]+>")
MIN_ABSTRACT_WORDS = 25          # shorter "abstracts" are usually a title or a citation string

ABSTRACT_SOURCES = ("openalex", "s2", "crossref", "europepmc")
FULLTEXT_SOURCES = ("unpaywall_pdf", "europepmc_oa", "s2_oa_pdf", "openalex_pdf", "arxiv_title", "core")
# What the site used before the November 2026 update, and what it uses after it (Crossref and Europe PMC abstracts,
# Semantic Scholar's and OpenAlex's open-access PDF links).  CORE is measured to decide whether it is worth adding.
BEFORE = {"abstract": ("openalex", "s2"), "fulltext": ("unpaywall_pdf", "europepmc_oa")}
AFTER = {"abstract": ("openalex", "s2", "crossref", "europepmc"),
         "fulltext": ("unpaywall_pdf", "europepmc_oa", "s2_oa_pdf", "openalex_pdf", "arxiv_title")}


# The same rules as src/fulltext.py in the site update, copied so this tool runs on any version of the site.
REPOSITORY_HOSTS = ("arxiv.org", "europepmc.org", "ncbi.nlm.nih.gov", "biorxiv.org", "medrxiv.org", "hal.science",
                    "zenodo.org", "osf.io", "core.ac.uk", "aclanthology.org", "openreview.net", ".edu/")
MIN_TITLE_MATCH, MIN_TITLE_WORDS, ARXIV_YEARS = 0.85, 5, (-3, 1)


def is_repository(url: str, kind: str = "") -> bool:
    return kind == "repository" or any(h in (url or "").lower() for h in REPOSITORY_HOSTS)


def title_tokens(title: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (title or "").lower())) - {"a", "an", "the", "of", "and", "for", "in", "on", "with"}


def same_title(a: str, b: str) -> bool:
    ta, tb = title_tokens(a), title_tokens(b)
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= MIN_TITLE_MATCH


def arxiv_match(entries: list, title: str, year=None):
    """The arXiv id of the entry that is this paper: a specific title that (almost) matches, from a close year."""
    if len(title_tokens(title)) < MIN_TITLE_WORDS:
        return None
    for aid, t, y in entries:
        if same_title(t, title) and not (year and y and not (year + ARXIV_YEARS[0] <= y <= year + ARXIV_YEARS[1])):
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


def read_dois(text: str) -> list:
    """DOIs in a file's text, lower-cased, in order, without duplicates (CSV headers and other columns are ignored)."""
    out = []
    for m in DOI_RE.finditer(text or ""):
        d = m.group(1).rstrip(".)]").lower()
        if d not in out:
            out.append(d)
    return out


def _words(text: str) -> int:
    return len(TAG_RE.sub(" ", text or "").split())


def abstract_from_inverted_index(inv) -> str:
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


class Http:
    """GET with a polite User-Agent, a key only for the host it belongs to, and a few retries on 429/5xx."""

    def __init__(self, session=None, mailto=None, s2_key=None, core_key=None, retries=3, timeout=20, sleep=time.sleep):
        if session is None:
            import requests

            session = requests.Session()
        self.session, self.mailto, self.s2_key, self.core_key = session, mailto, s2_key, core_key
        self.retries, self.timeout, self.sleep = retries, timeout, sleep

    def get_text(self, url: str, params: Optional[dict] = None):
        """(status, text or None), for the sources that answer in XML (arXiv)."""
        try:
            r = self.session.get(url, params=params, headers={"User-Agent": "CiteCheck-course-project/0.3"},
                                 timeout=self.timeout)
        except Exception:
            return "network", None
        return r.status_code, (getattr(r, "text", "") if r.status_code == 200 else None)

    def get(self, url: str, params: Optional[dict] = None):
        """(status, json or None).  status is the HTTP code, or 'network' when no answer came."""
        headers = {"User-Agent": "CiteCheck-course-project/0.3" + (f" (mailto:{self.mailto})" if self.mailto else "")}
        if self.s2_key and "api.semanticscholar.org" in url:
            headers["x-api-key"] = self.s2_key
        if self.core_key and "api.core.ac.uk" in url:
            headers["Authorization"] = f"Bearer {self.core_key}"
        status = "network"
        for attempt in range(self.retries):
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            except Exception:
                status = "network"
                self.sleep(2 ** attempt)
                continue
            status = r.status_code
            if status in (429, 500, 502, 503, 504):
                self.sleep(2 ** attempt * 1.5)
                continue
            if status != 200:
                return status, None
            try:
                return status, r.json()
            except ValueError:
                return status, None
        return status, None


def probe(doi: str, http: Http, mailto=None, openalex_key=None, core_key=None) -> dict:
    """What every source has for one DOI.  Values: True / False, or 'error <code>' when the source did not answer."""
    row = {"doi": doi}
    err = lambda status: f"error {status}"  # noqa: E731
    pdfs = []                           # (url, kind) of every PDF link any source lists
    title = ""

    oa_params = {k: v for k, v in (("mailto", mailto), ("api_key", openalex_key)) if v}
    st, j = http.get(f"https://api.openalex.org/works/https://doi.org/{doi}", oa_params or None)
    if j is not None:
        row["openalex"] = _words(abstract_from_inverted_index(j.get("abstract_inverted_index"))) >= MIN_ABSTRACT_WORDS
        locs = [j.get("best_oa_location") or {}] + list(j.get("locations") or [])
        row["openalex_pdf"] = any((loc or {}).get("pdf_url") for loc in locs)
        pdfs += [((loc or {}).get("pdf_url"), ((loc or {}).get("source") or {}).get("type", "")) for loc in locs]
        title = j.get("display_name") or j.get("title") or ""
        row["oa_status"] = (j.get("open_access") or {}).get("oa_status") or ""
        row["year"] = j.get("publication_year")
        row["publisher"] = ((j.get("primary_location") or {}).get("source") or {}).get("host_organization_name") or ""
    else:
        row["openalex"] = row["openalex_pdf"] = False if st == 404 else err(st)

    st, j = http.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                     {"fields": "abstract,isOpenAccess,openAccessPdf"})
    if j is not None:
        row["s2"] = _words(j.get("abstract") or "") >= MIN_ABSTRACT_WORDS
        row["s2_oa_pdf"] = bool((j.get("openAccessPdf") or {}).get("url"))
        pdfs.append(((j.get("openAccessPdf") or {}).get("url"), ""))
    else:
        row["s2"] = row["s2_oa_pdf"] = False if st == 404 else err(st)

    st, j = http.get(f"https://api.crossref.org/works/{quote(doi, safe='/')}", {"mailto": mailto} if mailto else None)
    if j is not None:
        row["crossref"] = _words((j.get("message") or {}).get("abstract") or "") >= MIN_ABSTRACT_WORDS
    else:
        row["crossref"] = False if st == 404 else err(st)

    st, j = http.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                     {"query": f'DOI:"{doi}"', "format": "json", "resultType": "core"})
    if j is not None:
        hits = ((j.get("resultList") or {}).get("result") or [])
        hit = hits[0] if hits else {}
        row["europepmc"] = _words(hit.get("abstractText") or "") >= MIN_ABSTRACT_WORDS
        row["europepmc_oa"] = bool(hit.get("pmcid")) and hit.get("isOpenAccess") == "Y"
    else:
        row["europepmc"] = row["europepmc_oa"] = err(st)

    if mailto:
        st, j = http.get(f"https://api.unpaywall.org/v2/{doi}", {"email": mailto})
        if j is not None:
            locs = [j.get("best_oa_location") or {}] + list(j.get("oa_locations") or [])
            row["unpaywall_pdf"] = any((loc or {}).get("url_for_pdf") for loc in locs)
            pdfs += [((loc or {}).get("url_for_pdf"), (loc or {}).get("host_type", "")) for loc in locs]
            row["unpaywall_landing_only"] = bool(j.get("is_oa")) and not row["unpaywall_pdf"]
        else:
            row["unpaywall_pdf"] = False if st == 404 else err(st)
            row["unpaywall_landing_only"] = False
    else:
        row["unpaywall_pdf"] = row["unpaywall_landing_only"] = "skipped (no CITECHECK_MAILTO)"

    if title and len(title_tokens(title)) >= MIN_TITLE_WORDS:
        q = re.sub(r"[^\w\s-]", " ", title).strip()
        st, text = http.get_text("http://export.arxiv.org/api/query", {"search_query": f'ti:"{q}"', "max_results": 3})
        if text is not None:
            hit = arxiv_match(arxiv_entries(text), title, row.get("year"))
            row["arxiv_title"] = hit is not None
            if hit:
                pdfs.append((f"https://arxiv.org/pdf/{hit}", "repository"))
        else:
            row["arxiv_title"] = err(st)
    else:
        row["arxiv_title"] = False

    if core_key:
        st, j = http.get("https://api.core.ac.uk/v3/search/works", {"q": f'doi:"{doi}"', "limit": 1})
        if j is not None:
            res = (j.get("results") or [{}])[0] if j.get("results") else {}
            row["core"] = bool(res.get("downloadUrl") or _words(res.get("fullText") or "") > 300)
        else:
            row["core"] = err(st)
    else:
        row["core"] = "skipped (no CORE_API_KEY)"

    pdfs = [(u, k) for u, k in pdfs if u]
    row["pdf_hosts"] = sorted({urlparse(u).netloc for u, _ in pdfs})
    row["repository_pdf"] = any(is_repository(u, k) for u, k in pdfs)
    for what, sources in (("abstract", ABSTRACT_SOURCES), ("fulltext", FULLTEXT_SOURCES)):
        row[f"{what}_before"] = any(row.get(s) is True for s in BEFORE[what])
        row[f"{what}_after"] = any(row.get(s) is True for s in AFTER[what])
        row[f"{what}_any"] = any(row.get(s) is True for s in sources)
    return row


def summarize(rows: list) -> dict:
    n = len(rows)
    count = lambda key: sum(1 for r in rows if r.get(key) is True)  # noqa: E731
    errors = lambda key: sum(1 for r in rows if str(r.get(key, "")).startswith("error"))  # noqa: E731
    skipped = lambda key: sum(1 for r in rows if str(r.get(key, "")).startswith("skipped"))  # noqa: E731
    by = {k: {"yes": count(k), "errors": errors(k), "skipped": skipped(k)} for k in ABSTRACT_SOURCES + FULLTEXT_SOURCES}
    only = {}                           # papers a source covers that the site did not before the change
    for k in ABSTRACT_SOURCES:
        only[k] = sum(1 for r in rows if r.get(k) is True and not r["abstract_before"])
    for k in FULLTEXT_SOURCES:
        only[k] = sum(1 for r in rows if r.get(k) is True and not r["fulltext_before"])
    out = {"n": n, "by_source": by, "adds_beyond_before": only, "unpaywall_landing_only": count("unpaywall_landing_only"),
           "repository_pdf": count("repository_pdf"),
           "publisher_only": sum(1 for r in rows if r.get("pdf_hosts") and not r.get("repository_pdf"))}
    for what in ("abstract", "fulltext"):
        for when in ("before", "after", "any"):
            out[f"{what}_{when}"] = count(f"{what}_{when}")
    return out


def to_markdown(report: dict) -> str:
    s, n = report["summary"], report["summary"]["n"]
    pct = lambda k: f"{k}/{n} ({100 * k / n:.0f}%)" if n else "0/0"  # noqa: E731
    lines = [f"# Source coverage for cited papers ({report['date']})", "",
             f"{n} DOIs cited on the live site. Each free source asked once per DOI; no PDF was downloaded.", "",
             *([f"**Incomplete run: {', '.join(k for k, b in s['by_source'].items() if b['skipped'])} skipped** "
                "(set CITECHECK_MAILTO, and CORE_API_KEY for CORE, then run again). The figures below leave them out.",
                ""] if any(b["skipped"] for b in s["by_source"].values()) else []),
             "| | the site before | the site after this update | every source tried |",
             "|---|---|---|---|",
             f"| abstract available | {pct(s['abstract_before'])} | {pct(s['abstract_after'])} | {pct(s['abstract_any'])} |",
             f"| full text available | {pct(s['fulltext_before'])} | {pct(s['fulltext_after'])} | {pct(s['fulltext_any'])} |",
             "", "| source | has it | not covered by the site before | did not answer | skipped |",
             "|---|---|---|---|---|"]
    for k in ABSTRACT_SOURCES + FULLTEXT_SOURCES:
        kind = "abstract" if k in ABSTRACT_SOURCES else "full text"
        b = s["by_source"][k]
        lines.append(f"| {k} ({kind}) | {b['yes']} | {s['adds_beyond_before'][k]} | {b['errors']} | {b['skipped']} |")
    lines += ["", f"Open access with only a web page, no PDF link, in Unpaywall: {s['unpaywall_landing_only']}.",
              f"A repository copy of the PDF (arXiv, a university, PMC...) exists for {s['repository_pdf']} papers; "
              f"for {s['publisher_only']} the only PDF links are on publisher sites, which often refuse programs.", "",
              "| DOI | year | publisher | abstract: before / after / any | full text: before / after / any "
              "| PDF hosts | repository copy |", "|---|---|---|---|---|---|---|"]
    yn = lambda v: "yes" if v is True else "no"  # noqa: E731
    for r in report["rows"]:
        lines.append(f"| {r['doi']} | {r.get('year') or ''} | {r.get('publisher') or ''} | "
                     f"{yn(r['abstract_before'])} / {yn(r['abstract_after'])} / {yn(r['abstract_any'])} | "
                     f"{yn(r['fulltext_before'])} / {yn(r['fulltext_after'])} / {yn(r['fulltext_any'])} | "
                     f"{', '.join(r.get('pdf_hosts') or []) or '-'} | {yn(r.get('repository_pdf'))} |")
    lines += ["", f"Run on {report['platform']}; keys used: {', '.join(report['keys_used']) or 'none'}."]
    return "\n".join(lines) + "\n"


def run(dois: list, http: Optional[Http] = None, env=os.environ, pause: Callable[[], None] = lambda: time.sleep(1.0),
        now=None) -> dict:
    mailto, oa_key, core_key = env.get("CITECHECK_MAILTO"), env.get("OPENALEX_API_KEY"), env.get("CORE_API_KEY")
    http = http or Http(mailto=mailto, s2_key=env.get("S2_API_KEY"), core_key=core_key)
    rows = []
    for d in dois:
        rows.append(probe(d, http, mailto=mailto, openalex_key=oa_key, core_key=core_key))
        pause()                           # Semantic Scholar allows about one request a second without a key
    keys = [k for k in ("CITECHECK_MAILTO", "OPENALEX_API_KEY", "S2_API_KEY", "CORE_API_KEY") if env.get(k)]
    return {"date": (now or datetime.now()).strftime("%Y-%m-%d"), "platform": platform.platform(terse=True),
            "keys_used": keys, "rows": rows, "summary": summarize(rows)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dois_file", help="text or CSV file with one DOI per line")
    ap.add_argument("--out-dir", default="docs/live_checks")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    dois = read_dois(Path(a.dois_file).read_text(encoding="utf-8", errors="replace"))
    if not dois:
        print("No DOIs found in that file.")
        return 1
    if not os.environ.get("CITECHECK_MAILTO"):
        print("Warning: CITECHECK_MAILTO is not set, so Unpaywall (which the site uses) is skipped and the result is "
              "incomplete. In PowerShell: $env:CITECHECK_MAILTO=\"you@example.edu\"")
    print(f"Checking {len(dois)} DOIs (about {len(dois) * 6} requests; this takes a few minutes)...")
    report = run(dois)
    md = to_markdown(report)
    print(md)
    if not a.no_write:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        stem = out / f"{report['date']}_source_coverage"
        stem.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        stem.with_suffix(".md").write_text(md, encoding="utf-8")
        print(f"Wrote {stem}.json and {stem}.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
