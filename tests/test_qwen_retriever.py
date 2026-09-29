import numpy as np
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
class Fake:
 def encode(self,texts,normalize_embeddings=True):
  out=[]
  for t in texts:
   s=t.lower()
   if "pricing" in s or "cost" in s: out.append([1.,0.,0.])
   elif "implementation" in s or "deploy" in s: out.append([0.,1.,0.])
   elif "trial" in s: out.append([0.,0.,1.])
   else: out.append([.1,.1,.1])
  return np.asarray(out)
def corpus():
 return {"chunks":[
  {"id":"price","topic":"Pricing","terms":"cost pricing","simple":"MDR costs X.","source":{"title":"Pricing","url":"p"}},
  {"id":"deploy","topic":"Implementation","terms":"deploy implementation","simple":"Deployment takes days.","source":{"title":"Deploy","url":"d"}}]}
def test_qwen_retriever_finds_semantic_candidate():
 r=QwenEmbeddingRetriever(corpus(),model=Fake())
 assert r.search("pricing question")[0].source_id=="price"
def test_retriever_does_not_turn_similarity_into_truth():
 r=QwenEmbeddingRetriever(corpus(),model=Fake())
 hits=r.search("trial")
 assert hits and hits[0].score>=0
