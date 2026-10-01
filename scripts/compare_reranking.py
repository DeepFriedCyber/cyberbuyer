import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.jina_reranker import JinaReranker

corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"))
cases=json.loads((ROOT/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
qwen=QwenEmbeddingRetriever(corpus)
jina=JinaReranker()

def hit(ids,gold,k):
    return bool(gold) and bool(set(ids[:k]) & set(gold))

rows=[]; stats={"qwen_top1":0,"qwen_top3":0,"jina_top1":0,"jina_top3":0}
eligible=0; lat=[]
for c in cases:
    gold=c.get("expected_evidence_ids",[])
    candidates=qwen.search(c["q"],6)
    t=time.perf_counter(); reranked=jina.rerank(c["q"],candidates); lat.append((time.perf_counter()-t)*1000)
    qids=[e.source_id for e in candidates]; jids=[e.source_id for e in reranked]
    if gold:
        eligible+=1
        for name,ids in (("qwen",qids),("jina",jids)):
            stats[f"{name}_top1"]+=int(hit(ids,gold,1))
            stats[f"{name}_top3"]+=int(hit(ids,gold,3))
    rows.append({"question":c["q"],"expected":c["expected"],"expected_evidence_ids":gold,
      "qwen_top3":qids[:3],"jina_top3":jids[:3],
      "qwen_top_score":round(candidates[0].score,4) if candidates else None,
      "jina_top_score":round(reranked[0].score,4) if reranked else None})
report={"cases":len(cases),"retrieval_gold_cases":eligible,
 "qwen_top1_recall":round(stats["qwen_top1"]/max(1,eligible),3),
 "qwen_top3_recall":round(stats["qwen_top3"]/max(1,eligible),3),
 "qwen_plus_jina_top1_recall":round(stats["jina_top1"]/max(1,eligible),3),
 "qwen_plus_jina_top3_recall":round(stats["jina_top3"]/max(1,eligible),3),
 "mean_jina_rerank_ms":round(sum(lat)/max(1,len(lat)),1),"rows":rows}
print(json.dumps(report,indent=2,ensure_ascii=False))
out=ROOT/"evaluation-results";out.mkdir(exist_ok=True)
(out/"jina-reranking-comparison.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
