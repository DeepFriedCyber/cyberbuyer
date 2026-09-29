import argparse,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/"src"))
from buyerjourney.rag import ApprovedCorpusRetriever,EvidenceGroundedService
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever

p=argparse.ArgumentParser();p.add_argument("--engine",choices=["lexical","qwen"],required=True);a=p.parse_args()
corpus=json.loads((root/"data/corpus.json").read_text(encoding="utf-8"))
cases=json.loads((root/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
retriever=ApprovedCorpusRetriever(corpus) if a.engine=="lexical" else QwenEmbeddingRetriever(corpus)
svc=EvidenceGroundedService(retriever)
rows=[];false_supported=0;supported_answered=0
for c in cases:
    raw=retriever.search(c["q"]); result=svc.answer(c["q"])
    is_answer=result["state"] in {"DIRECT","SYNTHESISED"}
    if c["expected"]=="UNSUPPORTED" and is_answer:false_supported+=1
    if c["expected"]=="SUPPORTED" and is_answer:supported_answered+=1
    rows.append({"question":c["q"],"expected":c["expected"],"actual":result["state"],
      "top_candidate":raw[0].title if raw else None,
      "similarity":round(raw[0].score,4) if raw else None})
supported=sum(x["expected"]=="SUPPORTED" for x in cases)
report={"engine":a.engine,"cases":len(cases),
 "supported_answer_rate":round(supported_answered/max(1,supported),3),
 "false_supported":false_supported,"rows":rows}
print(json.dumps(report,indent=2))
out=root/"evaluation-results";out.mkdir(exist_ok=True)
(out/f"retrieval-{a.engine}.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
