import type { Citation } from "./types";

export type Outcome = "Supported" | "Contradicted" | "Not enough evidence" | "Could not check";

export function outcome(c: Citation): Outcome {
  if (c.status !== "checked" || !c.verdict) return "Could not check";
  return c.verdict.label === "SUPPORT" ? "Supported" : c.verdict.label === "CONTRADICT" ? "Contradicted" : "Not enough evidence";
}

// A verdict that rests on the abstract alone: not on the full text, nor on text the researcher pasted.
export function abstractOnly(c: Citation): boolean {
  return c.status === "checked" && !!c.verdict && !c.read_full_text && !c.abstract_pasted;
}

// Looked for a free full text and could not read one (also for reports saved before full_text_status existed).
export function noFreeFullText(c: Citation): boolean {
  if (c.full_text_status) return ["not_found", "blocked", "off"].includes(c.full_text_status);
  return c.steps.some((s) => s.action === "find open-access full text");
}

// A free copy a person can open, when its website refused our download ("" when there is none).
export function freeCopyUrl(c: Citation): string {
  return c.steps.find((s) => s.action === "free copy")?.detail ?? "";
}

// What the card's label says: "Not in the abstract" when only the abstract could be read.
export function displayOutcome(c: Citation): string {
  const o = outcome(c);
  return o === "Not enough evidence" && abstractOnly(c) && noFreeFullText(c) ? "Not in the abstract" : o;
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
  "passage pasted": "You pasted a passage",
  "free copy": "A free copy exists, but its site refused our download",
};
