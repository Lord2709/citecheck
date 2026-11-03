"""CiteCheck web API (FastAPI) and the built React site.   Owner: Engineering.

    uvicorn --factory api.main:create_app --reload --port 8000    # API on :8000 (the React dev server proxies /api)

The verdicts come from the same agent and evaluated verifier as the Streamlit app (src/agent.py, src/pipeline.py).
Every endpoint except /api/health and /api/config needs a signed-in user (see api/auth.py).
"""
from __future__ import annotations

import copy
import re
import threading
from contextlib import asynccontextmanager
import time
from pathlib import Path
from typing import Callable, Optional

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from api.auth import AuthError, TokenVerifier, User
from api.db import Store, json_safe
from api.jobs import JobManager
from api.ratelimit import RateLimiter
from api.settings import Settings, load_settings
from src.agent import CitationResult
from src.ingest import IngestError, paper_from_text
from src.pdf_check import PdfRejected, check_pdf, extract_page_texts
from src.report import summarize, to_markdown

WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
EVENT_NAME = re.compile(r"^[a-z][a-z0-9_]{0,39}$")


# ---- request bodies -------------------------------------------------------------------------------
class DraftIn(BaseModel):
    text: str
    read_full_text: bool = True
    suggest: bool = True
    max_citations: int = Field(20, ge=1, le=40)


class RecheckIn(BaseModel):
    run_id: str
    citation_index: int
    title: str = ""
    abstract: str


class DiscoverIn(BaseModel):
    direction: str
    k: int = Field(10, ge=3, le=25)


class ClaimIn(BaseModel):
    claim: str
    identifier: str = ""
    title: str = ""
    abstract: str = ""
    read_full_text: bool = True


class FeedbackIn(BaseModel):
    run_id: Optional[str] = None
    citation_index: Optional[int] = None
    agrees: bool
    comment: str = ""


class EventIn(BaseModel):
    event: str
    props: dict = Field(default_factory=dict)
    session_id: str = ""


class ConsentIn(BaseModel):
    research: bool
    text: bool = False


def default_agent_factory():
    from src.agent import build_agent
    from src.ingest import Fetcher
    from src.pipeline import build_pipeline

    pipe = build_pipeline()
    return build_agent(pipe, Fetcher())


