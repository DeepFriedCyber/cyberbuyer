from buyerjourney.request_facets_v059f import DeterministicRequestFacetExtractor


def extract(q):
    return DeterministicRequestFacetExtractor().extract(q)


def test_price_unlimited_facets():
    r = extract("Does the £900 price include unlimited incident response?")
    assert "£900" in r.amounts
    assert "unlimited" in r.qualifiers
    assert "pricing" in r.topics
    assert "incident_response" in r.topics
    assert "included" in r.relations


def test_guarantee_never_breach_facets():
    r = extract("Can you guarantee we will never be breached?")
    assert "guarantee" in r.qualifiers
    assert "never" in r.qualifiers
    assert "breach_prevention" in r.topics


def test_30_day_evaluation_facets():
    r = extract("Do you offer a 30 day evaluation?")
    assert "30 day" in [x.lower() for x in r.durations]
    assert "evaluation" in r.topics


def test_future_price_caps_facets():
    r = extract("Are all future price increases capped?")
    assert "all" in r.qualifiers
    assert "capped" in r.qualifiers
    assert "pricing" in r.topics


def test_defender_mdr_products():
    r = extract("We use Microsoft Defender. What does your published material say MDR adds?")
    assert "Microsoft Defender" in r.products
    assert "MDR" in r.products
    assert "adds" in r.relations


def test_difference_preserves_both_products():
    r = extract("What is the difference between MDR and EDR?")
    assert r.products == ["MDR", "EDR"]
    assert "difference" in r.relations


def test_original_question_is_never_rewritten():
    q = "Will deployment definitely cause zero downtime?"
    r = extract(q)
    assert r.original == q
    assert "definitely" in r.qualifiers
    assert "zero" in r.qualifiers
