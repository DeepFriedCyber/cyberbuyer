from dataclasses import dataclass

from buyerjourney.evidence import Evidence
from buyerjourney.requirement_coverage_v060b import RequirementCoverageVerifier, target_hypothesis
from buyerjourney.requirement_normalization_v059h import VerificationTarget
from buyerjourney.requirement_retrieval_v060a import RequirementEvidence, RequirementRetrievalResult
from buyerjourney.specialist_verifier_v059 import NLIResult, NLIVerdict


class KeywordNLI:
    def check(self, premise, hypothesis):
        # Test double: explicit marker means semantic entailment.
        return NLIResult(NLIVerdict.ENTAILMENT if "MATCH" in premise else NLIVerdict.NEUTRAL, .99)


def ev(source_id, text):
    return Evidence(source_id, "title", "", text, .5, "test")


def result(targets, evidence_rows):
    return RequirementRetrievalResult("q", targets, [
        RequirementEvidence(t.requirement_id, "query", rows) for t, rows in zip(targets, evidence_rows)
    ])


def target(rid, kind="topic", canonical=None, constraints=None, description="Evidence addressing service"):
    return VerificationTarget(rid, kind, canonical or ["service"], ["service"], constraints or [], description)


def test_constraint_is_preferred_as_hypothesis():
    t=target("r1","qualifier",["zero"],["zero downtime"],"generic")
    assert target_hypothesis(t)=="zero downtime"


def test_one_entailing_candidate_supports_requirement():
    r=result([target("r1")],[[ev("a","irrelevant"),ev("b","MATCH service is provided")]])
    out=RequirementCoverageVerifier(KeywordNLI()).verify(r)
    assert out.requirements[0].state=="SUPPORTED"
    assert out.state=="SUPPORTED"


def test_relevant_candidates_do_not_imply_support():
    r=result([target("r1")],[[ev("a","service mentioned but not established")]])
    out=RequirementCoverageVerifier(KeywordNLI()).verify(r)
    assert out.state=="UNSUPPORTED"


def test_mixed_requirement_coverage_is_partial():
    r=result([target("r1"),target("r2")],[[ev("a","MATCH service")],[ev("b","related only")]])
    out=RequirementCoverageVerifier(KeywordNLI()).verify(r)
    assert out.state=="PARTIAL"


def test_all_requirements_must_pass_for_supported():
    r=result([target("r1"),target("r2")],[[ev("a","MATCH one")],[ev("b","MATCH two")]])
    assert RequirementCoverageVerifier(KeywordNLI()).verify(r).state=="SUPPORTED"


def test_numeric_constraint_fails_closed_even_if_nli_entails():
    t=target("r1","amount",["£900"],[],"Evidence explicitly supporting amount £900")
    r=result([t],[[ev("a","MATCH prices start from £500")]])
    out=RequirementCoverageVerifier(KeywordNLI()).verify(r)
    assert out.state=="UNSUPPORTED"
    assert out.requirements[0].candidates[0].numeric_check is False


def test_qualifier_constraint_fails_closed_even_if_nli_entails():
    t=target("r1","qualifier",["unlimited"],["unlimited incident response"],"x")
    r=result([t],[[ev("a","MATCH incident response is included")]])
    out=RequirementCoverageVerifier(KeywordNLI()).verify(r)
    assert out.state=="UNSUPPORTED"
    assert out.requirements[0].candidates[0].qualifier_check is False
