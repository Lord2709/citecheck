"""Configuration of the web API, from environment variables (all optional for local development).

  CITECHECK_AUTH           supabase (default when SUPABASE_URL is set) | off (local development and tests only)
  SUPABASE_URL             https://<project>.supabase.co
  SUPABASE_ANON_KEY        the project's public anon key (safe to expose; the frontend needs it too)
  DATABASE_URL             postgresql+psycopg://...  (Supabase connection string); default: a local SQLite file
  CITECHECK_DB_SCHEMA      Postgres schema for our tables (default "citecheck": NOT exposed by Supabase's REST API)
  CITECHECK_ADMIN_EMAILS   comma-separated e-mails allowed to download the anonymised research export
  CITECHECK_ORIGINS        comma-separated allowed browser origins (CORS); same-origin needs nothing
  CITECHECK_EXPORT_SALT    salt for hashing user ids in the research export (set it in production)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _list(name: str) -> list:
    return [x.strip() for x in os.environ.get(name, "").split(",") if x.strip()]


@dataclass
class Settings:
    auth_mode: str = "off"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    database_url: str = "sqlite:///data/cache/citecheck_web.db"
    db_schema: str = "citecheck"
    admin_emails: list = field(default_factory=list)
    origins: list = field(default_factory=list)
    export_salt: str = "citecheck-dev-salt"
    max_text_chars: int = 60_000
    max_pdf_bytes: int = 15_000_000
    max_citations: int = 30
    draft_checks_per_minute: int = 6
    searches_per_minute: int = 20
    dev_user_email: str = "dev@localhost"


def load_settings() -> Settings:
    s = Settings()
    s.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    s.supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
    s.auth_mode = os.environ.get("CITECHECK_AUTH", "supabase" if s.supabase_url else "off").lower()
    s.database_url = os.environ.get("DATABASE_URL", s.database_url)
    s.db_schema = os.environ.get("CITECHECK_DB_SCHEMA", s.db_schema)
    s.admin_emails = [e.lower() for e in _list("CITECHECK_ADMIN_EMAILS")]
    s.origins = _list("CITECHECK_ORIGINS")
    s.export_salt = os.environ.get("CITECHECK_EXPORT_SALT", s.export_salt)
    if s.auth_mode == "supabase" and not (s.supabase_url and s.supabase_anon_key):
        raise RuntimeError("CITECHECK_AUTH=supabase needs SUPABASE_URL and SUPABASE_ANON_KEY")
    if s.auth_mode not in ("supabase", "off"):
        raise RuntimeError("CITECHECK_AUTH must be 'supabase' or 'off'")
    return s
