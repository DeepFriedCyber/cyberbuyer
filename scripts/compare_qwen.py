import argparse,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/"src"))
from buyerjourney.decision import RulesEngine
from buyerjourney.evaluation import load_benchmark,evaluate,summary
p=argparse.ArgumentParser();p.add_argument("--engine",choices=["rules","embedding","qwen17"],default="rules");a=p.parse_args()
cases=load_benchmark(root/"data"/"decision_benchmark.json");rules=evaluate(RulesEngine(),cases);report={"rules":summary(rules)}
if a.engine=="embedding":
 from buyerjourney.qwen_embedding import QwenEmbeddingEngine
 report["qwen3_embedding_0.6b"]=summary(evaluate(QwenEmbeddingEngine(),cases))
elif a.engine=="qwen17":
 from buyerjourney.qwen_chat import QwenChatEngine
 report["qwen3_1.7b"]=summary(evaluate(QwenChatEngine(),cases))
if a.engine!="rules":
 report["theme_delta_vs_rules"]=round(list(report.values())[-1]["theme_accuracy"]-report["rules"]["theme_accuracy"],3)
out=root/"evaluation-results";out.mkdir(exist_ok=True)
(out/f"qwen-{a.engine}-comparison.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
