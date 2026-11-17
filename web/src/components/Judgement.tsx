import { useState } from "react";
import { post } from "../api";
import { track } from "../track";
import type { Label } from "../types";

// "Is this right?" on one citation.  The first click is saved at once, so a "No" is never lost; the right answer and a
// comment refine that same record.
type Answer = "AGREE" | "DISAGREE" | "UNSURE";
type Right = Label | "WRONG_PAPER";

const RIGHT: { value: Right; text: string }[] = [
  { value: "SUPPORT", text: "The paper supports it" },
  { value: "CONTRADICT", text: "The paper contradicts it" },
  { value: "NEI", text: "The paper doesn't say" },
  { value: "WRONG_PAPER", text: "It read the wrong paper" },
];

export default function Judgement({ runId, index, verdict }: { runId: string; index: number; verdict: Label }) {
  const [answer, setAnswer] = useState<Answer | null>(null);
  const [right, setRight] = useState<Right | null>(null);
  const [id, setId] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [commentSent, setCommentSent] = useState(false);
  const [error, setError] = useState("");

  async function choose(a: Answer) {
    setAnswer(a);
    setError("");
    try {
      const r = await post<{ id: number }>("/api/feedback", { run_id: runId, citation_index: index, label: a });
      setId(r.id);
      track("feedback", { answer: a, citation: index });
    } catch {
      setError("Your answer could not be saved. Please try again.");
      setAnswer(null);
    }
  }

  async function refine(body: { label?: Right; comment?: string }) {
    if (id === null) return;
    try {
      await post(`/api/feedback/${id}`, body);
      if (body.label) {
        setRight(body.label);
        track("feedback_detail", { right: body.label, citation: index });
      }
      if (body.comment !== undefined) setCommentSent(true);
    } catch {
      setError("That could not be saved. Please try again.");
    }
  }

  if (answer === null) {
    return (
      <div className="feedback">
        <span className="muted">Is this right?</span>
        <button className="chip" onClick={() => choose("AGREE")}>Yes</button>
        <button className="chip" onClick={() => choose("DISAGREE")}>No</button>
        <button className="chip" onClick={() => choose("UNSURE")}>Not sure</button>
        {error && <span className="error small">{error}</span>}
      </div>
    );
  }

  return (
    <div className="feedback feedback-open">
      <span className="muted">{answer === "AGREE" ? "Thanks, noted." : answer === "UNSURE" ? "Noted as not sure." : "Thanks. What is right?"}</span>
      {answer === "DISAGREE" && (
        <div className="chips" role="group" aria-label="What is right">
          {RIGHT.filter((r) => r.value !== verdict).map((r) => (
            <button key={r.value} className={`chip ${right === r.value ? "chip-on" : ""}`} aria-pressed={right === r.value}
                    onClick={() => refine({ label: r.value })}>{r.text}</button>
          ))}
        </div>
      )}
      {answer !== "AGREE" && !commentSent && (
        <div className="feedback-form">
          <input value={comment} onChange={(e) => setComment(e.target.value)} aria-label="Comment (optional)"
                 placeholder={answer === "DISAGREE" ? "Why? (optional)" : "What would help you decide? (optional)"} />
          <button className="btn btn-small" onClick={() => refine({ comment })} disabled={!comment.trim()}>Send</button>
        </div>
      )}
      {commentSent && <span className="muted">Comment saved.</span>}
      {error && <span className="error small">{error}</span>}
    </div>
  );
}
