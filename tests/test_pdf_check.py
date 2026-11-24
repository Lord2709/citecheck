"""Scanned-PDF refusal.  Real text PDFs are generated here byte by byte (no extra libraries); a 'scan' is a page with
no text layer.  The thresholds are starting guesses: these tests pin the behaviour, not the right cut-offs."""
import pytest

pypdf = pytest.importorskip("pypdf")

from src import pdf_check as pc  # noqa: E402

PARA = ("Statins lower LDL cholesterol in adults with high cardiovascular risk. In a randomised trial of four thousand "
        "patients the treatment group showed fewer heart attacks over five years. ")


def make_pdf(pages):
    """pages: list of str (text page) or None (blank page, like a scan without an OCR layer)."""
    objs = []
    n = len(pages)
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(n))
    objs.append("<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>")
    font_id = 3 + 2 * n
    for i, text in enumerate(pages):
        content_id = 4 + 2 * i
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {content_id} 0 R "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> >>")
        if text:
            lines = [text[j:j + 80] for j in range(0, len(text), 80)]
            body = "BT /F1 10 Tf 40 760 Td 12 TL " + " ".join(
                "(" + l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") '" for l in lines) + " ET"
        else:
            body = ""
        objs.append(f"<< /Length {len(body)} >>\nstream\n{body}\nendstream")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = b"%PDF-1.4\n"
    offsets = []
    for k, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{k} 0 obj\n{o}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{off:010d} 00000 n \n" for off in offsets).encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out


def test_readable_ratio_and_page_rule():
    assert pc.readable_ratio("") == 0.0
    assert pc.readable_ratio(PARA) > 0.9
    assert pc.readable_ratio("ÿþ\x00\x01 ¤¤¤ ##@@ 1234 %%%% ~~~") < 0.2         # broken-font garbage
    assert pc.page_is_text(PARA * 3) and not pc.page_is_text("Fig. 3")             # too short
    assert not pc.page_is_text("#@! " * 200)                                        # long but unreadable


def test_assess_pages_kinds():
    good, blank = PARA * 3, ""
    assert pc.assess_pages([good] * 5).kind == "text"
    assert pc.assess_pages([good] * 9 + [blank]).kind == "text"                     # one figure page is fine
    m = pc.assess_pages([good, blank, good, blank])
    assert m.kind == "mixed" and m.accepted and m.skipped_pages == (1, 3) and "page 2, 4" in m.user_message()
    s = pc.assess_pages([blank, blank, "  "])
    assert s.kind == "scanned" and not s.accepted and "scanned" in s.user_message() and "Paste" in s.user_message()
    e = pc.assess_pages([])
    assert e.kind == "empty" and not e.accepted


def test_real_pdf_bytes_text_vs_scan(tmp_path):
    text_pdf = make_pdf([PARA * 3, PARA * 3])
    a = pc.check_pdf(text_pdf)
    assert a.kind == "text" and a.n_pages == 2 and a.total_chars > 400
    scan_pdf = make_pdf([None, None, None])
    b = pc.check_pdf(scan_pdf)
    assert b.kind == "scanned" and b.n_pages == 3
    path = tmp_path / "paper.pdf"
    path.write_bytes(text_pdf)
    assert pc.check_pdf(str(path)).kind == "text"


def test_not_a_pdf_gives_friendly_error():
    with pytest.raises(pc.PdfRejected, match="could not open"):
        pc.check_pdf(b"this is not a pdf at all")


def test_running_headers_footers_and_page_numbers_are_removed():
    words = ["alpha", "beta", "gamma", "delta", "epsilon"]
    pages = [f"Procedia Computer Science 151 (2019) {1000 + i}-1012\nS. Author et al.\nThe {w} result holds [{i}].\n"
             f"Then {w} again in 3 trials.\n{i}" for i, w in enumerate(words, 1)]
    cleaned = pc.clean_page_texts(pages)
    assert all("Procedia" not in p and "Author et al" not in p for p in cleaned)
    assert cleaned[1] == "The beta result holds [2].\nThen beta again in 3 trials."   # the page number went too
    two = pc.clean_page_texts(["Journal X\nBody [1].", "Journal X\nMore [2]."])      # too few pages to tell
    assert two[0].startswith("Journal X")


def test_words_split_across_lines_are_joined_but_compounds_keep_their_hyphen():
    out = pc.clean_page_texts(["The evalu-\nation of self-\nsupervised models [1]. New-\nYork stays."])[0]
    assert "evaluation of self-supervised models [1]." in out and "New-\nYork" in out


def test_left_and_right_page_headers_and_the_papers_own_doi_are_removed():
    doi = "https://doi.org/10.1038/s42003-023-05456-z"
    pages = []
    for i, w in enumerate(["alpha", "beta", "gamma", "delta", "epsilon", "zeta"], 1):
        head = f"ARTICLE COMMUNICATIONS BIOLOGY | {doi}" if i % 2 else f"COMMUNICATIONS BIOLOGY | {doi} ARTICLE"
        pages.append(f"The {w} cohort was studied3.\nIt agreed with earlier work on {w}.\n{head}\n"
                     f"{i} COMMUNICATIONS BIOLOGY| (2023) 6:1089 | {doi} | www.nature.com/commsbio")
    pages[0] = "Abstract text ends here. " + doi + " OPEN\n" + pages[0]
    cleaned = pc.clean_page_texts(pages)
    assert not any("COMMUNICATIONS BIOLOGY" in p or "s42003" in p for p in cleaned)
    assert cleaned[1].startswith("The beta cohort was studied3.")


# A participant's paper (Session 11): figure labels and section headings ran into the next cited sentence.
P06_PAGE = ("Feature importance is shown in Fig. 3.\n"
            "XGBoost model\n"
            "Feature importance score\n"
            "B. Machine Learning models\n"
            "1) Random Forest: Random Forest (RF) is an ensemble of\n"
            "decision trees trained on bootstrap samples [12].\n"
            "II. RELATED WORK\n"
            "Honeypots and honeynets have been used to study IoT attacks [4].")


def test_headings_and_figure_labels_stay_out_of_cited_sentences():
    from src.claims import parse_draft
    text = "\n".join(pc.clean_page_texts([P06_PAGE]))
    claims = parse_draft(text + "\nReferences\n[4] A. Author. Honeypots. 2019.\n[12] B. Author. Forests. 2001.").claims
    assert [c.claim for c in claims] == [
        "Random Forest: Random Forest (RF) is an ensemble of decision trees trained on bootstrap samples.",
        "Honeypots and honeynets have been used to study IoT attacks."]


def test_ordinary_lines_are_left_alone():
    page = ("Federated learning keeps the data on each device and shares only\n"
            "Model updates with the server [3]. It was first proposed at Google in\n"
            "Mountain View")
    out = pc.close_headings(page)[0]
    assert out == page                                   # long lines, and a short line after an unfinished sentence


def test_nothing_is_changed_after_the_reference_heading():
    out, in_refs = pc.close_headings("Body text ends here.\nReferences\n[1] A. Author\nDeep Learning\nMIT Press")
    assert in_refs and out.endswith("[1] A. Author\nDeep Learning\nMIT Press")
    assert pc.close_headings("Smith J\nTitle Words", in_references=True)[0] == "Smith J\nTitle Words"


def test_ligatures_and_superscript_digits_become_plain_text():
    out = pc.clean_page_texts(["We deﬁne the ﬂow of data, as shown before¹²."])[0]
    assert out == "We define the flow of data, as shown before12."
