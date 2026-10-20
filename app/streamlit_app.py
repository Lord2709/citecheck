"""CiteCheck web app.   Owner: Engineering.

    streamlit run app/streamlit_app.py

Environment (all optional):
  CITECHECK_VERIFIER / _RETRIEVER / _TAU / _K / _DATA_DIR   override the evaluated configuration (=> UNVALIDATED banner)
  CITECHECK_LOG=logs/usage.jsonl                            where usage events go
  CITECHECK_LOG_ENABLED=0                                   turn logging off
  CITECHECK_DEMO_EXAMPLES=demo/demo_examples.json           live-demo examples (written by `python -m eval.pick_demo_examples`)
  CITECHECK_MAILTO=you@umd.edu                              polite-pool e-mail for OpenAlex requests
  S2_API_KEY=...                                            optional Semantic Scholar key (fewer rate limits)
  OPENALEX_API_KEY=...                                      optional free OpenAlex key (OpenAlex meters usage)
  CITECHECK_SEARCH_SOURCES=openalex,s2,arxiv                where the agent searches for papers (add ,corpus for SciFact)
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from src.agent import build_agent  # noqa: E402
from src.ingest import Fetcher, IngestError, paper_from_text  # noqa: E402
from src.pdf_check import PdfRejected, check_pdf, extract_page_texts  # noqa: E402
from src.pipeline import build_pipeline  # noqa: E402
from src.relevance import RelevanceScorer  # noqa: E402
from src.report import summarize, table_rows, to_markdown  # noqa: E402
from src.schema import CONTRADICT, DISPLAY, NEI, SUPPORT  # noqa: E402
from src.text_utils import truncate  # noqa: E402
from src.usage_log import UsageLogger  # noqa: E402

st.set_page_config(page_title="CiteCheck", page_icon="🔎", layout="wide")

EXAMPLE = {
    "claim": "Zorvex supplementation increases bone density in mice.",
    "title": "Zorvex supplementation and skeletal density in mice (INVENTED EXAMPLE)",
    "abstract": ("Bone loss is a major concern in ageing populations. We fed adult mice a diet supplemented with zorvex for "
                 "twelve weeks. Zorvex supplementation significantly increased femoral bone density compared with controls. "
                 "The effect was dose dependent and was not observed in mice fed a standard diet."),
}


def load_demo_examples(path=None) -> list:
    """Seeded, pre-checked SciFact dev examples for the live demo (main + backups + the honest failure, if picked)."""
    path = Path(path or os.environ.get("CITECHECK_DEMO_EXAMPLES", "demo/demo_examples.json"))
    try:
        j = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    items = list(j.get("examples") or []) + ([j["failure"]] if j.get("failure") else [])
    return [e for e in items if e.get("claim") and e.get("abstract")]


@st.cache_resource(show_spinner="Loading models (first start can take a minute)…")
def get_pipeline():
    return build_pipeline()


@st.cache_resource
def get_fetcher():
    return Fetcher()


@st.cache_resource
def get_agent():
    return build_agent(get_pipeline(), get_fetcher())


def logger() -> UsageLogger:
    if "logger" not in st.session_state:
        st.session_state.logger = UsageLogger(
            path=os.environ.get("CITECHECK_LOG", "logs/usage.jsonl"),
            enabled=os.environ.get("CITECHECK_LOG_ENABLED", "1") != "0",
            participant=st.query_params.get("p"),
        )
        st.session_state.logger.log("session_start")
    return st.session_state.logger


pipe, fetcher, log = get_pipeline(), get_fetcher(), logger()


# ----------------------------------------------------------------------------------------------
# Sidebar: honesty about what is running + researcher panel
# ----------------------------------------------------------------------------------------------
def sidebar():
    m = pipe.meta
    st.sidebar.header("Model status")
    if m.get("demo_only"):
        st.sidebar.error("DEMO BACKEND (word overlap). Verdicts are NOT reliable. The neural model did not load.")
    elif m.get("validated"):
        lo, hi = m.get("dev_macro_f1_ci95") or (None, None)
        st.sidebar.success(
            f"Validated configuration `{m.get('deployed_run')}`\n\n"
            f"SciFact dev macro-F1 **{m['dev_macro_f1']:.2f}** (95% CI {lo:.2f} to {hi:.2f}); "
            f"false-SUPPORT rate **{m['dev_false_support_rate']:.2f}**."
        )
    else:
        st.sidebar.warning("UNVALIDATED configuration: no evaluated run is deployed, or settings were overridden. "
                           "Do not quote numbers for this setup.")
    if m.get("validated") and not m.get("demo_only"):
        st.sidebar.caption("This is the exact model whose accuracy we report (eval/results). The numbers are from SciFact, "
                           "a biomedical dataset.")
    st.sidebar.info("**Check a draft** and **Find papers** are new agent features. Their verdicts come from the model above, "
                    "but the agent as a whole (full-text reading, suggested papers) has not been evaluated yet.")
    for w in pipe.warnings:
        st.sidebar.info(w)
    st.sidebar.caption(f"verifier `{m.get('verifier')}` · retriever `{m.get('retriever')}` · tau {m.get('tau')}")

    with st.sidebar.expander("Researcher panel (user tests)"):
        code = st.text_input("Participant code (P01, P02…; never a name)", value=log.participant or "", key="participant")
        consent = st.checkbox("Participant consented to logging what they type", key="consent")
        log.participant, log.log_text = (code.strip() or None), bool(consent)
        task = st.selectbox("Task", ["T1", "T2", "T3"], key="task_id")
        c1, c2, c3 = st.columns(3)
        if c1.button("▶ Start", key="task_start"):
            st.session_state.task_t0 = time.time()
            log.log("task_start", task_id=task)
        for col, key, label, outcome in ((c2, "task_ok", "✔ Done", "completed"), (c3, "task_fail", "✖ Gave up", "gave_up")):
            if col.button(label, key=key):
                t0 = st.session_state.get("task_t0")
                log.log("task_end", task_id=task, outcome=outcome, elapsed_s=round(time.time() - t0, 1) if t0 else None)
                st.session_state.task_t0 = None
        st.caption(f"logging to `{log.path}` · text logging {'ON' if log.log_text else 'off'}")
        st.download_button("Download this session's log", log.session_jsonl(), key="dl_log",
                           file_name=f"{log.participant or 'session'}_usage.jsonl", mime="application/json",
                           help="On the hosted app the server log is wiped on restart: download right after each session.")


sidebar()

st.title("🔎 CiteCheck")
st.markdown("**Does the paper you cite really support your claim?** CiteCheck finds the papers behind your citations, reads "
            "them and shows you the sentences that decide each verdict, so you can check it yourself. It can also find "
            "papers for a research direction.")
_h1, _h2, _h3 = st.columns(3)
_h1.markdown("**① Your text**  \nA paragraph or draft with citations, or one claim and the paper you cite.")
_h2.markdown("**② The papers**  \nCiteCheck resolves each reference and reads the abstract (and the open-access full text when unsure).")
_h3.markdown("**③ The verdicts**  \nSupports, contradicts, or not enough evidence, with the deciding sentences and better papers to read.")
tab_draft, tab_find, tab_check, tab_rel, tab_audit, tab_about = st.tabs(
    ["Check a draft", "Find papers", "Check a citation", "Is this paper relevant?", "Audit a paper (experimental)",
     "About & limits"])


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
HEADLINE = {
    SUPPORT: ("✅", "The abstract supports your claim"),
    CONTRADICT: ("❌", "The abstract contradicts your claim"),
    NEI: ("❔", "Not enough evidence in the abstract to decide"),
}
MEANING = {
    SUPPORT: "The model judged that the sentences below back up your claim. That is a strong hint, not proof: "
             "read them before you cite.",
    CONTRADICT: "The sentences below appear to conflict with your claim. Check whether the paper's population and "
                "conditions match yours before you drop or change the citation.",
    NEI: "Nothing in the abstract clearly supports or contradicts the claim. That does NOT mean the claim is false: "
         "CiteCheck only reads abstracts, and it says so instead of guessing when it is unsure.",
}


def render_verdict(v, key_prefix="v"):
    box = {SUPPORT: st.success, CONTRADICT: st.error, NEI: st.warning}[v.label]
    icon, headline = HEADLINE[v.label]
    box(f"#### {icon} {headline}\n**Verdict: {v.display_label}**  ·  model confidence {v.confidence:.2f}")
    st.progress(min(max(float(v.confidence), 0.0), 1.0),
                text=f"Model confidence {v.confidence:.0%}: a score from the model, not a guarantee")
    st.caption(MEANING[v.label] + (f"  ({v.note})" if v.label == NEI and v.note else ""))
    if v.evidence:
        st.markdown("**Evidence the model read**")
    for i, e in enumerate(v.evidence, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. [{e.title}]({e.url})**" if e.url else f"**{i}. {e.title}**")
            for s in e.sentences:
                st.markdown(f"> {s}")
            st.caption(f"How the model read these sentences: supports {e.probs.support:.0%} · "
                       f"neutral {e.probs.neutral:.0%} · contradicts {e.probs.contradict:.0%}")
    with st.expander("Technical details"):
        st.json({"latency_ms": round(v.latency_ms), "backend": v.backend, "abstained": v.abstained})


def source_inputs(prefix, allow_corpus):
    options = ["The paper I'm citing (DOI / arXiv / link)", "Paste an abstract"] + (["Search the SciFact corpus"] if allow_corpus else [])
    choice = st.radio("Where should I look for evidence?", options, horizontal=True, key=f"{prefix}_src",
                      help="Give the paper you cite. If it can't be fetched (no internet, no open abstract), paste its abstract.")
    ident = title = abstract = ""
    if choice == options[0]:
        ident = st.text_input("DOI, arXiv id or link", key=f"{prefix}_ident", placeholder="10.1038/nature14539  or  arXiv:2004.14974",
                              help="We look the paper up in OpenAlex, Semantic Scholar and arXiv and read its abstract.")
    elif choice == options[1]:
        title = st.text_input("Title (optional)", key=f"{prefix}_title")
        abstract = st.text_area("Abstract", key=f"{prefix}_abstract", height=160,
                                placeholder="Paste the paper's abstract here. Only the abstract is read.")
    return options.index(choice), ident, title, abstract


def resolve_paper(mode, ident, title, abstract):
    if mode == 0:
        return fetcher.fetch_paper(ident)
    return paper_from_text(title, abstract)


# ----------------------------------------------------------------------------------------------
# Tab 1: check a citation
# ----------------------------------------------------------------------------------------------
def fill_example(claim, title, abstract, gold=None):
    """Widget values must be set BEFORE the widgets are drawn, so this runs above them."""
    st.session_state.claim = claim
    st.session_state.chk_src = "Paste an abstract"
    st.session_state.chk_title = title
    st.session_state.chk_abstract = abstract
    st.session_state.demo_gold = (claim, gold) if gold else None
    st.session_state.pop("verdict", None)


def clear_check():
    """'Start over' (runs as a callback, before the widgets are drawn)."""
    for k in ("claim", "chk_title", "chk_abstract", "chk_ident", "fb_comment"):
        st.session_state[k] = ""
    for k in ("verdict", "demo_gold", "feedback_sent", "check_problem"):
        st.session_state.pop(k, None)


def missing_input(claim, mode, ident, abstract):
    """A friendly reason the check cannot run yet, or None."""
    if not claim.strip():
        return "Enter a claim to check: one sentence, as you would write it in your paper."
    if mode == 0 and not ident.strip():
        return "Enter the DOI, arXiv id or link of the paper you cite, or choose “Paste an abstract”."
    if mode == 1 and not abstract.strip():
        return "Paste the paper's abstract, or choose “The paper I'm citing” to look it up by DOI / arXiv id."
    return None


with tab_check:
    left, right = st.columns([1, 1], gap="large")
    with left:
        demo = load_demo_examples()
        if demo:
            with st.expander("Demo examples (SciFact dev, picked by seed; for presenters, not for participants)"):
                names = [f"{e.get('slot', '?')} · SciFact claim #{e.get('claim_id', '?')} · {e.get('role', '')}" for e in demo]
                pick = st.selectbox("Example", range(len(demo)), format_func=lambda i: names[i], key="demo_pick")
                if st.button("Load this example", key="btn_demo"):
                    e = demo[pick]
                    fill_example(e["claim"], e.get("title", ""), e["abstract"], e.get("gold"))
                    log.log("demo_example", slot=e.get("slot"), claim_id=e.get("claim_id"))
        if st.button("Fill in an invented example", key="btn_example", help="Loads a made-up claim and abstract to try the tool."):
            fill_example(EXAMPLE["claim"], EXAMPLE["title"], EXAMPLE["abstract"])
        claim = st.text_area("Your claim: the sentence you want the paper to support", key="claim", height=90,
                             placeholder="e.g. Antiretroviral therapy reduces the incidence of tuberculosis.",
                             help="One short, self-contained statement works best. Leave out the citation marker.")
        if len(claim) > 300:
            st.caption("Tip: CiteCheck works best on one short claim. Consider splitting long sentences.")
        mode, ident, title, abstract = source_inputs("chk", pipe.has_corpus)

        b1, b2 = st.columns([3, 1])
        clicked = b1.button("Check citation", type="primary", key="btn_check", use_container_width=True)
        b2.button("Start over", key="btn_clear", on_click=clear_check, use_container_width=True)
        if clicked:
            t0 = time.time()
            problem = missing_input(claim, mode, ident, abstract)
            if problem:
                st.session_state.pop("verdict", None)
                st.warning(problem)
                log.log("error", where="verify", message=problem[:200])
            else:
                try:
                    with st.spinner("Reading the abstract and weighing the evidence…"):
                        if mode == 2:
                            verdict = pipe.verify_claim(claim)
                        else:
                            verdict = pipe.verify_against_paper(claim, resolve_paper(mode, ident, title, abstract))
                    st.session_state.verdict = verdict
                    st.session_state.pop("feedback_sent", None)
                    log.log("verify", claim=claim, mode=["paper", "pasted", "corpus"][mode], verdict=verdict.label,
                            confidence=round(verdict.confidence, 3), abstained=verdict.abstained, n_evidence=len(verdict.evidence),
                            latency_ms=round(verdict.latency_ms), wall_ms=round(1000 * (time.time() - t0)),
                            verifier=verdict.backend.get("verifier"), validated=verdict.backend.get("validated"))
                except (IngestError, ValueError) as e:
                    st.session_state.pop("verdict", None)
                    st.error(f"Couldn't check this citation: {e}")
                    log.log("error", where="verify", message=str(e)[:200])

    with right:
        v = st.session_state.get("verdict")
        if v is None:
            st.info("**Your verdict will appear here.**  \nEnter a claim and the paper on the left, then press "
                    "**Check citation**. New here? Press **Fill in an invented example** first.")
        else:
            render_verdict(v)
            claim_gold = st.session_state.get("demo_gold")
            if claim_gold and claim_gold[0].strip() == v.claim:          # only if the example's claim was not edited
                gold = claim_gold[1]
                mark = "matches" if gold == v.label else "does NOT match"
                st.info(f"SciFact annotators' label for this claim and paper: **{DISPLAY.get(gold, gold)}**; the model {mark} it.")
            st.markdown("**Do you agree with this verdict?**")
            c1, c2, _ = st.columns([1, 1, 2])
            for col, key, label, val in ((c1, "fb_yes", "👍 Agree", "agree"), (c2, "fb_no", "👎 Disagree", "disagree")):
                if col.button(label, key=key):
                    st.session_state.feedback_sent = val
                    log.log("feedback", agrees=val == "agree", verdict=v.label)
            if st.session_state.get("feedback_sent"):
                st.success(f"Thanks: recorded “{st.session_state.feedback_sent}”.")
                comment = st.text_input("Anything we got wrong or confusing? (optional)", key="fb_comment")
                if comment and st.button("Send comment", key="fb_send"):
                    log.log("comment", comment=comment)
                    st.info("Comment saved.")

# ----------------------------------------------------------------------------------------------
# Tab 2: relevance
# ----------------------------------------------------------------------------------------------
with tab_rel:
    st.markdown("Describe what you are working on, then point me at a paper. This is a quick skim aid, **secondary** to citation checking.")
    direction = st.text_area("Your research direction", key="direction", height=80,
                             placeholder="e.g. Using NLP to verify scientific claims against cited evidence")
    rmode, rident, rtitle, rabstract = source_inputs("rel", False)
    if st.button("How relevant is it?", key="btn_rel"):
        if not direction.strip():
            st.warning("Describe your research direction first (one or two sentences).")
            st.stop()
        try:
            paper = resolve_paper(rmode, rident, rtitle, rabstract)
            r = RelevanceScorer().score(direction, paper)
            st.info(f"**{r.band}**  (score {r.score:.2f}, method: {r.method})")
            st.write("Matched terms: " + (", ".join(r.matched_terms) or "none"))
            st.caption(f"{paper.title} · {r.note}")
            log.log("relevance", direction=direction, band=r.band, score=round(r.score, 3))
        except (IngestError, ValueError) as e:
            st.error(str(e))

# ----------------------------------------------------------------------------------------------
# Tab 3: audit
# ----------------------------------------------------------------------------------------------
with tab_audit:
    st.warning("**Experimental.** We have no labelled data for this setting. Citing sentences in real papers are messier than "
               "the atomic claims we validated on, and many papers expose no citing sentences at all. Treat rows as leads to check.")
    aud_id = st.text_input("DOI, arXiv id or link of the paper to audit", key="aud_ident")
    n_refs = st.slider("References to check", 3, 15, 8, key="aud_n")
    if st.button("Audit its citations", key="btn_audit"):
        if not aud_id.strip():
            st.warning("Enter the DOI, arXiv id or link of the paper whose references you want to check.")
            st.stop()
        try:
            bar = st.progress(0.0, text="Fetching the reference list…")
            refs = fetcher.fetch_references(aud_id, limit=max(n_refs, 10))
            rows = pipe.audit(refs, max_items=n_refs, progress=lambda i, n: bar.progress(i / n, text=f"Checking reference {i} of {n}…"))
            bar.empty()
            table = [{
                "Cited paper": truncate(r.reference.cited.title, 80),
                "Citing sentence": truncate(r.reference.context, 140),
                "Verdict": r.verdict.display_label if r.verdict else f"skipped ({r.skipped_reason})",
                "Confidence": round(r.verdict.confidence, 2) if r.verdict else None,
            } for r in rows]
            st.dataframe(table)
            log.log("audit", identifier=aud_id, n_rows=len(rows), n_checked=sum(1 for r in rows if r.verdict))
        except (IngestError, ValueError) as e:
            st.error(str(e))

# ----------------------------------------------------------------------------------------------
# Tab 4: about
# ----------------------------------------------------------------------------------------------
with tab_about:
    st.markdown("""
