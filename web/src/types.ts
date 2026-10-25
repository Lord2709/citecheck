export type Label = "SUPPORT" | "CONTRADICT" | "NEI";

export interface Paper {
  paper_id: string;
  title: string;
  year?: number | null;
  venue?: string | null;
  doi?: string | null;
  url?: string | null;
  source?: string;
}

export interface Evidence {
  title: string;
  sentences: string[];
  probs: { support: number; neutral: number; contradict: number };
}

export interface Verdict {
  label: Label;
  display_label: string;
  confidence: number;
  abstained: boolean;
  note: string;
  evidence: Evidence[];
}

export interface Step {
  action: string;
  detail: string;
  ms: number;
}

export interface Suggestion {
  paper: Paper;
  confidence: number;
  sentences: string[];
}

export interface Citation {
  index: number;
  sentence: string;
  claim: string;
  marker: string;
  reference_text: string;
  identifier: string | null;
  status: "checked" | "unresolved" | "not_found" | "no_abstract" | "error";
  status_detail: string;
  paper: Paper | null;
  verdict: Verdict | null;
  read_full_text: boolean;
  full_text_source: string;
  suggestions: Suggestion[];
  steps: Step[];
  abstract_pasted?: boolean;
}

export interface Summary {
  citations: number;
  supported: number;
  contradicted: number;
  not_enough_evidence: number;
  could_not_check: number;
  needs_attention: number;
  read_full_text: number;
  with_suggestion: number;
}

export interface DraftReport {
  kind: "draft_check";
  citations: Citation[];
  warnings: string[];
  backend: Record<string, unknown>;
  tau_strict: number;
  created_at?: string;
}

export interface Job {
  id: string;
  run_id: string;
  status: "queued" | "running" | "done" | "error";
  done: number;
  total: number;
  citations: Citation[];
  report: DraftReport | null;
  error: string;
  summary: Summary;
}

export interface Candidate {
  paper: Paper & { has_abstract: boolean };
  sources: string[];
  score: number;
  band: string;
  matched_terms: string[];
  key_sentence: string;
}

export interface DiscoveryReport {
  kind: "discovery";
  direction: string;
  query: string;
  results: Candidate[];
  errors: Record<string, string>;
  note: string;
  run_id?: string;
}

export interface Me {
  id: string;
  email: string;
  is_admin: boolean;
  consent: { research: boolean | null; text: boolean };
  needs_consent: boolean;
}

export interface RunRow {
  id: string;
  kind: "draft_check" | "discovery" | "claim_check";
  created_at: string;
  status: string;
  summary: Record<string, unknown> | null;
  input_chars: number;
}
