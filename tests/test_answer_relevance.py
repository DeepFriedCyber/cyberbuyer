from buyerjourney.answer_relevance import *
class C:
 def __init__(self,v):self.v=v
 def classify(self,q,f):return RelevanceCheck(self.v,"x")
def test_direct():assert AnswerRelevanceGate(C(RelevanceVerdict.DIRECT)).check("q","f").verdict==RelevanceVerdict.DIRECT
def test_partial():assert AnswerRelevanceGate(C(RelevanceVerdict.PARTIAL)).check("q","f").verdict==RelevanceVerdict.PARTIAL
class Bad:
 def classify(self,q,f):raise RuntimeError()
def test_error_fails_closed():assert AnswerRelevanceGate(Bad()).check("q","f").verdict==RelevanceVerdict.IRRELEVANT
