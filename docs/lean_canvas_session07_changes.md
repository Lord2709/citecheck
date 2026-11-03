# Lean canvas changes, Session 7 (applied to `lean-canvas.md`)

Owner: Product.  Unlike Session 5, these changes are applied to the canvas itself in the same PR.

| Canvas section | Before (up to the midterm) | Now | Why |
|---|---|---|---|
| Solution | check one hand-typed claim against one paper | an agent with two jobs: find papers for a research direction, and check every citation in a draft | narrow product next to other teams; matches the researcher's real job (`docs/agent_plan.md`) |
| Unique value proposition | judge whether a paper is worth reading and whether its citations hold up | find papers and check every citation in a draft, with the deciding sentences shown, and say when unsure | the agent makes both halves real |
| Unfair advantage | NLP classification with evidence shown | a verifier we fine-tune and calibrate ourselves, plus an agent that decides when to read the full text | the verifier is our measured bottleneck (oracle ceiling 0.646) |
| Key metrics | citation-support F1 | SciFact dev macro-F1 + false-SUPPORT guardrail (unchanged), plus real-world set accuracy and agent metrics | SciFact claims are cleaner than real citations |
| Cost structure | "measured later" | free resources only; costs to watch are free-tier limits, latency and hosting memory | OpenAlex now meters usage |
| Ethics | evidence shown, limitations reported | + text-based PDFs only; open-access full text only; replacements are suggestions, never swaps | the agent can push users toward citing papers unread |
| Key risks | five | + free-tier limits and outages; full text often unavailable; scope risk now managed by build order | new dependencies the agent brings |
| Key assumption | grounded verdicts are useful | still untested (no user before the midterm); + checking a whole draft beats one claim at a time | the pivot rests on it |

Unchanged: target users, problem, channels, customer segments.
