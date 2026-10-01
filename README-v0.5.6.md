# CyberBuyer v0.5.6 — Evidence-First Answer Extraction

v0.5.5 reached 1 false-supported case, 94.1% unsupported rejection and 55.6% supported acceptance. Its main failure was question-only claim decomposition. v0.5.6 keeps the old path for comparison but adds an evidence-first path:

question -> Qwen Top-3 retrieval -> atomic evidence-backed fact extraction -> exact ID/quote validation -> strict entailment -> qualifier guard -> SUPPORTED / PARTIAL / UNSUPPORTED.

Run:
    python -m pytest
    python scripts/evaluate_evidence_first.py

Targets:
- false_supported = 0
- supported_accept_rate > 0.556
- PARTIAL works for compound questions where only the base facts are published.
