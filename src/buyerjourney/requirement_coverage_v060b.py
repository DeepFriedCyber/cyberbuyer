from dataclasses import dataclass, field

from .evidence_requirements_v059g import aggregate_requirement_states
from .specialist_verifier_v059 import EvidenceSpan, SpecialistVerifier


@dataclass(frozen=True)
class CandidateCheck:
    source_id: str
    verdict: str
    nli_verdict: str
    nli_confidence: float
    qualifier_check: bool
    numeric_check: bool


@dataclass(frozen=True)
class RequirementCheck:
    requirement_id: str
    hypothesis: str
    state: str
    candidates: list[CandidateCheck] = field(default_factory=list)


@dataclass(frozen=True)
class CoverageResult:
    state: str
    requirements: list[RequirementCheck]


def target_hypothesis(target) -> str:
    """Use the strongest preserved proposition available for verification."""
    if target.constraints:
        return " ; ".join(target.constraints)
    terms = [str(x).replace("_", " ") for x in target.canonical_terms]
    if target.kind == "relation" and len(terms) == 2:
        return f"There is evidence describing the difference between {terms[0]} and {terms[1]}."
    return target.description or " ; ".join(terms)


def evidence_span(evidence) -> EvidenceSpan:
    text = str(evidence.text)
    return EvidenceSpan(str(evidence.source_id), text, 0, len(text), text)


class RequirementCoverageVerifier:
    """Verify retrieved candidates per obligation; aggregate only after verification."""
    def __init__(self, nli):
        self.verifier = SpecialistVerifier(nli)

    def verify(self, retrieval_result) -> CoverageResult:
        checks = []
        for target, retrieved in zip(retrieval_result.targets, retrieval_result.retrieved):
            hypothesis = target_hypothesis(target)
            candidate_checks = []
            state = "UNSUPPORTED"
            for evidence in retrieved.evidence:
                result = self.verifier.verify(evidence_span(evidence), hypothesis)
                candidate_checks.append(CandidateCheck(
                    str(evidence.source_id), result.verdict, result.nli_verdict,
                    result.nli_confidence, result.qualifier_check, result.numeric_check,
                ))
                if result.verdict == "SUPPORTED":
                    state = "SUPPORTED"
            checks.append(RequirementCheck(target.requirement_id, hypothesis, state, candidate_checks))
        return CoverageResult(aggregate_requirement_states([x.state for x in checks]), checks)
