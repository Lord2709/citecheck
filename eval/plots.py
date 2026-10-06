"""Figures for the reports and the Oct 6 presentation.   Owner: Data & Evaluation (Sahil).

    python -m eval.plots                       # all REAL runs in eval/results -> eval/results/figures/*.png
    python -m eval.plots --run zero_shot_nli   # also confusion matrix + tau curve for that run

Synthetic-fixture runs are skipped unless --include-synthetic (they are plumbing checks, not results).
Every chart states n and the split in its title so a figure cannot be mistaken for something it is not.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BLUE, ORANGE, GREY = "#2b6cb0", "#dd6b20", "#718096"


def load_runs(root: Path, include_synthetic=False):
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*/results.json"))]
    runs = [r for r in runs if include_synthetic or not r["synthetic_fixture"]]
    return sorted(runs, key=lambda r: r["created_utc"])


def f1_bars(runs, out):
    if not runs:
        return
    fig, ax = plt.subplots(figsize=(1.6 * len(runs) + 2, 4))
    vals = [r["claim_level"]["macro_f1"] for r in runs]
    lo = [v - r["claim_level"]["macro_f1_ci95"][0] for v, r in zip(vals, runs)]
    hi = [r["claim_level"]["macro_f1_ci95"][1] - v for v, r in zip(vals, runs)]
    ax.bar([r["name"] for r in runs], vals, yerr=[lo, hi], color=BLUE, capsize=4)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_ylabel("claim-level macro-F1")
    r0 = runs[0]
    ax.set_title(f"Baselines vs. system ({r0['split']}, n={r0['claim_level']['n']}, 95% bootstrap CI)")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(out / "f1_by_run.png", dpi=160)
    plt.close(fig)


def safety_bars(runs, out):
    if not runs:
        return
    fig, ax = plt.subplots(figsize=(1.6 * len(runs) + 2, 4))
    ax.bar([r["name"] for r in runs], [r["claim_level"]["false_support_rate"] for r in runs], color=ORANGE)
    ax.set_ylabel("false-SUPPORT rate (lower is safer)")
    ax.set_title("How often a non-supporting paper is called SUPPORTS")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(out / "false_support_by_run.png", dpi=160)
    plt.close(fig)


def recall_curves(runs, out):
    seen = {}
    for r in runs:
        seen[r["config"]["retriever"]] = r  # latest run per retriever
    if not seen:
        return
    ks = [1, 3, 5, 10, 20]
    fig, ax = plt.subplots(figsize=(6, 4))
    for name, r in seen.items():
        ax.plot(ks, [r["retrieval"][f"recall@{k}"] for k in ks], marker="o", label=name)
    ax.set_xlabel("k")
    ax.set_ylabel("recall@k (gold paper in top k)")
    ax.set_ylim(0, 1.02)
    ax.set_title("Retrieval: does the right paper get judged?")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "retrieval_recall.png", dpi=160)
    plt.close(fig)


def confusion_plot(run, out):
    cm = run["claim_level"]["confusion_rows_gold_cols_pred"]
    labels, mat = cm["labels"], cm["matrix"]
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(mat, cmap="Blues")
    ax.set_xticks(range(len(labels)), labels)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("predicted")
    ax.set_ylabel("gold")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, mat[i][j], ha="center", va="center", color="black" if mat[i][j] < max(map(max, mat)) * 0.6 else "white")
    ax.set_title(f"{run['name']}: confusion ({run['split']})")
    fig.tight_layout()
    fig.savefig(out / f"confusion_{run['name']}.png", dpi=160)
    plt.close(fig)


def tau_plot(run, out):
    rows = run["tau_sweep_analysis_only"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([r["tau"] for r in rows], [r["macro_f1"] for r in rows], color=BLUE, label="macro-F1")
    ax.plot([r["tau"] for r in rows], [r["false_support_rate"] for r in rows], color=ORANGE, label="false-SUPPORT rate")
    ax.plot([r["tau"] for r in rows], [r["coverage"] for r in rows], color=GREY, linestyle="--", label="coverage (not abstained)")
    ax.axvline(run["config"]["tau"], color="black", linestyle=":", label=f"chosen tau={run['config']['tau']} (tuned on {run['tau_tuning'].get('split')})")
    ax.set_xlabel("confidence threshold tau")
    ax.set_title(f"{run['name']}: the accuracy / caution trade-off ({run['split']})")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / f"tau_{run['name']}.png", dpi=160)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="eval/results")
    ap.add_argument("--out", default=None)
    ap.add_argument("--run", action="append", default=[])
    ap.add_argument("--include-synthetic", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.results)
    out = Path(a.out) if a.out else root / "figures"
    out.mkdir(parents=True, exist_ok=True)
    runs = load_runs(root, a.include_synthetic)
    if not runs:
        print("No real runs found (synthetic runs are skipped). Run eval.run_eval first.")
        return
    f1_bars(runs, out)
    safety_bars(runs, out)
    recall_curves(runs, out)
    for r in runs:
        if r["name"] in a.run:
            confusion_plot(r, out)
            tau_plot(r, out)
    print(f"[saved] figures in {out}")


if __name__ == "__main__":
    main()
