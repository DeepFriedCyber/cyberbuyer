import math,re
from collections import Counter
from .evidence import Evidence,EvidenceGate,EvidenceState

def _tokens(s): return re.findall(r"[a-z0-9£]+", s.lower())
def _cos(a,b):
    keys=set(a)|set(b); dot=sum(a[k]*b[k] for k in keys)
    na=math.sqrt(sum(v*v for v in a.values())); nb=math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def normalize_corpus(corpus):
    """Accept CyberBuyer's {'chunks': [...]} schema or a legacy list of docs."""
    if isinstance(corpus, dict):
        docs=corpus.get("chunks")
        if not isinstance(docs,list):
            raise ValueError("corpus.json must contain a top-level 'chunks' list")
    elif isinstance(corpus,list):
        docs=corpus
    else:
        raise ValueError("corpus must be an object with 'chunks' or a list")
    if not all(isinstance(d,dict) for d in docs):
        raise ValueError("every corpus chunk must be an object")
    return docs

class ApprovedCorpusRetriever:
    def __init__(self,corpus): self.docs=normalize_corpus(corpus)
    def search(self,query,k=5):
        q=Counter(_tokens(query)); out=[]
        for i,d in enumerate(self.docs):
            source=d.get("source") if isinstance(d.get("source"),dict) else {}
            body=" ".join(str(d.get(x,"") or "") for x in ("terms","simple","technical","text","content","body"))
            searchable=" ".join((body,str(d.get("topic","") or ""),str(source.get("title","") or "")))
            score=_cos(q,Counter(_tokens(searchable)))
            evidence_text=" ".join(x for x in (str(d.get("simple","") or ""),str(d.get("technical","") or ""),str(d.get("text","") or "")) if x).strip()
            out.append(Evidence(
                source_id=str(d.get("id") or d.get("source_id") or i),
                title=str(source.get("title") or d.get("title") or d.get("topic") or "Approved source"),
                url=str(source.get("url") or d.get("url") or ""),
                text=evidence_text,
                score=score,
                section=str(d.get("topic") or d.get("section") or "")))
        return sorted(out,key=lambda x:x.score,reverse=True)[:k]

class EvidenceGroundedService:
    def __init__(self,retriever,gate=None,generator=None):
        self.retriever=retriever; self.gate=gate or EvidenceGate(); self.generator=generator
    def answer(self,question):
        decision=self.gate.decide(self.retriever.search(question))
        if decision.state==EvidenceState.UNSUPPORTED:
            return {"state":"UNSUPPORTED","answer":"I couldn't find an answer to that in the company's approved information, and I don't want to guess.","evidence":[],"offer_company_reply":True}
        if decision.state==EvidenceState.PARTIAL:
            return {"state":"PARTIAL","answer":"I found related company information, but not enough evidence to answer the whole question confidently.","evidence":[e.__dict__ for e in decision.evidence],"offer_company_reply":True}
        answer=self.generator.generate(question,decision.evidence) if self.generator else decision.evidence[0].text
        return {"state":decision.state.value,"answer":answer,"evidence":[e.__dict__ for e in decision.evidence],"offer_company_reply":False}
