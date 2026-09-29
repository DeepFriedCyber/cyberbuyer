from dataclasses import dataclass,field
from enum import Enum
class Verdict(str,Enum): SUPPORTED="SUPPORTED";PARTIAL="PARTIAL";UNSUPPORTED="UNSUPPORTED"
@dataclass
class Verification:
    verdict:Verdict
    supported_claims:list[str]=field(default_factory=list)
    unsupported_claims:list[str]=field(default_factory=list)
    evidence_ids:list[str]=field(default_factory=list)
    raw:dict|None=None

def validate_verification(v:Verification,evidence):
    valid={str(x.source_id) for x in evidence}
    cited=set(map(str,v.evidence_ids))
    if not cited.issubset(valid): raise ValueError("Verifier cited evidence it was not given")
    if v.verdict==Verdict.SUPPORTED and (not v.supported_claims or not cited):
        raise ValueError("SUPPORTED requires supported claims and supplied evidence IDs")
    if v.verdict==Verdict.UNSUPPORTED and v.supported_claims:
        raise ValueError("UNSUPPORTED cannot contain supported claims")
    if v.verdict==Verdict.PARTIAL and (not v.supported_claims or not v.unsupported_claims):
        raise ValueError("PARTIAL requires both supported and unsupported claims")
    return v
