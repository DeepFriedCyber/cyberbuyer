from buyerjourney.evidence import Evidence
from buyerjourney.evidence_first import CandidateFact
from buyerjourney.evidence_first_v057 import EvidenceFirstRelevanceService
from buyerjourney.claim_entailment import ClaimCheck,ClaimVerdict
from buyerjourney.answer_relevance import RelevanceCheck,RelevanceVerdict
def ev(i,t):return Evidence(i,i,"u",t,.9)
class X:
 def __init__(self,f):self.f=f
 def extract(self,q,e):return self.f
class T:
 def check(self,c,e):
  for x in e:
   if c in x.text:return ClaimCheck(c,ClaimVerdict.SUPPORTED,[x.source_id],[c])
  return ClaimCheck(c,ClaimVerdict.UNSUPPORTED,[],[])
class R:
 def __init__(self,v):self.v=v
 def check(self,q,f):return RelevanceCheck(self.v,"")
def test_irrelevant_supported_fact_is_unsupported():
 e=[ev("m","MDR provides human investigation.")]
 f=CandidateFact("MDR provides human investigation.",["m"],["MDR provides human investigation."])
 assert EvidenceFirstRelevanceService(X([f]),T(),R(RelevanceVerdict.IRRELEVANT)).assess("Can we run a proof of concept?",e)["state"]=="UNSUPPORTED"
def test_direct_fact_supported():
 e=[ev("p","MDR costs £900 per month.")]
 f=CandidateFact("MDR costs £900 per month.",["p"],["MDR costs £900 per month."])
 assert EvidenceFirstRelevanceService(X([f]),T(),R(RelevanceVerdict.DIRECT)).assess("What does MDR cost?",e)["state"]=="SUPPORTED"
def test_partial_fact_is_partial():
 e=[ev("p","MDR costs £900 per month.")]
 f=CandidateFact("MDR costs £900 per month.",["p"],["MDR costs £900 per month."])
 assert EvidenceFirstRelevanceService(X([f]),T(),R(RelevanceVerdict.PARTIAL)).assess("Does £900 include unlimited incident response?",e)["state"]=="PARTIAL"
