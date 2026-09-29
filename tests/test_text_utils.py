from src.text_utils import redact, split_sentences, tokenize, truncate


def test_split_sentences_scientific_abbreviations():
    text = ("Smith et al. reported a 12% rise (p < 0.05). See Fig. 2 for details. The i.e. case was excluded. "
            "J. Lee confirmed it. Was it robust? Yes.")
    out = split_sentences(text)
    assert out[0].startswith("Smith et al. reported") and out[0].endswith("0.05).")
    assert out[1] == "See Fig. 2 for details."
    assert "J. Lee confirmed it." in out
    assert out[-2:] == ["Was it robust?", "Yes."]
    assert split_sentences("") == [] and split_sentences("One sentence only") == ["One sentence only"]


def test_tokenize_stems_and_drops_stopwords():
    assert tokenize("The inhibition of Inhibitors") == ["inhibit", "inhibitor"]
    assert tokenize("IL-6 levels", stem=False) == ["il", "6", "levels"]


def test_redact_and_truncate():
    assert redact("mail me at a.b@umd.edu or call +1 (301) 555-0142 now") == "mail me at [email] or call [phone] now"
    assert truncate("x" * 500, 20).endswith("…") and len(truncate("x" * 500, 20)) == 20
