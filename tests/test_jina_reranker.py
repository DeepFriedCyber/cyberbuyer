from buyerjourney.evidence import Evidence
from buyerjourney.jina_reranker import JinaReranker,RerankingRetriever
def ev(i,text,score=.5):return Evidence(i,i,"u",text,score)
class FakeJina:
 def rerank(self,q,docs):
  return [{"document":docs[1],"relevance_score":.9},{"document":docs[0],"relevance_score":.2}]
def test_reranker_reorders_but_preserves_evidence_identity():
 r=JinaReranker(model=FakeJina())
 out=r.rerank("price?",[ev("a","general"),ev("pricing","price is £900")])
 assert [x.source_id for x in out]==["pricing","a"]
 assert out[0].text=="price is £900"
class Base:
 def search(self,q,k=5):return [ev("a","general"),ev("pricing","price is £900")]
def test_wrapper_is_retriever_compatible():
 r=RerankingRetriever(Base(),JinaReranker(model=FakeJina()))
 assert r.search("price?",1)[0].source_id=="pricing"
def test_empty_input_is_safe():
 assert JinaReranker(model=FakeJina()).rerank("x",[])==[]
