import re
from dataclasses import dataclass

from .question_coverage import RequestedComponent


# Terms whose loss can materially change what the buyer asked. This is deliberately
# deterministic and conservative; it validates decomposition rather than answering.
QUALIFIER_PATTERNS = [
    r"\bunlimited\b", r"\bguarantee(?:d)?\b", r"\bnever\b", r"\bzero\b",
    r"\bminimum\b", r"\bmaximum\b", r"\bcapped\b", r"\balways\b",
    r"\babsolutely\b", r"\bdefinitely\b", r"\ball\b", r"\bfree\b",
    r"\bmoney back\b", r"\b30\s*day\b", r"\bmonth[- ]to[- ]month\b",
    r"£\s?\d+(?:[,.]\d+)?", r"\$\s?\d+(?:[,.]\d+)?",
    r"\b\d+(?:\.\d+)?\s*(?:days?|hours?|weeks?|months?|years?|%)\b",
]


@dataclass(frozen=True)
class HybridDecompositionResult:
    components: list[RequestedComponent]
    route: str
    valid: bool
    missing_terms: list[str]


def material_terms(text: str) -> list[str]:
    out = []
    for pattern in QUALIFIER_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.I):
            value = match.group(0).strip()
            if value.lower() not in {x.lower() for x in out}:
                out.append(value)
    return out


def missing_material_terms(original: str, components: list[RequestedComponent]) -> list[str]:
    rendered = " ".join(c.question for c in components if c.material).lower()
    return [term for term in material_terms(original) if term.lower() not in rendered]


def is_probably_compound(question: str) -> bool:
    """High-precision compound detector.

    We prefer false negatives here: an atomic question should not be rewritten just
    because it contains ordinary conjunctions. Explicit multi-part punctuation or
    two interrogative clauses are stronger signals.
    """
    q = question.strip()
    if ";" in q:
        return True
    # Two question marks almost certainly indicate multiple requests.
    if q.count("?") > 1:
        return True
    # Explicit second interrogative after a conjunction.
    if re.search(r"\b(?:and|also)\s+(?:what|how|when|where|why|who|does|do|is|are|can|will|would)\b", q, re.I):
        return True
    return False


class HybridRequestedInformationDecomposer:
    def __init__(self, zero_shot_decomposer):
        self.zero_shot = zero_shot_decomposer

    def decompose_with_metadata(self, question: str) -> HybridDecompositionResult:
        if not is_probably_compound(question):
            return HybridDecompositionResult(
                [RequestedComponent("c1", question.strip(), True)],
                "preserve_atomic",
                True,
                [],
            )

        candidate = self.zero_shot.decompose(question)
        missing = missing_material_terms(question, candidate)
        if missing:
            # Fail closed on transformation: preserve the original request rather
            # than accepting a decomposition that lost material buyer language.
            return HybridDecompositionResult(
                [RequestedComponent("c1", question.strip(), True)],
                "fallback_preserve",
                False,
                missing,
            )
        return HybridDecompositionResult(candidate, "zero_shot_compound", True, [])

    def decompose(self, question: str):
        return self.decompose_with_metadata(question).components
