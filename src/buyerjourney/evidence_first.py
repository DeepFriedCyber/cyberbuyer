from dataclasses import dataclass,field
from typing import Protocol
MATERIAL_QUALIFIERS={"free","unlimited","guarantee","guaranteed","never","zero","minimum","maximum","capped","always","absolutely","definitely","all","30 day","30-day","money back"}
@dataclass
class CandidateFact:
    text:str
    evidence_ids:list[str]=field(default_factory=list)
    evidence_quotes:list[str]=field(default_factory=list)
def normalize(s): return " ".join(str(s).split()).strip()
def dedupe_facts(facts):
    seen=set();out=[]
    for f in facts:
        k=normalize(f.text).lower().rstrip(".?!")
        if k and k not in seen: seen.add(k);out.append(f)
    return out
def qualifier_guard(question,fact):
    q=normalize(question).lower();f=normalize(fact.text).lower();quotes=" ".join(normalize(x).lower() for x in fact.evidence_quotes)
    return all(not(term in q and term in f and term not in quotes) for term in MATERIAL_QUALIFIERS)
def mechanically_grounded(fact,evidence):
    by_id={e.source_id:e for e in evidence}
    if not fact.evidence_ids or not fact.evidence_quotes or any(i not in by_id for i in fact.evidence_ids): return False
    hay="\n".join(normalize(by_id[i].text) for i in fact.evidence_ids)
    return all(normalize(q) and normalize(q) in hay for q in fact.evidence_quotes)
class EvidenceFirstService:
    def __init__(self,extractor,entailer):self.extractor=extractor;self.entailer=entailer
    def assess(self,question,evidence):
        from .claim_entailment import validate_claim_check,ClaimVerdict
        facts=dedupe_facts(self.extractor.extract(question,evidence));checks=[]
        for fact in facts:
            if not mechanically_grounded(fact,evidence) or not qualifier_guard(question,fact):continue
            c=validate_claim_check(self.entailer.check(fact.text,evidence),evidence)
            if c.verdict==ClaimVerdict.SUPPORTED:checks.append((fact,c))
        if not checks:return {"state":"UNSUPPORTED","facts":[],"missing_qualifiers":[],"unanswered_question":question}
        q=normalize(question).lower();missing=[t for t in MATERIAL_QUALIFIERS if t in q and not any(t in " ".join(f.evidence_quotes).lower() for f,c in checks)]
        return {"state":"PARTIAL" if missing else "SUPPORTED","facts":[{"text":f.text,"evidence_ids":c.evidence_ids,"evidence_quotes":c.evidence_quotes} for f,c in checks],"missing_qualifiers":missing,"unanswered_question":question if missing else None}
