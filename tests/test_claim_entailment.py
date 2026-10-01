from buyerjourney.evidence import Evidence
from buyerjourney.claim_entailment import *
def ev(i,text): return Evidence(i,i,"u",text,.9)
class D:
 def __init__(self,claims):self.claims=claims
 def decompose(self,q):return [AtomicClaim(x) for x in self.claims]
class E:
 def __init__(self,checks):self.checks=iter(checks)
 def check(self,c,e):return next(self.checks)
def test_all_supported():
 s=ClaimLevelEvidenceService(D(["Price is £900."]),E([
  ClaimCheck("Price is £900.",ClaimVerdict.SUPPORTED,["pricing"],["Price is £900."])]))
 assert s.assess("q",[ev("pricing","Price is £900.")]).state=="SUPPORTED"
def test_mixed_becomes_partial():
 s=ClaimLevelEvidenceService(D(["Price is £900.","Response is unlimited."]),E([
  ClaimCheck("Price is £900.",ClaimVerdict.SUPPORTED,["pricing"],["Price is £900."]),
  ClaimCheck("Response is unlimited.",ClaimVerdict.UNSUPPORTED,[],[])]))
 r=s.assess("q",[ev("pricing","Price is £900. Incident response is included.")])
 assert r.state=="PARTIAL" and r.unsupported_claims==["Response is unlimited."]
def test_invented_evidence_id_fails_closed():
 s=ClaimLevelEvidenceService(D(["x"]),E([ClaimCheck("x",ClaimVerdict.SUPPORTED,["fake"],["x"])]))
 assert s.assess("q",[ev("real","x")]).state=="UNSUPPORTED"
def test_invented_quote_fails_closed():
 s=ClaimLevelEvidenceService(D(["Unlimited response."]),E([
  ClaimCheck("Unlimited response.",ClaimVerdict.SUPPORTED,["pricing"],["unlimited response"])]))
 assert s.assess("q",[ev("pricing","Incident response is included.")]).state=="UNSUPPORTED"
def test_empty_decomposition_falls_back_to_question():
 s=ClaimLevelEvidenceService(D([]),E([ClaimCheck("buyer q",ClaimVerdict.UNSUPPORTED,[],[])]))
 assert s.assess("buyer q",[ev("x","something")]).state=="UNSUPPORTED"
