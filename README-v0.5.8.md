# CyberBuyer v0.5.8 — Evidence Coverage

v0.5.7 established the safety baseline: zero false-supported answers on the 26-case benchmark.

v0.5.8 keeps the v0.5.7 gates but decomposes compound questions into neutral material information requests rather than factual assertions. Each request is independently tested against published evidence.

Aggregation:
- all material requests supported -> SUPPORTED
- some supported -> PARTIAL
- none supported -> UNSUPPORTED

Run:
    python -m pytest
    python scripts/evaluate_evidence_coverage_v058.py

Non-negotiable: false_supported = 0
Target: three_state_accuracy > 0.769, genuine PARTIAL > 0, spurious PARTIAL = 0.
