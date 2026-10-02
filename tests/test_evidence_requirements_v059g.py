from buyerjourney.evidence_requirements_v059g import (
    DeterministicEvidenceRequirementBuilder,
    aggregate_requirement_states,
)


def build(q):
    return DeterministicEvidenceRequirementBuilder().build(q)


def test_price_unlimited_creates_separate_obligations():
    r = build("Does the £900 price include unlimited incident response?")
    kinds = [x.kind for x in r.requirements]
    descriptions = " ".join(x.description for x in r.requirements).lower()
    assert "amount" in kinds
    assert "qualifier" in kinds
    assert "relation" in kinds
    assert "£900" in descriptions
    assert "unlimited" in descriptions
    assert "included" in descriptions


def test_guarantee_and_never_are_independent_obligations():
    r = build("Can you guarantee we will never be breached?")
    qualifiers = [x.required_terms for x in r.requirements if x.kind == "qualifier"]
    assert ["guarantee"] in qualifiers
    assert ["never"] in qualifiers


def test_duration_is_explicit_requirement():
    r = build("Do you offer a 30 day evaluation?")
    assert any(x.kind == "duration" and "30 day" in x.required_terms for x in r.requirements)


def test_product_difference_creates_comparison_requirement():
    r = build("What is the difference between MDR and EDR?")
    assert any(x.kind == "relation" and x.required_terms == ["MDR", "EDR"] for x in r.requirements)


def test_original_is_preserved():
    q = "What does MDR cost?"
    assert build(q).original == q


def test_all_requirements_supported_means_supported():
    assert aggregate_requirement_states(["SUPPORTED", "SUPPORTED"]) == "SUPPORTED"


def test_mixed_coverage_means_partial():
    assert aggregate_requirement_states(["SUPPORTED", "UNSUPPORTED", "SUPPORTED"]) == "PARTIAL"


def test_no_coverage_means_unsupported():
    assert aggregate_requirement_states(["UNSUPPORTED", "UNSUPPORTED"]) == "UNSUPPORTED"
