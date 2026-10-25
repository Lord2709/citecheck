"""Web API (api/) with fakes: deterministic verifier, invented papers, SQLite, no network, no real sign-in."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from api.auth import AuthError, TokenVerifier, User  # noqa: E402
from api.db import Store  # noqa: E402
from api.main import create_app  # noqa: E402
from api.settings import Settings  # noqa: E402
from src.agent import CiteCheckAgent  # noqa: E402
from src.data_io import load_corpus  # noqa: E402
from src.discovery import PaperSearch  # noqa: E402
from src.resolve import ReferenceResolver  # noqa: E402
from src.retrieval import BM25Retriever  # noqa: E402

from agent_fakes import FakeFetcher, make_pipeline, paper  # noqa: E402
from test_pdf_check import make_pdf  # noqa: E402

ZORVEX = paper("doi:10.1000/zorvex", "Zorvex and bone",
               "We studied zorvex in mice. Zorvex increases bone density in adult mice. The effect was dose dependent.",
               doi="10.1000/zorvex")
NOABS = paper("doi:10.1000/noabs", "Paywalled paper", "", doi="10.1000/noabs")
DRAFT = ("Zorvex increases bone density in adult mice [1]. Exercise improves sleep quality in older adults [2]. "
         "Coffee prevents all known cancers in humans [3].\n\nReferences\n"
         "[1] Doe. Zorvex and bone. 2021. doi:10.1000/zorvex\n[2] Roe. Paywalled. 2019. doi:10.1000/noabs\n")


def make_agent(fixture_dir):
    docs = load_corpus(fixture_dir / "corpus.jsonl")
    return CiteCheckAgent(make_pipeline(), fetcher=FakeFetcher({"10.1000/zorvex": ZORVEX, "10.1000/noabs": NOABS}),
                          resolver=ReferenceResolver(None), fulltext=None, search=lambda t, n: [ZORVEX],
                          discovery=PaperSearch(None, sources=("corpus",), retriever=BM25Retriever(docs)))


def client(tmp_path, fixture_dir, settings=None, verifier=None):
    s = settings or Settings(auth_mode="off", admin_emails=["dev@localhost"])
    app = create_app(s, agent_factory=lambda: make_agent(fixture_dir), store=Store(f"sqlite:///{tmp_path}/t.db"),
                     verifier=verifier, inline_jobs=True, warm=False)
    return TestClient(app), app


def test_public_endpoints_and_account(tmp_path, fixture_dir):
    c, _ = client(tmp_path, fixture_dir)
    assert c.get("/api/health").json()["ok"] is True
    assert c.get("/api/config").json()["auth"] == "off"
    me = c.get("/api/me").json()
    assert me["needs_consent"] is True and me["is_admin"] is True
    r = c.post("/api/me/consent", json={"research": False, "text": True}).json()
    assert r["consent"] == {"research": False, "text": False}          # text storage only with research consent
    assert c.get("/api/me").json()["needs_consent"] is False
    assert c.get("/api/status").json()["model"]["verifier"] == "keyword-fake"
    assert c.get("/api/nope").status_code == 404 and c.get("/api/runs/x").status_code == 404


def test_draft_check_job_history_report_and_recheck(tmp_path, fixture_dir):
    c, app = client(tmp_path, fixture_dir)
    c.post("/api/me/consent", json={"research": True, "text": False})
    start = c.post("/api/check-draft", json={"text": DRAFT, "read_full_text": False}).json()
    assert start["plan"] == "verify_draft"
    job = c.get(f"/api/jobs/{start['job_id']}").json()
    assert job["status"] == "done" and job["done"] == 3 and job["summary"]["supported"] == 1
    by = {x["marker"]: x for x in job["report"]["citations"]}
    assert by["[2]"]["status"] == "no_abstract" and by["[3]"]["status"] == "unresolved"
    runs = c.get("/api/history").json()["runs"]
    assert runs[0]["kind"] == "draft_check" and runs[0]["status"] == "done" and runs[0]["summary"]["citations"] == 3
    run = c.get(f"/api/runs/{start['run_id']}").json()
    assert "input_text" not in run and run["report"]["citations"]
    with app.state.store.engine.connect() as conn:                     # no text consent -> the draft is not stored
        stored = conn.execute(app.state.store.runs.select()).mappings().first()
    assert stored["input_text"] is None and stored["input_chars"] == len(DRAFT)
    md = c.get(f"/api/runs/{start['run_id']}/report.md")
    assert md.status_code == 200 and "# CiteCheck report" in md.text
    re = c.post("/api/recheck", json={"run_id": start["run_id"], "citation_index": by["[2]"]["index"], "title": "",
                                      "abstract": "We found that exercise improves sleep quality in older adults."}).json()
    assert re["citation"]["status"] == "checked" and re["citation"]["abstract_pasted"] and re["summary"]["supported"] == 2
    assert c.get(f"/api/runs/{start['run_id']}").json()["summary"]["supported"] == 2


def test_text_is_stored_only_with_consent(tmp_path, fixture_dir):
    c, app = client(tmp_path, fixture_dir)
    c.post("/api/me/consent", json={"research": True, "text": True})
    c.post("/api/check-draft", json={"text": DRAFT + " Contact me at a@b.org."})
    c.post("/api/feedback", json={"agrees": False, "comment": "Wrong for [3], mail x@y.com"})
    with app.state.store.engine.connect() as conn:
        run = conn.execute(app.state.store.runs.select()).mappings().first()
        fb = conn.execute(app.state.store.feedback.select()).mappings().first()
    assert "Zorvex" in run["input_text"] and "a@b.org" not in run["input_text"]          # stored, e-mail masked
    assert fb["comment"].endswith("[email]") and fb["agrees"] is False


def test_guidance_limits_and_errors(tmp_path, fixture_dir):
    c, _ = client(tmp_path, fixture_dir)
    assert c.post("/api/check-draft", json={"text": "  "}).status_code == 422
    plan = c.post("/api/check-draft", json={"text": "verifying scientific claims against abstracts"}).json()
    assert plan["plan"] == "discover" and "Find papers" in plan["message"]
    assert c.post("/api/check-draft", json={"text": "x" * 70_000}).status_code == 413
    codes = [c.post("/api/check-draft", json={"text": DRAFT, "suggest": False}).status_code for _ in range(8)]
    assert 429 in codes                                                  # draft checks are rate limited per user
    assert c.get("/api/jobs/unknown").status_code == 404
    assert c.post("/api/events", json={"event": "Bad Name!"}).status_code == 422


def test_pdf_upload_scanned_refused_text_accepted(tmp_path, fixture_dir):
    c, _ = client(tmp_path, fixture_dir)
    r = c.post("/api/check-pdf", files={"file": ("scan.pdf", make_pdf([None, None]), "application/pdf")})
    assert r.status_code == 422 and "scanned" in r.json()["detail"]
    body = (DRAFT + " ") * 3
    r = c.post("/api/check-pdf", files={"file": ("draft.pdf", make_pdf([body]), "application/pdf")},
               data={"suggest": "false"})
    assert r.status_code == 200 and r.json()["plan"] == "verify_draft" and r.json()["pdf"]["read_pages"] == 1


def test_discover_claim_feedback_events_and_export(tmp_path, fixture_dir):
    c, _ = client(tmp_path, fixture_dir)
    d = c.post("/api/discover", json={"direction": "bone density in mice", "k": 3}).json()
    assert d["kind"] == "discovery" and d["results"] and d["run_id"]
    one = c.post("/api/check-claim", json={"claim": "Zorvex increases bone density in adult mice.",
                                            "abstract": ZORVEX.abstract, "title": "Zorvex and bone"}).json()
    assert one["citation"]["verdict"]["label"] == "SUPPORT"
    assert c.post("/api/check-claim", json={"claim": "x y z"}).status_code == 422
    assert c.post("/api/events", json={"event": "page_view", "props": {"page": "check"}}).json()["stored"] is False
    c.post("/api/me/consent", json={"research": True})
    assert c.post("/api/events", json={"event": "page_view", "props": {"page": "check", "big": "x" * 500}}).json()["stored"]
    assert c.post("/api/feedback", json={"run_id": d["run_id"], "agrees": True, "comment": "useful"}).json()["comment_stored"] is False
    ex = c.get("/api/admin/export").json()
    assert ex["users_consented"] == 1 and len(ex["runs"]) == 2 and ex["events"][0]["props"] == {"page": "check"}
    assert "dev-user" not in str(ex) and "useful" not in str(ex)          # hashed ids, no free text


def test_supabase_mode_requires_a_valid_token(tmp_path, fixture_dir):
    s = Settings(auth_mode="supabase", supabase_url="https://x.supabase.co", supabase_anon_key="anon",
                 admin_emails=["boss@umd.edu"])
    calls = []

    def lookup(token):
        calls.append(token)
        if token != "good":
            raise AuthError("your session has expired; please sign in again")
        return User("u-1", "member@umd.edu")
    c, _ = client(tmp_path, fixture_dir, settings=s, verifier=TokenVerifier(s, lookup=lookup))
    assert c.get("/api/me").status_code == 401
    assert c.get("/api/me", headers={"Authorization": "Bearer bad"}).status_code == 401
    me = c.get("/api/me", headers={"Authorization": "Bearer good"}).json()
    assert me["email"] == "member@umd.edu" and me["is_admin"] is False
    c.get("/api/me", headers={"Authorization": "Bearer good"})
    assert calls.count("good") == 1                                       # cached
    assert c.get("/api/admin/export", headers={"Authorization": "Bearer good"}).status_code == 403
    assert c.get("/api/config").json()["supabase_url"] == "https://x.supabase.co"


def test_site_fallback_when_not_built(tmp_path, fixture_dir, monkeypatch):
    import api.main as m

    monkeypatch.setattr(m, "WEB_DIST", tmp_path / "nodist")
    c, _ = client(tmp_path, fixture_dir)
    r = c.get("/check")
    assert r.status_code == 404 and "npm run build" in r.json()["detail"]
    (tmp_path / "nodist").mkdir()
    (tmp_path / "nodist" / "index.html").write_text("<html>site</html>")
    assert "site" in c.get("/check").text and "site" in c.get("/").text
