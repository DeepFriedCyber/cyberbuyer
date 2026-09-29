import json
from pathlib import Path
from flask import Flask,jsonify,render_template,request
from .service import BuyerJourney,signals
from .insights import InsightStore
def create_app(test_config=None):
 base=Path(__file__).parents[2]; app=Flask(__name__,template_folder=str(Path(__file__).parent/"templates"),static_folder=str(Path(__file__).parent/"static"))
 if test_config: app.config.update(test_config)
 svc=BuyerJourney(json.loads((base/"data"/"corpus.json").read_text(encoding="utf-8"))["chunks"]); store=InsightStore(app.config.get("INSIGHTS_PATH",base/"data"/"insights.json"))
 @app.get("/")
 def home(): return render_template("index.html")
 @app.get("/insights")
 def insights(): return render_template("insights.html")
 @app.post("/api/ask")
 def ask():
  p=request.get_json(force=True); q=str(p.get("question","")).strip()
  if not q:return jsonify({"error":"question required"}),400
  r=svc.answer(q,p.get("mode","simple")); store.record(q,r["status"],r["topic"]); r["signals"]=signals(q); return jsonify(r)
 @app.get("/api/insights")
 def api_insights(): return jsonify(store.summary())
 return app