**What this is.** A course project (UMD DATA/MSML 641). It judges whether *evidence sentences from a paper's abstract*
entail, contradict, or are neutral to a claim, using a pretrained natural-language-inference model and a confidence threshold.

**What a wrong answer costs.** The worst error is a false **SUPPORTS**: it can make you trust a citation that does not hold up.
That is why the system abstains (“not enough evidence”) unless it is confident, and why every verdict shows the sentences it used.

**Known limits.**
- Trained/evaluated on **SciFact**, which is **biomedical**. Do not assume it works for other fields.
- It reads **abstracts only**; support that lives in a paper's results or methods is invisible to it.
- Claims work best when they are short, self-contained statements.
- Relevance scores are uncalibrated hints.
- It is a second pair of eyes. **You** are responsible for what you cite.

**Data & privacy.** Evaluation data: SciFact (claims CC BY 4.0, abstracts ODC-By 1.0). Usage logs store no personal
information; the text you type is only logged in research mode with your consent, with e-mails/phone numbers redacted.
""")

# ----------------------------------------------------------------------------------------------
# Agent tab 1: check every citation in a draft
# ----------------------------------------------------------------------------------------------
DRAFT_EXAMPLE = """Transformer models rely entirely on attention and dispense with recurrence and convolutions [1]. SciFact pairs
expert-written scientific claims with abstracts that contain the evidence for them [2]. Deep learning methods learn
representations of data with multiple levels of abstraction [3]. Attention-only models are always slower to train than
recurrent ones [1].

