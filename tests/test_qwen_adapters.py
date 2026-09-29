import sys,types,numpy as np
def test_embedding_adapter_without_download(monkeypatch):
 class Fake:
  def __init__(self,*a,**k):pass
  def encode(self,texts,normalize_embeddings=True):return np.array([[1.,0.] for _ in texts])
  def similarity(self,a,b):
   x=np.zeros((1,len(b)));x[0,0]=.9;return x
 monkeypatch.setitem(sys.modules,"sentence_transformers",types.SimpleNamespace(SentenceTransformer=Fake))
 from buyerjourney.qwen_embedding import QwenEmbeddingEngine
 assert QwenEmbeddingEngine().decide("test").gap_theme=="TRIAL_POC"
def test_chat_adapter_json_and_no_thinking(monkeypatch):
 class Tensor:
  shape=(1,2)
  def __getitem__(self,k):return self
 class Batch:
  def __init__(self):self.input_ids=Tensor()
  def to(self,*a,**k):return {"input_ids":self.input_ids}
 class Tok:
  def __init__(self):self.no_think=False
  @classmethod
  def from_pretrained(cls,*a,**k):return cls()
  def apply_chat_template(self,*a,**k):self.no_think=k.get("enable_thinking") is False;return "p"
  def __call__(self,*a,**k):return Batch()
  def decode(self,*a,**k):return '{"gap_theme":"MSP","intent":"research","stage":"researching"}'
 class Model:
  device="cpu"
  @classmethod
  def from_pretrained(cls,*a,**k):return cls()
  def generate(self,**k):return [Tensor()]
 monkeypatch.setitem(sys.modules,"transformers",types.SimpleNamespace(AutoModelForCausalLM=Model,AutoTokenizer=Tok))
 from buyerjourney.qwen_chat import QwenChatEngine
 e=QwenChatEngine();d=e.decide("We use an MSP")
 assert e.tok.no_think and d.gap_theme=="MSP"
