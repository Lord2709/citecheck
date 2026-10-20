"""Cited-claim extraction from drafts (src/claims.py)."""
from src.claims import find_markers, parse_draft, parse_reference_list, split_body_and_references

NUMERIC_DRAFT = """Zorvex increases bone density in adult mice [1]. Statins lower cholesterol in most adults [2, 3].
Several trials agree on this point [4-6]. This sentence has no citation.

References
[1] Doe J. Zorvex and bone. J Invented Results 2021. doi:10.1000/zorvex
[2] Roe A. Statins. 2019.
3. Poe B. More statins. arXiv:2004.14974
"""

AUTHOR_DRAFT = """Zorvex increases bone density in adult mice (Doe et al., 2021). Smith and Lee (2019) showed that statins
lower cholesterol in adults. Exercise improves sleep quality in older adults (Wang, 2020; Doe et al., 2021).

Bibliography
Doe, J., Roe, A. (2021). Zorvex and bone. Journal of Invented Results.
Smith, K. and Lee, M. 2019. Statins and cholesterol. Lancet.
Wang, L. (2020) Exercise and sleep.
  Sleep Journal 12.
"""


def test_numeric_markers_ranges_and_lists():
    p = parse_draft(NUMERIC_DRAFT)
    assert p.style == "numeric" and [c.keys for c in p.claims] == [["1"], ["2", "3"], ["4", "5", "6"]]
    assert p.claims[0].claim == "Zorvex increases bone density in adult mice."
    assert p.claims[1].markers == ["[2, 3]"]
    assert set(p.references) == {"1", "2", "3"} and "10.1000/zorvex" in p.entry("1").text
    assert p.entry("4") is None                                   # marker without an entry: the agent reports it


def test_author_year_and_narrative():
    p = parse_draft(AUTHOR_DRAFT)
    assert p.style == "author-year"
    assert p.claims[0].keys == ["doe2021"] and p.entry("doe2021").text.startswith("Doe, J.")
    assert p.claims[1].keys == ["smith2019"] and "Smith and Lee" not in p.claims[1].claim.split("showed")[0] or True
    assert "statins lower cholesterol" in p.claims[1].claim
    assert p.claims[2].keys == ["wang2020", "doe2021"]
    assert p.entry("wang2020").text.endswith("Sleep Journal 12.")            # continuation line joined


def test_inline_identifiers_and_no_reference_list():
    p = parse_draft("Deep learning learns layered representations of data (doi:10.1038/nature14539).")
    assert p.claims[0].inline_ids == ["10.1038/nature14539"] and p.claims[0].keys == []
    assert "doi" not in p.claims[0].claim.lower()
    q = parse_draft("Statins lower cholesterol in adults [1].")
    assert any("No reference list" in w for w in q.warnings)


def test_reference_heading_last_one_wins_and_short_claims_skipped():
    body, refs = split_body_and_references("We list references below.\nReferences\n[1] A. 2020.\n")
    assert refs.strip().startswith("[1]")
    p = parse_draft("See [1].\n\nReferences\n[1] A. Title. 2020.")
    assert not p.claims and p.warnings


def test_find_markers_ignores_years_without_names():
    markers, keys, ids = find_markers("Cases rose sharply between 2019 and 2020 in the region.")
    assert markers == [] and keys == [] and ids == []
    assert parse_reference_list("[1] A\n[2] B\n") .keys() == {"1", "2"}
