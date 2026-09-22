# Lean Canvas : CiteCheck

## 1. User and Problem

**Target users:**  
Students and researchers who regularly read and cite academic papers.

**Problem:**  
Researchers often need to decide whether a paper is relevant to their research direction and whether a cited paper actually supports a specific claim. Today, this usually requires skimming abstracts, manually reading papers, and checking cited evidence one paper at a time. This process is time-consuming and makes it easy to miss whether a citation genuinely supports the claim being made.

**Key alternatives:**
- Manually reading the full paper and its cited sources
- Google Scholar or Semantic Scholar for finding and exploring papers
- General-purpose chatbots for paper summaries, which may provide answers without retrieval-grounded evidence

---

## 2. Solution

CiteCheck is an NLP based paper judging tool that helps researchers evaluate academic papers more efficiently.

A user provides:
1. A research direction or short description of their topic
2. A paper link or DOI
3. A claim or citation that they want to verify

CiteCheck then:
- Retrieves relevant information from the paper and its cited sources
- Determines whether the cited evidence supports the claim
- Provides a verdict along with the relevant evidence passages
- Can also assess whether the paper is relevant to the user's research direction

The initial MVP will focus on **citation-support verification** as the primary NLP task.

Possible citation-support outputs:

- **SUPPORTS** : the cited evidence supports the claim
- **CONTRADICTS** : the cited evidence contradicts the claim
- **NOT ENOUGH EVIDENCE** : the available evidence does not adequately support or contradict the claim

---

## 3. Unique Value Proposition

 **CiteCheck helps researchers judge whether a paper is worth reading and whether its citations hold up, faster than manually reading papers or trusting an ungrounded chatbot.**

Unlike a traditional academic search engine, CiteCheck does not only help users find papers. It focuses on evaluating the relationship between a claim and the evidence provided by its cited paper.

---

## 4. Unfair Advantage

CiteCheck combines:
- Retrieval of relevant evidence from academic papers
- NLP-based citation-support classification
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

**Citation-support F1 score on a held-out labeled evaluation set.**

The primary technical evaluation will measure how accurately CiteCheck classifies citation relationships compared with labeled scientific claim-verification data such as SciFact/SciFact-Open.

### Supporting Metrics

**Retrieval Precision@k:**  
Measures whether the system retrieves relevant evidence passages among the top-k results.

**User task time:**  
Measures how long a researcher takes to reach a citation-support judgment using CiteCheck compared with their normal workflow.

**User agreement:**  
Measures how often researchers agree with CiteCheck's verdict when evaluating real examples.

Metrics will be tracked across iterations so that improvements or regressions are visible from one project session to the next.

---

## 8. Cost Structure

The initial prototype will prioritize low-cost infrastructure.

**Expected costs:**
- Local or self-hosted BM25/dense retrieval over an available academic corpus
- Computing resources for running NLP models
- Model inference costs if external APIs are used
- Storage for permitted academic datasets

The actual per-request inference cost will be measured once the end-to-end pipeline is running.

The project will prioritize openly available and appropriately licensed datasets and corpora to avoid unnecessary data acquisition costs.

---

## 9. Data and NLP Approach

The initial pipeline will follow:

**User claim → Retrieve relevant evidence → Citation-support classifier → Verdict + evidence**

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
Make citation-support verification the primary MVP and treat additional functionality as secondary or future work.

---

## 12. Key Assumption to Test

The most important early assumption is:

 **Students and researchers will find evidence-grounded citation-support judgments useful enough to reduce the time and effort required to verify citations.**

The first validation cycle will therefore focus on putting a working citation-verification pipeline in front of real students/researchers and measuring both system performance and user task time.
