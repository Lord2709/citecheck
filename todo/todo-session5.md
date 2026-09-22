# Todo — Session 5

## Engineering

* Build the end-to-end pipeline: DOI/link → `fetch_parser.py` → `retrieval.py` → verdict, runnable from `src/main.py`.
* Put up a minimal UI a user can run (Streamlit or Gradio is fine) so the task tests have a real product to use.

## Data and Evaluation

* Build the eval harness in `eval/`: one script that prints F1 on SciFact dev.
* Run the zero-shot baseline and record the number. This is your first metric.
* Measure retrieval precision@k on the current retriever.

## Product

* Write user stories and an MVP scope for the mid-semester demo: what's in, what's out.
* Settle the definition of the north-star metric with Sahil. Is it citation-support F1 alone, or task success in user tests too?

## Users and Research

* Recruit 3 outside users and keep an anonymized roster.
* Run the first task tests on the running product and commit the raw evidence to `evidence/session05/`.

## Report (e.g. Sakshaat)

* `reports/session05.md`.
