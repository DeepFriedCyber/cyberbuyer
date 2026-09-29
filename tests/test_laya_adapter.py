import sys,types
def test_laya_adapter_maps_typed_decisions(monkeypatch):
 class Agent:
  def predict(self,state,questions):
   return {"answers":{
    "theme":{"choice":"TRIAL_POC","confidence":.91},
    "intent":{"choice":"commercial","confidence":.88},
    "stage":{"choice":"evaluating","confidence":.86}}}
 fake=types.SimpleNamespace(load=lambda *a,**k:Agent())
 monkeypatch.setitem(sys.modules,"laya",fake)
 from buyerjourney.laya_adapter import LayaShadowEngine
 d=LayaShadowEngine().decide("Can we try it first?")
 assert d.gap_theme=="TRIAL_POC" and d.intent=="commercial" and d.stage=="evaluating"
 assert d.confidence==.86
