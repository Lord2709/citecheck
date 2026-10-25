import { useState } from "react";
import { post } from "../api";
import { track } from "../track";
import type { DiscoveryReport } from "../types";

const SOURCE_NAME: Record<string, string> = { openalex: "OpenAlex", s2: "Semantic Scholar", arxiv: "arXiv", corpus: "SciFact" };

export default function FindPapers() {
  const [direction, setDirection] = useState("");
  const [k, setK] = useState(10);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [rep, setRep] = useState<DiscoveryReport | null>(null);

  async function search() {
    setError("");
    if (!direction.trim()) return setError("Describe your research direction first, in a sentence or two.");
    setBusy(true);
    try {
      const r = await post<DiscoveryReport>("/api/discover", { direction, k });
      setRep(r);
      track("discover", { results: r.results.length });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <div className="page-head">
        <h1>Find papers</h1>
        <p className="lead">Describe what you're working on. CiteCheck searches OpenAlex, Semantic Scholar and arXiv, merges what they find, and shows the sentence that makes each paper relevant.</p>
      </div>
      <section className="card composer">
        <textarea value={direction} onChange={(e) => setDirection(e.target.value)} rows={3} aria-label="Research direction"
                  placeholder="e.g. checking whether cited papers actually support the claims made in scientific writing" />
        <div className="row">
          <label className="inline">Show
            <select value={k} onChange={(e) => setK(Number(e.target.value))}>
              {[5, 10, 15, 20].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
            papers</label>
          <button className="btn btn-primary" onClick={search} disabled={busy}>{busy ? "Searching…" : "Find papers"}</button>
        </div>
        {error && <p className="error" role="alert">{error}</p>}
      </section>

      {busy && <div className="progress-wrap"><div className="progress-text"><span className="spinner small" />Searching three sources…</div></div>}

      {rep && !busy && (
        <section className="results">
          {Object.entries(rep.errors).map(([s, m]) => (
            <div key={s} className="banner">{SOURCE_NAME[s] ?? s} didn't answer this time ({m.split(":")[0]}). Showing results from the others.</div>
          ))}
          {rep.results.length === 0 && <p className="muted">No papers found. Try fewer or more general words.</p>}
          <ol className="papers">
            {rep.results.map((c, i) => (
              <li key={i} className="card paper">
                <div className="paper-top">
                  <span className={`pill ${c.band.startsWith("likely relevant") ? "ok" : c.band.startsWith("maybe") ? "warn" : "muted"}`}>{c.band}</span>
                  <span className="muted small">{c.sources.map((s) => SOURCE_NAME[s] ?? s).join(" · ")}</span>
                </div>
                <h3>{c.paper.url ? <a href={c.paper.url} target="_blank" rel="noreferrer" onClick={() => track("paper_open", { rank: i + 1 })}>{c.paper.title}</a> : c.paper.title}</h3>
                <p className="muted small">{[c.paper.venue, c.paper.year].filter(Boolean).join(" · ")}{c.paper.has_abstract ? "" : " · no abstract available"}</p>
                {c.key_sentence && <blockquote className="evidence small">{c.key_sentence}</blockquote>}
                {c.matched_terms.length > 0 && (
                  <div className="terms">{c.matched_terms.slice(0, 8).map((t) => <span key={t} className="tag">{t}</span>)}</div>
                )}
              </li>
            ))}
          </ol>
          <p className="muted small">Search query: <code>{rep.query}</code>. {rep.note}</p>
        </section>
      )}
    </div>
  );
}
