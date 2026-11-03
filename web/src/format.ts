import type { Citation } from "./types";

export type Outcome = "Supported" | "Contradicted" | "Not enough evidence" | "Could not check";

export function outcome(c: Citation): Outcome {
  if (c.status !== "checked" || !c.verdict) return "Could not check";
  return c.verdict.label === "SUPPORT" ? "Supported" : c.verdict.label === "CONTRADICT" ? "Contradicted" : "Not enough evidence";
}

export const OUTCOME_CLASS: Record<Outcome, string> = {
  Supported: "ok",
  Contradicted: "bad",
  "Not enough evidence": "warn",
  "Could not check": "muted",
};

// The verifier is not calibrated yet: "1.00" would overstate certainty.
export function conf(x: number | null | undefined): string {
  if (x === null || x === undefined) return "–";
  return x >= 0.995 ? "≥ 0.99" : x.toFixed(2);
}

// Only follow ?next= to a path on this site: "/check" yes; "//evil.example", "/\\evil.example" or "https://..." no.
export function safeNext(next: string | null, fallback = "/check"): string {
  if (!next || !next.startsWith("/") || next.startsWith("//") || next.includes("\\") || /[\u0000-\u001f]/.test(next)) return fallback;
  return next;
}

export function when(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
  } catch {
    return iso;
  }
}

export const STEP_LABEL: Record<string, string> = {
  "resolve reference": "Found the reference",
  "fetch paper": "Fetched the paper",
  "verify abstract": "Read the abstract",
  "read full text?": "Full text needed?",
  "find open-access full text": "Looked for open-access full text",
  "verify full text": "Read the full text",
  "look for a replacement?": "Replacement search",
  "search for a replacement": "Searched for a better paper",
  "abstract pasted": "You pasted the abstract",
};
