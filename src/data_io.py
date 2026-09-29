"""Loading SciFact-format data.  Owner: Data & Evaluation (Sahil).

Schema (verified against https://github.com/allenai/scifact/blob/master/doc/data.md):

  corpus.jsonl : {"doc_id": int, "title": str, "abstract": [str, ...], "structured": bool}
  claims_*.jsonl: {"id": int, "claim": str,
                   "evidence": {doc_id: [{"label": "SUPPORT"|"CONTRADICT", "sentences": [int, ...]}]},
                   "cited_doc_ids": [int, ...]}

* A claim with an EMPTY evidence dict is NOT_ENOUGH_INFO (we call it NEI).
* claims_test.jsonl ships WITHOUT evidence: it cannot be scored locally.
* SciFact claims are citation sentences re-written into atomic claims, and
  cited_doc_ids are the papers that citation pointed to.  That is exactly the
  "does the cited paper support this claim" task CiteCheck targets.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from .schema import CONTRADICT, NEI, SUPPORT, Doc

MIXED = "MIXED"  # claim whose evidence documents disagree (rare); excluded from 3-class metrics


def load_jsonl(path) -> list:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no}: invalid JSON ({e})") from e
    return rows


def load_corpus(path) -> list:
    """corpus.jsonl -> list[Doc]  (doc_id is stored as str everywhere in our code)."""
    docs = []
    for row in load_jsonl(path):
        docs.append(
            Doc(
                doc_id=str(row["doc_id"]),
                title=row.get("title", "") or "",
                sentences=tuple(row.get("abstract", []) or []),
                source="scifact",
            )
        )
    return docs


@dataclass
class ClaimRecord:
    id: int
    claim: str
    evidence: dict = field(default_factory=dict)  # {doc_id(str): [{"label":..., "sentences":[...]}]}
    cited_doc_ids: list = field(default_factory=list)  # list[str]

    # ---- gold structure ---------------------------------------------------
    @property
    def gold_doc_labels(self) -> dict:
        """doc_id -> SUPPORT | CONTRADICT | MIXED (label of that abstract)."""
        out = {}
        for doc_id, rationales in self.evidence.items():
            labels = {r["label"] for r in rationales}
            out[str(doc_id)] = labels.pop() if len(labels) == 1 else MIXED
        return out

    @property
    def gold_docs(self) -> list:
        return sorted(self.gold_doc_labels)

    @property
    def gold_label(self) -> str:
        """Claim-level label: SUPPORT / CONTRADICT / NEI / MIXED."""
        labels = set(self.gold_doc_labels.values())
        if not labels:
            return NEI
        if labels == {SUPPORT}:
            return SUPPORT
        if labels == {CONTRADICT}:
            return CONTRADICT
        return MIXED

    def rationale_sets(self, doc_id) -> list:
        return [sorted(r["sentences"]) for r in self.evidence.get(str(doc_id), [])]

    def rationale_sentence_idxs(self, doc_id) -> list:
        idxs = set()
        for r in self.rationale_sets(doc_id):
            idxs.update(r)
        return sorted(idxs)


def load_claims(path) -> list:
    """claims_*.jsonl -> list[ClaimRecord]; tolerates a missing 'evidence' key (test split)."""
    records = []
    for row in load_jsonl(path):
        evidence = {str(k): v for k, v in (row.get("evidence") or {}).items()}
        records.append(
            ClaimRecord(
                id=int(row["id"]),
                claim=row["claim"],
                evidence=evidence,
                cited_doc_ids=[str(d) for d in row.get("cited_doc_ids", [])],
            )
        )
    return records


def split_has_labels(path) -> bool:
    """The public test split has no 'evidence' key at all."""
    rows = load_jsonl(path)
    return bool(rows) and all("evidence" in r for r in rows)


def find_scifact_dir(data_dir) -> Optional[Path]:
    """Return the directory that contains corpus.jsonl (data_dir itself or data_dir/data)."""
    base = Path(data_dir)
    for cand in (base, base / "data", base / "scifact"):
        if (cand / "corpus.jsonl").exists():
            return cand
    return None


def label_distribution(claims: Iterable) -> dict:
    return dict(Counter(c.gold_label for c in claims))


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_synthetic_fixture(path) -> bool:
    """Numbers computed on tests/fixtures/** are plumbing checks, never reportable results."""
    return "fixtures" in Path(path).resolve().parts
