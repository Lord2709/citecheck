# Lean Canvas : CiteCheck

_Last changed: 2026-10-20 (Session 7, after the midterm: CiteCheck becomes an agent that finds papers and checks every
citation in a draft). What changed and why: `docs/lean_canvas_session07_changes.md`. Plan: `docs/agent_plan.md`._

## 1. User and Problem

**Target users:**  
Students and researchers who regularly read and cite academic papers.

**Problem:**  
Researchers often need to decide whether a paper is relevant to their research direction and whether a cited paper actually supports a specific claim. Today, this usually requires skimming abstracts, manually reading papers, and checking cited evidence one paper at a time. This process is time-consuming and makes it easy to miss whether a citation genuinely supports the claim being made.

**Key alternatives:**
- Manually reading the full paper and its cited sources
- Google Scholar or Semantic Scholar for finding and exploring papers
- General-purpose chatbots for paper summaries, which may provide answers without retrieval-grounded evidence
- Reference managers (Zotero, Mendeley), which store citations but never check that a citation supports the sentence it is attached to

---

## 2. Solution

CiteCheck is an NLP agent with two jobs that share the same tools:

1. **Discovery:** the user describes a research direction; the agent searches open scholarly sources, ranks the
   candidates with our models and explains why each paper is relevant.
2. **Verification:** the user pastes a draft (or uploads a text-based PDF); the agent finds every cited claim, resolves
   each reference, fetches the cited paper, finds the evidence sentences and verifies the claim with our fine-tuned
   verifier. When unsure it reads the open-access full text; when a citation fails it suggests a paper that does
   support the claim, with the evidence shown.

The MVP up to the midterm checked one claim against one paper. Verification stays the core we evaluate most rigorously;
discovery feeds it.

Possible citation-support outputs:

- **SUPPORTS** : the cited evidence supports the claim
- **CONTRADICTS** : the cited evidence contradicts the claim
- **NOT ENOUGH EVIDENCE** : the available evidence does not adequately support or contradict the claim

---

## 3. Unique Value Proposition

 **CiteCheck helps researchers find papers for their research direction and check every citation in their draft, showing the sentences that decide each verdict and saying so when it is unsure, faster than reading every cited paper and safer than trusting an ungrounded chatbot.**

Unlike a traditional academic search engine, CiteCheck does not only help users find papers. It focuses on evaluating the relationship between a claim and the evidence provided by its cited paper.

---

## 4. Unfair Advantage

CiteCheck combines:
- Retrieval of relevant evidence from academic papers
- A citation-support verifier we fine-tune and calibrate ourselves, with a tuned abstain rule (false SUPPORTS are the failure we guard against)
- An agent that decides when an abstract is not enough and reads the full text, measured against our own fixed pipeline
- Evidence passages shown alongside the verdict
- Evaluation against labeled scientific claim-verification datasets
- User validation with researchers and students

The system is designed to provide an evidence-grounded judgment rather than relying only on a generated summary.

---

## 5. Channels

Initial user acquisition will focus on direct access to potential users:

- Cold outreach to students and researchers at UMD
- Adjacent university research labs
- Student communities
- Academic Slack and Discord communities
- Relevant online research communities such as academic discussion forums

Early validation will prioritize direct conversations and hands-on testing with researchers and students rather than large-scale distribution.

---

## 6. Customer Segments

**Primary users:**
- Students
- Academic researchers
- Research assistants
- Students writing research papers or thieses

**Early adopters:**
- Students and researchers who frequently review literature
- Students working on literature reviews
- Researchers who need to verify citations or scientific claims
- Researchers working with large numbers of academic papers

---

## 7. Key Metrics

### North-Star Metric

**Claim-level macro-F1 on SciFact dev** of the deployed model, with a 95% bootstrap CI, and the **false-SUPPORT rate** as
its guardrail (definitions and targets: `docs/north_star.md`).

From Session 9 we also report accuracy on our own **real-world citation set** (real citing sentences from two fields,
double-labelled), because SciFact's claims are cleaner than real citations.

### Supporting Metrics

**Retrieval Precision@k:**  
Measures whether the system retrieves relevant evidence passages among the top-k results.

**User task time:**  
Measures how long a researcher takes to reach a citation-support judgment using CiteCheck compared with their normal workflow.

**User agreement:**  
Measures how often researchers agree with CiteCheck's verdict when evaluating real examples.

**Agent metrics:**  
Share of "unsure" answers that reading the full text turns into correct verdicts, extra seconds per citation, and the
bad-replacement rate of suggested papers.

