"""v0.5.9b: run the specialist verifier against the real 26-case evidence benchmark.

This intentionally does not modify the v0.5.8 production path. For each benchmark
question, the expected evidence ids select the approved corpus chunks. The exact
chunk text is preserved as the EvidenceSpan premise; the buyer question is the NLI
hypothesis. Cases with no expected evidence are evaluated with no span and therefore
fail closed as UNSUPPORTED.
"""
import json
from pathlib import Path

from buyerjourney.specialist_verifier_v059 import EvidenceSpan, SpecialistVerifier, TransformersNLI


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def chunk_text(chunk):
    # Keep both approved audience renderings, verbatim, rather than asking a model
    # to paraphrase them before verification.
    return f"{chunk.get('simple','')}\n{chunk.get('technical','')}".strip()


def span_for(chunk):
    text = chunk_text(chunk)
    return EvidenceSpan(chunk["id"], text, 0, len(text), text)


def main():
    benchmark = load_json("data/evidence_benchmark.json")
    corpus = load_json("data/corpus.json")
    chunks = {c["id"]: c for c in corpus["chunks"]}

    nli = TransformersNLI()
    verifier = SpecialistVerifier(nli)
    rows = []
    correct = false_supported = 0

    for case in benchmark:
        question = case["q"]
        expected = case["expected"]
        evidence_ids = case.get("expected_evidence_ids", [])
        checks = []

        for evidence_id in evidence_ids:
            chunk = chunks.get(evidence_id)
            if chunk is None:
                checks.append({"source_id": evidence_id, "error": "missing_corpus_chunk", "combined_verdict": "UNSUPPORTED"})
                continue
            r = verifier.verify(span_for(chunk), question)
            checks.append({
                "source_id": evidence_id,
                "nli_verdict": r.nli_verdict,
                "nli_confidence": round(r.nli_confidence, 4),
                "provenance_check": r.provenance_check,
                "qualifier_check": r.qualifier_check,
                "numeric_check": r.numeric_check,
                "combined_verdict": r.verdict,
            })

        # At least one approved evidence chunk must substantiate the whole question.
        # Empty evidence fails closed.
        actual = "SUPPORTED" if any(x.get("combined_verdict") == "SUPPORTED" for x in checks) else "UNSUPPORTED"
        correct += actual == expected
        false_supported += expected != "SUPPORTED" and actual == "SUPPORTED"
        rows.append({
            "question": question,
            "expected": expected,
            "actual": actual,
            "expected_evidence_ids": evidence_ids,
            "checks": checks,
        })

    mismatches = [r for r in rows if r["actual"] != r["expected"]]
    out = {
        "version": "0.5.9b",
        "nli_model": nli.model_name,
        "cases": len(rows),
        "accuracy": round(correct / len(rows), 4),
        "false_supported": false_supported,
        "supported_count": sum(r["actual"] == "SUPPORTED" for r in rows),
        "unsupported_count": sum(r["actual"] == "UNSUPPORTED" for r in rows),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "rows": rows,
    }
    path = Path("evaluation-results/specialist-full-benchmark-v059.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
