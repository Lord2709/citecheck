"""What we store about use of the site, and how.  Owner: Engineering, with Users & Research.

Tables (in their own Postgres schema, "citecheck", which Supabase does NOT expose through its public REST API):
  users     one row per signed-in account: consent choices and first/last seen.  No e-mail address is stored
            here (Supabase Auth keeps it); the admin check uses the e-mail from the verified token.
  runs      one row per draft check or paper search: what was asked (as a length, or the text itself only when the
            person agreed to text storage), the summary counts and the full report shown to them.
  feedback  a judgement on one citation ("is this verdict right?", with the right answer when it is not) or on one
            paper-search result ("relevant to my direction?"), with an optional comment (stored only with text
            consent; e-mails and phone numbers are always masked).  Saved on the first click, refined afterwards.
  events    product activity (page views, button clicks), stored only when the person agreed to research use.

Each check records the model that produced it (`runs.options.model`), team accounts are flagged (`users.is_team`)
rather than removed, and a participant in a user study can enter the code the team gave them
(`users.participant_code`), so a session's notes can be matched to its usage without names.
Columns added after the first release are added to existing tables at start-up (`_add_missing_columns`).

Locally and in tests the same tables live in a SQLite file.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer, MetaData, String, Table, Text, create_engine,
                        delete, func, inspect, select, text)

from src.text_utils import redact


def now():
    return datetime.now(timezone.utc)


class Store:
    def __init__(self, url: str, schema: Optional[str] = "citecheck"):
        if url.startswith("sqlite:///"):
            from pathlib import Path

            path = url[len("sqlite:///"):]
            if path and path != ":memory:":
                Path(path).parent.mkdir(parents=True, exist_ok=True)
            self.engine = create_engine(url, connect_args={"check_same_thread": False}, future=True)
            schema = None                               # SQLite has no schemas
        else:
            self.engine = create_engine(url, pool_pre_ping=True, future=True)
        self.schema = schema
        md = MetaData(schema=schema)
        fk = (lambda t: f"{schema}.{t}") if schema else (lambda t: t)
        self.users = Table("users", md,
                           Column("id", String(64), primary_key=True),
                           Column("created_at", DateTime(timezone=True), default=now),
                           Column("last_seen", DateTime(timezone=True), default=now),
                           Column("consent_research", Boolean, nullable=True),
                           Column("consent_text", Boolean, default=False),
                           Column("consent_at", DateTime(timezone=True), nullable=True),
                           Column("participant_code", String(16), nullable=True),
                           Column("is_team", Boolean, nullable=True))
        self.runs = Table("runs", md,
                          Column("id", String(36), primary_key=True),
                          Column("user_id", String(64), ForeignKey(fk("users.id")), index=True),
                          Column("kind", String(20)),                # draft_check | discovery | claim_check
                          Column("created_at", DateTime(timezone=True), default=now),
                          Column("finished_at", DateTime(timezone=True), nullable=True),
                          Column("status", String(12), default="running"),
                          Column("input_chars", Integer, default=0),
                          Column("input_text", Text, nullable=True),  # only with consent_text
                          Column("options", JSON, nullable=True),
                          Column("summary", JSON, nullable=True),
                          Column("report", JSON, nullable=True),
                          Column("seconds", Integer, nullable=True),
                          Column("error", Text, nullable=True))
        self.feedback = Table("feedback", md,
                              Column("id", Integer, primary_key=True, autoincrement=True),
                              Column("user_id", String(64), ForeignKey(fk("users.id")), index=True),
                              Column("run_id", String(36), nullable=True, index=True),
                              Column("citation_index", Integer, nullable=True),   # citation number, or result rank
                              Column("agrees", Boolean),                            # None = "not sure"
                              Column("comment_chars", Integer, default=0),
                              Column("comment", Text, nullable=True),
                              Column("created_at", DateTime(timezone=True), default=now),
                              Column("kind", String(12), nullable=True),            # citation (default) | paper
                              Column("label", String(20), nullable=True),           # the answer (api/main.py)
                              Column("item_id", String(200), nullable=True),        # paper id of a search result
                              Column("updated_at", DateTime(timezone=True), nullable=True))
        self.events = Table("events", md,
                            Column("id", Integer, primary_key=True, autoincrement=True),
                            Column("user_id", String(64), ForeignKey(fk("users.id")), index=True),
                            Column("session_id", String(64), nullable=True),
                            Column("event", String(40)),
                            Column("props", JSON, nullable=True),
                            Column("created_at", DateTime(timezone=True), default=now))
        if schema:
            with self.engine.begin() as c:
                c.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
        md.create_all(self.engine)
        self._add_missing_columns()

    def _add_missing_columns(self):
        """create_all() never changes an existing table: add the columns introduced after the first release."""
        insp = inspect(self.engine)
        for table in (self.users, self.runs, self.feedback, self.events):
            have = {c["name"] for c in insp.get_columns(table.name, schema=self.schema)}
            for col in table.columns:
                if col.name in have:
                    continue
                name = f'"{self.schema}"."{table.name}"' if self.schema else table.name
                ddl = col.type.compile(dialect=self.engine.dialect)
                with self.engine.begin() as c:
                    c.execute(text(f'ALTER TABLE {name} ADD COLUMN "{col.name}" {ddl}'))

    # ---- users -----------------------------------------------------------------------------
    def touch_user(self, user_id: str, is_team: Optional[bool] = None) -> dict:
        with self.engine.begin() as c:
            row = c.execute(select(self.users).where(self.users.c.id == user_id)).mappings().first()
            if row is None:
                c.execute(self.users.insert().values(id=user_id, created_at=now(), last_seen=now(), is_team=is_team))
            else:
                values = {"last_seen": now()}
                if is_team is not None and row["is_team"] != is_team:
                    values["is_team"] = is_team
                c.execute(self.users.update().where(self.users.c.id == user_id).values(**values))
            row = c.execute(select(self.users).where(self.users.c.id == user_id)).mappings().first()
        return dict(row)

    def set_consent(self, user_id: str, research: bool, text_storage: bool, participant_code: Optional[str] = None):
        self.touch_user(user_id)
        with self.engine.begin() as c:
            c.execute(self.users.update().where(self.users.c.id == user_id).values(
                consent_research=bool(research), consent_text=bool(research and text_storage), consent_at=now(),
                participant_code=(participant_code or None) if research else None))

    def delete_user_data(self, user_id: str) -> dict:
        """Everything stored about this account in our tables (the sign-in account itself lives in Supabase Auth)."""
        out = {}
        with self.engine.begin() as c:
            for name, table in (("feedback", self.feedback), ("events", self.events), ("checks", self.runs)):
                out[name] = c.execute(delete(table).where(table.c.user_id == user_id)).rowcount
            c.execute(delete(self.users).where(self.users.c.id == user_id))
        return out

    # ---- runs ------------------------------------------------------------------------------
    def create_run(self, user: dict, kind: str, input_text: str, options: Optional[dict] = None) -> str:
        rid = str(uuid.uuid4())
        with self.engine.begin() as c:
            c.execute(self.runs.insert().values(
                id=rid, user_id=user["id"], kind=kind, created_at=now(), status="running",
                input_chars=len(input_text or ""), options=options or {},
                input_text=redact(input_text) if user.get("consent_text") else None))
        return rid

    def finish_run(self, run_id: str, report: Optional[dict], summary: Optional[dict], seconds: float,
                   error: Optional[str] = None):
        with self.engine.begin() as c:
            c.execute(self.runs.update().where(self.runs.c.id == run_id).values(
                status="error" if error else "done", finished_at=now(), report=report, summary=summary,
                seconds=int(round(seconds)), error=error))

    def update_report(self, run_id: str, user_id: str, report: dict, summary: dict) -> bool:
        with self.engine.begin() as c:
            res = c.execute(self.runs.update().where(self.runs.c.id == run_id, self.runs.c.user_id == user_id)
                            .values(report=report, summary=summary))
        return res.rowcount == 1

    def get_run(self, run_id: str, user_id: str) -> Optional[dict]:
        with self.engine.connect() as c:
            row = c.execute(select(self.runs).where(self.runs.c.id == run_id, self.runs.c.user_id == user_id)).mappings().first()
        return dict(row) if row else None

    def list_runs(self, user_id: str, limit: int = 50) -> list:
        cols = [self.runs.c.id, self.runs.c.kind, self.runs.c.created_at, self.runs.c.status, self.runs.c.summary,
                self.runs.c.input_chars]
        with self.engine.connect() as c:
            rows = c.execute(select(*cols).where(self.runs.c.user_id == user_id)
                             .order_by(self.runs.c.created_at.desc()).limit(limit)).mappings().all()
        return [dict(r) for r in rows]

    # ---- feedback and events ---------------------------------------------------------------
    def add_feedback(self, user: dict, run_id: Optional[str], citation_index: Optional[int], agrees: Optional[bool],
                     comment: str = "", kind: str = "citation", label: Optional[str] = None,
                     item_id: Optional[str] = None) -> int:
        comment = (comment or "").strip()[:2000]
        with self.engine.begin() as c:
            res = c.execute(self.feedback.insert().values(
                user_id=user["id"], run_id=run_id, citation_index=citation_index, agrees=agrees,
                comment_chars=len(comment), comment=redact(comment) if (comment and user.get("consent_text")) else None,
                created_at=now(), kind=kind, label=label, item_id=(item_id or None)))
            return int(res.inserted_primary_key[0])

    def update_feedback(self, feedback_id: int, user: dict, agrees: Optional[bool] = None, label: Optional[str] = None,
                        comment: Optional[str] = None) -> bool:
        """Refine one's own earlier answer (the right answer after a "No", or a comment)."""
        values = {"updated_at": now()}
        if label is not None:
            values["label"], values["agrees"] = label, agrees
        if comment is not None:
            comment = comment.strip()[:2000]
            values["comment_chars"] = len(comment)
            values["comment"] = redact(comment) if (comment and user.get("consent_text")) else None
        with self.engine.begin() as c:
            res = c.execute(self.feedback.update().where(self.feedback.c.id == feedback_id,
                                                         self.feedback.c.user_id == user["id"]).values(**values))
        return res.rowcount == 1

    def add_event(self, user: dict, event: str, props: Optional[dict], session_id: Optional[str]) -> bool:
        if not user.get("consent_research"):
            return False
        props = {k: v for k, v in (props or {}).items() if isinstance(v, (str, int, float, bool)) and len(str(v)) <= 200}
        with self.engine.begin() as c:
            c.execute(self.events.insert().values(user_id=user["id"], session_id=(session_id or "")[:64],
                                                  event=event[:40], props=props, created_at=now()))
        return True

    # ---- research export --------------------------------------------------------------------
    def export(self, salt: str) -> dict:
        """Everything a research write-up may need, with user ids replaced by salted hashes and no free text.
        Only people who agreed to research use are included.  Team accounts are included and flagged (`team`), so
        an analysis can count participants honestly.  `citations` has one row per citation checked, with the
        model that checked it and the person's judgement, if they gave one."""
        h = lambda uid: hashlib.sha256(f"{salt}:{uid}".encode()).hexdigest()[:12]  # noqa: E731
        iso = lambda d: d.isoformat() if d else None  # noqa: E731
        with self.engine.connect() as c:
            consented = select(self.users).where(self.users.c.consent_research.is_(True))
            people = [dict(r) for r in c.execute(consented).mappings()]
            ok = {p["id"] for p in people}
            runs = [dict(r) for r in c.execute(select(self.runs).order_by(self.runs.c.created_at)).mappings()
                    if r["user_id"] in ok]
            fb = [dict(r) for r in c.execute(select(self.feedback).order_by(self.feedback.c.id)).mappings()
                  if r["user_id"] in ok]
            ev = [dict(r) for r in c.execute(select(self.events)).mappings() if r["user_id"] in ok]
            n_users = c.execute(select(func.count()).select_from(self.users)).scalar()
        judged = {}
        for r in fb:                                     # the latest answer per citation wins
            if (r["kind"] or "citation") == "citation" and r["run_id"]:
                judged[(r["run_id"], r["citation_index"])] = r
        citations = []
        for r in runs:
            rep, opts = r["report"] or {}, r["options"] or {}
            backend = rep.get("backend") or {}
            for cit in rep.get("citations") or []:
                v, p = cit.get("verdict") or {}, cit.get("paper") or {}
                j = judged.get((r["id"], cit.get("index")))
                citations.append({
                    "user": h(r["user_id"]), "run": r["id"][:8], "created_at": iso(r["created_at"]),
                    "model": opts.get("model") or backend.get("verifier"), "tau": opts.get("tau", backend.get("tau")),
                    "index": cit.get("index"), "status": cit.get("status"), "verdict": v.get("label"),
                    "confidence": v.get("confidence"), "read_full_text": bool(cit.get("read_full_text")),
                    "abstract_pasted": bool(cit.get("abstract_pasted")), "suggestion": bool(cit.get("suggestions")),
                    "paper_id": p.get("paper_id"),
                    "judgement_agrees": j["agrees"] if j else None, "judgement_label": j["label"] if j else None})
        return {
            "generated_at": now().isoformat(), "users_total": n_users, "users_consented": len(ok),
            "users": [{"user": h(p["id"]), "participant_code": p["participant_code"], "team": bool(p["is_team"]),
                       "keeps_text": bool(p["consent_text"]), "first_seen": iso(p["created_at"]),
                       "last_seen": iso(p["last_seen"])} for p in people],
            "runs": [{"user": h(r["user_id"]), "run": r["id"][:8], "kind": r["kind"],
                      "created_at": iso(r["created_at"]), "status": r["status"], "seconds": r["seconds"],
                      "input_chars": r["input_chars"],
                      "options": r["options"], "summary": r["summary"]} for r in runs],
            "citations": citations,
            "feedback": [{"user": h(r["user_id"]), "run": (r["run_id"] or "")[:8], "kind": r["kind"] or "citation",
                          "index": r["citation_index"], "item_id": r["item_id"], "agrees": r["agrees"],
                          "label": r["label"], "comment_chars": r["comment_chars"], "created_at": iso(r["created_at"]),
                          "updated_at": iso(r["updated_at"])} for r in fb],
            "events": [{"user": h(r["user_id"]), "session": hashlib.sha256((r["session_id"] or "").encode()).hexdigest()[:8],
                        "event": r["event"], "props": r["props"], "created_at": iso(r["created_at"])} for r in ev],
            "note": "user ids are salted hashes; team accounts are flagged, not removed; free text (drafts, comments) "
                    "is never exported",
        }


def json_safe(row: dict) -> dict:
    return json.loads(json.dumps(row, default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o)))
