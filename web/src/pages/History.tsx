import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { get } from "../api";
import { when } from "../format";
import type { RunRow } from "../types";

const KIND: Record<string, string> = { draft_check: "Draft check", discovery: "Paper search", claim_check: "Single claim" };

function describe(r: RunRow): string {
  const s = r.summary as Record<string, number> | null;
  if (!s) return r.status === "running" ? "still running" : r.status === "error" ? "stopped with an error" : "";
  if (r.kind === "discovery") return `${s.results ?? 0} papers found`;
  return `${s.citations ?? 0} citations · ${s.supported ?? 0} supported · ${(s.contradicted ?? 0) + (s.not_enough_evidence ?? 0) + (s.could_not_check ?? 0)} need a look`;
}

export default function History() {
  const [runs, setRuns] = useState<RunRow[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    get<{ runs: RunRow[] }>("/api/history").then((r) => setRuns(r.runs)).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="page">
      <div className="page-head">
        <h1>History</h1>
        <p className="lead">Your past checks and searches. Only you can see them.</p>
      </div>
      {error && <p className="error">{error}</p>}
      {runs === null && !error && <span className="spinner" aria-label="Loading" />}
      {runs && runs.length === 0 && (
        <div className="card empty">
          <p>Nothing yet. <Link to="/check">Check a draft</Link> or <Link to="/papers">find papers</Link> to get started.</p>
        </div>
      )}
      {runs && runs.length > 0 && (
        <ul className="history">
          {runs.map((r) => (
            <li key={r.id}>
              <Link to={`/runs/${r.id}`} className="card history-row">
                <span className="tag">{KIND[r.kind] ?? r.kind}</span>
                <span className="history-desc">{describe(r)}</span>
                <span className="muted small">{when(r.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
