from dataclasses import dataclass
from .decision import Decision
@dataclass
class ShadowResult:
 primary:Decision; shadow:Decision|None; shadow_error:str|None
class ShadowDecisionEngine:
 """The primary controls the journey; the shadow is observational only."""
 def __init__(self,primary,shadow=None): self.primary=primary; self.shadow=shadow
 def decide(self,text,context=None):
  p=self.primary.decide(text,context)
  if self.shadow is None:return ShadowResult(p,None,"not_configured")
  try:return ShadowResult(p,self.shadow.decide(text,context),None)
  except Exception as e:return ShadowResult(p,None,type(e).__name__)
