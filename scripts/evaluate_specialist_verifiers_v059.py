import json
from pathlib import Path

from buyerjourney.specialist_verifier_v059 import EvidenceSpan, SpecialistVerifier, TransformersNLI


CASES = [
    ("The approved material publishes MDR from £900 per month.", "MDR is available from £900 per month.", "SUPPORTED"),
    ("The approved material publishes MDR from £900 per month.", "All MDR customers pay exactly £900 per month.", "UNSUPPORTED"),
    ("Full incident response is described as included.", "Incident response is included.", "SUPPORTED"),
    ("Full incident response is described as included.", "Incident response is unlimited.", "UNSUPPORTED"),
    ("MDR can integrate with existing Microsoft security tooling.", "Existing Microsoft security tooling can be retained.", "SUPPORTED"),
    ("MDR can integrate with existing Microsoft security tooling.", "Deployment requires absolutely no changes to the environment.", "UNSUPPORTED"),
    ("Monitoring can begin within 5 to 10 days.", "Monitoring can begin within 5 to 10 days.", "SUPPORTED"),
    ("Monitoring can begin within 5 to 10 days.", "Monitoring always begins within 5 days.", "UNSUPPORTED"),
    ("MDR provides 24/7 human investigation and response.", "The service includes human investigation and response.", "SUPPORTED"),
    ("MDR provides 24/7 human investigation and response.", "MDR guarantees the customer will never be breached.", "UNSUPPORTED"),
]


def make_span(text, i):
    return EvidenceSpan(f"case-{i}", text, 0, len(text), text)


def main():
    nli=TransformersNLI()
    verifier=SpecialistVerifier(nli)
    rows=[]
    correct=0
    false_supported=0
    overrides=0
    for i,(premise,hypothesis,expected) in enumerate(CASES,1):
        r=verifier.verify(make_span(premise,i),hypothesis)
        correct += r.verdict == expected
        false_supported += expected != "SUPPORTED" and r.verdict == "SUPPORTED"
        if r.nli_verdict == "ENTAILMENT" and r.verdict != "SUPPORTED":
            overrides += 1
        rows.append({
            "premise":premise,
            "hypothesis":hypothesis,
            "expected":expected,
            "nli_verdict":r.nli_verdict,
            "nli_confidence":round(r.nli_confidence,4),
            "provenance_check":r.provenance_check,
            "qualifier_check":r.qualifier_check,
            "numeric_check":r.numeric_check,
            "combined_verdict":r.verdict,
        })
    out={
        "version":"0.5.9",
        "nli_model":nli.model_name,
        "cases":len(rows),
        "combined_accuracy":round(correct/len(rows),4),
        "false_supported":false_supported,
        "deterministic_overrides_of_entailment":overrides,
        "rows":rows,
    }
    path=Path("evaluation-results/specialist-verifiers-v059.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
