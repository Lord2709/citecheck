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


NO_ABSTRACT = paper("doi:10.1000/noabs", "Paywalled paper", "", doi="10.1000/noabs")


def test_no_abstract_falls_back_to_open_access_full_text():
    fetcher = FakeFetcher({"10.1000/noabs": NO_ABSTRACT})
    draft = ("Exercise improves sleep quality in older adults [1].\n\nReferences\n"
             "[1] Doe. Paywalled paper. 2019. doi:10.1000/noabs\n")
    ft = FakeFullText({"doi:10.1000/noabs": ["Exercise improves sleep quality in older adults in our trial."]})
    rep = agent(fetcher=fetcher, fulltext=ft).check_draft(draft)
    c = rep.citations[0]
    assert c.status == "checked" and c.read_full_text and c.verdict.label == SUPPORT
    assert c.paper.title == "Paywalled paper" and c.paper.doi == "10.1000/noabs"      # title taken from the lookup message
    none = agent(fetcher=fetcher, fulltext=FakeFullText({})).check_draft(draft).citations[0]
    assert none.status == "no_abstract" and "No open-access full text" in none.status_detail
    off = agent(fetcher=fetcher, escalate=False).check_draft(draft).citations[0]
    assert off.status == "no_abstract" and off.steps[-1].detail.startswith("no abstract available")


def test_recheck_with_pasted_abstract():
    fetcher = FakeFetcher({"10.1000/noabs": NO_ABSTRACT})
    draft = ("Exercise improves sleep quality in older adults [1].\n\nReferences\n"
             "[1] Doe. Paywalled paper. 2019. doi:10.1000/noabs\n")
    a = agent(fetcher=fetcher, fulltext=FakeFullText({}))
    c = a.check_draft(draft).to_dict()["citations"][0]
    new = a.recheck_with_abstract(c, "Paywalled paper", "We found that exercise improves sleep quality in older adults.")
    assert new["status"] == "checked" and new["abstract_pasted"] and new["verdict"]["label"] == SUPPORT
    assert new["steps"][-2]["action"] == "abstract pasted" or any(s["action"] == "abstract pasted" for s in new["steps"])
    assert "abstract pasted by the researcher" in to_markdown({"kind": "draft_check", "citations": [new]})


def test_stub_paper():
    from src.agent import stub_paper

    s = stub_paper("10.1038/nature14539", "Found “Deep learning” but no abstract is available")
    assert s.title == "Deep learning" and s.doi == "10.1038/nature14539" and s.paper_id == "doi:10.1038/nature14539"
    a = stub_paper("arXiv:1706.03762")
    assert a.paper_id == "arxiv:1706.03762" and a.url.endswith("1706.03762")