Metrics will be tracked across iterations so that improvements or regressions are visible from one project session to the next.

---

## 8. Cost Structure

Everything runs on free resources: open scholarly APIs (OpenAlex, Semantic Scholar, arXiv, Crossref, Unpaywall,
Europe PMC), open models from Hugging Face, a laptop GPU for fine-tuning (free Colab as backup) and CPU for the agent.

**Costs to watch:**
- Free-tier limits: OpenAlex meters searches with a daily budget, so every response is cached and searches are spread across sources
- Latency, not money: about 0.5 s per claim on a laptop CPU for the current verifier; full-text reading adds more, which we measure
- Free hosting has little memory, which may limit the size of the model we can deploy

The project will prioritize openly available and appropriately licensed datasets and corpora to avoid unnecessary data acquisition costs.

---

## 9. Data and NLP Approach

The initial pipeline will follow:

**Draft → extract cited claims → resolve references → fetch paper → find evidence → fine-tuned verifier → (unsure: read full text) → verdict + evidence (+ suggested replacement)**

**Research direction → search open sources → rank and explain → papers to read**

The system will use academic claim-verification data such as **SciFact/SciFact-Open** for development and evaluation.

The evaluation will compare the NLP system against an appropriate baseline, such as a zero-shot or simpler classification approach.

The project will separately evaluate:
- Retrieval quality
- Citation-support classification
- End-to-end user performance

This separation will help identify whether errors come from retrieving the wrong evidence or from incorrectly classifying the retrieved evidence.

---

## 10. Ethical Considerations and Privacy

CiteCheck will use only appropriately licensed or openly available academic data.

Privacy principles:
- Do not collect unnecessary personal information
- Avoid storing personally identifiable information from users
- Anonymize user-testing evidence
- Clearly document the sources and licenses of datasets

Potential bias is an important concern because academic datasets and corpora may overrepresent highly cited research, English-language publications, and certain research communities.

CiteCheck reads text-based PDFs only and reads full text only when a legal open-access copy exists; for other papers it
says it read only the abstract. Replacement papers are suggestions to read, never automatic swaps, so the tool does not
encourage citing papers unread.

A particularly important failure mode is a false SUPPORTS judgment, because it could give researchers unwarranted confidence that a citation supports a claim when it does not.

The system will therefore expose supporting evidence and report limitations rather than presenting its predictions as guaranteed facts.

---

## 11. Key Risks

### 1. Retrieval quality

If the system retrieves irrelevant passages, even a strong NLP classifier may produce an incorrect verdict.

**Mitigation:**  
Track retrieval Precision@k and inspect retrieval errors separately from classification errors.

### 2. Citation-support classification accuracy

The NLI/classification model may not reliably understand complex scientific claims.

**Mitigation:**  
Establish a baseline on labeled data before fine-tuning and perform error analysis on incorrect predictions.

### 3. User trust

Researchers may be hesitant to rely on an automated citation-verification system.

**Mitigation:**  
Show the evidence passages supporting every verdict and clearly communicate uncertainty and limitations.

### 4. Data availability and licensing

Academic papers may be paywalled or have usage restrictions.

**Mitigation:**  
Use openly available and appropriately licensed corpora and avoid unauthorized scraping of restricted content.

### 5. Product scope

Trying to simultaneously solve paper relevance, citation verification, summarization, and PDF processing could make the MVP too broad.

**Mitigation:**  
Verification stays the core we evaluate rigorously; discovery reuses its tools. OCR is out (text-based PDFs only), and the
build order in `docs/agent_plan.md` puts the stretch items last.

### 6. Free-tier limits and source outages

OpenAlex now meters usage, and any free API can throttle or change.

**Mitigation:**  
Cache every response, spread calls across sources with fallbacks, and record live checks (`tools/live_sources_check.py`).

### 7. Full text is often not available

Most claims are supported in a paper's body, but paywalled papers have no legal full text.

**Mitigation:**  
Use open-access copies only, say when only the abstract was read, and measure how often full text was available.

---

## 12. Key Assumption to Test

The most important early assumption is:

 **Students and researchers will find evidence-grounded citation-support judgments useful enough to reduce the time and effort required to verify citations.**

Still untested: no outside user had used CiteCheck by the midterm. A second assumption now joins it: **checking a whole
draft at once is worth more to them than checking one claim at a time.**

The first validation cycle will therefore focus on putting a working citation-verification pipeline in front of real students/researchers and measuring both system performance and user task time.
