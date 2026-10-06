"""Headless UI tests with Streamlit's AppTest (no browser)."""
import json
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parent.parent / "app" / "streamlit_app.py")


@pytest.fixture()
def app(monkeypatch, tmp_path, fixture_dir):
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(fixture_dir))
    monkeypatch.setenv("CITECHECK_LOG", str(tmp_path / "usage.jsonl"))
    monkeypatch.setenv("CITECHECK_DEMO_EXAMPLES", str(tmp_path / "no_demo.json"))   # ignore the repo's demo/ file
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception, at.exception
    return at, tmp_path / "usage.jsonl"


def events(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def test_starts_and_is_honest_about_the_backend(app):
    at, _ = app
    errors = " ".join(e.value for e in at.sidebar.error)
    assert "DEMO BACKEND" in errors and "NOT reliable" in errors
    assert len(at.sidebar.success) == 0                # never claims a "Validated configuration" it does not have


def test_example_check_and_feedback_logged_without_text(app):
    at, log = app
    at.button(key="btn_example").click().run()
    assert at.text_area(key="claim").value.startswith("Zorvex")
    at.button(key="btn_check").click().run()
    assert not at.exception
    banner = " ".join(e.value for e in list(at.success) + list(at.error) + list(at.warning))
    assert any(w in banner for w in ("SUPPORTS", "CONTRADICTS", "NOT ENOUGH EVIDENCE"))
    at.button(key="fb_yes").click().run()
    ev = events(log)
    kinds = [e["event"] for e in ev]
    assert kinds[0] == "session_start" and "verify" in kinds and "feedback" in kinds
    verify = next(e for e in ev if e["event"] == "verify")
    assert "claim" not in verify and verify["claim_len"] > 0 and verify["mode"] == "pasted"   # privacy default


def test_errors_are_friendly(app):
    at, log = app
    at.button(key="btn_check").click().run()                                        # empty claim
    assert not at.exception and any("Enter a claim" in e.value for e in at.warning)  # a hint, not a red error
    assert not any("Enter a claim" in e.value for e in at.error)                       # (the sidebar's DEMO banner is the only error)
    assert any(e["event"] == "error" for e in events(log))


def test_verdict_area_explains_itself_before_a_check(app):
    at, _ = app
    assert any("Your verdict will appear here" in i.value for i in at.info)


def test_missing_abstract_or_identifier_is_a_hint_not_a_crash(app):
    at, _ = app
    at.text_area(key="claim").set_value("Zorvex increases bone density.").run()
    at.radio(key="chk_src").set_value("Paste an abstract").run()
    at.button(key="btn_check").click().run()
    assert not at.exception and any("Paste the paper's abstract" in w.value for w in at.warning)
    at.radio(key="chk_src").set_value("The paper I'm citing (DOI / arXiv / link)").run()
    at.button(key="btn_check").click().run()
    assert not at.exception and any("Enter the DOI" in w.value for w in at.warning)
    assert any("Your verdict will appear here" in i.value for i in at.info)          # no verdict was produced


def test_verdict_card_speaks_plainly_and_start_over_clears(app):
    at, _ = app
    at.button(key="btn_example").click().run()
    at.button(key="btn_check").click().run()
    card = " ".join(e.value for e in list(at.success) + list(at.error) + list(at.warning))
    assert "Verdict:" in card and any(h in card for h in ("supports your claim", "contradicts your claim", "Not enough evidence"))
    assert at.button(key="btn_clear")
    at.button(key="btn_clear").click().run()
    assert not at.exception and at.text_area(key="claim").value == "" and at.text_area(key="chk_abstract").value == ""
    assert any("Your verdict will appear here" in i.value for i in at.info)


def test_researcher_panel_times_tasks(app):
    at, log = app
    at.sidebar.text_input(key="participant").set_value("P07").run()
    at.sidebar.button(key="task_start").click().run()
    at.sidebar.button(key="task_ok").click().run()
    end = next(e for e in events(log) if e["event"] == "task_end")
    assert end["participant"] == "P07" and end["task_id"] == "T1" and end["outcome"] == "completed" and end["elapsed_s"] is not None


def test_demo_examples_load_and_show_the_gold_label(monkeypatch, tmp_path, fixture_dir):
    demo = {"examples": [{"slot": "SUPPORT-1", "role": "main", "claim_id": 1, "gold": "SUPPORT",
                          "claim": "Zorvex supplementation increases bone density in mice.",
                          "title": "Zorvex supplementation and skeletal density in mice.",
                          "abstract": "We fed adult mice a diet supplemented with zorvex for twelve weeks. Zorvex supplementation "
                                      "significantly increased femoral bone density compared with controls.",
                          "verdict": "SUPPORT"}]}
    (tmp_path / "demo.json").write_text(json.dumps(demo), encoding="utf-8")
    monkeypatch.setenv("CITECHECK_DEMO_EXAMPLES", str(tmp_path / "demo.json"))
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(fixture_dir))
    monkeypatch.setenv("CITECHECK_LOG", str(tmp_path / "usage.jsonl"))
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    at.button(key="btn_demo").click().run()
    assert at.text_area(key="claim").value == demo["examples"][0]["claim"]
    assert at.text_area(key="chk_abstract").value.startswith("We fed adult mice")
    at.button(key="btn_check").click().run()
    assert not at.exception
    assert any("SciFact annotators' label" in i.value for i in at.info)
    assert any(e["event"] == "demo_example" and e["claim_id"] == 1 for e in events(tmp_path / "usage.jsonl"))


def test_no_demo_file_means_no_demo_panel(app):
    at, _ = app
    assert not [b for b in at.button if b.key == "btn_demo"]
