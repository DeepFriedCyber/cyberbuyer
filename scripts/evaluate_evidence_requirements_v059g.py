"""v0.5.9g deterministic evidence-requirement benchmark.

No retrieval or model inference. Converts request facets into explicit evidence
obligations that can later be checked independently against retrieved source text.
"""
import json
from pathlib import Path
from buyerjourney.evidence_requirements_v059g import DeterministicEvidenceRequirementBuilder


def main():
    cases = json.loads(Path("data/evidence_benchmark.json").read_text(encoding="utf-8"))
    builder = DeterministicEvidenceRequirementBuilder()
    rows = []

    for i, case in enumerate(cases, 1):
        q = case["q"]
        result = builder.build(q)
        reqs = [
            {
                "id": r.requirement_id,
                "kind": r.kind,
                "description": r.description,
                "required_terms": r.required_terms,
            }
            for r in result.requirements
        ]
        rows.append({
            "question": q,
            "original_preserved": result.original == q,
            "requirement_count": len(reqs),
            "requirements": reqs,
        })
        print(f"[{i:02d}/{len(cases)}] {q}")
        for r in reqs:
            print(f"  {r['id']} {r['kind']}: {r['description']}")

    out = {
        "version": "0.5.9g",
        "purpose": "Convert deterministic request facets into independently checkable evidence obligations.",
        "cases": len(rows),
        "original_preserved_count": sum(x["original_preserved"] for x in rows),
        "total_requirements": sum(x["requirement_count"] for x in rows),
        "min_requirements": min(x["requirement_count"] for x in rows),
        "max_requirements": max(x["requirement_count"] for x in rows),
        "rows": rows,
    }
    path = Path("evaluation-results/evidence-requirements-v059g.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
