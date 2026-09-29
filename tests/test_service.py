import json
from pathlib import Path
from buyerjourney.service import BuyerJourney
s=BuyerJourney(json.loads((Path(__file__).parents[1]/"data"/"corpus.json").read_text())["chunks"])
def test_defender(): assert s.answer("We already have Microsoft Defender. Why need MDR?")["status"]=="supported"
def test_single_source(): assert len(s.answer("How long does this take to implement?")["sources"])==1
def test_trial_gap(): assert s.answer("Is there a trial period?")["status"]=="unsupported"
def test_absolute_gap(): assert s.answer("Can you guarantee we will never be hacked?")["status"]=="unsupported"
