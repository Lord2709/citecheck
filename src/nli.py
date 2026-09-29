"""Verifiers: judge whether a premise (evidence) supports / contradicts / is neutral to a claim.
Owner: Data & Evaluation (Sahil).

    MajorityVerifier   always "not enough evidence"       -> the floor every real model must beat
    LexicalVerifier    word-overlap + negation/direction   -> the "simpler approach" baseline (no ML)
    NLIVerifier        pretrained NLI transformer          -> the zero-shot baseline (and, pointed at a
                                                              fine-tuned checkpoint, our improved model)

All expose  .name  and  .predict_pairs([(premise, hypothesis), ...]) -> list[Probs].
"""
from __future__ import annotations

import re
import time
from typing import Optional, Sequence

from .schema import Probs
from .text_utils import _stem, split_sentences, tokenize

DEFAULT_NLI_MODEL = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"


class MajorityVerifier:
    name = "majority"

    def predict_pairs(self, pairs: Sequence) -> list:
        return [Probs(0.0, 1.0, 0.0) for _ in pairs]


# --------------------------------------------------------------------------- #
# Lexical baseline
# --------------------------------------------------------------------------- #
_NEG = frozenset(
    """no not without fail failed fails failure lack lacks lacked absence absent unchanged neither nor
    never cannot unable nonsignificant insignificant didn doesn isn wasn weren don won hasn haven
    hadn aren couldn wouldn""".split()
)
_DOWN = frozenset(
    """decrease decreased decreases decreasing lower lowered reduce reduced reduces reduction decline
    declined impair impaired inhibit inhibits inhibited suppress suppresses suppressed attenuate
    attenuated less fewer downregulate downregulated loss block blocked abolish abolished diminish
    diminished""".split()
)
_WORD = re.compile(r"[a-z0-9]+")
# match on stems too, so "lowers" / "lowered" / "lower" all hit the same cue
_NEG_STEMS = frozenset(_stem(w) for w in _NEG)
_DOWN_STEMS = frozenset(_stem(w) for w in _DOWN)


def _polarity(text: str) -> int:
    words = _WORD.findall(text.lower())
    n_neg = sum(w in _NEG or _stem(w) in _NEG_STEMS for w in words)
    n_down = sum(w in _DOWN or _stem(w) in _DOWN_STEMS for w in words)
    return (n_neg + n_down) % 2


class LexicalVerifier:
    """Coverage of the claim's content words by the premise, flipped by a negation/direction parity cue.

    Deliberately simple: it exists so that "did the neural model actually beat word overlap?" is a
    measured answer, and so the app works offline with no model download (demo/testing only).
    Coverage is measured on the whole premise; the polarity cue is read from the single sentence that
    overlaps the claim most, so a stray "loss" or "no" in an unrelated sentence cannot flip the verdict.
    """

    name = "lexical"

    def __init__(self, min_coverage: float = 0.4):
        self.min_coverage = min_coverage

    def predict_pairs(self, pairs: Sequence) -> list:
        out = []
        for premise, claim in pairs:
            q = set(tokenize(claim))
            cov = len(q & set(tokenize(premise))) / len(q) if q else 0.0
            if cov < self.min_coverage:
                out.append(Probs(0.10, 0.80, 0.10))
                continue
            strength = min(1.0, (cov - self.min_coverage) / (1 - self.min_coverage))
            conf = 0.5 + 0.4 * strength
            rest = (1 - conf) / 2
            sents = split_sentences(premise) or [premise]
            best = max(sents, key=lambda s: len(q & set(tokenize(s))))  # first wins ties
            flip = _polarity(best) != _polarity(claim)
            out.append(Probs(rest, rest, conf) if flip else Probs(conf, rest, rest))
        return out


# --------------------------------------------------------------------------- #
# Transformer NLI
# --------------------------------------------------------------------------- #
def resolve_label_indices(id2label: dict) -> dict:
    """Map a HF config's id2label onto our three classes by NAME, never by position.

    Different NLI checkpoints order their labels differently (e.g. contradiction/entailment/neutral
    vs entailment/neutral/contradiction), so hard-coding an order silently swaps SUPPORT and CONTRADICT.
    """
    found = {}
    for idx, name in id2label.items():
        n = str(name).lower()
        if n.startswith("entail"):
            found["support"] = int(idx)
        elif n.startswith("contradict"):
            found["contradict"] = int(idx)
        elif n.startswith("neutral") or n in ("not_entailment", "nei"):
            found["neutral"] = int(idx)
    missing = {"support", "neutral", "contradict"} - set(found)
    if missing:
        raise ValueError(f"cannot map NLI labels {dict(id2label)}; missing {sorted(missing)}")
    return found


class NLIVerifier:
    def __init__(
        self,
        model_name: str = DEFAULT_NLI_MODEL,
        device: Optional[str] = None,
        batch_size: int = 16,
        max_length: int = 384,
    ):
        self.model_name = model_name
        self.name = f"nli:{model_name}"
        self.batch_size, self.max_length = batch_size, max_length
        self._device_pref = device
        self._model = self._tok = self._idx = None
        self.total_pairs = 0
        self.total_seconds = 0.0

    # -- lazy load so importing this module never needs torch ---------------
    def _load(self):
        if self._model is not None:
            return
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self._torch = torch
        dev = self._device_pref
        if dev is None:
            if torch.cuda.is_available():
                dev = "cuda"
            elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                dev = "mps"
            else:
                dev = "cpu"
        self.device = dev
        self._tok = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(self.model_name).to(dev).eval()
        self._idx = resolve_label_indices(self._model.config.id2label)

    @property
    def n_params(self) -> int:
        self._load()
        return sum(p.numel() for p in self._model.parameters())

    def predict_pairs(self, pairs: Sequence) -> list:
        if not pairs:
            return []
        self._load()
        torch = self._torch
        t0 = time.perf_counter()
        order = sorted(range(len(pairs)), key=lambda i: len(pairs[i][0]) + len(pairs[i][1]))
        results = [None] * len(pairs)
        with torch.no_grad():
            for s in range(0, len(order), self.batch_size):
                batch = order[s : s + self.batch_size]
                enc = self._tok(
                    [pairs[i][0] for i in batch],
                    [pairs[i][1] for i in batch],
                    truncation="only_first",
                    max_length=self.max_length,
                    padding=True,
                    return_tensors="pt",
                ).to(self.device)
                probs = torch.softmax(self._model(**enc).logits.float(), dim=-1).cpu().numpy()
                for row, i in zip(probs, batch):
                    results[i] = Probs(
                        support=float(row[self._idx["support"]]),
                        neutral=float(row[self._idx["neutral"]]),
                        contradict=float(row[self._idx["contradict"]]),
                    )
        self.total_pairs += len(pairs)
        self.total_seconds += time.perf_counter() - t0
        return results


def build_verifier(spec: str = "nli", **kw):
    """spec: majority | lexical | nli | nli:<hf-id-or-local-path>"""
    spec = (spec or "nli").strip()
    low = spec.lower()
    if low == "majority":
        return MajorityVerifier()
    if low == "lexical":
        return LexicalVerifier()
    if low == "nli":
        return NLIVerifier(**kw)
    if low.startswith("nli:"):
        return NLIVerifier(model_name=spec[4:], **kw)
    raise ValueError(f"unknown verifier '{spec}' (majority | lexical | nli | nli:<model>)")
