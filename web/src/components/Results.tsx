import { useMemo, useState } from "react";
import { download } from "../api";
import { outcome, type Outcome } from "../format";
import { track } from "../track";
import type { Citation, Summary } from "../types";
import CitationCard from "./CitationCard";

interface Props {
  citations: Citation[];
  summary: Summary;
  warnings?: string[];
  runId?: string;
  done: boolean;
  onUpdate?: (c: Citation, s: Summary) => void;
}

const FILTERS: { key: "all" | Outcome; label: string; field?: keyof Summary; cls: string }[] = [
  { key: "all", label: "All", field: "citations", cls: "" },
  { key: "Supported", label: "Supported", field: "supported", cls: "ok" },
  { key: "Contradicted", label: "Contradicted", field: "contradicted", cls: "bad" },
  { key: "Not enough evidence", label: "Not enough evidence", field: "not_enough_evidence", cls: "warn" },
  { key: "Could not check", label: "Couldn't check", field: "could_not_check", cls: "muted" },
];

export default function Results({ citations, summary, warnings = [], runId, done, onUpdate }: Props) {
  const [filter, setFilter] = useState<"all" | Outcome>("all");
  const shown = useMemo(() => citations.filter((c) => filter === "all" || outcome(c) === filter), [citations, filter]);

  return (
    <section className="results" aria-live="polite">
      <div className="summary-row" role="group" aria-label="Filter by outcome">
        {FILTERS.map((f) => (
          <button key={f.key} className={`stat ${f.cls} ${filter === f.key ? "active" : ""}`} aria-pressed={filter === f.key}
                  onClick={() => { setFilter(f.key); track("filter", { filter: f.key }); }}>
            <span className="stat-l">{f.label}</span>
            <span className="stat-n">{f.field ? (summary[f.field] as number) : 0}</span>
          </button>
        ))}
      </div>
      {warnings.map((w, i) => <div key={i} className="banner">{w}</div>)}
      {done && !!summary.abstract_only && (
        <p className="note abstract-only">
          <strong>
            {summary.abstract_only} of {summary.citations - summary.could_not_check} verdict{summary.citations - summary.could_not_check === 1 ? "" : "s"}{" "}
            rest{summary.abstract_only === 1 ? "s" : ""} on the abstract alone
          </strong>
          {summary.no_free_full_text ? `, and for ${summary.no_free_full_text} of them no free full text exists` : ""}.
          Numbers and detailed results are usually only in the full paper: open a card to paste the passage that backs your sentence.
        </p>
      )}
      {done && summary.read_full_text + summary.with_suggestion > 0 && (
        <p className="muted small">
          Read the open-access full text for {summary.read_full_text} citation{summary.read_full_text === 1 ? "" : "s"};
          suggested a better paper for {summary.with_suggestion}.
        </p>
      )}
      <div className="cards">
        {shown.map((c) => <CitationCard key={`${c.index}-${c.status}-${c.verdict?.label ?? ""}`} c={c} runId={runId} onUpdate={onUpdate} />)}
        {shown.length === 0 && done && <p className="muted">Nothing here.</p>}
      </div>
      {done && runId && (
        <div className="actions">
          <button className="btn btn-ghost" onClick={() => { track("report_download", {}); download(`/api/runs/${runId}/report.md`, "citecheck_report.md"); }}>
            Download the report
          </button>
          <span className="muted small">Confidence is the model's score and is not calibrated yet: “≥ 0.99” means very sure, not certainly right.</span>
        </div>
      )}
    </section>
  );
}
