from buyerjourney.evidence import Evidence
from buyerjourney.rag import EvidenceGroundedService
class R:
 def __init__(self,x):self.x=x
 def search(self,q):return self.x
def e(s,t="approved"):return Evidence("s","S","u",t,s)
def test_unsupported():assert EvidenceGroundedService(R([])).answer("x")["state"]=="UNSUPPORTED"
def test_partial():assert EvidenceGroundedService(R([e(.25)])).answer("x")["state"]=="PARTIAL"
def test_direct():assert EvidenceGroundedService(R([e(.8)])).answer("x")["state"]=="DIRECT"
def test_synth():assert EvidenceGroundedService(R([e(.8),Evidence("s2","S2","u","b",.75)])).answer("x")["state"]=="SYNTHESISED"
