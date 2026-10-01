from buyerjourney.evidence import Evidence
from buyerjourney.evidence_first import *
from buyerjourney.claim_entailment import ClaimCheck,ClaimVerdict
def ev(i,text):return Evidence(i,i,"u",text,.9)
class X:
 def __init__(self,f):self.f=f
 def extract(self,q,e):return self.f
class T:
 def check(self,claim,e):
  for x in e:
   if claim in x.text:return ClaimCheck(claim,ClaimVerdict.SUPPORTED,[x.source_id],[claim])
  return ClaimCheck(claim,ClaimVerdict.UNSUPPORTED,[],[])
def test_supported_fact():
 e=[ev("pricing","MDR costs £900 per month.")]
 assert EvidenceFirstService(X([CandidateFact("MDR costs £900 per month.",["pricing"],["MDR costs £900 per month."])]),T()).assess("What does MDR cost?",e)["state"]=="SUPPORTED"
def test_free_trial_cannot_be_inferred_from_onboarding():
 e=[ev("onboarding","Active monitoring can begin within 5 to 10 days of contract signature.")]
 f=CandidateFact("A free trial is available.",["onboarding"],["Active monitoring can begin within 5 to 10 days of contract signature."])
 assert EvidenceFirstService(X([f]),T()).assess("Is there a free trial period?",e)["state"]=="UNSUPPORTED"
def test_unlimited_becomes_partial():
 e=[ev("pricing","MDR costs £900 per month. Incident response is included.")]
 fs=[CandidateFact("MDR costs £900 per month.",["pricing"],["MDR costs £900 per month."]),CandidateFact("Incident response is included.",["pricing"],["Incident response is included."])]
 r=EvidenceFirstService(X(fs),T()).assess("Does the £900 price include unlimited incident response?",e)
 assert r["state"]=="PARTIAL" and "unlimited" in r["missing_qualifiers"]
def test_invented_quote_fails_closed():
 e=[ev("pricing","MDR costs £900 per month.")]
 assert EvidenceFirstService(X([CandidateFact("MDR costs £900 per month.",["pricing"],["MDR is free."])]),T()).assess("What does MDR cost?",e)["state"]=="UNSUPPORTED"
def test_dedupes():
 f=CandidateFact("Incident response is included.",["p"],["Incident response is included."])
 assert len(dedupe_facts([f,f]))==1
