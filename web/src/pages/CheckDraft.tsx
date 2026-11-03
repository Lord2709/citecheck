import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, get, post, postForm } from "../api";
import Results from "../components/Results";
import { track } from "../track";
import type { Citation, Job, Summary } from "../types";

const EXAMPLE = `Transformer models rely entirely on attention and dispense with recurrence and convolutions [1]. SciFact pairs expert-written scientific claims with abstracts that contain the evidence for them [2]. Deep learning methods learn representations of data with multiple levels of abstraction [3]. Attention-only models are always slower to train than recurrent ones [1]. The base Transformer model uses 8 parallel attention heads [1].

References
[1] Vaswani et al. Attention Is All You Need. NeurIPS 2017. arXiv:1706.03762
[2] Wadden et al. Fact or Fiction: Verifying Scientific Claims. EMNLP 2020. doi:10.18653/v1/2020.emnlp-main.609
[3] LeCun, Bengio and Hinton. Deep learning. Nature 2015. doi:10.1038/nature14539`;

type Mode = "paste" | "pdf";

export default function CheckDraft() {
  const [mode, setMode] = useState<Mode>("paste");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [fullText, setFullText] = useState(true);
  const [suggest, setSuggest] = useState(true);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const [starting, setStarting] = useState(false);
  const timer = useRef<number | null>(null);
  const nav = useNavigate();

  useEffect(() => () => { if (timer.current) window.clearInterval(timer.current); }, []);

  function poll(jobId: string) {
    if (timer.current) window.clearInterval(timer.current);
    timer.current = window.setInterval(async () => {
      try {
        const j = await get<Job>(`/api/jobs/${jobId}`);
        setJob(j);
        if (j.status === "done" || j.status === "error") {
          if (timer.current) window.clearInterval(timer.current);
          track("check_finished", { status: j.status, citations: j.total });
        }
      } catch (e) {
        if (timer.current) window.clearInterval(timer.current);
        setError((e as Error).message);
      }
    }, 1000);
  }

  async function start() {
    setError("");
    setInfo("");
    setJob(null);
    if (mode === "paste" && !text.trim()) return setError("Paste your text, including its reference list, first.");
    if (mode === "pdf" && !file) return setError("Choose a PDF first.");
    setStarting(true);
    try {
      let r: { plan: string; job_id?: string; message?: string; pdf?: { note: string } };
      if (mode === "paste") {
        r = await post("/api/check-draft", { text, read_full_text: fullText, suggest });
      } else {
        const f = new FormData();
        f.append("file", file as File);
        f.append("read_full_text", String(fullText));
        f.append("suggest", String(suggest));
        r = await postForm("/api/check-pdf", f);
        if (r.pdf?.note) setInfo(r.pdf.note);
      }
      track("check_started", { source: mode, full_text: fullText, suggest });
      if (r.plan === "discover") {
        setInfo(r.message ?? "");
        return;
      }
      setJob({ id: r.job_id!, run_id: "", status: "queued", done: 0, total: 0, citations: [], report: null, error: "",
               summary: { citations: 0, supported: 0, contradicted: 0, not_enough_evidence: 0, could_not_check: 0,
                          needs_attention: 0, read_full_text: 0, with_suggestion: 0 } });
      poll(r.job_id!);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Something went wrong. Please try again.");
    } finally {
      setStarting(false);
    }
  }

  function onUpdate(c: Citation, summary: Summary) {
    setJob((j) => {
      if (!j) return j;
      const citations = (j.report?.citations ?? j.citations).map((x) => (x.index === c.index ? c : x));
      return { ...j, citations, report: j.report ? { ...j.report, citations } : null, summary };
    });
  }

  const running = job && (job.status === "queued" || job.status === "running");
  const citations = job?.report?.citations ?? job?.citations ?? [];
  const pct = job && job.total ? Math.round((100 * job.done) / job.total) : 0;

  return (
    <div className="page">
      <div className="page-head">
        <h1>Check a draft</h1>
        <p className="lead">Paste a paragraph or a whole section <strong>with its reference list</strong>. CiteCheck finds every cited sentence, reads the paper behind it, and tells you whether it backs you up.</p>
      </div>

      <section className="card composer">
        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={mode === "paste"} className={mode === "paste" ? "active" : ""} onClick={() => setMode("paste")}>Paste text</button>
          <button role="tab" aria-selected={mode === "pdf"} className={mode === "pdf" ? "active" : ""} onClick={() => setMode("pdf")}>Upload a PDF</button>
        </div>

        {mode === "paste" ? (
          <>
            <textarea className="draft" value={text} onChange={(e) => setText(e.target.value)} rows={12} aria-label="Your draft"
                      placeholder={"…reduces infection rates in adults [1].\n\nReferences\n[1] Author et al. Title. Venue 2020. doi:10.…"} />
            <div className="composer-meta">
              <button className="link-btn" onClick={() => { setText(EXAMPLE); track("example_loaded", {}); }}>Try an example with real papers</button>
              <span className="muted small">Citations like [1], [2–4] or (Smith et al., 2020).{text ? ` ${text.length.toLocaleString()} characters.` : ""}</span>
            </div>
          </>
        ) : (
          <label className={`dropzone ${dragging ? "drag" : ""}`}
                 onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                 onDragLeave={() => setDragging(false)}
                 onDrop={(e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) setFile(f); }}>
            <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            <span className="drop-title">{file ? file.name : "Drop a PDF here, or click to choose one"}</span>
            <span className="muted small">Text-based PDFs only (exported from Word, LaTeX or Google Docs). Scanned PDFs can't be read.</span>
          </label>
        )}

        <div className="options">
          <label className="toggle"><input type="checkbox" checked={fullText} onChange={(e) => setFullText(e.target.checked)} />
            <span>Read the open-access full text when the abstract isn't enough</span></label>
          <label className="toggle"><input type="checkbox" checked={suggest} onChange={(e) => setSuggest(e.target.checked)} />
            <span>Suggest a paper when a citation doesn't hold up</span></label>
        </div>

        {error && <p className="error" role="alert">{error}</p>}
        {info && (
          <div className="banner">
            {info}
            {info.includes("Find papers") && <button className="link-btn" onClick={() => nav("/papers")}>Go to Find papers</button>}
          </div>
        )}

        <button className="btn btn-primary" onClick={start} disabled={starting || !!running}>
          {starting ? "Starting…" : running ? "Checking…" : "Check every citation"}
        </button>
      </section>

      {job && (
        <>
          {running && (
            <div className="progress-wrap" aria-live="polite">
              <div className="progress-text">
                <span className="spinner small" aria-hidden="true" />
                {job.total ? `Checked ${job.done} of ${job.total} citations` : "Reading your text and finding the references…"}
              </div>
              <div className="progress"><div className="progress-bar" style={{ width: `${pct}%` }} /></div>
            </div>
          )}
          {job.status === "error" && <div className="banner banner-bad">The check stopped: {job.error}. Please try again.</div>}
          {(citations.length > 0 || job.status === "done") && (
            <Results citations={citations} summary={job.summary} warnings={job.report?.warnings ?? []}
                     runId={job.status === "done" ? job.run_id : undefined} done={job.status === "done"} onUpdate={onUpdate} />
          )}
        </>
      )}
    </div>
  );
}
