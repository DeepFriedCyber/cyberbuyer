import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.qwen_verifier import QwenEvidenceVerifier
from buyerjourney.verified_rag import VerifiedRAGService

corpus=json.loads((root/"data/corpus.json").read_text(encoding="utf-8"))
cases=json.loads((root/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
retriever=QwenEmbeddingRetriever(corpus); verifier=QwenEvidenceVerifier(); svc=VerifiedRAGService(retriever,verifier)
rows=[];supported_ok=false_supported=unsupported_ok=0
for c in cases:
    raw=retriever.search(c["q"],3); result=svc.assess(c["q"]); state=result["state"]
    if c["expected"]=="SUPPORTED" and state in {"SUPPORTED","PARTIAL"}: supported_ok+=1
    if c["expected"]=="UNSUPPORTED" and state=="SUPPORTED": false_supported+=1
    if c["expected"]=="UNSUPPORTED" and state in {"UNSUPPORTED","PARTIAL"}: unsupported_ok+=1
    rows.append({"question":c["q"],"expected":c["expected"],"verdict":state,
      "top_candidate":raw[0].title if raw else None,"similarity":round(raw[0].score,4) if raw else None,
      "supported_claims":result.get("supported_claims",[]),
      "unsupported_claims":result.get("unsupported_claims",[]),
      "evidence_ids":[e["source_id"] for e in result.get("evidence",[])]})
ns=sum(x["expected"]=="SUPPORTED" for x in cases);nu=len(cases)-ns
report={"engine":"qwen3-embedding-0.6b + qwen3-1.7b-verifier","cases":len(cases),
 "supported_accept_rate":round(supported_ok/max(1,ns),3),
 "unsupported_reject_rate":round(unsupported_ok/max(1,nu),3),
 "false_supported":false_supported,"rows":rows}
print(json.dumps(report,indent=2))
out=root/"evaluation-results";out.mkdir(exist_ok=True)
(out/"qwen-verifier.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
