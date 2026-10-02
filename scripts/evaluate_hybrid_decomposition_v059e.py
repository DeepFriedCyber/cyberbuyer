"""v0.5.9e decomposition-only benchmark with progress and checkpointing."""
import json
from pathlib import Path

from buyerjourney.qwen_question_coverage_v059d import QwenZeroShotRequestedInformationDecomposer
from buyerjourney.hybrid_decomposer_v059e import HybridRequestedInformationDecomposer, material_terms


def load_cases():
    return json.loads(Path("data/evidence_benchmark.json").read_text(encoding="utf-8"))


def serialise(rows):
    return [{"id": x.id, "question": x.question, "material": x.material} for x in rows]


def main():
    cases = load_cases()
    zero = QwenZeroShotRequestedInformationDecomposer()
    hybrid = HybridRequestedInformationDecomposer(zero)
    rows = []
    checkpoint = Path("evaluation-results/decomposition-v059e.checkpoint.json")
    output = Path("evaluation-results/decomposition-v059e.json")
    output.parent.mkdir(exist_ok=True)

    for i, case in enumerate(cases, 1):
        q = case["q"]
        print(f"[{i:02d}/{len(cases)}] {q}", flush=True)
        result = hybrid.decompose_with_metadata(q)
        print(f"  route={result.route} valid={result.valid} components={len(result.components)}", flush=True)
        rows.append({
            "question": q,
            "route": result.route,
            "valid": result.valid,
            "material_terms": material_terms(q),
            "missing_terms": result.missing_terms,
            "components": serialise(result.components),
        })
        checkpoint.write_text(json.dumps({"version":"0.5.9e","completed":i,"rows":rows}, indent=2, ensure_ascii=False), encoding="utf-8")

    routes = {}
    for r in rows:
        routes[r["route"]] = routes.get(r["route"], 0) + 1
    out = {
        "version": "0.5.9e",
        "purpose": "Hybrid decomposition only: preserve atomic questions, zero-shot explicit compounds, deterministic material-term validation.",
        "cases": len(rows),
        "routes": routes,
        "invalid_decompositions": sum(not r["valid"] for r in rows),
        "rows": rows,
    }
    output.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