References
[1] Vaswani et al. Attention Is All You Need. NeurIPS 2017. arXiv:1706.03762
[2] Wadden et al. Fact or Fiction: Verifying Scientific Claims. EMNLP 2020. doi:10.18653/v1/2020.emnlp-main.609
[3] LeCun, Bengio and Hinton. Deep learning. Nature 2015. doi:10.1038/nature14539
"""
OUTCOME_BOX = {"Supported": st.success, "Contradicted": st.error, "Not enough evidence": st.warning,
               "Could not check": st.info}


def render_draft_report(rep: dict):
    s = summarize(rep)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Citations", s["citations"])
    c2.metric("Supported", s["supported"])
    c3.metric("Contradicted", s["contradicted"])
    c4.metric("Not enough evidence", s["not_enough_evidence"])
    c5.metric("Could not check", s["could_not_check"])
    for w in rep.get("warnings") or []:
        st.info(w)
    if not rep.get("citations"):
        return
    st.dataframe(table_rows(rep), hide_index=True)
    for c, row in zip(rep["citations"], table_rows(rep)):
        with st.expander(f"{c['index']}. {row['Outcome']} · {c['marker']} · {truncate(c['claim'], 90)}"):
            st.markdown(f"**Your sentence:** {c['sentence']}")
            if c.get("reference_text"):
                st.markdown(f"**Reference:** {c['reference_text']}")
            p = c.get("paper")
            if p:
                st.markdown(f"**Paper read:** {p.get('title')}" + (f" ({p['year']})" if p.get("year") else "")
                            + (f" · [link]({p['url']})" if p.get("url") else ""))
            v = c.get("verdict")
            if v:
                where = "the open-access full text" if c.get("read_full_text") else "the abstract"
                OUTCOME_BOX[row["Outcome"]](f"**{v['display_label']}** (confidence {v['confidence']:.2f}), from {where}")
                if v.get("evidence"):
                    st.markdown("**Deciding sentences:**")
                    for sent in v["evidence"][0]["sentences"]:
                        st.markdown(f"> {sent}")
            else:
                st.info(f"Could not check: {c.get('status_detail')}")
            for sg in c.get("suggestions") or []:
                sp = sg["paper"]
                st.markdown(f"**A paper that does support this claim (to read, not to paste):** {sp.get('title')}"
                            + (f" · [link]({sp['url']})" if sp.get("url") else "") + f" (confidence {sg['confidence']:.2f})")
                for sent in sg.get("sentences") or []:
                    st.markdown(f"> {sent}")
            st.caption("How the agent decided: " + " → ".join(f"{x['action']}: {x['detail']}" for x in c.get("steps") or []))
    st.download_button("Download the report (Markdown)", to_markdown(rep), file_name="citecheck_report.md",
                       mime="text/markdown", key="dl_draft")


with tab_draft:
    st.markdown("Paste a paragraph or a whole draft **with its reference list**. CiteCheck finds every cited sentence, "
                "looks up each reference, reads the paper and tells you whether it supports the sentence.")
    src_mode = st.radio("Your text", ["Paste text", "Upload a PDF (text-based)"], horizontal=True, key="draft_src")
    draft_text = ""
    if src_mode == "Paste text":
        if st.button("Load an example (real papers; needs internet)", key="btn_draft_example"):
            st.session_state.draft = DRAFT_EXAMPLE
        draft_text = st.text_area("Draft with citations and a 'References' list", key="draft", height=220,
                                  placeholder="… reduces infection rates [1].\n\nReferences\n[1] Author et al. Title. Venue 2020. doi:10.…")
    else:
        up = st.file_uploader("PDF of your draft (scanned PDFs are not supported)", type=["pdf"], key="draft_pdf")
        if up is not None:
            try:
                data = up.getvalue()
                verdict = check_pdf(data)
                if not verdict.accepted:
                    st.error(verdict.user_message())
                    log.log("pdf_rejected", kind=verdict.kind, n_pages=verdict.n_pages)
                else:
                    if verdict.kind == "mixed":
                        st.info(verdict.user_message())
                    pages = extract_page_texts(data)
                    draft_text = "\n".join(pages[i] for i in verdict.text_pages)
                    st.caption(f"Read {len(verdict.text_pages)} of {verdict.n_pages} pages.")
            except PdfRejected as e:
                st.error(str(e))
    o1, o2, o3 = st.columns(3)
    escalate = o1.checkbox("Read the open-access full text when unsure", value=True, key="opt_ft")
    suggest = o2.checkbox("Suggest a paper when a citation fails", value=True, key="opt_suggest")
    max_cits = o3.number_input("Check at most", min_value=1, max_value=40, value=12, key="opt_max")
    if st.button("Check every citation", key="btn_draft", type="primary"):
        if not draft_text.strip():
            st.warning("Paste your text (with its reference list) or upload a text-based PDF first.")
        else:
            agent = get_agent()
            plan = agent.plan(draft_text)
            if plan.kind == "discover":
                st.info("I found no citations in this text. It looks like a research direction: try the **Find papers** tab.")
                log.log("agent_plan", plan=plan.kind)
            else:
                agent.escalate, agent.suggest = escalate, suggest
                bar = st.progress(0.0, text="Reading your citations…")
                t0 = time.time()
                rep = agent.check_draft(draft_text, max_citations=int(max_cits),
                                        progress=lambda i, n: bar.progress(i / n, text=f"Checking citation {i} of {n}…")).to_dict()
                bar.empty()
                st.session_state.draft_report = rep
                summ = summarize(rep)
                log.log("draft_check", draft=draft_text, n_citations=summ["citations"], supported=summ["supported"],
                        contradicted=summ["contradicted"], nei=summ["not_enough_evidence"],
                        could_not_check=summ["could_not_check"], read_full_text=summ["read_full_text"],
                        with_suggestion=summ["with_suggestion"], escalate=escalate, suggest=suggest,
                        seconds=round(time.time() - t0, 1))
    if st.session_state.get("draft_report"):
        render_draft_report(st.session_state.draft_report)
        f1, f2, _ = st.columns([1, 1, 4])
        if f1.button("👍 This report is useful", key="fb_draft_yes"):
            log.log("feedback", target="draft_report", agrees=True)
            st.toast("Thanks, noted.")
        if f2.button("👎 Something is wrong", key="fb_draft_no"):
            log.log("feedback", target="draft_report", agrees=False)
            st.toast("Thanks, noted. Tell the researcher what looked wrong.")

# ----------------------------------------------------------------------------------------------
# Agent tab 2: find papers for a research direction
# ----------------------------------------------------------------------------------------------
with tab_find:
    st.markdown("Describe your research direction. CiteCheck searches OpenAlex, Semantic Scholar and arXiv, merges what "
                "they return and ranks it, with the sentence that makes each paper relevant.")
    fdir = st.text_area("Your research direction", key="find_direction", height=90,
                        placeholder="e.g. verifying scientific claims against the abstracts of cited papers")
    n_find = st.slider("How many papers", 5, 20, 10, key="find_n")
    if st.button("Find papers", key="btn_find", type="primary"):
        if not fdir.strip():
            st.warning("Describe your research direction first (one or two sentences).")
        else:
            with st.spinner("Searching open sources…"):
                try:
                    st.session_state.find_report = get_agent().discover(fdir, k=n_find).to_dict()
                    r = st.session_state.find_report
                    log.log("discover", direction=fdir, n_results=len(r["results"]), failed_sources=sorted(r["errors"]))
                except ValueError as e:
                    st.warning(str(e))
    rep = st.session_state.get("find_report")
    if rep:
        for srcname, msg in rep["errors"].items():
            st.info(f"Source `{srcname}` did not answer ({truncate(msg, 100)}); showing results from the others.")
        if not rep["results"]:
            st.warning("No papers found. Try fewer or more general words.")
        st.caption(f"Search query: `{rep['query']}` · {rep['note']}")
        for i, c in enumerate(rep["results"], 1):
            p = c["paper"]
            meta = " · ".join(str(x) for x in (p.get("venue"), p.get("year")) if x)
            st.markdown(f"**{i}. {p['title']}**" + (f"  \n{meta}" if meta else "")
                        + (f" · [link]({p['url']})" if p.get("url") else ""))
            st.caption(f"{c['band']} (score {c['score']:.2f}) · found in {', '.join(c['sources'])}"
                       + (f" · matched: {', '.join(c['matched_terms'])}" if c["matched_terms"] else "")
                       + ("" if p.get("has_abstract") else " · no abstract available"))
            if c["key_sentence"]:
                st.markdown(f"> {c['key_sentence']}")
        st.download_button("Download the list (Markdown)", to_markdown(rep), file_name="citecheck_papers.md",
                           mime="text/markdown", key="dl_find")
