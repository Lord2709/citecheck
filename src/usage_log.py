"""Privacy-preserving usage log: the raw material for user evidence.   Owner: Engineering (Sakshaat).

One JSON object per line, e.g.

  {"ts": "2026-09-29T15:02:11+00:00", "session_id": "9f1c...", "participant": "P01", "event": "verify",
   "claim_len": 88, "mode": "paper", "verdict": "SUPPORT", "confidence": 0.91, "latency_ms": 412.3}

Rules:
  * Free text (claims, comments, abstracts) is NOT stored unless `log_text=True` (the researcher panel turns this
    on only when the participant has consented), and e-mails / phone numbers are always redacted.
  * The participant is a code (P01, P02...) chosen by the researcher: never a name or e-mail.
  * Logs go to logs/ (git-ignored).  Anonymize with tools/anonymize_log.py, then commit to evidence/sessionNN/.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .text_utils import redact

TEXT_KEYS = ("claim", "comment", "abstract", "direction", "identifier", "notes")


class UsageLogger:
    def __init__(self, path="logs/usage.jsonl", enabled: bool = True, log_text: bool = False,
                 participant: Optional[str] = None, session_id: Optional[str] = None):
        self.path = Path(path)
        self.enabled = enabled
        self.log_text = log_text
        self.participant = participant
        self.session_id = session_id or uuid.uuid4().hex

    def log(self, event: str, **payload) -> dict:
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_id": self.session_id,
            "participant": self.participant,
            "event": event,
        }
        for key, val in payload.items():
            if key in TEXT_KEYS and isinstance(val, str):
                rec[f"{key}_len"] = len(val)
                if self.log_text:
                    rec[key] = redact(val)
            else:
                rec[key] = val
        if self.enabled:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec
