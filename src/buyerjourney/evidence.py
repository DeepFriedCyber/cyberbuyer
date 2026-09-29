from dataclasses import dataclass,field
from enum import Enum
class EvidenceState(str,Enum): DIRECT="DIRECT";SYNTHESISED="SYNTHESISED";PARTIAL="PARTIAL";UNSUPPORTED="UNSUPPORTED"
@dataclass(frozen=True)
class Evidence: source_id:str;title:str;url:str;text:str;score:float;section:str=""
@dataclass
class EvidenceDecision: state:EvidenceState;evidence:list[Evidence]=field(default_factory=list);reason:str=""
class EvidenceGate:
 def __init__(self,strong=.34,weak=.20):self.strong=strong;self.weak=weak
 def decide(self,items):
  if not items or items[0].score<self.weak:return EvidenceDecision(EvidenceState.UNSUPPORTED,[],"No sufficiently relevant approved evidence.")
  strong=[x for x in items if x.score>=self.strong]
  if not strong:return EvidenceDecision(EvidenceState.PARTIAL,items[:2],"Related evidence is insufficient.")
  if len(strong)>1 and abs(strong[0].score-strong[1].score)<=.12:return EvidenceDecision(EvidenceState.SYNTHESISED,strong[:3],"Multiple passages support the answer.")
  return EvidenceDecision(EvidenceState.DIRECT,strong[:1],"Direct approved evidence.")
