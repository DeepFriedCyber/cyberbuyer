from .evidence import Evidence
from .rag import normalize_corpus

class QwenEmbeddingRetriever:
    """Semantic candidate retrieval only. Similarity is relevance, not proof."""
    def __init__(self, corpus, model_name="Qwen/Qwen3-Embedding-0.6B", model=None):
        self.docs=normalize_corpus(corpus)
        if model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise RuntimeError('Install with: pip install -e ".[qwen-embed]"') from e
            model=SentenceTransformer(model_name)
        self.model=model
        self.texts=[self._search_text(d) for d in self.docs]
        self.embeddings=self.model.encode(self.texts,normalize_embeddings=True)

    @staticmethod
    def _search_text(d):
        source=d.get("source") if isinstance(d.get("source"),dict) else {}
        fields=(d.get("topic",""),d.get("terms",""),d.get("simple",""),
                d.get("technical",""),source.get("title",""))
        return " ".join(str(x or "") for x in fields)

    def search(self, query, k=5):
        import numpy as np
        q=self.model.encode([query],normalize_embeddings=True)[0]
        scores=np.asarray(self.embeddings) @ np.asarray(q)
        order=np.argsort(-scores)[:k]
        out=[]
        for idx in order:
            d=self.docs[int(idx)]
            source=d.get("source") if isinstance(d.get("source"),dict) else {}
            body=" ".join(x for x in (str(d.get("simple","") or ""),
                                      str(d.get("technical","") or ""),
                                      str(d.get("text","") or "")) if x)
            out.append(Evidence(
                source_id=str(d.get("id") or idx),
                title=str(source.get("title") or d.get("topic") or "Approved source"),
                url=str(source.get("url") or ""),
                text=body,
                score=float(scores[int(idx)]),
                section=str(d.get("topic") or "")))
        return out
