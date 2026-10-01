from .qwen_claims import _QwenBase,_json_from
from .question_coverage import RequestedComponent

class QwenRequestedInformationDecomposer(_QwenBase):
    SYSTEM="""Decompose a buyer QUESTION into the smallest MATERIAL INFORMATION REQUESTS needed to fully answer it. Decompose requested information, NOT factual claims. Write each component as a neutral question. Do not answer. Do not add requirements. Preserve amounts, products and qualifiers exactly, including free, unlimited, guaranteed, guarantee, never, zero, no changes, minimum, maximum, capped, always, absolutely, definitely, 30 day and money back.
Examples:
"What does MDR cost?" -> ["What is the published MDR price?"]
"Does the £900 price include unlimited incident response?" -> ["Is £900 a published MDR price?","Is incident response included in that published price?","Is the included incident response unlimited?"]
Return JSON only: {"components":[{"id":"c1","question":"neutral information request","material":true}]}"""

    def decompose(self, question):
        try:
            d = _json_from(self._run(self.SYSTEM, f"QUESTION:\n{question}", 350))
        except Exception:
            return [RequestedComponent("c1", question, True)]
        out = []
        for i, x in enumerate(d.get("components", [])[:8], 1):
            q = str(x.get("question", "")).strip()
            if q:
                out.append(
                    RequestedComponent(
                        str(x.get("id") or f"c{i}"),
                        q,
                        bool(x.get("material", True)),
                    )
                )
        return out or [RequestedComponent("c1", question, True)]