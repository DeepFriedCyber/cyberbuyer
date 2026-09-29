import json
from buyerjourney.rag import ApprovedCorpusRetriever,normalize_corpus

def test_real_corpus_schema_is_supported():
    corpus={"chunks":[{"id":"x","topic":"Deployment","terms":"deploy onboarding",
      "simple":"Deployment normally takes several days.","technical":"Implementation details.",
      "source":{"title":"Deployment guide","url":"https://example.test/deploy"}}]}
    docs=normalize_corpus(corpus)
    assert len(docs)==1
    hit=ApprovedCorpusRetriever(corpus).search("How long does deployment take?")[0]
    assert hit.source_id=="x"
    assert hit.title=="Deployment guide"
    assert hit.url=="https://example.test/deploy"

def test_bad_corpus_shape_fails_clearly():
    try: normalize_corpus({"wrong":[]})
    except ValueError as e: assert "chunks" in str(e)
    else: raise AssertionError("expected ValueError")
