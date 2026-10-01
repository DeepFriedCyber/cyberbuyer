import json
from .claim_entailment import AtomicClaim, ClaimCheck, ClaimVerdict


def _json_from(raw):
    """
    Strictly extract and parse the outer JSON object.

    Deliberately raises on malformed model output.
    Model adapters are responsible for failing closed.
    """
    if not isinstance(raw, str):
        raise ValueError("Model returned non-string output")

    a, b = raw.find("{"), raw.rfind("}")

    if a < 0 or b < a:
        raise ValueError("Model returned invalid JSON")

    return json.loads(raw[a:b + 1])


class _QwenBase:
    def __init__(
        self,
        model_name="Qwen/Qwen3-1.7B",
        tokenizer=None,
        model=None,
    ):
        if tokenizer is None or model is None:
            from transformers import AutoTokenizer, AutoModelForCausalLM

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype="auto",
            )

        self.tok = tokenizer
        self.model = model

    def _run(self, system, user, max_new_tokens=400):
        prompt = self.tok.apply_chat_template(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        batch = self.tok([prompt], return_tensors="pt")
        n = batch.input_ids.shape[1]

        inputs = (
            batch.to(self.model.device)
            if hasattr(batch, "to")
            else batch
        )

        out = self.model.generate(  # pyright: ignore[reportAttributeAccessIssue]
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

        return self.tok.decode(
            out[0][n:],
            skip_special_tokens=True,
        )


class QwenClaimDecomposer(_QwenBase):
    SYSTEM = """Decompose the buyer question into the smallest independently verifiable factual claims.
Preserve material qualifiers exactly: unlimited, guaranteed, never, zero downtime, 30 day,
minimum, capped, all, definitely, absolutely, price amounts, dates and product names.
Do not answer the question and do not add facts. Return JSON only:
{"claims":["claim 1","claim 2"]}"""

    def decompose(self, question):
        try:
            raw = self._run(
                self.SYSTEM,
                f"QUESTION:\n{question}",
            )
            d = _json_from(raw)
        except Exception:
            # Fail closed: malformed model output creates no claims.
            return []

        try:
            claims = [
                str(x).strip()
                for x in d.get("claims", [])
                if str(x).strip()
            ]
        except Exception:
            return []

        return [AtomicClaim(x) for x in claims[:8]]


class QwenClaimEntailer(_QwenBase):
    SYSTEM = """You are a strict claim-to-evidence entailment checker.
Use ONLY the supplied company evidence. Relevance is not entailment.
A claim is SUPPORTED only if the cited evidence explicitly substantiates the whole claim,
including every material qualifier. Otherwise it is UNSUPPORTED.
For SUPPORTED, quote the smallest exact verbatim passage(s) from supplied evidence.
Never cite the buyer question as evidence. Return JSON only:
{"verdict":"SUPPORTED|UNSUPPORTED","evidence_ids":["id"],"evidence_quotes":["exact quote"]}"""

    def check(self, claim, evidence):
        packed = "\n\n".join(
            f"EVIDENCE_ID={e.source_id}\nTEXT={e.text}"
            for e in evidence
        )

        try:
            raw = self._run(
                self.SYSTEM,
                f"CLAIM:\n{claim}\n\nEVIDENCE:\n{packed}",
            )
            d = _json_from(raw)
        except Exception:
            # Fail closed: malformed output can NEVER support a claim.
            return ClaimCheck(
                claim,
                ClaimVerdict.UNSUPPORTED,
                [],
                [],
            )

        try:
            verdict = ClaimVerdict(
                str(
                    d.get(
                        "verdict",
                        "UNSUPPORTED",
                    )
                ).upper()
            )
        except Exception:
            verdict = ClaimVerdict.UNSUPPORTED

        # Never retain evidence references for an unsupported verdict.
        if verdict != ClaimVerdict.SUPPORTED:
            return ClaimCheck(
                claim,
                ClaimVerdict.UNSUPPORTED,
                [],
                [],
            )

        try:
            evidence_ids = [
                str(x)
                for x in d.get("evidence_ids", [])
            ]

            evidence_quotes = [
                str(x)
                for x in d.get("evidence_quotes", [])
            ]
        except Exception:
            return ClaimCheck(
                claim,
                ClaimVerdict.UNSUPPORTED,
                [],
                [],
            )

        return ClaimCheck(
            claim,
            verdict,
            evidence_ids,
            evidence_quotes,
        )