import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
from buyerjourney.qwen_retriever import QwenEmbeddingRetriever
from buyerjourney.qwen_evidence_first import QwenEvidenceFirstExtractor
from buyerjourney.qwen_claims import QwenClaimEntailer
from buyerjourney.qwen_relevance import QwenAnswerRelevanceClassifier
from buyerjourney.qwen_question_coverage import QwenRequestedInformationDecomposer
from buyerjourney.answer_relevance import AnswerRelevanceGate
from buyerjourney.evidence_coverage_v058 import EvidenceCoverageService
corpus=json.loads((ROOT/"data/corpus.json").read_text(encoding="utf-8"));cases=json.loads((ROOT/"data/evidence_benchmark_v058.json").read_text(encoding="utf-8"))
retriever=QwenEmbeddingRetriever(corpus);decomposer=QwenRequestedInformationDecomposer();extractor=QwenEvidenceFirstExtractor(tokenizer=decomposer.tok,model=decomposer.model);entailer=QwenClaimEntailer(tokenizer=decomposer.tok,model=decomposer.model);classifier=QwenAnswerRelevanceClassifier(tokenizer=decomposer.tok,model=decomposer.model);svc=EvidenceCoverageService(decomposer,extractor,entailer,AnswerRelevanceGate(classifier))
rows=[];correct=false_supported=0
for c in cases:
 e=retriever.search(c["question"],3);r=svc.assess(c["question"],e);correct+=r["state"]==c["expected_state"];false_supported+=c["expected_state"]!="SUPPORTED" and r["state"]=="SUPPORTED"
 rows.append({"question":c["question"],"expected":c["expected_state"],"actual":r["state"],"components":r["components"],"unanswered_components":r["unanswered_components"]})
report={"cases":len(cases),"three_state_accuracy":round(correct/max(1,len(cases)),3),"false_supported":false_supported,"supported_count":sum(x["actual"]=="SUPPORTED" for x in rows),"partial_count":sum(x["actual"]=="PARTIAL" for x in rows),"unsupported_count":sum(x["actual"]=="UNSUPPORTED" for x in rows),"rows":rows}
print(json.dumps(report,indent=2,ensure_ascii=False));out=ROOT/"evaluation-results";out.mkdir(exist_ok=True);(out/"evidence-coverage-v058.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
