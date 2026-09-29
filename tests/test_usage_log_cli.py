import io
import json

import pytest

from src.main import main
from src.usage_log import UsageLogger


def lines(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]


def test_log_drops_text_by_default(tmp_path):
    lg = UsageLogger(tmp_path / "u.jsonl", participant="P01")
    lg.log("verify", claim="Secret unpublished idea", verdict="SUPPORT", confidence=0.9)
    (rec,) = lines(tmp_path / "u.jsonl")
    assert "claim" not in rec and rec["claim_len"] == 23 and rec["participant"] == "P01" and rec["verdict"] == "SUPPORT"
    assert rec["session_id"] == lg.session_id and rec["ts"].endswith("+00:00")


def test_log_text_is_redacted_when_consented(tmp_path):
    lg = UsageLogger(tmp_path / "u.jsonl", log_text=True)
    lg.log("comment", comment="email me at jo@umd.edu or +1 301 555 0100")
    (rec,) = lines(tmp_path / "u.jsonl")
    assert rec["comment"] == "email me at [email] or [phone]" and rec["comment_len"] > 0


def test_disabled_logger_writes_nothing(tmp_path):
    lg = UsageLogger(tmp_path / "sub" / "u.jsonl", enabled=False)
    assert lg.log("x")["event"] == "x" and not (tmp_path / "sub").exists()


def test_cli_paths(monkeypatch, fixture_dir, capsys):
    monkeypatch.setenv("CITECHECK_VERIFIER", "lexical")
    monkeypatch.setenv("CITECHECK_DATA_DIR", str(fixture_dir))
    out = io.StringIO()
    v = main(["verify", "--claim", "Vantrol lowers LDL cholesterol.", "--abstract",
              "We tested vantrol. After twelve weeks vantrol did not lower LDL cholesterol compared with placebo."], out=out)
    assert v.label == "CONTRADICT" and "CONTRADICTS" in out.getvalue() and "DEMO BACKEND" in out.getvalue()
    js = io.StringIO()
    main(["verify", "--claim", "Meditation reduces cortisol in adults.", "--json"], out=js)
    assert json.loads(js.getvalue())["display_label"] in ("SUPPORTS", "CONTRADICTS", "NOT ENOUGH EVIDENCE")
    info = io.StringIO()
    main(["info"], out=info)
    assert json.loads(info.getvalue())["validated"] is False
    r = main(["relevance", "--direction", "bone density in mice", "--abstract", "Zorvex raised femoral bone density in mice."], out=io.StringIO())
    assert r.band == "likely relevant" and "bone" in r.matched_terms
    with pytest.raises(SystemExit) as e:
        main(["relevance", "--direction", "x"], out=io.StringIO())              # no paper given -> friendly error, exit 2
    assert e.value.code == 2
