import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.qwen_evidence_first import QwenEvidenceFirstExtractor
from buyerjourney.qwen_claims import QwenClaimEntailer
from buyerjourney.evidence_first import EvidenceFirstService
corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"));cases=json.loads((ROOT/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
retriever=QwenEmbeddingRetriever(corpus);extractor=QwenEvidenceFirstExtractor();entailer=QwenClaimEntailer(tokenizer=extractor.tok,model=extractor.model);svc=EvidenceFirstService(extractor,entailer)
rows=[];fs=sa=ur=0;ns=sum(c["expected"]=="SUPPORTED" for c in cases);nu=len(cases)-ns
for c in cases:
 e=retriever.search(c["q"],3);r=svc.assess(c["q"],e)
 if c["expected"]=="SUPPORTED":sa+=r["state"]=="SUPPORTED"
 else:ur+=r["state"]!="SUPPORTED";fs+=r["state"]=="SUPPORTED"
 rows.append({"question":c["q"],"expected":c["expected"],"actual":r["state"],"facts":r["facts"],"missing_qualifiers":r.get("missing_qualifiers",[])})
report={"cases":len(cases),"supported_accept_rate":round(sa/max(1,ns),3),"unsupported_reject_rate":round(ur/max(1,nu),3),"false_supported":fs,"partial_count":sum(x["actual"]=="PARTIAL" for x in rows),"rows":rows}
print(json.dumps(report,indent=2,ensure_ascii=False));out=ROOT/"evaluation-results";out.mkdir(exist_ok=True);(out/"evidence-first.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
