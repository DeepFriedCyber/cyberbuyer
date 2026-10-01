from dataclasses import dataclass,field
from enum import Enum
from typing import Protocol

class ClaimVerdict(str,Enum):
    SUPPORTED="SUPPORTED"
    UNSUPPORTED="UNSUPPORTED"

@dataclass
class AtomicClaim:
    text:str

@dataclass
class ClaimCheck:
    claim:str
    verdict:ClaimVerdict
    evidence_ids:list[str]=field(default_factory=list)
    evidence_quotes:list[str]=field(default_factory=list)

@dataclass
class ClaimResult:
    state:str
    claims:list[ClaimCheck]
    supported_claims:list[str]
    unsupported_claims:list[str]
    evidence_ids:list[str]

class Decomposer(Protocol):
    def decompose(self,question:str)->list[AtomicClaim]: ...

class Entailer(Protocol):
    def check(self,claim:str,evidence)->ClaimCheck: ...

def _norm(s:str)->str:
    return " ".join(str(s).split())

def validate_claim_check(check:ClaimCheck,evidence)->ClaimCheck:
    """Fail closed unless every cited id and quote is mechanically valid."""
    by_id={e.source_id:e for e in evidence}
    if check.verdict==ClaimVerdict.SUPPORTED:
        if not check.evidence_ids or not check.evidence_quotes:
            return ClaimCheck(check.claim,ClaimVerdict.UNSUPPORTED,[],[])
        if any(i not in by_id for i in check.evidence_ids):
            return ClaimCheck(check.claim,ClaimVerdict.UNSUPPORTED,[],[])
        hay="\n".join(_norm(by_id[i].text) for i in check.evidence_ids)
        if any(_norm(q) not in hay for q in check.evidence_quotes if _norm(q)):
            return ClaimCheck(check.claim,ClaimVerdict.UNSUPPORTED,[],[])
        if not all(_norm(q) for q in check.evidence_quotes):
            return ClaimCheck(check.claim,ClaimVerdict.UNSUPPORTED,[],[])
    return check

class ClaimLevelEvidenceService:
    def __init__(self,decomposer:Decomposer,entailer:Entailer):
        self.decomposer=decomposer;self.entailer=entailer

    def assess(self,question,evidence)->ClaimResult:
        claims=self.decomposer.decompose(question)
        if not claims:
            claims=[AtomicClaim(question)]
        checks=[validate_claim_check(self.entailer.check(c.text,evidence),evidence) for c in claims]
        supported=[c.claim for c in checks if c.verdict==ClaimVerdict.SUPPORTED]
        unsupported=[c.claim for c in checks if c.verdict!=ClaimVerdict.SUPPORTED]
        if supported and unsupported: state="PARTIAL"
        elif supported: state="SUPPORTED"
        else: state="UNSUPPORTED"
        ids=[]
        for c in checks:
            for i in c.evidence_ids:
                if i not in ids: ids.append(i)
        return ClaimResult(state,checks,supported,unsupported,ids)
