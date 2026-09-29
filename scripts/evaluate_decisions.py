import csv,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"src"))
from buyerjourney.decision import RulesEngine
from buyerjourney.evaluation import load_benchmark,evaluate,summary
rows=evaluate(RulesEngine(),load_benchmark(root/"data"/"decision_benchmark.json"))
out=root/"evaluation-results"; out.mkdir(exist_ok=True)
(out/"rules-summary.json").write_text(json.dumps(summary(rows),indent=2),encoding="utf-8")
with (out/"rules-results.csv").open("w",newline="",encoding="utf-8") as f:
 w=csv.DictWriter(f,fieldnames=rows[0].__dict__.keys()); w.writeheader()
 for r in rows:w.writerow(r.__dict__)
print(json.dumps(summary(rows),indent=2))
