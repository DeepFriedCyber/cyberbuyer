import re
from collections import Counter
TOKEN=re.compile(r"[a-zA-Z0-9£]+")
STOP={"the","a","an","is","are","to","of","and","or","we","our","i","you","it","in","on","for","do","does","with","what","how","why","can","this","there"}
def toks(s): return [x.lower() for x in TOKEN.findall(s) if x.lower() not in STOP and len(x)>1]
class Retriever:
 def __init__(self,chunks): self.chunks=chunks
 def search(self,q):
  qt=Counter(toks(q)); out=[]
  for c in self.chunks:
   dt=Counter(toks(c["terms"])); score=sum(min(dt[t],3)*n for t,n in qt.items() if t in dt)
   if score: out.append((score,c))
  return sorted(out,key=lambda x:x[0],reverse=True)
