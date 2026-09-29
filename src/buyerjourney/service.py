from .retriever import Retriever
class BuyerJourney:
 def __init__(self,chunks): self.r=Retriever(chunks)
 def answer(self,q,mode="simple"):
  if any(x in q.lower() for x in ["guarantee we will never","never be hacked","100% secure"]): return self.unsupported()
  hits=self.r.search(q)
  if not hits or hits[0][0]<1:return self.unsupported()
  _,c=hits[0]
  return {"status":"supported","answer":c["technical" if mode=="technical" else "simple"],"sources":[c["source"]],"asset":c["asset"],"followups":c["follow"],"topic":c["topic"]}
 def unsupported(self):
  return {"status":"unsupported","answer":"I can't find approved material that answers that question. I've treated it as a content gap rather than guessing. You can keep researching anonymously or choose to ask a human specialist.","sources":[],"asset":None,"followups":["Show me MDR pricing","How quickly can monitoring start?","What happens at 2am?"],"topic":None}
def signals(q):
 q=q.lower(); rules=[(("microsoft","m365","defender"),"Microsoft environment / interest"),(("msp","it provider"),"Existing MSP / IT provider mentioned"),(("2am","overnight","weekend"),"Out-of-hours monitoring concern"),(("price","pricing","cost","£"),"Commercial / pricing interest"),(("incident","breach","attack"),"Security incident / threat concern"),(("onboarding","implement","deploy","how long"),"Implementation / onboarding interest")]
 return [label for terms,label in rules if any(t in q for t in terms)]
