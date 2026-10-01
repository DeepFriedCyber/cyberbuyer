from .qwen_claims import _QwenBase,_json_from
from .answer_relevance import RelevanceCheck,RelevanceVerdict

class QwenAnswerRelevanceClassifier(_QwenBase):
    SYSTEM="""You are a strict answer-relevance classifier.
Given a BUYER QUESTION and one evidence-backed CANDIDATE FACT, decide whether that fact actually answers the question.
DIRECT = directly answers the whole substantive question.
PARTIAL = directly answers a material part of a compound question, but not all of it.
IRRELEVANT = does not directly answer any material part.
Topical similarity is not enough. Never infer trials, contract terms, guarantees, insurance/compliance outcomes, employee impact or absolutes.
A fact about onboarding timing does not answer whether a free trial exists.
A fact about integration does not answer whether deployment affects zero employees.
A fact about human investigation does not answer whether a proof of concept is offered.
Preserve qualifiers such as free, unlimited, guaranteed, never, zero, minimum, maximum, capped, always, absolutely, definitely, 30-day and money-back.
Return JSON only: {"verdict":"DIRECT|PARTIAL|IRRELEVANT","reason":"brief reason"}"""
    def classify(self,question,fact):
        d=_json_from(self._run(self.SYSTEM,f"BUYER QUESTION:\n{question}\n\nCANDIDATE FACT:\n{fact}",120))
        try:v=RelevanceVerdict(str(d.get("verdict","IRRELEVANT")).upper())
        except Exception:v=RelevanceVerdict.IRRELEVANT
        return RelevanceCheck(v,str(d.get("reason","")))
