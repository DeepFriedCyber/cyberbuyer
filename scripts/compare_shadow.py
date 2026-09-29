import argparse,csv,json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root/"src"))
from buyerjourney.decision import RulesEngine
from buyerjourney.evaluation import load_benchmark,evaluate,summary

p=argparse.ArgumentParser()
p.add_argument("--engine",choices=["rules","laya"],default="rules")
p.add_argument("--checkpoint",default="convaiinnovations/laya")
p.add_argument("--subfolder",default=None)
args=p.parse_args()
cases=load_benchmark(root/"data"/"decision_benchmark.json")
rules=evaluate(RulesEngine(),cases)
report={"rules":summary(rules)}
out=root/"evaluation-results";out.mkdir(exist_ok=True)

if args.engine=="laya":
 from buyerjourney.laya_adapter import LayaShadowEngine
 shadow=evaluate(LayaShadowEngine(args.checkpoint,args.subfolder),cases)
 report["laya"]=summary(shadow)
 disagreements=[]
 for r,s in zip(rules,shadow):
  if (r.actual_theme,r.actual_intent,r.actual_stage)!=(s.actual_theme,s.actual_intent,s.actual_stage):
   disagreements.append({"id":r.id,"question":r.question,"expected":r.expected_theme,
    "rules_theme":r.actual_theme,"laya_theme":s.actual_theme,
    "rules_confidence":r.confidence,"laya_confidence":s.confidence})
 with (out/"shadow-disagreements.csv").open("w",newline="",encoding="utf-8") as f:
  fields=["id","question","expected","rules_theme","laya_theme","rules_confidence","laya_confidence"]
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(disagreements)
 report["disagreements"]=len(disagreements)

(out/"shadow-comparison.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
