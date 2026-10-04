"""Pre-demo check: run on the PRESENTING laptop the day before and an hour before.  Owner: Engineering (Sakshaat).

    python -m tools.demo_check              # Wi-Fi-off rehearsal: the model must load from the local cache
    python -m tools.demo_check --online     # allow model downloads (first run on a new laptop)

Automates the "Pre-demo checklist" in docs/midterm_oct6.md:

  1. no CITECHECK_* override is set (otherwise the sidebar says UNVALIDATED and the demo is not the evaluated model)
  2. the pipeline builds with NO fallback, offline by default (HF_HUB_OFFLINE=1): the "Wi-Fi off" check
  3. the sidebar would say "Validated configuration <run>" with the dev numbers from deployed_config.json
  4. every example in demo/demo_examples.json gives, through the app's paste-an-abstract path, the verdict recorded when it
     was picked (main examples must match; a backup that changed is a warning)
  5. the code is what is on origin/main (warning only)

Writes demo/DEMO_CHECK.md (commit it: it is the evidence that the demo was checked on the machine that presents).
Exit code 1 if anything FAILs.

demo/demo_examples.json contract (written by `python -m eval.pick_demo_examples`):
  {"examples": [{"slot", "role": "main"|"backup", "claim_id", "claim", "title", "abstract", "gold", "verdict"}, ...],
   "failure": {... same keys, role "honest failure"} | null}
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
MODEL_ENV = ("CITECHECK_RETRIEVER", "CITECHECK_VERIFIER", "CITECHECK_EMBED_MODEL", "CITECHECK_K", "CITECHECK_TAU",
             "CITECHECK_MARGIN")


def _git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def check_overrides(environ=None) -> tuple:
    env = os.environ if environ is None else environ
    set_ = [v for v in MODEL_ENV if env.get(v)]
    if set_:
        return ("no model overrides", FAIL, f"unset {', '.join(set_)} (they make the configuration UNVALIDATED)")
    return ("no model overrides", PASS, "none of " + ", ".join(MODEL_ENV) + " is set")


def check_backend(pipe) -> tuple:
    m = pipe.meta
    if m.get("demo_only"):
        return ("validated backend", FAIL, "DEMO BACKEND (word overlap): the neural model did not load")
    if not m.get("validated"):
        return ("validated backend", FAIL, "UNVALIDATED: no deployed run, or settings overridden")
    lo, hi = m.get("dev_macro_f1_ci95") or (float("nan"), float("nan"))
    return ("validated backend", PASS,
            f"sidebar: Validated configuration `{m.get('deployed_run')}`, dev macro-F1 {m.get('dev_macro_f1'):.2f} "
            f"(95% CI {lo:.2f} to {hi:.2f}), false-SUPPORT {m.get('dev_false_support_rate'):.2f}; "
            f"verifier `{m.get('verifier')}`, tau {m.get('tau')}")


def load_examples(path: Path) -> list:
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(j.get("examples") or []) + ([j["failure"]] if j.get("failure") else [])


def check_examples(pipe, examples: list) -> list:
    from src.ingest import paper_from_text

    rows = []
    for e in examples:
        name = f"example {e.get('slot')} (claim #{e.get('claim_id')})"
        t0 = time.perf_counter()
        try:
            v = pipe.verify_against_paper(e["claim"], paper_from_text(e.get("title", ""), e["abstract"]))
        except Exception as ex:  # a crash on stage is the worst outcome: report it, keep checking the rest
            rows.append((name, FAIL, f"crashed: {type(ex).__name__}: {ex}"))
            continue
        ms = 1000 * (time.perf_counter() - t0)
        same = v.label == e.get("verdict")
        status = PASS if same else (FAIL if e.get("role") == "main" else WARN)
        rows.append((name, status, f"got {v.display_label} {v.confidence:.2f} (expected {e.get('verdict')}), "
                                   f"SciFact gold {e.get('gold')}, {ms:.0f} ms"))
    return rows


def check_git() -> tuple:
    head, main = _git("rev-parse", "HEAD"), _git("rev-parse", "origin/main")
    if not head:
        return ("code is origin/main", WARN, "not a git checkout")
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    if head != main:
        return ("code is origin/main", WARN, f"HEAD {head[:7]} != origin/main {main[:7] or '?'}: `git checkout main && git pull`")
    if dirty:
        return ("code is origin/main", WARN, "tracked files modified locally (line endings? `git config core.autocrlf true`)")
    return ("code is origin/main", PASS, f"HEAD = origin/main = {head[:7]} (last fetch)")


def run(examples_path: Path, online: bool = False, pipe=None, environ=None) -> list:
    rows = [check_overrides(environ)]
    if pipe is None:
        if not online:  # must be set before transformers is imported
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from src.pipeline import build_pipeline

        t0 = time.perf_counter()
        try:
            pipe = build_pipeline(allow_fallback=False)
        except Exception as e:
            hint = " (offline: run once with --online on Wi-Fi to cache the model)" if not online else ""
            return rows + [("pipeline builds" + (" offline" if not online else ""), FAIL, f"{type(e).__name__}: {e}{hint}")]
        rows.append(("pipeline builds" + (" offline" if not online else ""), PASS,
                     f"{1000 * (time.perf_counter() - t0):.0f} ms; corpus search {'on' if pipe.has_corpus else 'OFF'}"))
    rows.append(check_backend(pipe))
    for w in pipe.warnings:
        rows.append(("pipeline warning", WARN, w))
    if Path(examples_path).exists():
        rows += check_examples(pipe, load_examples(examples_path))
    else:
        rows.append(("demo examples", FAIL, f"{examples_path} missing: run `python -m eval.pick_demo_examples`"))
    rows.append(check_git())
    return rows


def render(rows: list, online: bool) -> str:
    worst = FAIL if any(r[1] == FAIL for r in rows) else (WARN if any(r[1] == WARN for r in rows) else PASS)
    lines = ["# Demo check (generated by `python -m tools.demo_check`; do not edit by hand)", "",
             f"- when: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
             f"- machine: {platform.platform()}, Python {platform.python_version()}, processor {platform.processor() or '?'}",
             f"- network: {'allowed (--online)' if online else 'model loaded OFFLINE (HF_HUB_OFFLINE=1)'}",
             f"- overall: **{worst}**", "", "| check | result | detail |", "|---|---|---|"]
    lines += [f"| {n} | {s} | {d.replace('|', '/')} |" for n, s, d in rows]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--examples", default=os.environ.get("CITECHECK_DEMO_EXAMPLES", "demo/demo_examples.json"))
    ap.add_argument("--online", action="store_true")
    ap.add_argument("--out", default="demo/DEMO_CHECK.md")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)
    rows = run(Path(a.examples), online=a.online)
    text = render(rows, a.online)
    print(text)
    if not a.no_write:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    return 1 if any(r[1] == FAIL for r in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
