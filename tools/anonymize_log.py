"""Anonymize app usage logs before committing them.   Owner: Users & Research (Ritika).

    python -m tools.anonymize_log logs/usage.jsonl --out evidence/session05/usage_logs --scrub "Alice Smith,Bob"

  * session_id -> salted hash (same person keeps the same pseudonym, but it can't be looked up)
  * free-text fields are DROPPED unless --keep-text; kept text is re-redacted (e-mails/phones) and every --scrub name is masked
  * splits the log into one file per participant code (P01.jsonl ...); events with no participant go to unassigned.jsonl
  * refuses to write a file that still contains an '@'
Raw, un-anonymized material (recordings, notes with names) belongs in evidence/**/raw_unredacted/ which is git-ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from src.text_utils import redact

TEXT_KEYS = ("claim", "comment", "abstract", "direction", "identifier", "notes")


def anonymize_record(rec: dict, salt: str, keep_text=False, scrub=()) -> dict:
    out = dict(rec)
    if out.get("session_id"):
        out["session_id"] = hashlib.sha256((salt + str(out["session_id"])).encode()).hexdigest()[:12]
    for k in TEXT_KEYS:
        if k in out:
            if not keep_text:
                del out[k]
            else:
                text = redact(str(out[k]))
                for name in scrub:
                    if name.strip():
                        text = re.sub(re.escape(name.strip()), "[name]", text, flags=re.I)
                out[k] = text
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--salt", default="citecheck")
    ap.add_argument("--keep-text", action="store_true", help="only for participants who consented to text logging")
    ap.add_argument("--scrub", default="", help="comma-separated names to mask")
    a = ap.parse_args(argv)
    scrub = [s for s in a.scrub.split(",") if s.strip()]

    by_p = defaultdict(list)
    for path in a.logs:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = anonymize_record(json.loads(line), a.salt, a.keep_text, scrub)
                by_p[re.sub(r"[^A-Za-z0-9_-]", "", rec.get("participant") or "") or "unassigned"].append(rec)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for p, recs in by_p.items():
        body = "\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n"
        if "@" in body:
            raise SystemExit(f"refusing to write {p}.jsonl: it still contains an '@' (e-mail?). Inspect the raw log.")
        with open(out / f"{p}.jsonl", "w", encoding="utf-8", newline="\n") as f:  # Path.write_text(newline=) needs Python 3.10
            f.write(body)
    print({p: len(r) for p, r in by_p.items()}, "->", out)


if __name__ == "__main__":
    main()
