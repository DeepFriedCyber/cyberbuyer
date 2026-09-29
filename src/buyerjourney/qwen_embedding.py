from .decision import Decision
EXAMPLES={
"TRIAL_POC":["Can we trial the service?","Can we test this before committing?","Do you offer a proof of concept?","Could we evaluate it for a month first?"],
"PRICING":["How much does this cost?","What is included in the price?","How does pricing scale?"],
"IMPLEMENTATION":["How long does implementation take?","How quickly can you deploy?","What does onboarding involve?"],
"DOWNTIME":["Will deployment cause downtime?","Will this disrupt our users?","Will there be an outage during setup?"],
"MSP":["Does this replace our MSP?","We already use an IT provider. Where do you fit?","Would we still need our MSP?"],
"INCIDENT":["What happens if we are attacked overnight?","Who responds to a breach at 2am?","What happens after an incident is detected?"],
"CONTRACT":["Can we cancel?","What contract commitment is required?","Are we locked into a long contract?"],
"INSURANCE":["Does this help with cyber insurance?","Will our insurer recognise the service?"],
"OTHER":["What is MDR?","Do you support Microsoft 365?","What is MDR versus EDR?","Can I keep researching without a sales call?"],
}
class QwenEmbeddingEngine:
 name="qwen3-embedding-0.6b"
 def __init__(self,model_name="Qwen/Qwen3-Embedding-0.6B",min_similarity=0.0):
  try: from sentence_transformers import SentenceTransformer
  except ImportError as e: raise RuntimeError("Install optional qwen-embed dependencies") from e
  self.model=SentenceTransformer(model_name);self.min_similarity=min_similarity
  self.labels=[];texts=[]
  for label,examples in EXAMPLES.items():
   for x in examples:self.labels.append(label);texts.append(x)
  self.example_embeddings=self.model.encode(texts,normalize_embeddings=True)
 def decide(self,text,context=None):
  q=self.model.encode([text],normalize_embeddings=True)
  sims=self.model.similarity(q,self.example_embeddings)[0]
  idx=int(sims.argmax());score=float(sims[idx]);theme=self.labels[idx]
  if score<self.min_similarity:theme="OTHER"
  commercial=theme in {"TRIAL_POC","PRICING","CONTRACT"}
  return Decision(theme.replace("_"," ").title(),"commercial" if commercial else "research",
   "evaluating" if commercial else "researching",theme,("KEEP_EXPLORING",),max(0,min(1,score)),self.name)
