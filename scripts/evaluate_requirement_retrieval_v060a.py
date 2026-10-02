"""v0.6.0a requirement-aware retrieval benchmark.

Qwen embedding retrieval + Jina reranking are used only to discover/rank candidate
source evidence independently for each normalized requirement. No support verdict is
produced in this experiment.
"""
import json, sys, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.jina_reranker import JinaReranker
from buyerjourney.requirement_retrieval_v060a import RequirementAwareRetriever


def main():
    corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"))
    cases=json.loads((ROOT/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
    print("Loading Qwen embedding retriever...",flush=True)
    qwen=QwenEmbeddingRetriever(corpus)
    print("Loading Jina reranker...",flush=True)
    jina=JinaReranker()
    service=RequirementAwareRetriever(qwen,jina,candidate_k=6,top_k=3)
    rows=[];total_targets=0;lat=[]

    for i,c in enumerate(cases,1):
        q=c["q"]
        print(f"[{i:02d}/{len(cases)}] {q}",flush=True)
        t=time.perf_counter();result=service.retrieve(q);lat.append((time.perf_counter()-t)*1000)
        retrieved=[]
        for target,row in zip(result.targets,result.retrieved):
            total_targets+=1
            candidates=[{"source_id":e.source_id,"score":round(float(e.score),4),"title":e.title} for e in row.evidence]
            retrieved.append({
                "requirement_id":target.requirement_id,
                "kind":target.kind,
                "canonical_terms":target.canonical_terms,
                "evidence_terms":target.evidence_terms,
                "constraints":target.constraints,
                "query":row.query,
                "candidates":candidates,
            })
            ids=[x["source_id"] for x in candidates]
            print(f"  {target.requirement_id} {target.kind}: {ids}",flush=True)
        rows.append({"question":q,"expected":c.get("expected"),"expected_evidence_ids":c.get("expected_evidence_ids",[]),"targets":retrieved})

    out={
        "version":"0.6.0a",
        "purpose":"Requirement-aware candidate retrieval. Retrieval/reranking does not decide support.",
        "cases":len(rows),
        "total_targets":total_targets,
        "mean_question_retrieval_ms":round(sum(lat)/max(1,len(lat)),1),
        "rows":rows,
    }
    path=ROOT/"evaluation-results/requirement-retrieval-v060a.json";path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps({k:v for k,v in out.items() if k!="rows"},indent=2,ensure_ascii=False))


if __name__=="__main__":main()
