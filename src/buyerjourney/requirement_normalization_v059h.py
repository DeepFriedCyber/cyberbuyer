import re
from dataclasses import dataclass, field

from .evidence_requirements_v059g import (
    DeterministicEvidenceRequirementBuilder,
    EvidenceRequirement,
)


@dataclass(frozen=True)
class VerificationTarget:
    requirement_id: str
    kind: str
    canonical_terms: list[str] = field(default_factory=list)
    evidence_terms: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    description: str = ""


@dataclass(frozen=True)
class NormalizedEvidenceRequest:
    original: str
    targets: list[VerificationTarget]


CANONICAL_EVIDENCE_TERMS = {
    "implementation": ["implementation", "deployment", "onboarding"],
    "pricing": ["price", "pricing", "cost"],
    "evaluation": ["trial", "evaluation", "proof of concept"],
    "contract": ["contract", "cancellation", "cancel", "notice period"],
    "incident_response": ["incident response", "incident", "response"],
    "insurance": ["cyber insurance", "insurance", "renewal", "premium"],
    "breach_prevention": ["breach", "breached", "ransomware"],
    "compliance": ["regulatory compliance", "compliance"],
    "monitoring": ["monitoring"],
    "human_investigation": ["human investigation", "investigation"],
    "security_tools": ["security tools", "Microsoft Defender", "Defender"],
    "service_scope": ["service includes", "included", "include", "service scope"],
    "included": ["included", "include", "includes"],
    "adds": ["adds", "add", "additional"],
    "keep_existing": ["keep existing", "existing security tools", "continue using"],
    "reduce": ["reduce", "reduction"],
    "affect": ["affect", "impact"],
    "require": ["require", "requires", "required"],
    "begin": ["begin", "start", "commence"],
}


def _unique(values):
    out = []
    seen = set()
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            out.append(value)
    return out


def extract_constraints(question: str) -> list[str]:
    """Preserve high-risk semantic constraints as phrases, not isolated tokens."""
    q = question.strip()
    patterns = [
        r"\babsolutely\s+no\s+changes\b",
        r"\bnot\s+affect\s+any\s+employee\b",
        r"\bnever\s+be\s+breached\b",
        r"\bzero\s+downtime\b",
        r"\ball\s+future\s+price\s+increases\s+capped\b",
        r"\bunlimited\s+incident\s+response\b",
        r"\b30\s*day\s+evaluation\b",
        r"\bminimum\s+contract\s+term\b",
        r"\bmoney\s+back\s+guarantee\b",
        r"\bguarantee\s+regulatory\s+compliance\b",
        r"\bguarantee\s+(?:my\s+)?cyber\s+insurance\s+renewal\b",
    ]
    found = []
    for pattern in patterns:
        m = re.search(pattern, q, flags=re.I)
        if m:
            found.append(m.group(0))
    # Promise is itself material even where the following phrase is captured.
    if re.search(r"\bpromise\b", q, flags=re.I):
        found.append("promise")
    return _unique(found)


class DeterministicRequirementNormalizer:
    def __init__(self, builder=None):
        self.builder = builder or DeterministicEvidenceRequirementBuilder()

    def _terms(self, requirement: EvidenceRequirement) -> list[str]:
        out = []
        for term in requirement.required_terms:
            out.extend(CANONICAL_EVIDENCE_TERMS.get(term, [term]))
        return _unique(out)

    def normalize(self, question: str) -> NormalizedEvidenceRequest:
        request = self.builder.build(question)
        global_constraints = extract_constraints(question)
        targets = []
        for r in request.requirements:
            constraints = []
            lower_desc = r.description.lower()
            # Attach phrase-level constraints to the most relevant target(s), while
            # also preserving them globally through at least one target.
            for c in global_constraints:
                lc = c.lower()
                if (
                    any(t.lower() in lc for t in r.required_terms)
                    or r.kind in {"qualifier", "amount", "duration"}
                ):
                    constraints.append(c)
            targets.append(VerificationTarget(
                requirement_id=r.requirement_id,
                kind=r.kind,
                canonical_terms=list(r.required_terms),
                evidence_terms=self._terms(r),
                constraints=_unique(constraints),
                description=r.description,
            ))

        # If no individual requirement naturally owns a phrase-level constraint,
        # create a dedicated constraint target rather than silently losing it.
        attached = {c.lower() for t in targets for c in t.constraints}
        for c in global_constraints:
            if c.lower() not in attached:
                targets.append(VerificationTarget(
                    requirement_id=f"r{len(targets)+1}",
                    kind="constraint",
                    canonical_terms=[c],
                    evidence_terms=[c],
                    constraints=[c],
                    description=f"Evidence explicitly supporting constraint '{c}'",
                ))
        return NormalizedEvidenceRequest(request.original, targets)
