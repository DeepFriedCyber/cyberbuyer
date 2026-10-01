"""v0.5.9c end-to-end experiment.

Question -> Qwen requested-information decomposition -> approved benchmark evidence ->
Qwen evidence-derived propositions with exact quote provenance -> specialist NLI and
deterministic gates -> component coverage.

This does not modify the production v0.5.8 path.
"""
import json
from pathlib import Path
from types import SimpleNamespace

from buyerjourney.qwen_question_coverage import QwenRequestedInformationDecomposer
from buyerjourney.qwen_propositions_v059c import QwenEvidencePropositionGenerator
from buyerjourney.evidence_propositions_v059c import (
    RequestedComponent,
    EvidencePropositionCoverage,
)
from buyerjourney.specialist_verifier_v059 import SpecialistVerifier, TransformersNLI


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def chunk_text(chunk):
    return f"{chunk.get('simple', '')}\n{chunk.get('technical', '')}".strip()


def main():
    benchmark = load_json("data/evidence_benchmark.json")
    corpus = load_json("data/corpus.json")
    chunks = {c["id"]: c for c in corpus["chunks"]}

    decomposer = QwenRequestedInformationDecomposer()
    generator = QwenEvidencePropositionGenerator(
        tokenizer=decomposer.tok,
        model=decomposer.model,
    )
    nli = TransformersNLI()
    coverage = EvidencePropositionCoverage(SpecialistVerifier(nli))

    rows = []
    exact_correct = false_supported = 0
    state_counts = {"SUPPORTED": 0, "PARTIAL": 0, "UNSUPPORTED": 0}

    for case in benchmark:
        question = case["q"]
        expected = case["expected"]
        evidence_ids = case.get("expected_evidence_ids", [])
        evidence = [
            SimpleNamespace(source_id=eid, text=chunk_text(chunks[eid]))
            for eid in evidence_ids if eid in chunks
        ]

        raw_components = decomposer.decompose(question)
        components = [
            RequestedComponent(c.component_id, c.question)
            for c in raw_components if getattr(c, "material", True)
        ]
        propositions = generator.generate(components, evidence) if evidence else []
        result = coverage.assess(components, propositions)
        actual = result["state"]
        state_counts[actual] += 1

        # Existing benchmark is binary. PARTIAL is intentionally not silently
        # converted to SUPPORTED; report it separately for manual adjudication.
        exact_correct += actual == expected
        false_supported += expected != "SUPPORTED" and actual == "SUPPORTED"

        rows.append({
            "question": question,
            "expected": expected,
            "actual": actual,
            "expected_evidence_ids": evidence_ids,
            "components": [
                {
                    "component_id": c.component_id,
                    "question": c.question,
                    "state": c.state,
                    "proposition": c.proposition,
                    "source_id": c.source_id,
                    "nli_verdict": c.nli_verdict,
                    "nli_confidence": round(c.nli_confidence, 4),
                    "qualifier_check": c.qualifier_check,
                    "numeric_check": c.numeric_check,
                    "provenance_check": c.provenance_check,
                }
                for c in result["components"]
            ],
            "generated_propositions": [
                {
                    "component_id": p.component_id,
                    "text": p.text,
                    "source_id": p.span.source_id,
                    "quote": p.span.quote,
                }
                for p in propositions
            ],
        })

    mismatches = [r for r in rows if r["actual"] != r["expected"]]
    partials = [r for r in rows if r["actual"] == "PARTIAL"]
    out = {
        "version": "0.5.9c",
        "cases": len(rows),
        "binary_gold_note": "Existing benchmark has SUPPORTED/UNSUPPORTED labels; PARTIAL is reported as a distinct experimental state.",
        "exact_three_state_vs_binary_gold_accuracy": round(exact_correct / len(rows), 4),
        "false_supported": false_supported,
        "supported_count": state_counts["SUPPORTED"],
        "partial_count": state_counts["PARTIAL"],
        "unsupported_count": state_counts["UNSUPPORTED"],
        "mismatch_count": len(mismatches),
        "partial_cases": partials,
        "mismatches": mismatches,
        "rows": rows,
    }
    path = Path("evaluation-results/evidence-propositions-v059c.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
