from __future__ import annotations
from .decision import Decision

THEMES = {
 "TRIAL_POC":"trial, proof of concept, test-before-commitment",
 "PRICING":"price, cost, commercial pricing",
 "IMPLEMENTATION":"deployment, onboarding, implementation timescale",
 "DOWNTIME":"downtime, disruption, outage caused by implementation",
 "MSP":"relationship with an MSP or IT provider",
 "INCIDENT":"incident or breach response",
 "CONTRACT":"contract length, cancellation or commitment",
 "INSURANCE":"cyber insurance or insurer",
 "OTHER":"another product-research topic",
}

class LayaShadowEngine:
 name="laya"
 def __init__(self, checkpoint="convaiinnovations/laya", subfolder=None):
  try:
   import laya
  except ImportError as e:
   raise RuntimeError("Laya is optional. Install with: pip install laya") from e
  kwargs={}
  if subfolder: kwargs["subfolder"]=subfolder
  self.agent=laya.load(checkpoint,**kwargs)

 def decide(self,text,context=None):
  state={"buyer_question":text}
  questions={
   "theme":{"type":"choice","instructions":"Classify the buyer question into exactly one CyberBuyer topic.","criteria":THEMES},
   "intent":{"type":"choice","instructions":"Classify the buyer's primary intent.","criteria":{"commercial":"commercial terms such as price, trial or contract","research":"product, technical or general research"}},
   "stage":{"type":"choice","instructions":"Classify the buyer journey stage.","criteria":{"evaluating":"actively evaluating commercial fit or terms","researching":"learning or researching without a clear commercial commitment signal"}},
  }
  raw=self.agent.predict(state,questions)
  a=raw["answers"]
  def picked(k):
   v=a[k]
   return v.get("choice") or v.get("selected") or v.get("answer")
  def conf(k):
   v=a[k]
   if isinstance(v.get("confidence"),(int,float)): return float(v["confidence"])
   probs=v.get("probabilities") or v.get("probs") or {}
   return float(max(probs.values())) if probs else 0.0
  theme=picked("theme"); intent=picked("intent"); stage=picked("stage")
  confidence=min(conf("theme"),conf("intent"),conf("stage"))
  return Decision(str(theme).replace("_"," ").title(),str(intent),str(stage),str(theme),
                  ("KEEP_EXPLORING",),confidence,self.name)
