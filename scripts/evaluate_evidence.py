import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/"src"))
from buyerjourney.rag import ApprovedCorpusRetriever,EvidenceGroundedService
corpus=json.loads((root/"data/corpus.json").read_text(encoding="utf-8"))
cases=json.loads((root/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
svc=EvidenceGroundedService(ApprovedCorpusRetriever(corpus))
rows=[]
for c in cases:
    result=svc.answer(c["q"])
    rows.append({"question":c["q"],"expected":c["expected"],"actual":result["state"],
                 "top_source":result["evidence"][0]["title"] if result["evidence"] else None})
print(json.dumps({"cases":len(cases),"rows":rows},indent=2))
