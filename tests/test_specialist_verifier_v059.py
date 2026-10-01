from buyerjourney.specialist_verifier_v059 import (
    EvidenceSpan,
    NLIResult,
    NLIVerdict,
    SpecialistVerifier,
    numeric_compatible,
    qualifier_compatible,
    range_scope_compatible,
)


class StubNLI:
    def __init__(self, verdict=NLIVerdict.ENTAILMENT, confidence=.99):
        self.result=NLIResult(verdict,confidence)
    def check(self,premise,hypothesis):
        return self.result


def span(text):
    return EvidenceSpan("s1",text,0,len(text),text)


def test_exact_span_validates():
    assert span("Full incident response is included.").valid()


def test_invalid_offsets_fail_provenance():
    s=EvidenceSpan("s1","incident",1,9,"incident")
    assert not s.valid()


def test_quote_must_equal_source_slice():
    s=EvidenceSpan("s1","included",0,8,"excluded")
    assert not s.valid()


def test_included_does_not_support_unlimited():
    assert not qualifier_compatible("Full incident response is included.","Incident response is unlimited.")


def test_integration_does_not_support_no_changes():
    assert not qualifier_compatible(
        "MDR can integrate with existing Microsoft security tooling.",
        "Deployment requires absolutely no changes to the environment.",
    )


def test_numeric_preservation():
    assert numeric_compatible("MDR is available from £900 per month.","MDR is available from £900 per month.")
    assert not numeric_compatible("MDR is available from £900 per month.","MDR costs £1200 per month.")


def test_from_price_not_universal_exact_price():
    p="The approved material publishes MDR from £900 per month."
    assert range_scope_compatible(p,"MDR is available from £900 per month.")
    assert not range_scope_compatible(p,"All MDR customers pay exactly £900 per month.")


def test_deterministic_gate_overrides_semantic_entailment():
    verifier=SpecialistVerifier(StubNLI())
    r=verifier.verify(span("Full incident response is included."),"Incident response is unlimited.")
    assert r.nli_verdict=="ENTAILMENT"
    assert not r.qualifier_check
    assert r.verdict=="UNSUPPORTED"


def test_invalid_provenance_cannot_be_supported():
    verifier=SpecialistVerifier(StubNLI())
    bad=EvidenceSpan("s1","included",0,8,"excluded")
    r=verifier.verify(bad,"included")
    assert not r.provenance_check
    assert r.verdict=="UNSUPPORTED"


def test_nli_error_fails_closed():
    verifier=SpecialistVerifier(StubNLI(NLIVerdict.ERROR,0.0))
    r=verifier.verify(span("MDR includes human investigation."),"MDR includes human investigation.")
    assert r.verdict=="UNSUPPORTED"
