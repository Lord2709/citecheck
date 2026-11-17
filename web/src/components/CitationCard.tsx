import { useState } from "react";
import { post } from "../api";
import { abstractOnly, conf, displayOutcome, freeCopyUrl, noFreeFullText, outcome, OUTCOME_CLASS, STEP_LABEL } from "../format";
import type { Citation, Summary } from "../types";
import Judgement from "./Judgement";

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
  const [abstract, setAbstract] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const v = c.verdict;
  const onlyAbstract = abstractOnly(c) && noFreeFullText(c);
  const freeCopy = freeCopyUrl(c);
  const citesNumber = /\d/.test(c.claim);
  // No abstract: paste the abstract.  A verdict from the abstract alone that is not "supported": paste the passage of
  // the paper that backs the sentence (the researcher often has the paper through their library).
  const pasteKind: "abstract" | "passage" | null = !runId ? null
    : c.status !== "checked" ? (c.status === "no_abstract" || /abstract/i.test(c.status_detail) ? "abstract" : null)
    : v && abstractOnly(c) && v.label !== "SUPPORT" ? "passage" : null;

  async function recheck() {
    if (!abstract.trim()) {
      setErr(pasteKind === "passage" ? "Paste the passage first." : "Paste the abstract first.");
      return;
    }
    setBusy(true);
    setErr("");
    try {
      const r = await post<{ citation: Citation; summary: Summary }>("/api/recheck", {
        run_id: runId, citation_index: c.index, title: c.paper?.title ?? "", abstract, kind: pasteKind ?? "abstract",
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
        <span className={`pill ${OUTCOME_CLASS[o]}`}>{displayOutcome(c)}</span>
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
                  {c.abstract_pasted ? <span className="tag">{c.pasted_kind === "passage" ? "passage you pasted" : "abstract you pasted"}</span>
                    : c.read_full_text ? <span className="tag">open-access full text</span>
                    : <span className="tag">{onlyAbstract ? "abstract only" : "abstract"}</span>}
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
              {onlyAbstract ? (
                <p className="hint abstract-only">
                  {c.full_text_status === "off"
                    ? <><strong>Only the abstract was read:</strong> full-text reading was switched off for this check.</>
                    : freeCopy
                      ? <><strong>Only the abstract could be read:</strong> a free copy of this paper exists, but its website refused
                          our download. <a href={freeCopy} target="_blank" rel="noreferrer">Open the free copy</a> and paste the
                          passage that backs your sentence below.</>
                      : <><strong>Only the abstract could be read:</strong> no free full text of this paper was found.</>}
                  {o === "Not enough evidence" ? " Numbers, methods and detailed results are usually only in the full paper, so this does not mean your sentence is wrong."
                    : freeCopy ? "" : " The full paper may say more."}
                  {o === "Not enough evidence" && citesNumber ? " Your sentence cites a number; abstracts rarely include them." : ""}
                </p>
              ) : o === "Not enough evidence" && (
                <p className="hint">
                  The {c.read_full_text ? "paper" : c.abstract_pasted ? "text you pasted" : "abstract"} doesn't clearly say this either way. That does not mean your sentence is wrong.
                </p>
              )}
            </div>
          ) : (
            <div className="field">
              <div className="field-label">Why we couldn't check it</div>
              <p>{sentenceCase(c.status_detail) || "We could not find this paper."}</p>
              {freeCopy && (
                <p className="hint">
                  A free copy exists, but its website refused our download: <a href={freeCopy} target="_blank" rel="noreferrer">open
                  it</a> and paste its abstract, or the passage that backs your sentence, below.
                </p>
              )}
            </div>
          )}

          {pasteKind && (
            <div className="field paste">
              <div className="field-label">
                {pasteKind === "passage" ? "Have the paper? Paste the passage that backs your sentence, and we'll check against it"
                  : "Have the paper? Paste its abstract, or the passage that backs your sentence, and we'll check against it"}
              </div>
              <textarea value={abstract} onChange={(e) => setAbstract(e.target.value)} rows={4} maxLength={20000}
                        placeholder={pasteKind === "passage" ? "Paste the paragraph or table caption from the paper" : "Paste the paper's abstract or a passage here"}
                        aria-label={pasteKind === "passage" ? "Passage from the paper" : "Abstract"} />
              {err && <p className="error">{err}</p>}
              <button className="btn" onClick={recheck} disabled={busy}>
                {busy ? "Checking…" : pasteKind === "passage" ? "Check with this passage" : "Check with this text"}
              </button>
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

          {v && runId && <Judgement runId={runId} index={c.index} verdict={v.label} />}
        </div>
      )}
    </article>
  );
}
