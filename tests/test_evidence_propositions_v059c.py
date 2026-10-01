from buyerjourney.evidence_propositions_v059c import (
    RequestedComponent, EvidenceProposition, EvidencePropositionCoverage,
    aggregate_component_coverage, ComponentCoverage,
)
from buyerjourney.specialist_verifier_v059 import EvidenceSpan, NLIResult, NLIVerdict, SpecialistVerifier


class ExactishNLI:
    def check(self, premise, hypothesis):
        p, h = premise.lower(), hypothesis.lower()
        # deterministic test double for the coverage architecture
        if premise == hypothesis:
            return NLIResult(NLIVerdict.ENTAILMENT, .99)
        pairs = [
            ("publishes mdr from £900 per month", "is £900 a published mdr price"),
            ("full incident response is described as included", "is incident response included"),
        ]
        if any(a in p and b in h for a, b in pairs):
            return NLIResult(NLIVerdict.ENTAILMENT, .95)
        return NLIResult(NLIVerdict.NEUTRAL, .9)


def span(source_id, text):
    return EvidenceSpan(source_id, text, 0, len(text), text)


def test_aggregate_partial():
    rows = [ComponentCoverage("c1", "a", "SUPPORTED"), ComponentCoverage("c2", "b", "UNSUPPORTED")]
    assert aggregate_component_coverage(rows) == "PARTIAL"


def test_aggregate_supported_and_unsupported():
    assert aggregate_component_coverage([ComponentCoverage("c1", "a", "SUPPORTED")]) == "SUPPORTED"
    assert aggregate_component_coverage([ComponentCoverage("c1", "a", "UNSUPPORTED")]) == "UNSUPPORTED"


def test_900_unlimited_question_becomes_partial():
    pricing = "The approved material publishes MDR from £900 per month. Full incident response is described as included."
    components = [
        RequestedComponent("c1", "Is £900 a published MDR price?"),
        RequestedComponent("c2", "Is incident response included?"),
        RequestedComponent("c3", "Is the included incident response unlimited?"),
    ]
    propositions = [
        EvidenceProposition("c1", "The approved material publishes MDR from £900 per month.", span("pricing", pricing[:60])),
        EvidenceProposition("c2", "Full incident response is described as included.", span("pricing", "Full incident response is described as included.")),
    ]
    # Rebuild spans with internally exact source text; production extraction will
    # retain offsets into the original chunk.
    propositions = [
        EvidenceProposition("c1", p.text, span("pricing", p.text)) if p.component_id == "c1" else
        EvidenceProposition("c2", p.text, span("pricing", p.text)) for p in propositions
    ]
    result = EvidencePropositionCoverage(SpecialistVerifier(ExactishNLI())).assess(components, propositions)
    assert result["state"] == "PARTIAL"
    assert [x.state for x in result["components"]] == ["SUPPORTED", "SUPPORTED", "UNSUPPORTED"]


def test_unlimited_cannot_be_smuggled_into_proposition():
    evidence = "Full incident response is described as included."
    component = RequestedComponent("c1", "Is incident response unlimited?")
    proposition = EvidenceProposition("c1", "Incident response is unlimited.", span("pricing", evidence))
    result = EvidencePropositionCoverage(SpecialistVerifier(ExactishNLI())).assess([component], [proposition])
    assert result["state"] == "UNSUPPORTED"
