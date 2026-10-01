from .question_coverage import ComponentCoverage,CoverageVerdict,aggregate_coverage
from .evidence_first import dedupe_facts,mechanically_grounded,qualifier_guard
from .claim_entailment import validate_claim_check,ClaimVerdict
from .answer_relevance import RelevanceVerdict
class EvidenceCoverageService:
 def __init__(self,decomposer,extractor,entailer,relevance_gate):self.decomposer=decomposer;self.extractor=extractor;self.entailer=entailer;self.relevance_gate=relevance_gate
 def _assess_component(self,component,evidence):
  accepted=[];rejected=[]
  for fact in dedupe_facts(self.extractor.extract(component.question,evidence)):
   if not mechanically_grounded(fact,evidence):rejected.append({"text":fact.text,"reason":"not_mechanically_grounded"});continue
   if not qualifier_guard(component.question,fact):rejected.append({"text":fact.text,"reason":"qualifier_guard"});continue
   ent=validate_claim_check(self.entailer.check(fact.text,evidence),evidence)
   if ent.verdict!=ClaimVerdict.SUPPORTED:rejected.append({"text":fact.text,"reason":"not_entailed"});continue
   rel=self.relevance_gate.check(component.question,fact.text)
   if rel.verdict!=RelevanceVerdict.DIRECT:rejected.append({"text":fact.text,"reason":"not_direct"});continue
   accepted.append({"text":fact.text,"evidence_ids":ent.evidence_ids,"evidence_quotes":ent.evidence_quotes})
  return ComponentCoverage(component,CoverageVerdict.SUPPORTED if accepted else CoverageVerdict.UNSUPPORTED,accepted,rejected)
 def assess(self,question,evidence):
  coverage=[self._assess_component(c,evidence) for c in self.decomposer.decompose(question)];state=aggregate_coverage(coverage)
  return {"state":state,"components":[{"id":x.component.id,"question":x.component.question,"material":x.component.material,"verdict":x.verdict.value,"facts":x.facts,"rejected_facts":x.rejected_facts} for x in coverage],"unanswered_components":[x.component.question for x in coverage if x.component.material and x.verdict==CoverageVerdict.UNSUPPORTED],"unanswered_question":question if state!="SUPPORTED" else None}
