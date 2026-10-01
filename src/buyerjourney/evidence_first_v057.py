from .evidence_first import dedupe_facts,mechanically_grounded,qualifier_guard,MATERIAL_QUALIFIERS,normalize
from .claim_entailment import validate_claim_check,ClaimVerdict
from .answer_relevance import RelevanceVerdict

class EvidenceFirstRelevanceService:
    def __init__(self,extractor,entailer,relevance_gate):
        self.extractor=extractor;self.entailer=entailer;self.relevance_gate=relevance_gate
    def assess(self,question,evidence):
        accepted=[];rejected=[]
        for fact in dedupe_facts(self.extractor.extract(question,evidence)):
            if not mechanically_grounded(fact,evidence):
                rejected.append({"text":fact.text,"reason":"not_mechanically_grounded"});continue
            if not qualifier_guard(question,fact):
                rejected.append({"text":fact.text,"reason":"qualifier_guard"});continue
            ent=validate_claim_check(self.entailer.check(fact.text,evidence),evidence)
            if ent.verdict!=ClaimVerdict.SUPPORTED:
                rejected.append({"text":fact.text,"reason":"not_entailed"});continue
            rel=self.relevance_gate.check(question,fact.text)
            if rel.verdict==RelevanceVerdict.IRRELEVANT:
                rejected.append({"text":fact.text,"reason":"irrelevant"});continue
            accepted.append({"text":fact.text,"evidence_ids":ent.evidence_ids,"evidence_quotes":ent.evidence_quotes,"relevance":rel.verdict.value})
        if not accepted:
            return {"state":"UNSUPPORTED","facts":[],"missing_qualifiers":[],"rejected_facts":rejected,"unanswered_question":question}
        q=normalize(question).lower()
        quoted=" ".join(" ".join(x["evidence_quotes"]).lower() for x in accepted)
        missing=sorted(t for t in MATERIAL_QUALIFIERS if t in q and t not in quoted)
        has_direct=any(x["relevance"]=="DIRECT" for x in accepted)
        has_partial=any(x["relevance"]=="PARTIAL" for x in accepted)
        state="PARTIAL" if missing or (has_partial and not has_direct) else "SUPPORTED"
        return {"state":state,"facts":accepted,"missing_qualifiers":missing,"rejected_facts":rejected,"unanswered_question":question if state!="SUPPORTED" else None}
