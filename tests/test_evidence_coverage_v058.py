from buyerjourney.evidence import Evidence
from buyerjourney.evidence_first import CandidateFact
from buyerjourney.evidence_coverage_v058 import EvidenceCoverageService
from buyerjourney.question_coverage import RequestedComponent
from buyerjourney.claim_entailment import ClaimCheck,ClaimVerdict
from buyerjourney.answer_relevance import RelevanceCheck,RelevanceVerdict
def ev(i,t):return Evidence(i,i,"u",t,.9)
class D:
 def __init__(self,cs):self.cs=cs
 def decompose(self,q):return self.cs
class X:
 def __init__(self,byq):self.byq=byq
 def extract(self,q,e):return self.byq.get(q,[])
class T:
 def check(self,c,e):
  for x in e:
   if c in x.text:return ClaimCheck(c,ClaimVerdict.SUPPORTED,[x.source_id],[c])
  return ClaimCheck(c,ClaimVerdict.UNSUPPORTED,[],[])
class R:
 def check(self,q,f):return RelevanceCheck(RelevanceVerdict.DIRECT,"")
def test_compound_question_becomes_real_partial():
 cs=[RequestedComponent("c1","Is £900 a published MDR price?"),RequestedComponent("c2","Is incident response included?"),RequestedComponent("c3","Is incident response unlimited?")]
 e=[ev("p","MDR costs £900 per month. Incident response is included.")]
 x=X({cs[0].question:[CandidateFact("MDR costs £900 per month.",["p"],["MDR costs £900 per month."])],cs[1].question:[CandidateFact("Incident response is included.",["p"],["Incident response is included."])],cs[2].question:[]})
 r=EvidenceCoverageService(D(cs),x,T(),R()).assess("Does £900 include unlimited incident response?",e)
 assert r["state"]=="PARTIAL" and r["unanswered_components"]==["Is incident response unlimited?"]
def test_unrelated_fact_cannot_create_partial():
 cs=[RequestedComponent("c1","Is there a free trial?")]
 assert EvidenceCoverageService(D(cs),X({}),T(),R()).assess("Is there a free trial?",[ev("o","Monitoring starts within 5 to 10 days.")])["state"]=="UNSUPPORTED"
def test_simple_supported_question_stays_supported():
 cs=[RequestedComponent("c1","What is the published MDR price?")];e=[ev("p","MDR costs £900 per month.")]
 x=X({cs[0].question:[CandidateFact("MDR costs £900 per month.",["p"],["MDR costs £900 per month."])]})
 assert EvidenceCoverageService(D(cs),x,T(),R()).assess("What does MDR cost?",e)["state"]=="SUPPORTED"
