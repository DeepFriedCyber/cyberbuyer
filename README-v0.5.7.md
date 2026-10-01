# CyberBuyer v0.5.7 — Answer Relevance Gate

Adds a separate question-to-fact relevance gate after grounding and entailment.

Candidate facts must pass:
1. exact evidence ID/quote validation
2. evidence-to-fact entailment
3. question-to-fact relevance (DIRECT / PARTIAL / IRRELEVANT)
4. material qualifier coverage

IRRELEVANT evidence is discarded even when the evidence itself is valid.

Run:
    python -m pytest
    python scripts/evaluate_evidence_first_v057.py

Primary target: false_supported = 0 while preserving high acceptance of genuinely supported questions.
