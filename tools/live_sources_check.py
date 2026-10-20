"""Live check of the paper sources the app and the planned agent depend on.   Owner: Engineering.

    python -m tools.live_sources_check                       # prints a table, writes docs/live_checks/<today>.{json,md}
    python -m tools.live_sources_check --no-write            # print only

Why: src/ingest.py was written from the API docs and only spot-checked live once (2026-09-29, reports/session05.md).
OpenAlex started metering usage in 2026, and the agent plan (docs/agent_plan.md) adds Crossref, Unpaywall and Europe PMC.
This script calls every source with a FIXED list of real identifiers and records, per call: did it answer, how long it took,
and whether we got a usable abstract.  Run it on a machine with internet; the output is a dated, committed record, so the
report can say exactly what was tested and what failed.

Optional environment variables (never written to the output files):
  CITECHECK_MAILTO   contact e-mail: Crossref "polite pool", Unpaywall (required there), OpenAlex
  OPENALEX_API_KEY   free OpenAlex key
  S2_API_KEY         free Semantic Scholar key
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from src.ingest import Fetcher, IngestError, looks_like_citation

# Real papers chosen to cover the cases we care about.  Change this list only in a reviewed PR, so runs stay comparable.
PAPER_PROBES = [
    {"id": "doi-cs-nature", "query": "10.1038/nature14539", "why": "CS paper in a paywalled journal (Deep learning, Nature 2015)"},
    {"id": "doi-biomed-oa", "query": "10.1371/journal.pmed.0020124", "why": "open-access biomedical paper (PLOS Medicine 2005)"},
    {"id": "doi-biomed-nejm", "query": "10.1056/NEJMoa2034577", "why": "high-profile clinical trial (NEJM 2020); publisher abstracts are often missing"},
    {"id": "doi-scifact", "query": "10.18653/v1/2020.emnlp-main.609", "why": "returned a citation string instead of an abstract on 2026-09-29"},
    {"id": "arxiv-new", "query": "arXiv:2004.14974", "why": "new-style arXiv id (SciFact paper)"},
    {"id": "arxiv-transformer", "query": "arXiv:1706.03762", "why": "heavily cited CS preprint"},
]
REFERENCES_PROBE = "arXiv:2004.14974"


def _planned_probes(mailto: Optional[str], openalex_key: Optional[str]) -> list:
    """Sources the agent plan adds.  Each: (id, url, params, check(json) -> (ok, detail)).  Secrets go in params only."""
    def oa_params(extra):
        p = dict(extra)
        if openalex_key:
            p["api_key"] = openalex_key
        if mailto:
            p["mailto"] = mailto
        return p

    def crossref_check(j):
        items = ((j or {}).get("message") or {}).get("items") or []
        doi = (items[0].get("DOI") or "").lower() if items else ""
        return doi == "10.18653/v1/2020.emnlp-main.609", f"top DOI {doi or 'none'}"

    def unpaywall_check(j):
        best = (j or {}).get("best_oa_location") or {}
        return bool((j or {}).get("is_oa")), f"is_oa={(j or {}).get('is_oa')}, pdf={'yes' if best.get('url_for_pdf') else 'no'}"

    def epmc_check(j):
        res = (((j or {}).get("resultList") or {}).get("result") or [])
        first = res[0] if res else {}
        return bool(res), f"hits={(j or {}).get('hitCount')}, open_access={first.get('isOpenAccess')}"

    def count_check(key):
        def f(j):
            n = len((j or {}).get(key) or [])
            return n > 0, f"{n} result(s)"
        return f

    probes = [
        ("crossref-resolve", "https://api.crossref.org/works",
         dict({"query.bibliographic": "Fact or Fiction: Verifying Scientific Claims, Wadden et al., EMNLP 2020", "rows": 1},
              **({"mailto": mailto} if mailto else {})), crossref_check),
        ("europepmc-search", "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
         {"query": 'DOI:"10.1371/journal.pmed.0020124"', "format": "json", "resultType": "lite"}, epmc_check),
        ("openalex-search", "https://api.openalex.org/works",
         oa_params({"search": "scientific claim verification", "per_page": 3}), count_check("results")),
        ("s2-search", "https://api.semanticscholar.org/graph/v1/paper/search",
         {"query": "scientific claim verification", "limit": 3, "fields": "title,year"}, count_check("data")),
    ]
    if mailto:  # Unpaywall refuses requests without an e-mail address
        probes.append(("unpaywall-oa", "https://api.unpaywall.org/v2/10.1371/journal.pmed.0020124", {"email": mailto},
                       unpaywall_check))
    return probes


def check_papers(fetcher: Fetcher, clock: Callable[[], float] = time.monotonic) -> list:
    rows = []
    for probe in PAPER_PROBES:
        t0 = clock()
        row = {"probe": probe["id"], "query": probe["query"], "why": probe["why"]}
        try:
            p = fetcher.fetch_paper(probe["query"], use_cache=False)
            row.update(ok=True, source=p.source, title=(p.title or "")[:90], abstract_words=len(p.abstract.split()),
                       looks_like_citation=looks_like_citation(p.abstract), error="")
        except IngestError as e:
            row.update(ok=False, source="", title="", abstract_words=0, looks_like_citation=False, error=str(e)[:200])
        except Exception as e:  # anything unexpected is a finding, not a crash
            row.update(ok=False, source="", title="", abstract_words=0, looks_like_citation=False,
                       error=f"unexpected {type(e).__name__}: {str(e)[:150]}")
        row["seconds"] = round(clock() - t0, 2)
        rows.append(row)
    return rows


def check_references(fetcher: Fetcher, clock: Callable[[], float] = time.monotonic) -> dict:
    t0 = clock()
    try:
        refs = fetcher.fetch_references(REFERENCES_PROBE, limit=50)
        out = {"ok": bool(refs), "n_references": len(refs), "n_with_citing_sentence": sum(1 for r in refs if r.context), "error": ""}
    except Exception as e:
        out = {"ok": False, "n_references": 0, "n_with_citing_sentence": 0, "error": f"{type(e).__name__}: {str(e)[:150]}"}
    out.update(probe="s2-references", query=REFERENCES_PROBE, seconds=round(clock() - t0, 2))
    return out


def check_planned(session, mailto, openalex_key, timeout=20, clock: Callable[[], float] = time.monotonic) -> list:
    rows = []
    ua = "CiteCheck-course-project/0.3" + (f" (mailto:{mailto})" if mailto else "")
    for pid, url, params, check in _planned_probes(mailto, openalex_key):
        t0 = clock()
        row = {"probe": pid, "url": url}
        try:
            r = session.get(url, params=params, headers={"User-Agent": ua}, timeout=timeout)
            row["http"] = r.status_code
            if r.status_code == 200:
                ok, detail = check(r.json())
                row.update(ok=bool(ok), detail=detail)
            else:
                row.update(ok=False, detail=f"HTTP {r.status_code}")
        except Exception as e:
            row.update(http=None, ok=False, detail=f"{type(e).__name__}: {str(e)[:150]}")
        row["seconds"] = round(clock() - t0, 2)
        rows.append(row)
    return rows


def redact(text: str, secrets) -> str:
    for s in secrets:
        if s:
            text = text.replace(s, "<redacted>")
    return text


def to_markdown(report: dict) -> str:
    lines = [f"# Live source check, {report['run_at']}", "",
             f"Generated by `python -m tools.live_sources_check` on {report['platform']}. "
             f"Keys set: OpenAlex {'yes' if report['keys']['openalex'] else 'no'}, Semantic Scholar "
             f"{'yes' if report['keys']['s2'] else 'no'}, contact e-mail {'yes' if report['keys']['mailto'] else 'no'}.", "",
             "## Paper lookups (what the app does today)", "",
             "| probe | identifier | answered | source | abstract words | looks like a citation | seconds | error |",
             "|---|---|---|---|---|---|---|---|"]
    for r in report["papers"]:
        lines.append(f"| {r['probe']} | `{r['query']}` | {'yes' if r['ok'] else '**no**'} | {r['source'] or '-'} | "
                     f"{r['abstract_words']} | {'**yes**' if r['looks_like_citation'] else 'no'} | {r['seconds']} | {r['error'] or ''} |")
    ref = report["references"]
    lines += ["", "## Reference list with citing sentences (Semantic Scholar)", "",
              f"`{ref['query']}`: {'answered' if ref['ok'] else '**failed**'}, {ref['n_references']} references, "
              f"{ref['n_with_citing_sentence']} with a citing sentence, {ref['seconds']} s. {ref['error']}".rstrip(),
              "", "## Sources the agent plan adds (reachability only)", "",
              "| probe | answered as expected | HTTP | detail | seconds |", "|---|---|---|---|---|"]
    for r in report["planned"]:
        lines.append(f"| {r['probe']} | {'yes' if r['ok'] else '**no**'} | {r.get('http') or '-'} | {r['detail']} | {r['seconds']} |")
    if not report["keys"]["mailto"]:
        lines += ["", "Unpaywall was not checked: it needs `CITECHECK_MAILTO`."]
    n_ok = sum(r["ok"] for r in report["papers"])
    lines += ["", f"**Summary:** {n_ok} of {len(report['papers'])} paper lookups returned an abstract; "
              f"{sum(r['ok'] for r in report['planned'])} of {len(report['planned'])} planned sources answered as expected. "
              "These are single calls on one day from one network, not a reliability measurement."]
    return "\n".join(lines) + "\n"


def run(fetcher=None, session=None, clock=time.monotonic, now=None) -> dict:
    mailto = os.environ.get("CITECHECK_MAILTO")
    oa_key = os.environ.get("OPENALEX_API_KEY")
    s2_key = os.environ.get("S2_API_KEY")
    if fetcher is None:
        fetcher = Fetcher(cache_dir=None, retries=2)
    if session is None:
        session = fetcher.session
    now = now or datetime.now().astimezone()
    return {
        "run_at": now.isoformat(timespec="seconds"),
        "platform": f"{platform.system()} {platform.release()} / Python {platform.python_version()}",
        "keys": {"openalex": bool(oa_key), "s2": bool(s2_key), "mailto": bool(mailto)},
        "papers": check_papers(fetcher, clock),
        "references": check_references(fetcher, clock),
        "planned": check_planned(session, mailto, oa_key, clock=clock),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Call every paper source once with fixed real identifiers and record the outcome.")
    ap.add_argument("--out-dir", default="docs/live_checks")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    report = run()
    secrets = [os.environ.get("OPENALEX_API_KEY"), os.environ.get("S2_API_KEY"), os.environ.get("CITECHECK_MAILTO")]
    md = redact(to_markdown(report), secrets)
    print(md)
    if not a.no_write:
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        day = report["run_at"][:10]
        (out / f"{day}.json").write_text(redact(json.dumps(report, indent=2), secrets), encoding="utf-8")
        (out / f"{day}.md").write_text(md, encoding="utf-8")
        print(f"[written] {out / (day + '.json')} and .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
