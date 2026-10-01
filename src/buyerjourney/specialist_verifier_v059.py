from dataclasses import dataclass
from enum import Enum
import re


@dataclass(frozen=True)
class EvidenceSpan:
    source_id: str
    quote: str
    start_char: int
    end_char: int
    source_text: str

    def valid(self) -> bool:
        return (
            self.start_char >= 0
            and self.end_char >= self.start_char
            and self.end_char <= len(self.source_text)
            and self.source_text[self.start_char:self.end_char] == self.quote
            and bool(self.quote)
        )


class NLIVerdict(str, Enum):
    ENTAILMENT = "ENTAILMENT"
    NEUTRAL = "NEUTRAL"
    CONTRADICTION = "CONTRADICTION"
    ERROR = "ERROR"


@dataclass(frozen=True)
class NLIResult:
    verdict: NLIVerdict
    confidence: float = 0.0


@dataclass(frozen=True)
class VerificationResult:
    verdict: str
    provenance_check: bool
    qualifier_check: bool
    numeric_check: bool
    nli_verdict: str
    nli_confidence: float


QUALIFIER_GROUPS = {
    "unlimited": ("unlimited",),
    "guarantee": ("guarantee", "guaranteed", "guarantees", "promise", "promised"),
    "never": ("never",),
    "zero": ("zero", "no downtime"),
    "minimum": ("minimum", "at least"),
    "maximum": ("maximum", "at most"),
    "capped": ("capped", "cap"),
    "always": ("always",),
    "absolute": ("absolutely", "definitely"),
    "free": ("free",),
    "money_back": ("money back", "money-back"),
    "no_changes": ("no changes", "without changes", "requires no changes"),
}


def _norm(text: str) -> str:
    return " ".join(str(text).lower().replace("£", " £").split())


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) is not None


def material_qualifiers(text: str) -> set[str]:
    t = _norm(text)
    found = set()
    for name, forms in QUALIFIER_GROUPS.items():
        if any(_contains_phrase(t, form) for form in forms):
            found.add(name)
    if re.search(r"\b30[ -]?day\b", t):
        found.add("30_day")
    return found


def qualifier_compatible(premise: str, hypothesis: str) -> bool:
    """A material qualifier introduced by the hypothesis must be explicit in evidence."""
    return material_qualifiers(hypothesis).issubset(material_qualifiers(premise))


_NUMBER_RE = re.compile(r"(?<!\w)(?:£|\$|€)?\s*\d+(?:[,.]\d+)*(?:\s*%|\s*(?:day|days|hour|hours|month|months|year|years))?", re.I)


def numeric_tokens(text: str) -> set[str]:
    return {re.sub(r"\s+", "", m.group(0).lower()) for m in _NUMBER_RE.finditer(text)}


def numeric_compatible(premise: str, hypothesis: str) -> bool:
    requested = numeric_tokens(hypothesis)
    return not requested or requested.issubset(numeric_tokens(premise))


def range_scope_compatible(premise: str, hypothesis: str) -> bool:
    """Protect entry/range pricing from being promoted to universal exact pricing."""
    p, h = _norm(premise), _norm(hypothesis)
    if "from £" in p or "from $" in p or "from €" in p:
        universal = any(x in h for x in ("all ", "everyone", "every customer", "exactly"))
        if universal:
            return False
    return True


class TransformersNLI:
    """Small configurable sequence-classification NLI adapter. Errors fail closed."""

    def __init__(self, model_name="cross-encoder/nli-deberta-v3-small", tokenizer=None, model=None):
        self.model_name = model_name
        if tokenizer is None or model is None:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.tokenizer = tokenizer
        self.model = model

    def check(self, premise: str, hypothesis: str) -> NLIResult:
        try:
            import torch
            batch = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True)
            device = next(self.model.parameters()).device
            batch = {k: v.to(device) for k, v in batch.items()}
            with torch.no_grad():
                logits = self.model(**batch).logits[0]
                probs = torch.softmax(logits, dim=-1)
            idx = int(probs.argmax().item())
            confidence = float(probs[idx].item())
            label = str(self.model.config.id2label.get(idx, "")).upper()
            if "ENTAIL" in label:
                verdict = NLIVerdict.ENTAILMENT
            elif "CONTRAD" in label:
                verdict = NLIVerdict.CONTRADICTION
            elif "NEUTRAL" in label:
                verdict = NLIVerdict.NEUTRAL
            else:
                verdict = NLIVerdict.ERROR
            return NLIResult(verdict, confidence)
        except Exception:
            return NLIResult(NLIVerdict.ERROR, 0.0)


class SpecialistVerifier:
    def __init__(self, nli):
        self.nli = nli

    def verify(self, span: EvidenceSpan, hypothesis: str) -> VerificationResult:
        provenance = span.valid()
        qualifier = qualifier_compatible(span.quote, hypothesis) and range_scope_compatible(span.quote, hypothesis)
        numeric = numeric_compatible(span.quote, hypothesis)
        nli = self.nli.check(span.quote, hypothesis) if provenance else NLIResult(NLIVerdict.ERROR, 0.0)
        supported = provenance and qualifier and numeric and nli.verdict == NLIVerdict.ENTAILMENT
        return VerificationResult(
            "SUPPORTED" if supported else "UNSUPPORTED",
            provenance,
            qualifier,
            numeric,
            nli.verdict.value,
            nli.confidence,
        )
