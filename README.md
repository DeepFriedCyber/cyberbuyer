# Cyber Buyer Journey v0.3 — Decision Resilience

This increment makes a Jev-style semantic decision model optional rather than a dependency.

## Core flow

**Deterministic policy → semantic/Jev adapter → schema + confidence gate → deterministic Rules fallback**

If the semantic engine crashes, times out, returns invalid output, or is below the confidence threshold, the buyer journey continues through deterministic rules.

Policy always wins. A semantic model cannot create an email/contact action unless the required application state permits it.

## Deliberate failover test

`DisabledSemanticEngine` always raises an exception. It exists to prove the fallback path works before Laya, Kev, SemIf, Rizzo, or another decision model is connected.

## Run

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
pytest
```

Expected: 6 decision-resilience tests pass.

## Next integration

Keep `ResilientDecisionEngine` unchanged and add adapters implementing:

```python
decide(text, context) -> Decision
```

This makes the semantic implementation replaceable without changing the buyer journey.


## v0.3.1 Shadow Decision Evaluation
Adds a 50-question labelled benchmark plus a shadow-engine harness. The primary remains authoritative; the shadow can be compared without changing the buyer journey.

Run:
```powershell
pytest
python scripts/evaluate_decisions.py
```
The benchmark produces `evaluation-results/rules-summary.json` and `rules-results.csv`. A future Laya/Kev/SemIf adapter should be evaluated against the same corpus before receiving control.


## v0.3.2 — Optional Laya shadow adapter

Laya is **not** a runtime requirement. The deterministic Rules engine remains the baseline and failover.

Baseline only:
```powershell
python scripts/compare_shadow.py --engine rules
```

Install Laya only for the experiment:
```powershell
pip install -e ".[dev,laya]"
python scripts/compare_shadow.py --engine laya
```

The first Laya run may download model weights. The adapter asks three bounded typed questions: `theme`, `intent`, and `stage`. It does not generate buyer-facing text and cannot alter the buyer journey in this shadow evaluation.

Outputs:
- `evaluation-results/shadow-comparison.json`
- `evaluation-results/shadow-disagreements.csv`

If Laya fails to install/load/run, CyberBuyer remains usable through the existing deterministic engine. Do not promote Laya from shadow mode based on the upstream benchmark; evaluate it on CyberBuyer's own labelled corpus first.

## v0.4 — Qwen Semantic Bake-Off
Rules remain the control/failover. Qwen adapters are shadow experiments only.

```powershell
pip install -e ".[dev,qwen-embed]"
python scripts/compare_qwen.py --engine embedding

pip install -e ".[dev,qwen-chat]"
python scripts/compare_qwen.py --engine qwen17
```

The embedding experiment uses Qwen3-Embedding-0.6B nearest labelled examples. The 1.7B experiment requests strict JSON classification with thinking disabled. Model weights are downloaded only when each experiment is first run.

## v0.5 — Evidence-Grounded RAG
Critical buyer answers are evidence-first. Adds DIRECT / SYNTHESISED / PARTIAL / UNSUPPORTED evidence states, fail-closed unsupported handling, an optional Qwen3-1.7B grounded generator with source-ID validation, and an evidence benchmark. The lexical retriever is a dependency-free baseline; Qwen embeddings/reranking can replace retrieval later without changing evidence policy.

## v0.5.2 — Qwen semantic retrieval experiment

Adds `QwenEmbeddingRetriever` using `Qwen/Qwen3-Embedding-0.6B`. It only retrieves candidate evidence; the existing EvidenceGate remains authoritative about whether the buyer path may answer.

Compare:
```powershell
python scripts/compare_retrieval.py --engine lexical
python scripts/compare_retrieval.py --engine qwen
```

The report exposes the raw top candidate and similarity even when the evidence gate refuses. This is intentional: semantic relevance must not be confused with evidential support. The benchmark is expanded with adversarial questions that contain supported premises plus unsupported conclusions.

## v0.5.3 — Evidence verifier

Freezes the 26-question evidence benchmark and adds a second gate after semantic retrieval. Qwen3-Embedding-0.6B finds candidate company material; Qwen3-1.7B must decide whether that material actually substantiates the buyer proposition. Similarity is never treated as proof.

Run:
```powershell
pytest
python scripts/evaluate_verifier.py
```

The verifier must return structured SUPPORTED / PARTIAL / UNSUPPORTED output, claim lists, and only evidence IDs it was actually supplied. Invalid output, invented evidence IDs, exceptions, or verifier failure fail closed.
