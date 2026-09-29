import time
from buyerjourney.decision import Decision, ResilientDecisionEngine

class Good:
    def decide(self, text, context=None):
        return Decision("Pricing","commercial","evaluating","PRICING",
                        ("KEEP_EXPLORING","SHOW_PRICING"),0.91,"good")

class Broken:
    def decide(self, text, context=None):
        raise RuntimeError("boom")

class Low:
    def decide(self, text, context=None):
        return Decision("Other","research","researching","OTHER",
                        ("KEEP_EXPLORING",),0.20,"low")

class Slow:
    def decide(self, text, context=None):
        time.sleep(0.05)
        return Decision("Other","research","researching","OTHER",
                        ("KEEP_EXPLORING",),0.90,"slow")

class Contact:
    def decide(self, text, context=None):
        return Decision("Other","research","researching","OTHER",
                        ("EMAIL_ANSWER","TALK_TO_SPECIALIST","KEEP_EXPLORING"),
                        0.90,"contact")

class Invalid:
    def decide(self, text, context=None):
        return {"not": "a Decision"}

def test_valid_primary_is_used():
    d = ResilientDecisionEngine(Good()).decide("price")
    assert d.engine == "good"
    assert d.fallback_reason is None

def test_exception_falls_back():
    d = ResilientDecisionEngine(Broken()).decide("trial")
    assert d.engine == "rules"
    assert d.fallback_reason == "exception"

def test_low_confidence_falls_back():
    d = ResilientDecisionEngine(Low()).decide("trial")
    assert d.engine == "rules"
    assert d.fallback_reason == "low_confidence"

def test_timeout_falls_back():
    d = ResilientDecisionEngine(Slow(), timeout_ms=5).decide("trial")
    assert d.engine == "rules"
    assert d.fallback_reason == "timeout"

def test_invalid_output_falls_back():
    d = ResilientDecisionEngine(Invalid()).decide("trial")
    assert d.engine == "rules"
    assert d.fallback_reason == "invalid"

def test_policy_blocks_contact_without_permission():
    d = ResilientDecisionEngine(Contact()).decide("hello", {})
    assert "EMAIL_ANSWER" not in d.actions
    assert "TALK_TO_SPECIALIST" not in d.actions
    assert "KEEP_EXPLORING" in d.actions
