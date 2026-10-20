"""The agent loop end to end with fakes (src/agent.py): no network, deterministic verifier."""
import json

from src.agent import CiteCheckAgent, chunk, default_tau_strict
from src.fulltext import FullText
from src.report import summarize, to_markdown
from src.resolve import ReferenceResolver
from src.schema import CONTRADICT, NEI, SUPPORT

from agent_fakes import FakeFetcher, make_pipeline, paper

ZORVEX = paper("doi:10.1000/zorvex", "Zorvex and bone",
               "We studied zorvex in mice. Zorvex increases bone density in adult mice. The effect was dose dependent.",
               doi="10.1000/zorvex")
STATIN = paper("doi:10.1000/statin", "Statins", "Statins lower cholesterol in most adults.", doi="10.1000/statin")
CONTRA = paper("doi:10.1000/contra", "Zorvex null result",
               "Zorvex increases bone density in adult mice was tested. We found zorvex had no effect.", doi="10.1000/contra")
VAGUE = paper("doi:10.1000/vague", "A vague paper", "We describe a cohort of patients. Methods are reported in full.",
              doi="10.1000/vague")
GOOD_ALT = paper("doi:10.1000/alt", "Sleep and exercise", "Exercise improves sleep quality in older adults.", doi="10.1000/alt")

DRAFT = """Zorvex increases bone density in adult mice [1]. Statins lower cholesterol in most adults [2].
Exercise improves sleep quality in older adults [3]. Coffee prevents all known cancers in humans [4].

References
[1] Doe. Zorvex and bone. 2021. doi:10.1000/zorvex
[2] Roe. Statins. 2019. doi:10.1000/statin
[3] Poe. A vague paper. 2018. doi:10.1000/vague
"""


class FakeFullText:
    def __init__(self, texts):
        self.texts, self.last_detail = texts, ""

    def find(self, p):
        s = self.texts.get(p.paper_id)
        self.last_detail = "found" if s else "no open-access copy"
        return FullText("fake", "https://example.org/ft", s) if s else None


def agent(**kw):
    fetcher = FakeFetcher({"10.1000/zorvex": ZORVEX, "10.1000/statin": STATIN, "10.1000/vague": VAGUE})
    defaults = dict(fetcher=fetcher, resolver=ReferenceResolver(None),
                    fulltext=FakeFullText({"doi:10.1000/vague": ["Intro sentence about cohorts and methods here.",
                                                                 "Exercise improves sleep quality in older adults strongly."]}),
                    search=lambda text, n: [CONTRA, STATIN, GOOD_ALT, ZORVEX])
    defaults.update(kw)
    return CiteCheckAgent(make_pipeline(), **defaults)


def test_plan():
    a = agent()
    assert a.plan(DRAFT).kind == "verify_draft"
    assert a.plan("verifying scientific claims against cited abstracts").kind == "discover"


def test_check_draft_end_to_end():
    rep = agent().check_draft(DRAFT)
    by = {c.marker: c for c in rep.citations}
    assert by["[1]"].verdict.label == SUPPORT and not by["[1]"].read_full_text and not by["[1]"].suggestions
    assert by["[2]"].verdict.label == SUPPORT
    v3 = by["[3]"]                                   # abstract says nothing -> full text read -> supported
    assert v3.read_full_text and v3.full_text_source == "fake" and v3.verdict.label == SUPPORT
    assert [s.action for s in v3.steps][:4] == ["resolve reference", "fetch paper", "verify abstract", "find open-access full text"]
    assert by["[4]"].status == "unresolved" and "no entry" in by["[4]"].status_detail
    d = rep.to_dict()
    json.dumps(d)                                    # serialisable for the app and the download
    assert summarize(d)["supported"] == 3 and summarize(d)["could_not_check"] == 1
    assert "## 3. Supported" in to_markdown(d)


def test_contradiction_triggers_replacement_with_strict_threshold():
    a = agent()
    v, read_ft, _, sugg, steps = a.check_claim("Zorvex increases bone density in adult mice.", CONTRA)
    assert v.label == CONTRADICT and not read_ft                    # confident contradiction: no full text needed
    assert [s.paper.paper_id for s in sugg] == ["doi:10.1000/zorvex"] and sugg[0].confidence >= a.tau_strict
    assert any(s.action == "search for a replacement" for s in steps)


def test_no_suggestion_for_the_failed_paper_or_future_papers():
    a = agent(search=lambda t, n: [STATIN])
    _, _, _, sugg, _ = a.check_claim("Statins lower cholesterol in most adults.", VAGUE)
    assert sugg and sugg[0].paper.paper_id == "doi:10.1000/statin"
    _, _, _, sugg, _ = a.check_claim("Statins lower cholesterol in most adults.", VAGUE, draft_year=2018)
    assert sugg == []                                  # the candidate (2020) is newer than the draft
    a2 = agent(search=lambda t, n: [VAGUE])
    _, _, _, sugg, _ = a2.check_claim("Exercise improves sleep quality in older adults.", VAGUE)
    assert sugg == []


def test_switches_and_failures_are_reported_not_raised():
    a = agent(escalate=False, suggest=False)
    v, read_ft, _, sugg, steps = a.check_claim("Exercise improves sleep quality in older adults.", VAGUE)
    assert v.label == NEI and not read_ft and not sugg and "off" in steps[1].detail
    boom = agent(search=lambda t, n: (_ for _ in ()).throw(RuntimeError("down")))
    _, _, _, sugg, steps = boom.check_claim("Coffee prevents cancer in humans.", VAGUE)
    assert sugg == [] and "search failed" in steps[-1].detail
    rep = agent(fetcher=FakeFetcher({})).check_draft(DRAFT)
    assert {c.status for c in rep.citations} == {"not_found", "unresolved"}


def test_helpers():
    assert chunk(list(range(12)), 5) == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11]]
    assert default_tau_strict(0.6) == 0.85 and default_tau_strict(0.9) == 0.95
