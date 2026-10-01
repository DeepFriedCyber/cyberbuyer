import json
from pathlib import Path
def test_frozen_benchmark_has_retrieval_gold_annotations():
 root=Path(__file__).resolve().parents[1]
 rows=json.loads((root/"data/evidence_benchmark.json").read_text(encoding="utf-8"))
 assert len(rows)==26
 assert all("expected_evidence_ids" in r for r in rows)
 assert any(r["expected"]=="UNSUPPORTED" and r["expected_evidence_ids"] for r in rows)
