import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestFacets:
    original: str
    topics: list[str] = field(default_factory=list)
    qualifiers: list[str] = field(default_factory=list)
    amounts: list[str] = field(default_factory=list)
    durations: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)


QUALIFIERS = (
    "unlimited", "guarantee", "guaranteed", "never", "zero", "minimum",
    "maximum", "capped", "all", "always", "absolutely", "definitely",
    "free", "money back", "month to month", "month-to-month",
)

TOPIC_RULES = (
    ("implementation", ("implementation", "deployment", "onboarding")),
    ("pricing", ("cost", "price", "pricing", "premium", "price increases")),
    ("evaluation", ("trial", "proof of concept", "evaluation")),
    ("contract", ("contract", "cancel", "cancellation", "notice period")),
    ("incident_response", ("incident response", "incident", "response")),
    ("insurance", ("cyber insurance", "insurance renewal", "insurance premium")),
    ("breach_prevention", ("breached", "breach", "ransomware")),
    ("compliance", ("regulatory compliance", "compliance")),
    ("monitoring", ("monitoring",)),
    ("human_investigation", ("human investigation", "investigation")),
    ("security_tools", ("security tools", "microsoft defender", "defender")),
    ("service_scope", ("included", "include", "adds")),
)

PRODUCT_RULES = (
    ("MDR", r"\bMDR\b"),
    ("EDR", r"\bEDR\b"),
    ("Microsoft Defender", r"\bMicrosoft Defender\b|\bDefender\b"),
)

RELATION_RULES = (
    ("included", r"\binclude(?:d|s)?\b"),
    ("adds", r"\badds?\b"),
    ("keep_existing", r"\bkeep\b.*\bexisting\b"),
    ("difference", r"\bdifference\b"),
    ("reduce", r"\breduce\b"),
    ("affect", r"\baffect\b"),
    ("require", r"\brequire\b"),
    ("begin", r"\bbegin\b"),
)


def _unique(values):
    out = []
    seen = set()
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


class DeterministicRequestFacetExtractor:
    def extract(self, question: str) -> RequestFacets:
        q = question.strip()
        lower = q.lower()

        qualifiers = [x for x in QUALIFIERS if x in lower]
        # Canonicalise the spelling variant while preserving the material concept.
        if "month-to-month" in qualifiers and "month to month" not in qualifiers:
            qualifiers.append("month to month")
        qualifiers = [x for x in qualifiers if x != "month-to-month"]

        amounts = re.findall(r"(?:£|\$)\s?\d+(?:[,.]\d+)?", q)
        durations = re.findall(r"\b\d+(?:\.\d+)?\s*(?:days?|hours?|weeks?|months?|years?)\b", q, flags=re.I)

        topics = []
        for name, needles in TOPIC_RULES:
            if any(needle in lower for needle in needles):
                topics.append(name)

        products = [name for name, pattern in PRODUCT_RULES if re.search(pattern, q, flags=re.I)]
        relations = [name for name, pattern in RELATION_RULES if re.search(pattern, q, flags=re.I)]

        return RequestFacets(
            original=q,
            topics=_unique(topics),
            qualifiers=_unique(qualifiers),
            amounts=_unique(amounts),
            durations=_unique(durations),
            products=_unique(products),
            relations=_unique(relations),
        )
