"""v0.6.0b: retrieval -> strict per-requirement verification -> deterministic coverage."""
import json, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.jina_reranker import JinaReranker
from buyerjourney.requirement_retrieval_v060a import RequirementAwareRetriever
from buyerjourney.requirement_coverage_v060b import RequirementCoverageVerifier
from buyerjourney.specialist_verifier_v059 import TransformersNLI


def main():
    corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"))
    cases=json.loads((ROOT/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
    print("Loading Qwen embedding retriever...",flush=True);qwen=QwenEmbeddingRetriever(corpus)
    print("Loading Jina reranker...",flush=True);jina=JinaReranker()
    print("Loading DeBERTa NLI verifier...",flush=True);nli=TransformersNLI()
    retrieval=RequirementAwareRetriever(qwen,jina,candidate_k=6,top_k=3)
    verifier=RequirementCoverageVerifier(nli)
    rows=[];correct=0;false_supported=0;lat=[]

    for i,c in enumerate(cases,1):
        q=c["q"];expected=c.get("expected",c.get("expected_state"))
        print(f"[{i:02d}/{len(cases)}] {q}",flush=True)
        started=time.perf_counter();retrieved=retrieval.retrieve(q);coverage=verifier.verify(retrieved);lat.append((time.perf_counter()-started)*1000)
        ok=coverage.state==expected;correct+=int(ok);false_supported+=int(expected!="SUPPORTED" and coverage.state=="SUPPORTED")
        reqs=[]
        for rc in coverage.requirements:
            reqs.append({"requirement_id":rc.requirement_id,"hypothesis":rc.hypothesis,"state":rc.state,"candidates":[vars(x) for x in rc.candidates]})
            print(f"  {rc.requirement_id}: {rc.state} | {rc.hypothesis}",flush=True)
        print(f"  => expected={expected} actual={coverage.state} {'OK' if ok else 'MISS'}",flush=True)
        rows.append({"question":q,"expected":expected,"actual":coverage.state,"correct":ok,"requirements":reqs})

    out={
        "version":"0.6.0b",
        "purpose":"Strict per-requirement evidence verification after requirement-aware retrieval.",
        "cases":len(rows),"correct":correct,"accuracy":round(correct/max(1,len(rows)),4),
        "false_supported":false_supported,"mean_end_to_end_ms":round(sum(lat)/max(1,len(lat)),1),"rows":rows,
    }
    path=ROOT/"evaluation-results/requirement-coverage-v060b.json";path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print("\nSUMMARY");print(json.dumps({k:v for k,v in out.items() if k!="rows"},indent=2))


if __name__=="__main__":main()
