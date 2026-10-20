"""Report rendering (src/report.py) on hand-made dicts."""
import pytest

from src import report

DRAFT = {"kind": "draft_check", "warnings": ["Checked the first 2 of 3 citations."], "tau_strict": 0.85,
         "backend": {"verifier": "nli", "tau": 0.6}, "created_at": "2026-10-20T15:00:00-04:00", "citations": [
    {"index": 1, "marker": "[1]", "sentence": "A holds [1].", "claim": "A holds.", "reference_text": "Doe 2020",
     "status": "checked", "paper": {"title": "Paper A", "year": 2020, "url": "https://x/a"}, "read_full_text": True,
     "verdict": {"label": "SUPPORT", "display_label": "SUPPORTS", "confidence": 0.91,
                 "evidence": [{"sentences": ["A holds in mice."]}]}, "suggestions": [],
     "steps": [{"action": "verify abstract", "detail": "NOT ENOUGH EVIDENCE"}]},
    {"index": 2, "marker": "[2]", "sentence": "B | C [2].", "claim": "B | C.", "status": "checked",
     "paper": {"title": "Paper B"}, "read_full_text": False,
     "verdict": {"label": "CONTRADICT", "display_label": "CONTRADICTS", "confidence": 0.8, "evidence": []},
     "suggestions": [{"paper": {"title": "Paper C", "url": "https://x/c"}, "confidence": 0.9, "sentences": ["B and C."]}]},
    {"index": 3, "marker": "[7]", "sentence": "D [7].", "claim": "D.", "status": "unresolved",
     "status_detail": "no entry for [7] in the reference list", "verdict": None, "suggestions": []},
]}


def test_summary_and_rows():
    s = report.summarize(DRAFT)
    assert s == {"citations": 3, "supported": 1, "contradicted": 1, "not_enough_evidence": 0, "could_not_check": 1,
                 "needs_attention": 2, "read_full_text": 1, "with_suggestion": 1}
    rows = report.table_rows(DRAFT)
    assert rows[1]["Suggestion"] == "Paper C" and rows[2]["Outcome"] == "Could not check" and rows[2]["Note"]


def test_markdown_draft_and_discovery():
    md = report.to_markdown(DRAFT)
    assert "1 supported, 1 contradicted" in md and "| Paper B |" in md and "Suggested paper to read:** Paper C" in md
    assert "after reading the open-access full text" in md and "no entry for [7]" in md and "Paper A (2020)" in md
    disc = {"kind": "discovery", "direction": "claims", "query": "claims", "note": "uncalibrated",
            "errors": {"s2": "HTTP 429"}, "results": [{"paper": {"title": "P", "year": 2020, "venue": "EMNLP",
                                                                  "url": "https://x"}, "score": 0.5, "band": "maybe relevant",
                                                        "sources": ["openalex"], "matched_terms": ["claims"],
                                                        "key_sentence": "We verify claims."}]}
    md2 = report.to_markdown(disc)
    assert "1. **P** (EMNLP, 2020)" in md2 and "did not answer" in md2
    with pytest.raises(ValueError):
        report.to_markdown({"kind": "other"})
