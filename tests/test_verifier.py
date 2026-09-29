import pytest
from buyerjourney.evidence import Evidence
from buyerjourney.verifier import Verification,Verdict,validate_verification
from buyerjourney.verified_rag import VerifiedRAGService
def ev(i="a"):return Evidence(i,"T","u","company evidence",.8)
def test_rejects_hallucinated_evidence_id():
 with pytest.raises(ValueError):validate_verification(Verification(Verdict.SUPPORTED,["claim"],[],["fake"]),[ev()])
def test_supported_requires_evidence():
 with pytest.raises(ValueError):validate_verification(Verification(Verdict.SUPPORTED,["claim"],[],[]),[ev()])
def test_partial_requires_supported_and_unsupported():
 with pytest.raises(ValueError):validate_verification(Verification(Verdict.PARTIAL,["claim"],[],["a"]),[ev()])
class R:
 def search(self,q,k):return [ev()]
class V:
 def verify(self,q,e):return Verification(Verdict.UNSUPPORTED,[],["trial not stated"],[])
def test_unsupported_offers_company_reply():
 r=VerifiedRAGService(R(),V()).assess("trial?")
 assert r["state"]=="UNSUPPORTED" and r["offer_company_reply"]
class Broken:
 def verify(self,q,e):raise RuntimeError("boom")
def test_verifier_failure_fails_closed():
 r=VerifiedRAGService(R(),Broken()).assess("x")
 assert r["state"]=="UNSUPPORTED" and r["offer_company_reply"]
