# CyberBuyer v0.5.5 — Claim-Level Entailment

The pipeline now separates four jobs:
1. retrieval (Qwen embedding),
2. optional reranking (Jina experiment),
3. atomic claim decomposition,
4. strict claim-to-evidence entailment.

A SUPPORTED claim must cite a real evidence ID and an exact verbatim quote that exists in
the supplied evidence. Invalid IDs, invented quotes, malformed evidence, or missing proof
fail closed to UNSUPPORTED.

Run:
    python -m pytest
    python scripts/analyze_reranker_scores.py
    python scripts/evaluate_claim_entailment.py

Primary target: false_supported = 0 on the frozen 26-case benchmark.
The claim evaluator intentionally uses Qwen retrieval alone first, because the previous
benchmark achieved 100% gold-evidence Top-3 recall without Jina. Jina remains optional.
