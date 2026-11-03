"""Evaluate the agent's own decisions.   Owner: Data & Evaluation.   Experiments: docs/agent_plan.md.

E3  swap test (offline, SciFact):
    python -m eval.agent_eval swap --name agent_swap --verifier nli --split dev
  For SciFact claims labelled SUPPORT, cite a WRONG but plausible paper (the best BM25 hit that is not a gold paper)
  and let the agent check it, with replacement search over the SciFact corpus.  Reports:
    flagged_rate          wrong citation NOT judged "supports"   (the agent notices the bad citation)
    suggestion_rate       a replacement was suggested
    suggestion_gold_rate  suggestions that are a gold SUPPORT paper of that claim
    bad_replacement_upper suggestions that are NOT a gold paper: an UPPER bound on bad replacements, because SciFact
                          only labels the papers a claim cites (a non-gold paper may still support it). Hand-check a
                          sample before quoting it as "bad".
    control_kept_rate     with the GOLD paper cited, the agent keeps it ("supports") without searching
  Each rate has a Wilson 95% interval.

E2  escalation on a real-world set (needs internet; the set comes from tools/realworld_set.py):
    python -m eval.agent_eval escalation --gold data/cache/realworld/gold_v1.jsonl --name agent_escalation
  Same agent, full-text reading off vs on: accuracy, macro-F1, how many "unsure" answers the full text resolved, and
  the extra seconds per escalated citation.  SciFact cannot show this (its evidence is always in the abstract).

Results go to eval/results/<name>/results.json + summary.md, flagged synthetic when run on tests/fixtures.
tau comes from eval/results/deployed_config.json (tuned on train), never from these runs.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import time
from datetime import datetime
from pathlib import Path

from src.agent import CiteCheckAgent, corpus_search
from src.config import load_deployed
from src.data_io import find_scifact_dir, is_synthetic_fixture, load_claims, load_corpus, sha256_file
from src.evidence import LexicalSentenceScorer
from src.nli import build_verifier
from src.pipeline import CiteCheckPipeline
from src.retrieval import BM25Retriever
from src.schema import CONTRADICT, NEI, SUPPORT, Paper


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]


def rate(k: int, n: int) -> dict:
    return {"k": k, "n": n, "rate": round(k / n, 4) if n else None, "ci95": wilson(k, n)}


def doc_paper(doc) -> Paper:
    return Paper(paper_id=f"scifact:{doc.doc_id}", title=doc.title, abstract=doc.abstract, source="scifact")


def build(data_dir, verifier_spec, tau=None, k=3, m=3):
    d = find_scifact_dir(data_dir)
    if d is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    corpus = load_corpus(d / "corpus.jsonl")
    retriever = BM25Retriever(corpus)
    dep = load_deployed() or {}
    tau = tau if tau is not None else dep.get("tau", 0.5)
    pipe = CiteCheckPipeline(build_verifier(verifier_spec), retriever, LexicalSentenceScorer.from_docs(corpus),
                             k=k, sentences_per_paper=m, tau=tau)
    return d, corpus, retriever, pipe


def swap_test(claims, corpus_by_id, retriever, pipe, n=None, seed=0, tau_strict=None, max_candidates=5):
    """Returns (metrics, per-claim rows).  Only claims whose gold label is SUPPORT are used."""
    pool = sorted((c for c in claims if c.gold_label == SUPPORT and c.gold_docs), key=lambda c: c.id)
    if n and n < len(pool):
        pool = sorted(random.Random(seed).sample(pool, n), key=lambda c: c.id)
    agent = CiteCheckAgent(pipe, search=corpus_search(retriever), escalate=False, tau_strict=tau_strict,
                           max_candidates=max_candidates)
    rows = []
    for c in pool:
        gold = set(c.gold_docs)
        gold_support = {d for d, lab in c.gold_doc_labels.items() if lab == SUPPORT}
        wrong = next((h.doc for h in retriever.search(c.claim, 20) if h.doc.doc_id not in gold), None)
        gdoc = corpus_by_id.get(sorted(gold_support)[0]) if gold_support else None
        if wrong is None or gdoc is None:
            continue
        v_ctrl, *_ = agent.check_claim(c.claim, doc_paper(gdoc))
        v, _, _, sugg, _ = agent.check_claim(c.claim, doc_paper(wrong))
        sids = [s.paper.paper_id.split(":", 1)[1] for s in sugg]
        rows.append({"id": c.id, "wrong_doc": wrong.doc_id, "verdict_on_wrong": v.label, "confidence": round(v.confidence, 4),
                     "suggested": sids, "suggested_gold": [s for s in sids if s in gold_support],
                     "control_verdict": v_ctrl.label})
    n_rows = len(rows)
    n_sugg = sum(len(r["suggested"]) for r in rows)
    metrics = {
        "n_claims": n_rows,
        "flagged_rate": rate(sum(r["verdict_on_wrong"] != SUPPORT for r in rows), n_rows),
        "false_keep_rate": rate(sum(r["verdict_on_wrong"] == SUPPORT for r in rows), n_rows),
        "suggestion_rate": rate(sum(bool(r["suggested"]) for r in rows), n_rows),
        "recovered_gold_rate": rate(sum(bool(r["suggested_gold"]) for r in rows), n_rows),
        "suggestion_gold_rate": rate(sum(len(r["suggested_gold"]) for r in rows), n_sugg),
        "bad_replacement_upper": rate(n_sugg - sum(len(r["suggested_gold"]) for r in rows), n_sugg),
        "control_kept_rate": rate(sum(r["control_verdict"] == SUPPORT for r in rows), n_rows),
        "tau": pipe.tau, "tau_strict": agent.tau_strict, "max_candidates": max_candidates,
    }
    return metrics, rows


def macro_f1(golds, preds, labels=(SUPPORT, CONTRADICT, NEI)) -> float:
    f1s = []
    for lab in labels:
        tp = sum(g == lab and p == lab for g, p in zip(golds, preds))
        fp = sum(g != lab and p == lab for g, p in zip(golds, preds))
        fn = sum(g == lab and p != lab for g, p in zip(golds, preds))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return round(sum(f1s) / len(f1s), 4)


def escalation_eval(items, agent_off, agent_on, fetch, clock=time.perf_counter):
    """items: [{"item_id", "claim", "cited_identifier", "gold"}]; fetch(identifier) -> Paper (or raises)."""
    rows = []
    for it in items:
        try:
            paper = fetch(it["cited_identifier"])
        except Exception as e:
            rows.append({"item_id": it["item_id"], "skipped": f"{type(e).__name__}"})
            continue
        t0 = clock()
        v_off, *_ = agent_off.check_claim(it["claim"], paper)
        t1 = clock()
        v_on, read_ft, ft_src, _, _ = agent_on.check_claim(it["claim"], paper)
        t2 = clock()
        rows.append({"item_id": it["item_id"], "gold": it["gold"], "off": v_off.label, "on": v_on.label,
                     "read_full_text": read_ft, "full_text_source": ft_src,
                     "seconds_off": round(t1 - t0, 3), "seconds_on": round(t2 - t1, 3)})
    done = [r for r in rows if "skipped" not in r]
    golds = [r["gold"] for r in done]
    unsure = [r for r in done if r["off"] == NEI]
    resolved = [r for r in unsure if r["read_full_text"] and r["on"] != NEI and r["on"] == r["gold"]]
    extra = [r["seconds_on"] - r["seconds_off"] for r in done if r["read_full_text"]]
    metrics = {
        "n_items": len(items), "n_scored": len(done), "n_skipped": len(rows) - len(done),
        "accuracy_off": rate(sum(r["off"] == r["gold"] for r in done), len(done)),
        "accuracy_on": rate(sum(r["on"] == r["gold"] for r in done), len(done)),
        "macro_f1_off": macro_f1(golds, [r["off"] for r in done]) if done else None,
        "macro_f1_on": macro_f1(golds, [r["on"] for r in done]) if done else None,
        "escalated": sum(r["read_full_text"] for r in done),
        "unsure_resolved_correctly": rate(len(resolved), len(unsure)),
        "median_extra_seconds_when_escalated": round(statistics.median(extra), 2) if extra else None,
    }
    return metrics, rows


def write(out_dir: Path, name: str, results: dict, rows: list, summary: str):
    d = out_dir / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    with open(d / "predictions.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (d / "summary.md").write_text(summary, encoding="utf-8")
    return d


def _fmt(r: dict) -> str:
    if not r or r.get("rate") is None:
        return "n/a"
    lo, hi = r["ci95"]
    return f"{r['rate']:.3f} [{lo:.3f}, {hi:.3f}] ({r['k']}/{r['n']})"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate the agent's decisions (E3 swap test, E2 escalation).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("swap")
    s.add_argument("--name", default="agent_swap")
    s.add_argument("--data-dir", default="data/scifact")
    s.add_argument("--split", default="dev", choices=["dev", "train"])
    s.add_argument("--verifier", default="nli")
    s.add_argument("--tau", type=float, default=None, help="default: the deployed tau (tuned on train)")
    s.add_argument("--tau-strict", type=float, default=None, help="default: the agent's placeholder")
    s.add_argument("--n", type=int, default=None, help="sample n claims (seeded); default all SUPPORT claims")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--out", default="eval/results")
    e = sub.add_parser("escalation")
    e.add_argument("--name", default="agent_escalation")
    e.add_argument("--gold", required=True, help="JSONL from tools/realworld_set.py merge")
    e.add_argument("--data-dir", default="data/scifact")
    e.add_argument("--verifier", default="nli")
    e.add_argument("--tau", type=float, default=None)
    e.add_argument("--out", default="eval/results")
    a = ap.parse_args(argv)
    t0 = time.time()

    if a.cmd == "swap":
        d, corpus, retriever, pipe = build(a.data_dir, a.verifier, a.tau)
        path = d / f"claims_{a.split}.jsonl"
        metrics, rows = swap_test(load_claims(path), {x.doc_id: x for x in corpus}, retriever, pipe, a.n, a.seed, a.tau_strict)
        results = {"name": a.name, "experiment": "E3 swap test", "split": a.split, "verifier": pipe.verifier.name,
                   "synthetic_fixture": is_synthetic_fixture(path), "partial": bool(a.n),
                   "data_sha256": sha256_file(path)[:16], "args": vars(a), "metrics": metrics,
                   "seconds": round(time.time() - t0, 1), "created_at": datetime.now().astimezone().isoformat(timespec="seconds")}
        m = metrics
        summary = "\n".join([
            f"# {a.name}: E3 swap test on SciFact {a.split}" + ("  (SYNTHETIC FIXTURE: plumbing only)" if results["synthetic_fixture"] else ""),
            "", f"{m['n_claims']} SUPPORT claims; each cites a wrong-but-plausible paper (best non-gold BM25 hit). "
            f"Verifier `{pipe.verifier.name}`, tau {m['tau']}, tau_strict {m['tau_strict']} (placeholder, not tuned).", "",
            "| metric | rate [95% Wilson CI] (k/n) |", "|---|---|",
            f"| wrong citation flagged (not 'supports') | {_fmt(m['flagged_rate'])} |",
            f"| wrong citation kept as 'supports' | {_fmt(m['false_keep_rate'])} |",
            f"| a replacement was suggested | {_fmt(m['suggestion_rate'])} |",
            f"| a gold paper was among the suggestions | {_fmt(m['recovered_gold_rate'])} |",
            f"| suggestions that are gold papers | {_fmt(m['suggestion_gold_rate'])} |",
            f"| suggestions that are not gold (UPPER bound on bad replacements) | {_fmt(m['bad_replacement_upper'])} |",
            f"| control: gold paper cited, kept as 'supports' | {_fmt(m['control_kept_rate'])} |", "",
            "Non-gold suggestions are not necessarily wrong: SciFact labels only the papers each claim cites. "
            "Hand-check a sample before calling them bad."])
    else:
        from src.ingest import Fetcher
        from src.fulltext import FullTextFinder

        d, corpus, retriever, pipe = build(a.data_dir, a.verifier, a.tau)
        items = [json.loads(l) for l in Path(a.gold).read_text(encoding="utf-8").splitlines() if l.strip()]
        fetcher = Fetcher()
        off = CiteCheckAgent(pipe, escalate=False, suggest=False)
        on = CiteCheckAgent(pipe, fulltext=FullTextFinder(fetcher), escalate=True, suggest=False)
        metrics, rows = escalation_eval(items, off, on, fetcher.fetch_paper)
        results = {"name": a.name, "experiment": "E2 escalation", "gold_file": a.gold, "verifier": pipe.verifier.name,
                   "synthetic_fixture": False, "partial": False, "args": vars(a), "metrics": metrics,
                   "seconds": round(time.time() - t0, 1), "created_at": datetime.now().astimezone().isoformat(timespec="seconds")}
        m = metrics
        summary = "\n".join([
            f"# {a.name}: E2 full-text escalation on {a.gold}", "",
            f"{m['n_scored']} of {m['n_items']} items scored ({m['n_skipped']} could not be fetched).", "",
            f"- accuracy, abstract only: {_fmt(m['accuracy_off'])}; with escalation: {_fmt(m['accuracy_on'])}",
            f"- macro-F1: {m['macro_f1_off']} -> {m['macro_f1_on']}",
            f"- escalated: {m['escalated']}; 'unsure' answers the full text resolved correctly: {_fmt(m['unsure_resolved_correctly'])}",
            f"- median extra seconds per escalated citation: {m['median_extra_seconds_when_escalated']}"])
    out = write(Path(a.out), a.name, results, rows, summary + "\n")
    print(summary)
    print(f"[written] {out}")
    return results


if __name__ == "__main__":
    main()
