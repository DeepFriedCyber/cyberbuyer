class DisabledSemanticEngine:
    """Deliberately unavailable primary used to prove failover works."""
    name = "semantic-disabled"

    def decide(self, text, context=None):
        raise RuntimeError("No semantic/Jev adapter configured")
