from buyerjourney.insights import InsightStore
def test_gap_aggregation(tmp_path):
 s=InsightStore(tmp_path/"i.json"); s.record("Is there a trial period?","unsupported"); s.record("Is there a trial period?","unsupported"); s.record("How much does MDR cost?","supported","Pricing"); x=s.summary(); assert x["total_questions"]==3 and x["gaps"][0]["count"]==2
