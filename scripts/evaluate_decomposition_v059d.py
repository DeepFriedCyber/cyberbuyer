"""v0.5.9d decomposition-only benchmark.

Compares the existing few-shot decomposer with a zero-shot variant on the same
26 buyer questions. No retrieval, proposition generation, NLI, or answer model is
run. The purpose is to isolate prompt contamination and topic preservation.
"""
import json
import re
from pathlib import Path

from buyerjourney.qwen_question_coverage import QwenRequestedInformationDecomposer
from buyerjourney.qwen_question_coverage_v059d import QwenZeroShotRequestedInformationDecomposer


CONTAMINATION_TERMS = {
    "£900": "price_example",
    "published mdr price": "price_example",
    "incident response included": "unlimited_example",
    "included incident response unlimited": "unlimited_example",
}


def load_cases():
    return json.loads(Path("data/evidence_benchmark.json").read_text(encoding="utf-8"))


def serialise(rows):
    return [{"id": x.id, "question": x.question, "material": x.material} for x in rows]


def contamination(question, components):
    source = question.lower()
    rendered = " ".join(x.question for x in components).lower()
    hits = []
    for term, family in CONTAMINATION_TERMS.items():
        if term.lower() in rendered and term.lower() not in source:
            hits.append({"term": term, "family": family})
    return hits


def main():
    few = QwenRequestedInformationDecomposer()
    zero = QwenZeroShotRequestedInformationDecomposer(tokenizer=few.tok, model=few.model)
    rows = []
    few_contaminated = zero_contaminated = 0

    for case in load_cases():
        q = case["q"]
        few_rows = few.decompose(q)
        zero_rows = zero.decompose(q)
        few_hits = contamination(q, few_rows)
        zero_hits = contamination(q, zero_rows)
        few_contaminated += bool(few_hits)
        zero_contaminated += bool(zero_hits)
        rows.append({
            "question": q,
            "few_shot": serialise(few_rows),
            "zero_shot": serialise(zero_rows),
            "few_shot_contamination": few_hits,
            "zero_shot_contamination": zero_hits,
            "same_decomposition": serialise(few_rows) == serialise(zero_rows),
        })

    changed = [r for r in rows if not r["same_decomposition"]]
    out = {
        "version": "0.5.9d",
        "purpose": "Decomposition-only comparison; no retrieval, NLI or answer generation.",
        "cases": len(rows),
        "few_shot_contaminated_cases": few_contaminated,
        "zero_shot_contaminated_cases": zero_contaminated,
        "changed_decomposition_cases": len(changed),
        "changed_cases": changed,
        "rows": rows,
    }
    path = Path("evaluation-results/decomposition-v059d.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
