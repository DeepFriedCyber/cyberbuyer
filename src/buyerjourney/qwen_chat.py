import json
from .decision import Decision
THEMES=["TRIAL_POC","PRICING","IMPLEMENTATION","DOWNTIME","MSP","INCIDENT","CONTRACT","INSURANCE","OTHER"]
class QwenChatEngine:
 name="qwen3-1.7b"
 def __init__(self,model_name="Qwen/Qwen3-1.7B"):
  try: from transformers import AutoModelForCausalLM,AutoTokenizer
  except ImportError as e: raise RuntimeError("Install optional qwen-chat dependencies") from e
  self.tok=AutoTokenizer.from_pretrained(model_name)
  self.model=AutoModelForCausalLM.from_pretrained(model_name,device_map="auto",torch_dtype="auto")
 def decide(self,text,context=None):
  system="Classify cybersecurity buyer questions. Return JSON only: gap_theme, intent, stage. gap_theme must be one of "+",".join(THEMES)+". intent: commercial or research. stage: evaluating or researching."
  prompt=self.tok.apply_chat_template([{"role":"system","content":system},{"role":"user","content":text}],
   tokenize=False,add_generation_prompt=True,enable_thinking=False)
  batch=self.tok([prompt],return_tensors="pt")
  input_len=batch.input_ids.shape[1]
  inputs=batch.to(self.model.device)
  out=self.model.generate(**inputs,max_new_tokens=80,do_sample=False)
  raw=self.tok.decode(out[0][input_len:],skip_special_tokens=True).strip()
  start,end=raw.find("{"),raw.rfind("}")
  if start<0 or end<start:raise ValueError("Qwen returned no JSON object")
  d=json.loads(raw[start:end+1]);theme=d["gap_theme"];intent=d["intent"];stage=d["stage"]
  if theme not in THEMES or intent not in {"commercial","research"} or stage not in {"evaluating","researching"}:raise ValueError("Invalid Qwen classification")
  return Decision(theme.replace("_"," ").title(),intent,stage,theme,("KEEP_EXPLORING",),0.5,self.name)
