import json,time
from dataclasses import dataclass,asdict
from pathlib import Path
@dataclass
class EvalRow:
 id:str; question:str; expected_theme:str; actual_theme:str; expected_intent:str; actual_intent:str; expected_stage:str; actual_stage:str; theme_ok:bool; intent_ok:bool; stage_ok:bool; confidence:float; engine:str; latency_ms:float
def load_benchmark(path): return json.loads(Path(path).read_text(encoding="utf-8"))["cases"]
def evaluate(engine,cases):
 rows=[]
 for c in cases:
  t=time.perf_counter(); d=engine.decide(c["question"],{}); ms=(time.perf_counter()-t)*1000; e=c["expected"]
  rows.append(EvalRow(c["id"],c["question"],e["gap_theme"],d.gap_theme,e["intent"],d.intent,e["stage"],d.stage,e["gap_theme"]==d.gap_theme,e["intent"]==d.intent,e["stage"]==d.stage,d.confidence,d.engine,round(ms,3)))
 return rows
def summary(rows):
 n=len(rows) or 1
 return {"cases":len(rows),"theme_accuracy":round(sum(r.theme_ok for r in rows)/n,3),"intent_accuracy":round(sum(r.intent_ok for r in rows)/n,3),"stage_accuracy":round(sum(r.stage_ok for r in rows)/n,3)}
