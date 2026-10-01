import pytest

from buyerjourney.claim_entailment import ClaimVerdict
from buyerjourney.qwen_claims import (
    _json_from,
    QwenClaimDecomposer,
    QwenClaimEntailer,
)
from buyerjourney.qwen_evidence_first import QwenEvidenceFirstExtractor
from buyerjourney.qwen_question_coverage import (
    QwenRequestedInformationDecomposer,
)

MALFORMED = """Here is the result:{
  "facts": [
    {
      "text": "MDR costs £900 per month."
      "evidence_ids": ["pricing"]
    }
  ]
}"""


def broken_run(*args, **kwargs):
    return MALFORMED


def test_strict_json_parser_rejects_malformed_json():
    with pytest.raises(Exception):
        _json_from(MALFORMED)


def test_evidence_extractor_fails_closed_on_malformed_json():
    extractor = QwenEvidenceFirstExtractor(tokenizer=object(), model=object())
    extractor._run = broken_run
    assert extractor.extract("What does MDR cost?", []) == []


def test_claim_decomposer_fails_closed_on_malformed_json():
    decomposer = QwenClaimDecomposer(tokenizer=object(), model=object())
    decomposer._run = broken_run
    assert decomposer.decompose("What does MDR cost?") == []


def test_entailer_fails_closed_on_malformed_json():
    entailer = QwenClaimEntailer(tokenizer=object(), model=object())
    entailer._run = broken_run
    check = entailer.check("MDR costs £900 per month.", [])
    assert check.verdict == ClaimVerdict.UNSUPPORTED
    assert check.evidence_ids == []
    assert check.evidence_quotes == []


def test_coverage_decomposer_falls_back_to_original_question():
    decomposer = QwenRequestedInformationDecomposer(tokenizer=object(), model=object())
    decomposer._run = broken_run
    components = decomposer.decompose("What does MDR cost?")
    assert len(components) == 1
    assert components[0].question == "What does MDR cost?"