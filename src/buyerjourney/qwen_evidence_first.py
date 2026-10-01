from .evidence_first import CandidateFact
from .qwen_claims import _QwenBase,_json_from
class QwenEvidenceFirstExtractor(_QwenBase):
    SYSTEM="""Extract answer facts from supplied company evidence. Start from EVIDENCE, not assumptions. Return only atomic facts directly stated by evidence and useful to the buyer question. Never invent a proposition because the buyer asked it. Preserve material qualifiers exactly. Do not add free, unlimited, guaranteed, never, zero, minimum, maximum, capped, always, absolutely, definitely, 30 day, or money back unless evidence explicitly supports it. Every fact requires real EVIDENCE_ID values and exact verbatim quotes. If evidence contains related facts but not a requested qualifier, return only the related supported facts. If nothing answers the topic, return no facts. No general knowledge. JSON only: {"facts":[{"text":"atomic fact","evidence_ids":["id"],"evidence_quotes":["exact verbatim quote"]}]}"""
    def extract(self, question, evidence):
        packed = "\n\n".join(
            f"[{e.source_id}] {e.text}" for e in evidence
        )

        try:
            raw = self._run(
                self.SYSTEM,
                f"BUYER QUESTION:\n{question}\n\nEVIDENCE:\n{packed}",
                700,
            )
            d = _json_from(raw)
        except Exception:
            return []

        facts = []

        for x in d.get("facts", []):
            try:
                facts.append(
                    CandidateFact(
                        text=str(x.get("text", "")).strip(),
                        evidence_ids=list(x.get("evidence_ids", [])),
                        evidence_quotes=list(x.get("evidence_quotes", [])),
                    )
                )
            except Exception:
                continue

        return [f for f in facts if f.text]
