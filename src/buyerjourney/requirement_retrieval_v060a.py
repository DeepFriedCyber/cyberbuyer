from dataclasses import dataclass, field

from .requirement_normalization_v059h import DeterministicRequirementNormalizer, VerificationTarget


@dataclass(frozen=True)
class RequirementEvidence:
    requirement_id: str
    query: str
    evidence: list = field(default_factory=list)


@dataclass(frozen=True)
class RequirementRetrievalResult:
    original: str
    targets: list[VerificationTarget]
    retrieved: list[RequirementEvidence]


def build_target_query(original: str, target: VerificationTarget) -> str:
    """Build a retrieval query from source-language terms, never internal labels."""
    parts = []
    parts.extend(target.evidence_terms)
    parts.extend(target.constraints)
    # Product/amount/duration/qualifier targets benefit from original context while
    # retaining the exact obligation. Retrieval is candidate discovery, not proof.
    if target.kind in {"product", "amount", "duration", "qualifier", "constraint"}:
        parts.append(original)
    out = []
    seen = set()
    for part in parts:
        text = str(part).strip()
        if text and text.lower() not in seen:
            seen.add(text.lower())
            out.append(text)
    return " ; ".join(out) or original


class RequirementAwareRetriever:
    """Retrieve and optionally rerank candidates independently for each obligation.

    This class deliberately exposes no support/entailment decision. A high retrieval
    score means relevant candidate evidence only.
    """
    def __init__(self, retriever, reranker=None, normalizer=None, candidate_k=6, top_k=3):
        self.retriever = retriever
        self.reranker = reranker
        self.normalizer = normalizer or DeterministicRequirementNormalizer()
        self.candidate_k = candidate_k
        self.top_k = top_k

    def retrieve(self, question: str) -> RequirementRetrievalResult:
        request = self.normalizer.normalize(question)
        rows = []
        for target in request.targets:
            query = build_target_query(question, target)
            candidates = self.retriever.search(query, self.candidate_k)
            if self.reranker is not None:
                candidates = self.reranker.rerank(query, candidates, top_n=self.top_k)
            else:
                candidates = candidates[:self.top_k]
            rows.append(RequirementEvidence(target.requirement_id, query, candidates))
        return RequirementRetrievalResult(request.original, request.targets, rows)
