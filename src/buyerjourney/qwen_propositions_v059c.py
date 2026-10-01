from .evidence_propositions_v059c import EvidenceProposition
from .specialist_verifier_v059 import EvidenceSpan
from .qwen_claims import _QwenBase, _json_from


class QwenEvidencePropositionGenerator(_QwenBase):
    SYSTEM = """Create candidate propositions ONLY from supplied company evidence.
The proposition is a compact declarative restatement of an exact evidence quote that may help answer the requested information.
Never answer from general knowledge or from the buyer question. Never add a qualifier, number, promise, scope, price, duration, guarantee or implication that is absent from the exact quote.
Each proposition MUST include one real EVIDENCE_ID and one EXACT verbatim quote copied from that evidence. If evidence is related but does not substantiate the requested information, you may still return the related proposition without adding the missing qualifier. If nothing relevant exists, return no propositions.
JSON only: {"propositions":[{"component_id":"c1","text":"evidence-derived proposition","evidence_id":"id","quote":"exact verbatim quote"}]}"""

    def generate(self, components, evidence):
        component_text = "\n".join(f"[{c.component_id}] {c.question}" for c in components)
        packed = "\n\n".join(f"EVIDENCE_ID={e.source_id}\nTEXT={e.text}" for e in evidence)
        try:
            raw = self._run(
                self.SYSTEM,
                f"REQUESTED INFORMATION:\n{component_text}\n\nEVIDENCE:\n{packed}",
                700,
            )
            data = _json_from(raw)
        except Exception:
            return []

        by_id = {e.source_id: e.text for e in evidence}
        valid_components = {c.component_id for c in components}
        out = []
        for item in data.get("propositions", []):
            try:
                component_id = str(item.get("component_id", "")).strip()
                text = str(item.get("text", "")).strip()
                evidence_id = str(item.get("evidence_id", "")).strip()
                quote = str(item.get("quote", "")).strip()
                source_text = by_id.get(evidence_id, "")
                if not component_id or component_id not in valid_components or not text or not quote or not source_text:
                    continue
                start = source_text.find(quote)
                if start < 0:
                    continue
                span = EvidenceSpan(evidence_id, quote, start, start + len(quote), source_text)
                if not span.valid():
                    continue
                out.append(EvidenceProposition(component_id, text, span))
            except Exception:
                continue
        return out
