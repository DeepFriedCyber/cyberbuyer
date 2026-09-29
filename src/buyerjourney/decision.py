from dataclasses import dataclass, asdict
import concurrent.futures

ALLOWED_ACTIONS = {
    "KEEP_EXPLORING", "SHOW_PRICING", "SHOW_IMPLEMENTATION",
    "ASK_TEAM", "EMAIL_ANSWER", "TALK_TO_SPECIALIST", "STOP_HERE"
}

@dataclass(frozen=True)
class Decision:
    topic: str
    intent: str
    stage: str
    gap_theme: str | None
    actions: tuple[str, ...]
    confidence: float
    engine: str
    fallback_reason: str | None = None

    def public(self):
        return asdict(self)

class RulesEngine:
    name = "rules"

    def decide(self, text, context=None):
        x = text.lower()
        themes = [
            ("TRIAL_POC", ("trial", "poc", "proof of concept", "try it")),
            ("PRICING", ("price", "pricing", "cost", "£")),
            ("IMPLEMENTATION", ("implement", "deployment", "onboarding", "how long")),
            ("DOWNTIME", ("downtime", "outage", "disruption")),
            ("MSP", ("msp", "it provider")),
            ("INCIDENT", ("incident", "breach", "attack", "2am", "overnight")),
            ("CONTRACT", ("cancel", "contract", "commitment")),
            ("INSURANCE", ("insurance", "insurer")),
        ]
        theme = next((n for n, words in themes if any(w in x for w in words)), "OTHER")
        commercial = theme in {"TRIAL_POC", "PRICING", "CONTRACT"}
        actions = (
            ("KEEP_EXPLORING", "SHOW_PRICING", "SHOW_IMPLEMENTATION", "ASK_TEAM")
            if commercial else
            ("KEEP_EXPLORING", "SHOW_IMPLEMENTATION", "ASK_TEAM")
        )
        return Decision(
            topic=theme.replace("_", " ").title(),
            intent="commercial" if commercial else "research",
            stage="evaluating" if commercial else "researching",
            gap_theme=theme,
            actions=actions,
            confidence=0.70,
            engine=self.name,
        )

class Policy:
    def filter_actions(self, actions, context=None):
        context = context or {}
        out = []
        for action in actions:
            if action not in ALLOWED_ACTIONS:
                continue
            if action == "EMAIL_ANSWER" and not context.get("email_supplied"):
                continue
            if action == "TALK_TO_SPECIALIST" and not context.get("contact_consent"):
                continue
            if action not in out:
                out.append(action)
        return tuple(out) or ("KEEP_EXPLORING", "STOP_HERE")

class Health:
    def __init__(self):
        self.counts = {k: 0 for k in (
            "primary", "fallback", "timeout", "exception",
            "invalid", "low_confidence", "policy_filtered"
        )}

    def hit(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1

    def snapshot(self):
        return {
            **self.counts,
            "requests": self.counts["primary"] + self.counts["fallback"],
        }

class ResilientDecisionEngine:
    def __init__(self, primary, fallback=None, timeout_ms=250,
                 min_confidence=0.65, health=None, policy=None):
        self.primary = primary
        self.fallback = fallback or RulesEngine()
        self.timeout_ms = timeout_ms
        self.min_confidence = min_confidence
        self.health = health or Health()
        self.policy = policy or Policy()

    def _valid(self, d):
        return (
            isinstance(d, Decision)
            and 0 <= d.confidence <= 1
            and bool(d.actions)
            and all(a in ALLOWED_ACTIONS for a in d.actions)
        )

    def decide(self, text, context=None):
        reason = None
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(self.primary.decide, text, context)
            try:
                d = future.result(timeout=self.timeout_ms / 1000)
            except concurrent.futures.TimeoutError:
                reason = "timeout"
                executor.shutdown(wait=False, cancel_futures=True)
            else:
                executor.shutdown(wait=False)

            if reason is None:
                if not self._valid(d):
                    reason = "invalid"
                elif d.confidence < self.min_confidence:
                    reason = "low_confidence"
                else:
                    filtered = self.policy.filter_actions(d.actions, context)
                    if filtered != d.actions:
                        self.health.hit("policy_filtered")
                    self.health.hit("primary")
                    return Decision(
                        d.topic, d.intent, d.stage, d.gap_theme,
                        filtered, d.confidence, d.engine
                    )
        except Exception:
            reason = "exception"
            executor.shutdown(wait=False, cancel_futures=True)

        self.health.hit(reason or "exception")
        self.health.hit("fallback")
        fb = self.fallback.decide(text, context)
        return Decision(
            fb.topic, fb.intent, fb.stage, fb.gap_theme,
            self.policy.filter_actions(fb.actions, context),
            fb.confidence, fb.engine, reason
        )
