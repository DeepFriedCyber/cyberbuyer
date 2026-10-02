from dataclasses import dataclass, field
from .request_facets_v059f import DeterministicRequestFacetExtractor, RequestFacets


@dataclass(frozen=True)
class EvidenceRequirement:
    requirement_id: str
    kind: str
    description: str
    required_terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvidenceRequest:
    original: str
    facets: RequestFacets
    requirements: list[EvidenceRequirement]


class DeterministicEvidenceRequirementBuilder:
    """Build explicit evidence obligations without rewriting the buyer question."""

    def __init__(self, facet_extractor=None):
        self.facets = facet_extractor or DeterministicRequestFacetExtractor()

    def build(self, question: str) -> EvidenceRequest:
        f = self.facets.extract(question)
        reqs = []

        def add(kind, description, terms=None):
            reqs.append(EvidenceRequirement(f"r{len(reqs)+1}", kind, description, list(terms or [])))

        # Core subject/topic obligations.
        for topic in f.topics:
            add("topic", f"Evidence addressing {topic.replace('_', ' ')}", [topic])

        # Product comparison/use obligations should survive even if no broad topic matched.
        if "difference" in f.relations and len(f.products) >= 2:
            add("relation", f"Evidence describing the difference between {f.products[0]} and {f.products[1]}", f.products[:2])

        for relation in f.relations:
            if relation == "difference":
                continue
            add("relation", f"Evidence supporting relation: {relation.replace('_', ' ')}", [relation])

        # Exact buyer constraints are separate obligations. This is what prevents
        # related evidence from satisfying a stronger question.
        for amount in f.amounts:
            add("amount", f"Evidence explicitly supporting amount {amount}", [amount])
        for duration in f.durations:
            add("duration", f"Evidence explicitly supporting duration {duration}", [duration])
        for qualifier in f.qualifiers:
            add("qualifier", f"Evidence explicitly supporting qualifier '{qualifier}'", [qualifier])

        # Products are useful retrieval/coverage constraints when they have not
        # already been represented by a comparison requirement.
        compared = set(f.products[:2]) if "difference" in f.relations and len(f.products) >= 2 else set()
        for product in f.products:
            if product not in compared:
                add("product", f"Evidence specifically about {product}", [product])

        # No extracted facet should result in an empty obligation set. Preserve the
        # original request as the retrieval target rather than inventing semantics.
        if not reqs:
            add("original", "Evidence directly addressing the original buyer question", [question])

        return EvidenceRequest(question, f, reqs)


def aggregate_requirement_states(states: list[str]) -> str:
    """Aggregate independently checked requirements.

    SUPPORTED requires every obligation. PARTIAL means at least one but not all
    obligations are supported. No supported obligations means UNSUPPORTED.
    """
    normal = [str(x).upper() for x in states]
    if not normal:
        return "UNSUPPORTED"
    supported = sum(x == "SUPPORTED" for x in normal)
    if supported == len(normal):
        return "SUPPORTED"
    if supported:
        return "PARTIAL"
    return "UNSUPPORTED"
