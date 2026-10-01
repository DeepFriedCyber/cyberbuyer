import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.qwen_claims import QwenClaimDecomposer,QwenClaimEntailer
from buyerjourney.claim_entailment import ClaimLevelEvidenceService

corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"))
cases=json.loads((ROOT/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
retriever=QwenEmbeddingRetriever(corpus)
decomposer=QwenClaimDecomposer()
entailer=QwenClaimEntailer(tokenizer=decomposer.tok,model=decomposer.model)
svc=ClaimLevelEvidenceService(decomposer,entailer)
rows=[]; false_supported=0;supported_accept=0;unsupported_reject=0
n_sup=sum(c["expected"]=="SUPPORTED" for c in cases);n_uns=len(cases)-n_sup
for c in cases:
    evidence=retriever.search(c["q"],3)
    r=svc.assess(c["q"],evidence)
    if c["expected"]=="SUPPORTED": supported_accept+=int(r.state=="SUPPORTED")
    else:
        unsupported_reject+=int(r.state!="SUPPORTED")
        false_supported+=int(r.state=="SUPPORTED")
    rows.append({"question":c["q"],"expected":c["expected"],"actual":r.state,
      "claims":[{"claim":x.claim,"verdict":x.verdict.value,"evidence_ids":x.evidence_ids,
                 "evidence_quotes":x.evidence_quotes} for x in r.claims]})
report={"cases":len(cases),"supported_accept_rate":round(supported_accept/max(1,n_sup),3),
 "unsupported_reject_rate":round(unsupported_reject/max(1,n_uns),3),
 "false_supported":false_supported,"partial_count":sum(x["actual"]=="PARTIAL" for x in rows),"rows":rows}
print(json.dumps(report,indent=2,ensure_ascii=False))
out=ROOT/"evaluation-results";out.mkdir(exist_ok=True)
(out/"claim-entailment.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
