from dataclasses import dataclass
from enum import Enum

class RelevanceVerdict(str, Enum):
    DIRECT="DIRECT"
    PARTIAL="PARTIAL"
    IRRELEVANT="IRRELEVANT"

@dataclass
class RelevanceCheck:
    verdict: RelevanceVerdict
    reason: str=""

class AnswerRelevanceGate:
    def __init__(self,classifier): self.classifier=classifier
    def check(self,question,fact):
        try:
            r=self.classifier.classify(question,fact)
            v=r.verdict if isinstance(r.verdict,RelevanceVerdict) else RelevanceVerdict(str(r.verdict).upper())
            return RelevanceCheck(v,getattr(r,"reason",""))
        except Exception:
            return RelevanceCheck(RelevanceVerdict.IRRELEVANT,"classifier_error")
