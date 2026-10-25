import { useState } from "react";
import { post } from "../api";
import { conf, outcome, OUTCOME_CLASS, STEP_LABEL } from "../format";
import { track } from "../track";
import type { Citation, Summary } from "../types";

interface Props {
  c: Citation;
  runId?: string;
  onUpdate?: (c: Citation, summary: Summary) => void;
  defaultOpen?: boolean;
}

const sentenceCase = (t: string) => (t ? t[0].toUpperCase() + t.slice(1) : t);

function Sentence({ text, marker }: { text: string; marker: string }) {
  if (!marker || !text.includes(marker)) return <>{text}</>;
  const i = text.indexOf(marker);
  return (
    <>
      {text.slice(0, i)}
      <mark className="marker">{marker}</mark>
      {text.slice(i + marker.length)}
    </>
  );
}

export default function CitationCard({ c, runId, onUpdate, defaultOpen = false }: Props) {
  const o = outcome(c);
  const [open, setOpen] = useState(defaultOpen || o !== "Supported");
  const [vote, setVote] = useState<null | boolean>(null);
  const [comment, setComment] = useState("");
  const [sent, setSent] = useState(false);
  const [abstract, setAbstract] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const v = c.verdict;
  const canPaste = !!runId && c.status !== "checked" && (c.status === "no_abstract" || /abstract/i.test(c.status_detail));

  async function sendFeedback(agrees: boolean, withComment = false) {
    setVote(agrees);
    if (agrees || withComment) {
      await post("/api/feedback", { run_id: runId ?? null, citation_index: c.index, agrees, comment: withComment ? comment : "" })
        .catch(() => undefined);
      setSent(true);
      track("feedback", { agrees, citation: c.index, with_comment: withComment && !!comment.trim() });
    }
  }

  async function recheck() {
    if (!abstract.trim()) {
      setErr("Paste the abstract first.");
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const r = await post<{ citation: Citation; summary: Summary }>("/api/recheck", {
        run_id: runId, citation_index: c.index, title: c.paper?.title ?? "", abstract,
      });
      onUpdate?.(r.citation, r.summary);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <article className={`card cite ${OUTCOME_CLASS[o]}`}>
      <button className="cite-head" onClick={() => setOpen(!open)} aria-expanded={open}>
        <span className={`pill ${OUTCOME_CLASS[o]}`}>{o}</span>
        <span className="cite-marker">{c.marker || "claim"}</span>
        <span className="cite-claim">{c.claim}</span>
        {v && <span className="cite-conf" title="Model confidence (not calibrated yet)">{conf(v.confidence)}</span>}
        <span className={`chev ${open ? "up" : ""}`} aria-hidden="true">⌄</span>
      </button>

      {open && (
        <div className="cite-body">
          <div className="field">
            <div className="field-label">Your sentence</div>
            <p className="quote-plain"><Sentence text={c.sentence} marker={c.marker} /></p>
          </div>

          {(c.paper || c.reference_text) && (
            <div className="field">
              <div className="field-label">{c.paper ? "Paper we read" : "Reference"}</div>
              {c.paper ? (
                <p>
                  {c.paper.url ? <a href={c.paper.url} target="_blank" rel="noreferrer">{c.paper.title}</a> : c.paper.title}
                  {c.paper.year ? <span className="muted"> · {c.paper.year}</span> : null}
                  {c.abstract_pasted ? <span className="tag">abstract you pasted</span> : c.read_full_text ? <span className="tag">open-access full text</span> : <span className="tag">abstract</span>}
                </p>
              ) : (
                <p className="muted">{c.reference_text}</p>
              )}
            </div>
          )}

          {v ? (
            <div className="field">
              <div className="field-label">
                {o === "Supported" ? "Sentences that support it" : o === "Contradicted" ? "Sentences that conflict with it" : "Closest sentences we found"}
              </div>
              {(v.evidence[0]?.sentences ?? []).map((s, i) => <blockquote key={i} className="evidence">{s}</blockquote>)}
              {o === "Not enough evidence" && (
                <p className="hint">
                  The {c.read_full_text ? "paper" : "abstract"} doesn't clearly say this either way. That does not mean your sentence is wrong.
                </p>
              )}
            </div>
          ) : (
            <div className="field">
              <div className="field-label">Why we couldn't check it</div>
              <p>{sentenceCase(c.status_detail) || "We could not find this paper."}</p>
            </div>
          )}

          {canPaste && (
            <div className="field paste">
              <div className="field-label">Have the abstract? Paste it and we'll check against it</div>
              <textarea value={abstract} onChange={(e) => setAbstract(e.target.value)} rows={4}
                        placeholder="Paste the paper's abstract here" aria-label="Abstract" />
              {err && <p className="error">{err}</p>}
              <button className="btn" onClick={recheck} disabled={busy}>{busy ? "Checking…" : "Check with this abstract"}</button>
            </div>
          )}

          {c.suggestions.length > 0 && (
            <div className="field suggest">
              <div className="field-label">A paper that does support this (to read, not to paste)</div>
              {c.suggestions.map((s, i) => (
                <div key={i} className="suggestion">
                  <p>
                    {s.paper.url ? <a href={s.paper.url} target="_blank" rel="noreferrer">{s.paper.title}</a> : s.paper.title}
                    <span className="muted"> · confidence {conf(s.confidence)}</span>
                  </p>
                  {s.sentences.slice(0, 2).map((t, j) => <blockquote key={j} className="evidence small">{t}</blockquote>)}
                </div>
              ))}
            </div>
          )}

          {c.steps.length > 0 && (
            <details className="steps">
              <summary>How CiteCheck decided</summary>
              <ol>
                {c.steps.map((s, i) => (
                  <li key={i}><strong>{STEP_LABEL[s.action] ?? s.action}</strong> <span>{s.detail}</span></li>
                ))}
              </ol>
            </details>
          )}

          <div className="feedback">
            {sent ? (
              <span className="muted">Thanks, noted.</span>
            ) : vote === false ? (
              <div className="feedback-form">
                <input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="What looks wrong? (optional)"
                       aria-label="What looks wrong" />
                <button className="btn btn-small" onClick={() => sendFeedback(false, true)}>Send</button>
              </div>
            ) : (
              <>
                <span className="muted">Does this look right?</span>
                <button className="chip" onClick={() => sendFeedback(true)}>👍 Yes</button>
                <button className="chip" onClick={() => setVote(false)}>👎 No</button>
              </>
            )}
          </div>
        </div>
      )}
    </article>
  );
}
