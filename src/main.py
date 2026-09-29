"""CiteCheck command line.   Owner: Engineering (Sakshaat).   (Replaces the Session-4 placeholder.)

    python -m src.main info
    python -m src.main verify --claim "Zorvex increases bone density" --abstract "…text of the paper you cite…"
    python -m src.main verify --claim "…" --paper 10.1038/nature14539        # the paper you cite, by DOI/arXiv
    python -m src.main verify --claim "…"                                    # search the SciFact corpus
    python -m src.main relevance --direction "graph neural networks for drug discovery" --paper arXiv:2004.14974
    python -m src.main audit --paper 10.1038/nature14539 --max 5             # experimental
    add --json to any command for machine-readable output
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap

from .config import load_config
from .ingest import Fetcher, IngestError, paper_from_text
from .pipeline import build_pipeline
from .relevance import RelevanceScorer


def _paper(args, fetcher):
    if getattr(args, "abstract", None):
        return paper_from_text(getattr(args, "title", "") or "", args.abstract)
    if getattr(args, "abstract_file", None):
        return paper_from_text(getattr(args, "title", "") or "", open(args.abstract_file, encoding="utf-8").read())
    if getattr(args, "paper", None):
        return fetcher.fetch_paper(args.paper)
    return None


def _print_verdict(v, out):
    out.write(f"\n{v.display_label}   (confidence {v.confidence:.2f}{', abstained' if v.abstained else ''})\n")
    if v.note:
        out.write(f"  note: {v.note}\n")
    for i, e in enumerate(v.evidence, 1):
        out.write(f"\n  [{i}] {e.title}\n      P(support)={e.probs.support:.2f}  P(neutral)={e.probs.neutral:.2f}  P(contradict)={e.probs.contradict:.2f}\n")
        for s in e.sentences:
            out.write(textwrap.fill(s, 96, initial_indent="      • ", subsequent_indent="        ") + "\n")
    b = v.backend
    out.write(f"\n  backend: {b.get('verifier')} + {b.get('retriever')}, tau={b.get('tau')}, {v.latency_ms:.0f} ms"
              f"{'  [DEMO BACKEND: not reliable]' if b.get('demo_only') else ''}"
              f"{'' if b.get('validated') else '  [UNVALIDATED configuration]'}\n")


def main(argv=None, out=sys.stdout):
    ap = argparse.ArgumentParser(prog="citecheck", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("verify", "relevance", "audit", "info"):
        p = sub.add_parser(name)
        p.add_argument("--json", action="store_true")
        if name in ("verify", "relevance"):
            p.add_argument("--paper", help="DOI / arXiv id / link of the paper")
            p.add_argument("--abstract", help="abstract text (offline)")
            p.add_argument("--abstract-file")
            p.add_argument("--title", default="")
        if name == "verify":
            p.add_argument("--claim", required=True)
        if name == "relevance":
            p.add_argument("--direction", required=True)
        if name == "audit":
            p.add_argument("--paper", required=True)
            p.add_argument("--max", type=int, default=10)
    a = ap.parse_args(argv)

    cfg = load_config()
    if a.cmd == "info":
        info = {"config": cfg.describe(), "validated": cfg.validated, "overrides": cfg.overrides, "deployed": cfg.deployed}
        out.write(json.dumps(info, indent=2) + "\n")
        return info

    fetcher = Fetcher()
    try:
        if a.cmd == "relevance":
            paper = _paper(a, fetcher)
            if paper is None:
                raise IngestError("Give --paper or --abstract.")
            r = RelevanceScorer().score(a.direction, paper)
            out.write(json.dumps(r.__dict__, indent=2) + "\n" if a.json else
                      f"{r.band.upper()}  (score {r.score:.2f}, {r.method})\nmatched terms: {', '.join(r.matched_terms) or '-'}\n{r.note}\n")
            return r
        pipe = build_pipeline(cfg)
        for w in pipe.warnings:
            sys.stderr.write(f"[warning] {w}\n")
        if a.cmd == "verify":
            paper = _paper(a, fetcher)
            v = pipe.verify_against_paper(a.claim, paper) if paper else pipe.verify_claim(a.claim)
            out.write(json.dumps(v.to_dict(), indent=2, default=str) + "\n" if a.json else "")
            if not a.json:
                _print_verdict(v, out)
            return v
        if a.cmd == "audit":
            rows = pipe.audit(fetcher.fetch_references(a.paper, limit=max(a.max, 10)), max_items=a.max)
            for r in rows:
                if a.json:
                    continue
                head = f"- {r.reference.cited.title[:80]}"
                out.write(head + ("   -> skipped: " + r.skipped_reason if r.skipped_reason else f"   -> {r.verdict.display_label} ({r.verdict.confidence:.2f})") + "\n")
            if a.json:
                out.write(json.dumps([{"cited": r.reference.cited.title, "context": r.reference.context,
                                       "verdict": r.verdict.to_dict() if r.verdict else None, "skipped": r.skipped_reason}
                                      for r in rows], indent=2, default=str) + "\n")
            return rows
    except (IngestError, ValueError) as e:
        sys.stderr.write(f"error: {e}\n")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
