import json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"evaluation-results/jina-reranking-comparison.json"
if not p.exists(): raise SystemExit("Run scripts/compare_reranking.py first.")
d=json.loads(p.read_text(encoding="utf-8"))
groups={}
for r in d["rows"]:
    key=r["expected"]
    groups.setdefault(key,[]).append(r["jina_top_score"])
print(json.dumps({k:{"n":len(v),"mean":round(statistics.mean(v),4),
 "median":round(statistics.median(v),4),"min":round(min(v),4),"max":round(max(v),4)}
 for k,v in groups.items()},indent=2))
