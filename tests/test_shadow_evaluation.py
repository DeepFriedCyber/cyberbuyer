from buyerjourney.decision import Decision,RulesEngine
from buyerjourney.shadow import ShadowDecisionEngine
from buyerjourney.evaluation import evaluate,summary
class Shadow:
 def decide(self,t,c=None):return Decision("Trial Poc","commercial","evaluating","TRIAL_POC",("KEEP_EXPLORING",),.9,"shadow")
class Broken:
 def decide(self,t,c=None):raise RuntimeError("offline")
def test_shadow_cannot_control_primary():
 r=ShadowDecisionEngine(RulesEngine(),Shadow()).decide("Is there a trial?")
 assert r.primary.engine=="rules" and r.shadow.engine=="shadow"
def test_shadow_failure_does_not_break_primary():
 r=ShadowDecisionEngine(RulesEngine(),Broken()).decide("How much does it cost?")
 assert r.primary.gap_theme=="PRICING" and r.shadow is None and r.shadow_error=="RuntimeError"
def test_evaluator():
 c=[{"id":"1","question":"Is there a trial?","expected":{"gap_theme":"TRIAL_POC","intent":"commercial","stage":"evaluating"}}]
 s=summary(evaluate(RulesEngine(),c)); assert s["theme_accuracy"]==1
