from .verifier import Verdict
class VerifiedRAGService:
    """Retrieval finds candidates; verifier decides evidential support."""
    def __init__(self,retriever,verifier,k=3):self.retriever=retriever;self.verifier=verifier;self.k=k
    def assess(self,question):
        evidence=self.retriever.search(question,self.k)
        if not evidence:return {"state":"UNSUPPORTED","verification":None,"evidence":[],"offer_company_reply":True}
        try:v=self.verifier.verify(question,evidence)
        except Exception as exc:
            # Verifier failure must never degrade into an unsupported factual answer.
            return {"state":"UNSUPPORTED","verification_error":type(exc).__name__,
                    "evidence":[],"offer_company_reply":True}
        used=[e for e in evidence if str(e.source_id) in set(v.evidence_ids)]
        return {"state":v.verdict.value,
                "supported_claims":v.supported_claims,
                "unsupported_claims":v.unsupported_claims,
                "evidence":[e.__dict__ for e in used],
                "offer_company_reply":v.verdict!=Verdict.SUPPORTED}
