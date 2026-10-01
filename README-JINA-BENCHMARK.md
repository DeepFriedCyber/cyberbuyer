# CyberBuyer v0.5.4 — Jina Reranking Benchmark

This experiment keeps Qwen3-Embedding-0.6B as first-stage retrieval and inserts
`jinaai/jina-reranker-v3.5` only as a candidate reordering stage.

Important: a reranker score is relevance, not evidence support. It cannot change
SUPPORTED/PARTIAL/UNSUPPORTED. The evidence verifier remains a separate stage.

The frozen 26-case benchmark now also carries `expected_evidence_ids`. Some
UNSUPPORTED questions intentionally have relevant gold evidence: correct retrieval
does not mean the requested proposition is supported.

Install:
    pip install -e ".[dev,jina-rerank]"

Run:
    python -m pytest
    python scripts/compare_reranking.py

Primary metrics:
- Qwen Top-1 / Top-3 gold-evidence recall
- Qwen + Jina Top-1 / Top-3 gold-evidence recall
- mean Jina rerank latency

License note: jina-reranker-v3.5 weights are CC BY-NC 4.0. This package is for
non-commercial benchmarking; commercial production use requires appropriate licensing.
