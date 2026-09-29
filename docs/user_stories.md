# User stories and acceptance tests

Owner: Product (Vyom), with Users & Research (Ritika).  Each story maps to a task in `evidence/templates/runbook.md`, so a
user test is also an acceptance test.

| # | As a... | I want to... | So that... | Acceptance criterion | Task test |
|---|---|---|---|---|---|
| 1 | grad student writing related work | paste my sentence and the DOI of the paper I cite | I catch a citation that does not say what I claimed | verdict + evidence within 2 min, unaided | T1-1..3 (seeded SciFact claims), T2 (own citation) |
| 2 | careful reviewer | see the exact sentences behind the verdict | I can verify the tool instead of trusting it | participant names the deciding sentence | T1 (recorded in notes) |
| 3 | cautious researcher | get "not enough evidence" when the abstract is silent | I am not falsely reassured | on NEI stimuli the tool abstains or the user notices the evidence is unrelated | T1 (NEI stimulus) |
| 4 | researcher on a bad connection | paste an abstract when a DOI lookup fails | I am never blocked | pasted-abstract path works offline | any |
| 5 | reader triaging papers (secondary) | describe my topic and get a relevance hint | I skim faster | participant can say what the hint was based on | optional |

## Personas to recruit (Ritika)

Grad students and research assistants who **cite papers weekly** and are not on our team. Prefer at least one biomedical /
life-science user (our validated domain) and at least one from another field (to see the domain gap first-hand).

## What "success" means for a user test

Completed without help **and** reached the correct answer when a gold answer exists (computed by `tools/summarize_tasktests.py`).
n is 3-6: describe what happened, never quote a percentage as if it generalises.
