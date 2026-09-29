"""Fine-tune the NLI verifier on SciFact TRAIN.   Owner: Data & Evaluation (Sahil).   (STRETCH goal)

    python -m eval.finetune_nli --out models/citecheck-nli-ft --epochs 2 --lr 1e-5 --batch-size 8
    python -m eval.run_eval --name finetuned_nli --retriever bm25 --verifier nli --model models/citecheck-nli-ft \\
        --oracle --compare-with eval/results/zero_shot_nli

What it trains on (train split only; dev/test are never read):
  * positives : gold rationale sentences of each evidence paper -> SUPPORT / CONTRADICT
  * NEI       : for claims with no evidence, the best sentences of the papers the claim cited -> neutral
  * hard negatives: papers OUR retriever ranks high that are not gold -> neutral (teaches the model to
                    abstain on plausible-looking but irrelevant papers, exactly what happens at inference)

Runs on CPU (slow: budget ~15-30 min/epoch for a base model) or a free Colab GPU.  Model weights go to
models/ which is git-ignored: do NOT commit them (record the run in eval/results instead).
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from src.data_io import MIXED, find_scifact_dir, load_claims, load_corpus, sha256_file
from src.evidence import LexicalSentenceScorer, build_premise, select_sentences
from src.nli import DEFAULT_NLI_MODEL, resolve_label_indices
from src.retrieval import BM25Retriever
from src.schema import NEI, SUPPORT


def build_training_pairs(claims, corpus_by_id, retriever, scorer, m=3, neg_per_claim=1):
    """Returns list of (premise, claim, class) with class in {"support","neutral","contradict"}."""
    pairs = []
    for c in claims:
        gold = set(c.gold_docs)
        for doc_id, lab in c.gold_doc_labels.items():
            doc = corpus_by_id.get(doc_id)
            if lab == MIXED or doc is None:
                continue
            for rset in c.rationale_sets(doc_id):
                premise = " ".join(doc.sentences[i] for i in rset if i < len(doc.sentences))
                if premise:
                    pairs.append((premise, c.claim, "support" if lab == SUPPORT else "contradict"))
        if c.gold_label == NEI:
            for doc_id in c.cited_doc_ids:
                doc = corpus_by_id.get(doc_id)
                if doc is None or not doc.sentences:
                    continue
                pairs.append((build_premise(doc.sentences, select_sentences(c.claim, doc.sentences, m, scorer)), c.claim, "neutral"))
        if retriever is not None and neg_per_claim > 0:
            taken = 0
            for hit in retriever.search(c.claim, neg_per_claim + len(gold) + 3):
                if hit.doc.doc_id in gold or not hit.doc.sentences:
                    continue
                pairs.append((build_premise(hit.doc.sentences, select_sentences(c.claim, hit.doc.sentences, m, scorer)), c.claim, "neutral"))
                taken += 1
                if taken >= neg_per_claim:
                    break
    return pairs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_NLI_MODEL)
    ap.add_argument("--data-dir", default="data/scifact")
    ap.add_argument("--out", default="models/citecheck-nli-ft")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-length", type=int, default=320)
    ap.add_argument("--neg-per-claim", type=int, default=1)
    ap.add_argument("--sentences", type=int, default=3)
    ap.add_argument("--max-steps", type=int, default=None, help="stop early (smoke test)")
    ap.add_argument("--class-weights", default="auto", choices=["auto", "none"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--device", default=None)
    a = ap.parse_args(argv)

    import numpy as np
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    random.seed(a.seed)
    np.random.seed(a.seed)
    torch.manual_seed(a.seed)

    data_dir = find_scifact_dir(a.data_dir)
    if data_dir is None:
        raise SystemExit("SciFact not found. Run: python -m data.fetch_scifact")
    corpus = load_corpus(data_dir / "corpus.jsonl")
    by_id = {d.doc_id: d for d in corpus}
    train_path = data_dir / "claims_train.jsonl"  # dev and test are deliberately never opened here
    claims = load_claims(train_path)
    pairs = build_training_pairs(claims, by_id, BM25Retriever(corpus), LexicalSentenceScorer.from_docs(corpus),
                                 m=a.sentences, neg_per_claim=a.neg_per_claim)
    counts = {k: sum(1 for p in pairs if p[2] == k) for k in ("support", "neutral", "contradict")}
    print(f"{len(pairs)} training pairs: {counts}")

    dev = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.base)
    model = AutoModelForSequenceClassification.from_pretrained(a.base).to(dev)
    idx = resolve_label_indices(model.config.id2label)
    labels = [idx[p[2]] for p in pairs]

    if a.class_weights == "auto":
        w = torch.zeros(model.config.num_labels)
        for k, v in counts.items():
            w[idx[k]] = len(pairs) / (3 * max(v, 1))
        loss_fn = torch.nn.CrossEntropyLoss(weight=w.to(dev))
    else:
        loss_fn = torch.nn.CrossEntropyLoss()

    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    steps_per_epoch = (len(pairs) + a.batch_size - 1) // a.batch_size
    total = min(steps_per_epoch * a.epochs, a.max_steps or 10**9)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * total), total)

    log, step, t0 = [], 0, time.time()
    model.train()
    for epoch in range(a.epochs):
        order = list(range(len(pairs)))
        random.shuffle(order)
        for s in range(0, len(order), a.batch_size):
            b = order[s : s + a.batch_size]
            enc = tok([pairs[i][0] for i in b], [pairs[i][1] for i in b], truncation="only_first",
                      max_length=a.max_length, padding=True, return_tensors="pt").to(dev)
            y = torch.tensor([labels[i] for i in b]).to(dev)
            loss = loss_fn(model(**enc).logits, y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad()
            step += 1
            if step % 20 == 0 or step == 1:
                print(f"epoch {epoch + 1} step {step}/{total} loss {loss.item():.4f}  ({time.time() - t0:.0f}s)")
                log.append({"step": step, "loss": float(loss.item())})
            if a.max_steps and step >= a.max_steps:
                break
        if a.max_steps and step >= a.max_steps:
            break

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out)
    tok.save_pretrained(out)
    (out / "train_log.json").write_text(json.dumps({
        "base": a.base, "args": vars(a), "n_pairs": len(pairs), "class_counts": counts, "loss_log": log,
        "train_file_sha256": sha256_file(train_path)[:16], "seconds": time.time() - t0,
        "note": "trained on claims_train.jsonl only; evaluate with eval.run_eval on dev",
    }, indent=2), encoding="utf-8")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
