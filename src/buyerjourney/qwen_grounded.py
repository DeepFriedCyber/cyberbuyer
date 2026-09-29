import json
class QwenGroundedGenerator:
 def __init__(self,model_name="Qwen/Qwen3-1.7B"):
  from transformers import AutoModelForCausalLM,AutoTokenizer
  self.tok=AutoTokenizer.from_pretrained(model_name);self.model=AutoModelForCausalLM.from_pretrained(model_name,device_map="auto",torch_dtype="auto")
 def generate(self,q,evidence):
  ev="\n\n".join(f"[{x.source_id}] {x.text}" for x in evidence)
  sys="Answer only from EVIDENCE. Omit unsupported claims. Return JSON with answer and citations (source IDs)."
  p=self.tok.apply_chat_template([{"role":"system","content":sys},{"role":"user","content":f"QUESTION:\n{q}\n\nEVIDENCE:\n{ev}"}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
  b=self.tok([p],return_tensors="pt");n=b.input_ids.shape[1];o=self.model.generate(**b.to(self.model.device),max_new_tokens=250,do_sample=False);raw=self.tok.decode(o[0][n:],skip_special_tokens=True);a,z=raw.find("{"),raw.rfind("}")
  if a<0 or z<a:raise ValueError("Invalid grounded JSON")
  d=json.loads(raw[a:z+1]);valid={x.source_id for x in evidence};c=set(map(str,d.get("citations",[])))
  if not c or not c.issubset(valid):raise ValueError("Citation outside supplied evidence")
  return d["answer"]
