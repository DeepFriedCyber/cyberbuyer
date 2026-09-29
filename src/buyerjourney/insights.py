import json,re
from pathlib import Path
def norm(q): return " ".join(re.sub(r"[^a-z0-9£ ]+"," ",q.lower()).split())
class InsightStore:
 def __init__(self,path):
  self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
  if not self.path.exists(): self.path.write_text("[]",encoding="utf-8")
 def record(self,q,status,topic=None):
  rows=json.loads(self.path.read_text(encoding="utf-8")); rows.append({"question":q,"normalized":norm(q),"status":status,"topic":topic}); self.path.write_text(json.dumps(rows,indent=2),encoding="utf-8")
 def summary(self):
  rows=json.loads(self.path.read_text(encoding="utf-8")); groups={}
  for r in rows:
   g=groups.setdefault(r["normalized"],{"question":r["question"],"count":0,"status":r["status"]}); g["count"]+=1
  gaps=sorted((g for g in groups.values() if g["status"]!="supported"),key=lambda x:x["count"],reverse=True)
  sup=sum(r["status"]=="supported" for r in rows)
  return {"total_questions":len(rows),"supported":sup,"unsupported":len(rows)-sup,"coverage_pct":round(100*sup/len(rows),1) if rows else 0,"gaps":gaps[:25]}
