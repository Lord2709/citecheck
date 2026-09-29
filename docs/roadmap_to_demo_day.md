# Roadmap: Session 5 to demo day (Dec 1)

Owner: Product (Vyom).  Every week runs the same loop from the guidelines: **build, put it in front of a user, capture raw evidence
that week, measure one number vs last week, write the report by 5:00pm Tuesday.** Fall Break Oct 13 has no class.

| session / date | build (merged to `main`) | user evidence | number to move | risk we retire |
|---|---|---|---|---|
| **5** Sep 29 | end-to-end pipeline, app, eval harness, baseline ladder | 3 outside task tests | first macro-F1 with CI, false-SUPPORT | "is there a product / a metric at all?" |
| **6** Oct 6 | midterm demo; **pivot/persevere decision** | evidence shown live | metric vs baselines | direction |
| **7** Oct 20 | hybrid retrieval + reranker ablation; fine-tuned NLI (train split only); deploy so a stranger can use it (HF Spaces or similar) | 3+ NEW participants on the improved model | macro-F1 (compare to zero-shot with paired CI) | "does training help, or is it noise?" |
| **8** Oct 27 | fixes chosen from error analysis; threshold/abstention work (risk-coverage) | task tests on the fixes | false-SUPPORT rate | over-confidence |
| **9** Nov 3 | a small labelled set of REAL citations from participants' own papers (n about 50) | those participants label our verdicts | accuracy on real citations vs SciFact | the domain/atomic-claim gap |
| **10** Nov 10 | out-of-domain or SciFact-Open check; cost/latency numbers | more task tests | generalisation gap | "works only on SciFact" |
| **11** Nov 17 | feature freeze; final model chosen and promoted; demo-day slot assigned | dress rehearsal with a user | final dev number | last-minute change |
| **12** Nov 24 | final report and slides drafted; README a stranger can follow; recorded backup demo | stranger follows the README | (none: polish) | packaging |
| **13** Dec 1 5pm | `reports/final/` committed to `main` | | | deadline |

Rules for the roadmap: never plan a week with no user contact; if a week ships nothing, the report says so and why (that is credited).
Each row becomes issues with labels, assignees and the milestone for that session.
