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