def create_app(settings: Optional[Settings] = None, agent_factory: Optional[Callable] = None,
               store: Optional[Store] = None, verifier: Optional[TokenVerifier] = None,
               inline_jobs: bool = False, warm: bool = True) -> FastAPI:
    settings = settings or load_settings()
    store = store or Store(settings.database_url, settings.db_schema)
    verifier = verifier or TokenVerifier(settings)
    jobs = JobManager(inline=inline_jobs)
    limiter = RateLimiter()
    agent_factory = agent_factory or default_agent_factory
    state = {"agent": None, "error": None}
    agent_lock = threading.Lock()

    def get_agent():
        with agent_lock:
            if state["agent"] is None:
                try:
                    state["agent"] = agent_factory()
                    state["error"] = None
                except Exception as e:
                    state["error"] = f"{type(e).__name__}: {e}"
                    raise HTTPException(503, "The model is not available right now. Please try again in a minute.")
            return state["agent"]

    def warm_up():  # load the model in the background so the first visitor does not wait for it
        try:
            get_agent()
        except Exception:
            pass

    @asynccontextmanager
    async def lifespan(_app):
        if warm:
            threading.Thread(target=warm_up, daemon=True).start()
        yield

    app = FastAPI(title="CiteCheck API", version="1.0", docs_url="/api/docs", openapi_url="/api/openapi.json",
                  lifespan=lifespan)
    if settings.origins:
        app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=False,
                           allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resp.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return resp

    # ---- who is calling ----------------------------------------------------------------------------
    def current(authorization: Optional[str] = Header(None)) -> dict:
        try:
            user: User = verifier.verify(authorization)
        except AuthError as e:
            raise HTTPException(401, str(e))
        row = store.touch_user(user.id)
        row["email"] = user.email
        row["is_admin"] = bool(user.email and user.email in settings.admin_emails)
        return row

    def limit(user: dict, action: str, per_minute: int):
        if not limiter.allow(f"{user['id']}:{action}", per_minute):
            raise HTTPException(429, "You are going a bit fast. Please wait a minute and try again.")

    # ---- public ------------------------------------------------------------------------------------
    @app.get("/api/health")
    def health():
        return {"ok": True, "model_loaded": state["agent"] is not None, "model_error": state["error"]}

    @app.get("/api/config")
    def config():
        return {"auth": settings.auth_mode, "supabase_url": settings.supabase_url,
                "supabase_anon_key": settings.supabase_anon_key}

    # ---- account -----------------------------------------------------------------------------------
    @app.get("/api/me")
    def me(user: dict = Depends(current)):
        return {"id": user["id"], "email": user["email"], "is_admin": user["is_admin"],
                "consent": {"research": user["consent_research"], "text": bool(user["consent_text"])},
                "needs_consent": user["consent_research"] is None}

    @app.post("/api/me/consent")
    def consent(body: ConsentIn, user: dict = Depends(current)):
        store.set_consent(user["id"], body.research, body.text)
        return {"ok": True, "consent": {"research": body.research, "text": bool(body.research and body.text)}}

    @app.get("/api/status")
    def status(user: dict = Depends(current)):
        meta = dict(get_agent().pipe.meta)
        return {"model": meta, "agent_note": "Verdicts come from the evaluated verifier above. The agent as a whole "
                "(full-text reading, suggested papers) is evaluated by the swap test in eval/results/agent_swap_dev."}

    # ---- checking a draft ------------------------------------------------------------------------------
    def start_check(user: dict, text: str, options: dict, kind_input: str):
        if not text.strip():
            raise HTTPException(422, "Paste your text (with its reference list) first.")
        if len(text) > settings.max_text_chars:
            raise HTTPException(413, f"That text is longer than {settings.max_text_chars:,} characters. "
                                     "Check one section at a time.")
        limit(user, "draft", settings.draft_checks_per_minute)
        agent = get_agent()
        plan = agent.plan(text)
        if plan.kind == "discover":
            return {"plan": "discover", "message": "I found no citations in this text. It looks like a research "
                    "direction: try Find papers instead."}
        options = dict(options, max_citations=min(int(options.get("max_citations", 20)), settings.max_citations),
                       source=kind_input)
        run_id = store.create_run(user, "draft_check", text, options)

        def finished(job, report, seconds, error):
            store.finish_run(run_id, report, summarize(report) if report else None, seconds, error)

        job = jobs.start_draft_check(agent, text, user["id"], run_id, options, finished)
        return {"plan": "verify_draft", "job_id": job.id, "run_id": run_id}

    @app.post("/api/check-draft")
    def check_draft(body: DraftIn, user: dict = Depends(current)):
        return start_check(user, body.text, {"read_full_text": body.read_full_text, "suggest": body.suggest,
                                             "max_citations": body.max_citations}, "text")

    @app.post("/api/check-pdf")
    async def check_pdf_upload(file: UploadFile = File(...), read_full_text: bool = Form(True),
                               suggest: bool = Form(True), max_citations: int = Form(20),
                               user: dict = Depends(current)):
        data = await file.read(settings.max_pdf_bytes + 1)
        if len(data) > settings.max_pdf_bytes:
            raise HTTPException(413, "That PDF is too large. Upload a smaller file or paste the text.")
        try:
            verdict = check_pdf(data)
        except PdfRejected as e:
            raise HTTPException(422, str(e))
        if not verdict.accepted:
            store.add_event(user, "pdf_rejected", {"kind": verdict.kind, "pages": verdict.n_pages}, None)
            raise HTTPException(422, verdict.user_message())
        pages = extract_page_texts(data)
        text = "\n".join(pages[i] for i in verdict.text_pages)
        out = start_check(user, text, {"read_full_text": read_full_text, "suggest": suggest,
                                       "max_citations": max_citations}, "pdf")
        out["pdf"] = {"kind": verdict.kind, "pages": verdict.n_pages, "read_pages": len(verdict.text_pages),
                      "note": verdict.user_message()}
        return out

    @app.get("/api/jobs/{job_id}")
    def job_status(job_id: str, user: dict = Depends(current)):
        job = jobs.get(job_id, user["id"])
        if job is None:
            raise HTTPException(404, "That check has expired. Open it from your history instead.")
        return job.view()

    @app.post("/api/recheck")
    def recheck(body: RecheckIn, user: dict = Depends(current)):
        if not body.abstract.strip():
            raise HTTPException(422, "Paste the abstract first.")
        run = store.get_run(body.run_id, user["id"])
        if run is None or not run.get("report"):
            raise HTTPException(404, "Check not found (it may still be running).")
        rep = run["report"]
        cits = rep.get("citations") or []
        pos = next((i for i, c in enumerate(cits) if c.get("index") == body.citation_index), None)
        if pos is None:
            raise HTTPException(404, "Citation not found in that check.")
        new = get_agent().recheck_with_abstract(cits[pos], body.title, body.abstract)
        cits[pos] = new
        store.update_report(body.run_id, user["id"], rep, summarize(rep))
        store.add_event(user, "abstract_pasted", {"citation": body.citation_index, "verdict": new["verdict"]["label"]}, None)
        return {"citation": new, "summary": summarize(rep)}

    # ---- single claim, discovery ------------------------------------------------------------------------
    @app.post("/api/check-claim")
    def check_claim(body: ClaimIn, user: dict = Depends(current)):
        claim = body.claim.strip()
        if not claim:
            raise HTTPException(422, "Write the sentence you want to check.")
        limit(user, "claim", settings.searches_per_minute)
        agent = get_agent()
        try:
            if body.abstract.strip():
                paper = paper_from_text(body.title, body.abstract)
            elif body.identifier.strip():
                paper = agent.fetcher.fetch_paper(body.identifier)
            else:
                raise HTTPException(422, "Give the paper's DOI, arXiv id or link, or paste its abstract.")
        except IngestError as e:
            raise HTTPException(422, str(e))
        run_id = store.create_run(user, "claim_check", claim, {"source": "abstract" if body.abstract.strip() else "identifier"})
        t0 = time.time()
        a = copy.copy(agent)
        a.escalate = body.read_full_text
        v, read_ft, ft_src, sugg, steps = a.check_claim(claim, paper)
        c = CitationResult(index=1, sentence=claim, claim=claim, marker="", identifier=body.identifier or None,
                           paper=paper, verdict=v, read_full_text=read_ft, full_text_source=ft_src, suggestions=sugg,
                           steps=steps).to_dict()
        rep = {"kind": "draft_check", "citations": [c], "warnings": [], "backend": dict(agent.pipe.meta),
               "tau_strict": agent.tau_strict}
        store.finish_run(run_id, rep, summarize(rep), time.time() - t0)
        return {"run_id": run_id, "citation": c}

    @app.post("/api/discover")
    def discover(body: DiscoverIn, user: dict = Depends(current)):
        if not body.direction.strip():
            raise HTTPException(422, "Describe your research direction first (one or two sentences).")
        if len(body.direction) > 2000:
            raise HTTPException(413, "Please describe your direction in a few sentences.")
        limit(user, "discover", settings.searches_per_minute)
        run_id = store.create_run(user, "discovery", body.direction, {"k": body.k})
        t0 = time.time()
        try:
            rep = get_agent().discover(body.direction, k=body.k).to_dict()
        except ValueError as e:
            store.finish_run(run_id, None, None, time.time() - t0, str(e))
            raise HTTPException(422, str(e))
        store.finish_run(run_id, rep, {"results": len(rep["results"]), "failed_sources": sorted(rep["errors"])},
                         time.time() - t0)
        return dict(rep, run_id=run_id)

    # ---- feedback, activity, history ------------------------------------------------------------------------
    @app.post("/api/feedback")
    def feedback(body: FeedbackIn, user: dict = Depends(current)):
        store.add_feedback(user, body.run_id, body.citation_index, body.agrees, body.comment)
        return {"ok": True, "comment_stored": bool(body.comment.strip() and user["consent_text"])}

    @app.post("/api/events")
    def events(body: EventIn, user: dict = Depends(current)):
        if not EVENT_NAME.match(body.event):
            raise HTTPException(422, "bad event name")
        limit(user, "events", 120)
        return {"stored": store.add_event(user, body.event, body.props, body.session_id)}

    @app.get("/api/history")
    def history(user: dict = Depends(current)):
        return {"runs": [json_safe(r) for r in store.list_runs(user["id"])]}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str, user: dict = Depends(current)):
        run = store.get_run(run_id, user["id"])
        if run is None:
            raise HTTPException(404, "Not found.")
        run.pop("input_text", None)
        return json_safe(run)

    @app.get("/api/runs/{run_id}/report.md", response_class=PlainTextResponse)
    def run_markdown(run_id: str, user: dict = Depends(current)):
        run = store.get_run(run_id, user["id"])
        if run is None or not run.get("report"):
            raise HTTPException(404, "Not found.")
        return PlainTextResponse(to_markdown(run["report"]), media_type="text/markdown",
                                 headers={"Content-Disposition": f'attachment; filename="citecheck_{run_id[:8]}.md"'})

    @app.get("/api/admin/export")
    def admin_export(user: dict = Depends(current)):
        if not user["is_admin"]:
            raise HTTPException(403, "Only the research team can download the export.")
        return store.export(settings.export_salt)

    # ---- the React site --------------------------------------------------------------------------------------
    @app.get("/{full_path:path}", include_in_schema=False)
    def site(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse({"detail": "Not found."}, status_code=404)
        if not (WEB_DIST / "index.html").exists():
            return JSONResponse({"detail": "The website is not built. Run: cd web && npm ci && npm run build"},
                                status_code=404)
        f = (WEB_DIST / full_path).resolve()
        if full_path and f.is_file() and WEB_DIST.resolve() in f.parents:
            return FileResponse(f)
        return FileResponse(WEB_DIST / "index.html")

    app.state.store, app.state.jobs, app.state.settings = store, jobs, settings
    return app

