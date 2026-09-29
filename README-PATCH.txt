CyberBuyer v0.5.1 corpus-schema fix

Overwrite these files in your existing project:
  src/buyerjourney/rag.py
  scripts/evaluate_evidence.py
Add:
  tests/test_corpus_integration.py

Then run:
  pytest
  python scripts/evaluate_evidence.py

Fix: v0.5 incorrectly assumed corpus.json was a top-level list. CyberBuyer's actual schema is {"chunks":[...]}, with answer text in simple/technical and provenance under source.
