"""Shared fakes for agent tests: a deterministic verifier, a fetcher that serves invented papers, no network."""
from src.ingest import IngestError
from src.pipeline import CiteCheckPipeline
from src.schema import Paper, Probs
from src.text_utils import tokenize


class KeywordVerifier:
    """support 0.95 when the premise covers >= 80% of the claim's content words; contradict 0.9 if it also says
    'no effect'; otherwise neutral 0.9.  Deterministic, so agent decisions are predictable in tests."""
    name = "keyword-fake"

    def predict_pairs(self, pairs):
        out = []
        for premise, claim in pairs:
            c, p = set(tokenize(claim)), set(tokenize(premise))
            cov = len(c & p) / max(len(c), 1)
            if cov >= 0.8 and "no effect" in premise.lower():
                out.append(Probs(0.03, 0.07, 0.9))
            elif cov >= 0.8:
                out.append(Probs(0.95, 0.04, 0.01))
            else:
                out.append(Probs(0.05, 0.9, 0.05))
        return out


def make_pipeline(tau=0.6):
    return CiteCheckPipeline(KeywordVerifier(), None, None, k=3, sentences_per_paper=3, tau=tau,
                             meta={"verifier": "keyword-fake", "tau": tau})


class FakeFetcher:
    def __init__(self, papers, mailto=None):
        self.papers, self.mailto, self.calls = papers, mailto, []

    def fetch_paper(self, ident, use_cache=True):
        self.calls.append(ident)
        if ident not in self.papers:
            raise IngestError("No paper found for that identifier.")
        p = self.papers[ident]
        if not p.abstract:
            raise IngestError(f"Found “{p.title}” but no abstract is available from open sources. Paste the abstract instead.")
        return p


def paper(pid, title, abstract, year=2020, doi=None):
    return Paper(paper_id=pid, title=title, abstract=abstract, year=year, doi=doi, url=f"https://example.org/{pid}",
                 source="fake")
