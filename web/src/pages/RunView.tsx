import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { get } from "../api";
import Results from "../components/Results";
import { when } from "../format";
import type { Citation, DiscoveryReport, DraftReport, Summary } from "../types";

interface Run {
  id: string;
  kind: string;
  created_at: string;
  status: string;
  summary: Summary | null;
  report: DraftReport | DiscoveryReport | null;
  error: string | null;
}

export default function RunView() {
  const { id } = useParams();
  const [run, setRun] = useState<Run | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    get<Run>(`/api/runs/${id}`).then(setRun).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <div className="page"><p className="error">{error}</p><Link to="/history">← Back to history</Link></div>;
  if (!run) return <div className="page center"><span className="spinner" aria-label="Loading" /></div>;

  const rep = run.report;
  return (
    <div className="page">
      <Link to="/history" className="back">← History</Link>
      <div className="page-head">
        <h1>{run.kind === "discovery" ? "Paper search" : "Citation check"}</h1>
        <p className="muted">{when(run.created_at)}</p>
      </div>
      {run.status === "error" && <div className="banner banner-bad">This check stopped with an error: {run.error}</div>}
      {rep && rep.kind === "draft_check" && run.summary && (
        <Results citations={rep.citations} summary={run.summary} warnings={rep.warnings} runId={run.id} done
                 onUpdate={(c: Citation, s: Summary) => setRun({ ...run, summary: s,
                   report: { ...rep, citations: rep.citations.map((x) => (x.index === c.index ? c : x)) } })} />
      )}
      {rep && rep.kind === "discovery" && (
        <section className="results">
          <p className="lead small">“{rep.direction}”</p>
          <ol className="papers">
            {rep.results.map((c, i) => (
              <li key={i} className="card paper">
                <h3>{c.paper.url ? <a href={c.paper.url} target="_blank" rel="noreferrer">{c.paper.title}</a> : c.paper.title}</h3>
                <p className="muted small">{[c.paper.venue, c.paper.year].filter(Boolean).join(" · ")} · {c.band}</p>
                {c.key_sentence && <blockquote className="evidence small">{c.key_sentence}</blockquote>}
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  );
}
