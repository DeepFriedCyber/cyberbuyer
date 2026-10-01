from .qwen_claims import _QwenBase, _json_from
from .question_coverage import RequestedComponent


class QwenZeroShotRequestedInformationDecomposer(_QwenBase):
    """Zero-shot decomposition experiment.

    Deliberately contains no worked examples so we can measure whether the
    v0.5.8 few-shot prompt is contaminating unrelated decompositions.
    """

    SYSTEM = """Decompose the buyer QUESTION into the smallest MATERIAL INFORMATION REQUESTS needed to fully answer it.
Decompose requested information, NOT factual claims.
Write each component as a neutral question.
Do not answer the buyer question.
Do not introduce a topic, product, amount, duration, contract term, guarantee, qualifier, or requirement that is absent from the buyer question.
Preserve every material qualifier that IS present in the buyer question exactly.
Do not infer hidden requirements.
Prefer one component when the question asks for one thing. Use multiple components only when the buyer explicitly asks for multiple independently answerable things.
Return JSON only in this schema:
{"components":[{"id":"c1","question":"neutral information request","material":true}]}"""

    def decompose(self, question):
        try:
            data = _json_from(self._run(self.SYSTEM, f"QUESTION:\n{question}", 350))
        except Exception:
            return [RequestedComponent("c1", question, True)]
        out = []
        for i, item in enumerate(data.get("components", [])[:8], 1):
            q = str(item.get("question", "")).strip()
            if not q:
                continue
            out.append(RequestedComponent(
                str(item.get("id") or f"c{i}"),
                q,
                bool(item.get("material", True)),
            ))
        return out or [RequestedComponent("c1", question, True)]
