from dataclasses import dataclass
from typing import Iterable

from .specialist_verifier_v059 import EvidenceSpan, SpecialistVerifier


@dataclass(frozen=True)
class RequestedComponent:
    component_id: str
    question: str


@dataclass(frozen=True)
class EvidenceProposition:
    component_id: str
    text: str
    span: EvidenceSpan


@dataclass(frozen=True)
class ComponentCoverage:
    component_id: str
    question: str
    state: str
    proposition: str | None = None
    source_id: str | None = None
    nli_verdict: str | None = None
    nli_confidence: float = 0.0
    qualifier_check: bool = False
    numeric_check: bool = False
    provenance_check: bool = False


def aggregate_component_coverage(rows: Iterable[ComponentCoverage]) -> str:
    rows = list(rows)
    if not rows:
        return "UNSUPPORTED"
    supported = sum(r.state == "SUPPORTED" for r in rows)
    if supported == len(rows):
        return "SUPPORTED"
    if supported:
        return "PARTIAL"
    return "UNSUPPORTED"


class EvidencePropositionCoverage:
    """Verify evidence-derived propositions against requested information.

    Proposition text may be generated, but it never becomes provenance: every
    proposition must still be verified against its exact source span before it can
    satisfy a requested component.
    """

    def __init__(self, verifier: SpecialistVerifier):
        self.verifier = verifier

    def assess_component(self, component: RequestedComponent, propositions: Iterable[EvidenceProposition]) -> ComponentCoverage:
        best = None
        for proposition in propositions:
            if proposition.component_id != component.component_id:
                continue
            # First prove that the evidence actually entails the evidence-derived
            # proposition. This prevents a generator from smuggling in an answer.
            grounded = self.verifier.verify(proposition.span, proposition.text)
            if grounded.verdict != "SUPPORTED":
                continue
            # Then test whether the grounded proposition semantically satisfies the
            # requested information. Deterministic guards remain vetoes here too.
            satisfies = self.verifier.verify(
                EvidenceSpan(
                    proposition.span.source_id,
                    proposition.text,
                    0,
                    len(proposition.text),
                    proposition.text,
                ),
                component.question,
            )
            row = ComponentCoverage(
                component.component_id,
                component.question,
                satisfies.verdict,
                proposition.text,
                proposition.span.source_id,
                satisfies.nli_verdict,
                satisfies.nli_confidence,
                satisfies.qualifier_check,
                satisfies.numeric_check,
                grounded.provenance_check,
            )
            if row.state == "SUPPORTED":
                return row
            if best is None:
                best = row
        return best or ComponentCoverage(component.component_id, component.question, "UNSUPPORTED")

    def assess(self, components: Iterable[RequestedComponent], propositions: Iterable[EvidenceProposition]):
        components = list(components)
        propositions = list(propositions)
        rows = [self.assess_component(c, propositions) for c in components]
        return {"state": aggregate_component_coverage(rows), "components": rows}
