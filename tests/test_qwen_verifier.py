import numpy as np
from types import SimpleNamespace
from buyerjourney.evidence import Evidence
from buyerjourney.qwen_verifier import QwenEvidenceVerifier
class Batch(dict):
 @property
 def input_ids(self):return np.array([[1,2]])
 def to(self,d):return self
class Tok:
 def apply_chat_template(self,*a,**k):return "prompt"
 def __call__(self,*a,**k):return Batch(input_ids=np.array([[1,2]]))
 def decode(self,*a,**k):return '{"verdict":"SUPPORTED","supported_claims":["MDR costs X"],"unsupported_claims":[],"evidence_ids":["p"]}'
class Model:
 device="cpu"
 def generate(self,**k):return np.array([[1,2,3]])
def test_qwen_verifier_parses_and_validates():
 v=QwenEvidenceVerifier(tokenizer=Tok(),model=Model()).verify("cost?",[Evidence("p","Pricing","u","MDR costs X",.8)])
 assert v.verdict.value=="SUPPORTED" and v.evidence_ids==["p"]
