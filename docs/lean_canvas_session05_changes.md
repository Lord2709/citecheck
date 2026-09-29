# Proposed lean-canvas edits (Vyom applies them to `lean-canvas.md` in his own PR)

These come from what the Session 5 work taught us. Apply only what the team agrees with; the report's "Lean canvas changes"
section must describe what actually changed in the PR.

1. **Sharpen the value proposition and MVP job (section 3 / 2).**
   "We help researchers check, in under a minute, whether the paper they cite supports their claim, by showing the evidence
   sentences, instead of re-reading it or trusting an ungrounded chatbot." Relevance and citation audit move to *secondary*.
2. **Key metrics (section 7).** North star = end-to-end claim-level macro-F1 on SciFact dev with a CI. Add the guardrail
   **false-SUPPORT rate** and the validation metrics (task success, time, agreement). See `docs/north_star.md`.
3. **Data and approach (section 9).** Note that SciFact claims are rewritten citation sentences with `cited_doc_ids`, so it is the
   right proxy; state the domain limit (biomedical) and that we read abstracts only.
4. **Cost structure (section 8).** Replace "will be measured" with the measured latency per claim and "$0 marginal for a local model".
5. **Key risks (section 11).** Add: (a) domain shift beyond biomedicine, (b) abstract-only evidence misses support in results/methods,
   (c) real citation sentences are messier than SciFact's atomic claims, (d) dependence on free paper APIs that can rate-limit.
6. **Key assumption to test (section 12).** Make it measurable: "at least `<<TBD>>` of outside participants complete the citation-check
   task correctly and unaided, and prefer it to their current method."
