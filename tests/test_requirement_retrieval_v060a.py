from dataclasses import dataclass

from buyerjourney.evidence import Evidence
from buyerjourney.requirement_normalization_v059h import VerificationTarget
from buyerjourney.requirement_retrieval_v060a import RequirementAwareRetriever, build_target_query


class FakeRetriever:
    def __init__(self):
        self.queries = []
    def search(self, query, k=5):
        self.queries.append((query, k))
        return [Evidence("s1", "Source", "", "candidate evidence", 0.5, "test")]


class FakeReranker:
    def __init__(self):
        self.calls = []
    def rerank(self, query, evidence, top_n=None):
        self.calls.append((query, top_n))
        return evidence[:top_n]


class FakeNormalizer:
    def normalize(self, question):
        class R: pass
        r=R();r.original=question;r.targets=[
            VerificationTarget("r1","topic",["incident_response"],["incident response","incident","response"],[],"Evidence addressing incident response"),
            VerificationTarget("r2","qualifier",["unlimited"],["unlimited"],["unlimited incident response"],"Evidence explicitly supporting qualifier unlimited"),
        ];return r


def test_query_uses_evidence_language_not_internal_label():
    target=VerificationTarget("r1","topic",["incident_response"],["incident response","incident","response"],[],"")
    q=build_target_query("What happens if an incident starts?",target)
    assert "incident_response" not in q
    assert "incident response" in q


def test_constraint_is_present_in_query():
    target=VerificationTarget("r1","qualifier",["unlimited"],["unlimited"],["unlimited incident response"],"")
    q=build_target_query("Does it include unlimited incident response?",target)
    assert "unlimited incident response" in q


def test_retrieves_independently_per_requirement():
    base=FakeRetriever()
    result=RequirementAwareRetriever(base,normalizer=FakeNormalizer(),candidate_k=6,top_k=3).retrieve("buyer question")
    assert len(result.retrieved)==2
    assert len(base.queries)==2
    assert all(k==6 for _,k in base.queries)


def test_optional_reranker_receives_each_requirement_query():
    base=FakeRetriever();reranker=FakeReranker()
    RequirementAwareRetriever(base,reranker,FakeNormalizer(),candidate_k=6,top_k=3).retrieve("buyer question")
    assert len(reranker.calls)==2
    assert all(top_n==3 for _,top_n in reranker.calls)


def test_retrieval_layer_has_no_support_state():
    base=FakeRetriever()
    result=RequirementAwareRetriever(base,normalizer=FakeNormalizer()).retrieve("buyer question")
    assert not hasattr(result,"state")
    assert not hasattr(result.retrieved[0],"supported")
