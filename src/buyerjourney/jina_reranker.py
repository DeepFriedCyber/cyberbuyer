from dataclasses import replace

class JinaReranker:
    """Reorders retrieved Evidence objects. It never decides support/answerability."""
    def __init__(self, model_name="jinaai/jina-reranker-v3.5", model=None):
        if model is None:
            try:
                from transformers import AutoModel
            except ImportError as e:
                raise RuntimeError('Install the Jina experiment dependencies first.') from e
            model=AutoModel.from_pretrained(model_name,dtype="auto",trust_remote_code=True)
            model.eval()
        self.model=model

    def rerank(self,query,evidence,top_n=None):
        if not evidence:return []
        docs=[e.text for e in evidence]
        raw=list(self.model.rerank(query,docs))
        # Jina returns ranked dictionaries with document and relevance_score.
        # Match by document text, retaining the original trusted Evidence object.
        buckets={}
        for i,e in enumerate(evidence): buckets.setdefault(e.text,[]).append((i,e))
        ranked=[]
        for item in raw:
            doc=item.get("document","")
            if doc not in buckets or not buckets[doc]: continue
            _,e=buckets[doc].pop(0)
            score=float(item.get("relevance_score",0.0))
            ranked.append(replace(e,score=score))
        # Defensive fallback: never lose candidates because a model response is odd.
        seen={e.source_id for e in ranked}
        ranked.extend(e for e in evidence if e.source_id not in seen)
        return ranked[:top_n] if top_n else ranked

class RerankingRetriever:
    """Retriever-compatible wrapper: retrieve candidates, then reorder them."""
    def __init__(self,retriever,reranker,candidate_k=6):
        self.retriever=retriever;self.reranker=reranker;self.candidate_k=candidate_k
    def search(self,query,k=5):
        candidates=self.retriever.search(query,self.candidate_k)
        return self.reranker.rerank(query,candidates,top_n=k)
