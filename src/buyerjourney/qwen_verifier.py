import json,re
from .verifier import Verification,Verdict,validate_verification

SYSTEM="""You are an evidence verifier, not a salesperson and not an answer generator.
Decide whether the supplied COMPANY EVIDENCE substantiates the buyer's question/proposition.
Do not use outside knowledge. Relevance is not support. Do not infer guarantees, inclusions,
commercial terms, contract terms, outcomes, or promises that are not explicitly supported.
Return JSON only:
{"verdict":"SUPPORTED|PARTIAL|UNSUPPORTED",
 "supported_claims":["..."],
 "unsupported_claims":["..."],
 "evidence_ids":["..."]}
SUPPORTED means the material substantiates the factual answer requested.
PARTIAL means a material part is supported and a material part is not.
UNSUPPORTED means the requested proposition/answer is not substantiated.
Evidence IDs must be chosen only from those supplied."""

class QwenEvidenceVerifier:
    def __init__(self,model_name="Qwen/Qwen3-1.7B",tokenizer=None,model=None):
        if tokenizer is None or model is None:
            try:
                from transformers import AutoModelForCausalLM,AutoTokenizer
            except ImportError as e: raise RuntimeError('Install with: pip install -e ".[qwen-chat]"') from e
            tokenizer=AutoTokenizer.from_pretrained(model_name)
            model=AutoModelForCausalLM.from_pretrained(model_name,device_map="auto",torch_dtype="auto")
        self.tok=tokenizer;self.model=model
    def verify(self,question,evidence):
        packed="\n\n".join(f"EVIDENCE_ID={e.source_id}\nTITLE={e.title}\nTEXT={e.text}" for e in evidence)
        user=f"BUYER QUESTION:\n{question}\n\nCOMPANY EVIDENCE:\n{packed}"
        prompt=self.tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":user}],
          tokenize=False,add_generation_prompt=True,enable_thinking=False)
        batch=self.tok([prompt],return_tensors="pt"); n=batch.input_ids.shape[1]
        inputs=batch.to(self.model.device) if hasattr(batch,"to") else batch
        out=self.model.generate(**inputs,max_new_tokens=300,do_sample=False)
        raw=self.tok.decode(out[0][n:],skip_special_tokens=True)
        a,b=raw.find("{"),raw.rfind("}")
        if a<0 or b<a: raise ValueError("Verifier returned invalid JSON")
        d=json.loads(raw[a:b+1])
        try: verdict=Verdict(str(d["verdict"]).upper())
        except Exception as e: raise ValueError("Verifier returned invalid verdict") from e
        v=Verification(verdict,
          [str(x) for x in d.get("supported_claims",[])],
          [str(x) for x in d.get("unsupported_claims",[])],
          [str(x) for x in d.get("evidence_ids",[])],d)
        return validate_verification(v,evidence)
