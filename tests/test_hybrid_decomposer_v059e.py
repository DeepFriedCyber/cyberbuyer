from buyerjourney.hybrid_decomposer_v059e import (
    HybridRequestedInformationDecomposer,
    is_probably_compound,
    material_terms,
)
from buyerjourney.question_coverage import RequestedComponent


class FakeZeroShot:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.calls = 0
    def decompose(self, question):
        self.calls += 1
        return self.rows


def test_atomic_question_is_preserved_without_model_call():
    model = FakeZeroShot()
    d = HybridRequestedInformationDecomposer(model)
    r = d.decompose_with_metadata("What does MDR cost?")
    assert r.route == "preserve_atomic"
    assert r.components[0].question == "What does MDR cost?"
    assert model.calls == 0


def test_atomic_guarantee_question_is_preserved_exactly():
    model = FakeZeroShot()
    q = "Can you guarantee regulatory compliance?"
    r = HybridRequestedInformationDecomposer(model).decompose_with_metadata(q)
    assert r.components[0].question == q
    assert model.calls == 0


def test_explicit_compound_uses_zero_shot_when_terms_survive():
    q = "What does MDR cost; and is incident response unlimited?"
    rows = [
        RequestedComponent("c1", "What does MDR cost?", True),
        RequestedComponent("c2", "Is incident response unlimited?", True),
    ]
    r = HybridRequestedInformationDecomposer(FakeZeroShot(rows)).decompose_with_metadata(q)
    assert r.route == "zero_shot_compound"
    assert r.valid
    assert len(r.components) == 2


def test_compound_falls_back_if_material_qualifier_is_lost():
    q = "What does MDR cost; and is incident response unlimited?"
    rows = [
        RequestedComponent("c1", "What does MDR cost?", True),
        RequestedComponent("c2", "Is incident response included?", True),
    ]
    r = HybridRequestedInformationDecomposer(FakeZeroShot(rows)).decompose_with_metadata(q)
    assert r.route == "fallback_preserve"
    assert not r.valid
    assert "unlimited" in [x.lower() for x in r.missing_terms]
    assert r.components[0].question == q


def test_material_terms_capture_price_and_strong_qualifiers():
    terms = [x.lower() for x in material_terms("Does the £900 price include unlimited response with absolutely zero downtime?")]
    assert "£900" in terms
    assert "unlimited" in terms
    assert "absolutely" in terms
    assert "zero" in terms


def test_price_unlimited_sentence_is_not_forced_through_model_by_weak_heuristic():
    # This is intentionally conservative. v0.5.9e first establishes that ordinary
    # conjunctions do not justify rewriting a buyer request. A later structured
    # request parser can split semantic subfields without prompt examples.
    q = "Does the £900 price include unlimited incident response?"
    assert not is_probably_compound(q)
