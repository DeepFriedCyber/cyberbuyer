"""v0.5.9h deterministic verification-target normalization benchmark."""
import json
from pathlib import Path

from buyerjourney.requirement_normalization_v059h import DeterministicRequirementNormalizer


def main():
    cases = json.loads(Path("data/evidence_benchmark.json").read_text(encoding="utf-8"))
    normalizer = DeterministicRequirementNormalizer()
    rows = []
    leaked_internal = []

    internal_tokens = {
        "incident_response", "security_tools", "service_scope", "keep_existing",
        "human_investigation", "breach_prevention",
    }

    for i, case in enumerate(cases, 1):
        q = case["q"]
        result = normalizer.normalize(q)
        targets = []
        for t in result.targets:
            bad = sorted(internal_tokens.intersection(t.evidence_terms))
            if bad:
                leaked_internal.extend(bad)
            targets.append({
                "requirement_id": t.requirement_id,
                "kind": t.kind,
                "canonical_terms": t.canonical_terms,
                "evidence_terms": t.evidence_terms,
                "constraints": t.constraints,
                "description": t.description,
            })
        rows.append({
            "question": q,
            "original_preserved": result.original == q,
            "target_count": len(targets),
            "targets": targets,
        })
        print(f"[{i:02d}/{len(cases)}] {q}")
        for t in targets:
            print(f"  {t['requirement_id']} {t['kind']} evidence={t['evidence_terms']} constraints={t['constraints']}")

    out = {
        "version": "0.5.9h",
        "purpose": "Normalize internal evidence requirements into source-language verification targets while preserving phrase-level constraints.",
        "cases": len(rows),
        "original_preserved_count": sum(r["original_preserved"] for r in rows),
        "total_targets": sum(r["target_count"] for r in rows),
        "internal_label_leaks": sorted(set(leaked_internal)),
        "rows": rows,
    }
    path = Path("evaluation-results/requirement-normalization-v059h.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
