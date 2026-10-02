"""v0.5.9f deterministic request-facet benchmark.

No LLM, retrieval, NLI or answer generation. The buyer's original wording remains
immutable; this experiment only extracts structured facets alongside it.
"""
import json
from pathlib import Path

from buyerjourney.request_facets_v059f import DeterministicRequestFacetExtractor


def main():
    cases = json.loads(Path("data/evidence_benchmark.json").read_text(encoding="utf-8"))
    extractor = DeterministicRequestFacetExtractor()
    rows = []

    for i, case in enumerate(cases, 1):
        q = case["q"]
        r = extractor.extract(q)
        row = {
            "question": q,
            "original_preserved": r.original == q,
            "topics": r.topics,
            "qualifiers": r.qualifiers,
            "amounts": r.amounts,
            "durations": r.durations,
            "products": r.products,
            "relations": r.relations,
        }
        rows.append(row)
        print(f"[{i:02d}/{len(cases)}] {q}")
        print(f"  topics={r.topics} qualifiers={r.qualifiers} amounts={r.amounts} durations={r.durations} products={r.products} relations={r.relations}")

    out = {
        "version": "0.5.9f",
        "purpose": "Deterministic request-facet extraction without rewriting buyer language.",
        "cases": len(rows),
        "original_preserved_count": sum(r["original_preserved"] for r in rows),
        "questions_with_topics": sum(bool(r["topics"]) for r in rows),
        "questions_with_qualifiers": sum(bool(r["qualifiers"]) for r in rows),
        "questions_with_amounts": sum(bool(r["amounts"]) for r in rows),
        "questions_with_durations": sum(bool(r["durations"]) for r in rows),
        "questions_with_products": sum(bool(r["products"]) for r in rows),
        "questions_with_relations": sum(bool(r["relations"]) for r in rows),
        "rows": rows,
    }
    path = Path("evaluation-results/request-facets-v059f.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps({k:v for k,v in out.items() if k != "rows"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
