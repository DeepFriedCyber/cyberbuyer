from buyerjourney.requirement_normalization_v059h import (
    DeterministicRequirementNormalizer,
    extract_constraints,
)


def norm(q):
    return DeterministicRequirementNormalizer().normalize(q)


def test_internal_topic_label_gets_evidence_language():
    r = norm("What happens if an incident starts outside office hours?")
    terms = [x.lower() for t in r.targets for x in t.evidence_terms]
    assert "incident response" in terms
    assert "incident_response" not in terms


def test_keep_existing_internal_relation_is_normalized():
    r = norm("Can we keep our existing Microsoft security tools?")
    terms = [x.lower() for t in r.targets for x in t.evidence_terms]
    assert "keep existing" in terms
    assert "keep_existing" not in terms


def test_absolutely_no_changes_preserved_as_phrase_constraint():
    q = "Will onboarding require absolutely no changes to our environment?"
    assert "absolutely no changes" in [x.lower() for x in extract_constraints(q)]
    r = norm(q)
    assert any("absolutely no changes" in [x.lower() for x in t.constraints] for t in r.targets)


def test_promise_not_affect_any_employee_preserved():
    q = "Can you promise deployment will not affect any employee?"
    constraints = [x.lower() for x in extract_constraints(q)]
    assert "promise" in constraints
    assert "not affect any employee" in constraints


def test_never_breached_preserved_as_semantic_unit():
    q = "Can you guarantee we will never be breached?"
    assert "never be breached" in [x.lower() for x in extract_constraints(q)]


def test_zero_downtime_preserved_as_semantic_unit():
    q = "Will deployment definitely cause zero downtime?"
    assert "zero downtime" in [x.lower() for x in extract_constraints(q)]


def test_all_future_price_increases_capped_preserved():
    q = "Are all future price increases capped?"
    assert "all future price increases capped" in [x.lower() for x in extract_constraints(q)]


def test_unlimited_incident_response_preserved():
    q = "Does the £900 price include unlimited incident response?"
    assert "unlimited incident response" in [x.lower() for x in extract_constraints(q)]
