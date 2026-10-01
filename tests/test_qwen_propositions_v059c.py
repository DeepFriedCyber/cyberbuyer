import json
from types import SimpleNamespace

from buyerjourney.evidence_propositions_v059c import RequestedComponent
from buyerjourney.qwen_propositions_v059c import QwenEvidencePropositionGenerator


class FakeGenerator(QwenEvidencePropositionGenerator):
    def __init__(self, payload):
        self.payload = payload
    def _run(self, *args, **kwargs):
        return json.dumps(self.payload)


def evidence(text="MDR starts from £900 per month."):
    return [SimpleNamespace(source_id="s1", text=text)]


def test_accepts_exact_quote_and_preserves_offsets():
    g = FakeGenerator({"propositions":[{"component_id":"c1","text":"MDR starts from £900 per month.","evidence_id":"s1","quote":"MDR starts from £900 per month."}]})
    rows = g.generate([RequestedComponent("c1", "What is the published MDR price?")], evidence())
    assert len(rows) == 1
    assert rows[0].span.valid()
    assert rows[0].span.source_text[rows[0].span.start_char:rows[0].span.end_char] == rows[0].span.quote


def test_rejects_invented_quote():
    g = FakeGenerator({"propositions":[{"component_id":"c1","text":"MDR costs £900.","evidence_id":"s1","quote":"All customers pay exactly £900."}]})
    assert g.generate([RequestedComponent("c1", "What is the price?")], evidence()) == []


def test_rejects_unknown_evidence_id():
    g = FakeGenerator({"propositions":[{"component_id":"c1","text":"MDR starts from £900.","evidence_id":"missing","quote":"MDR starts from £900 per month."}]})
    assert g.generate([RequestedComponent("c1", "What is the price?")], evidence()) == []


def test_rejects_unknown_component_id():
    g = FakeGenerator({"propositions":[{"component_id":"c99","text":"MDR starts from £900.","evidence_id":"s1","quote":"MDR starts from £900 per month."}]})
    assert g.generate([RequestedComponent("c1", "What is the price?")], evidence()) == []
