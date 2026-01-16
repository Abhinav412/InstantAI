from fastapi import FastAPI
from pydantic import BaseModel
from pipeline.orchestrator import run_pipeline
import traceback

app = FastAPI()

class RankRequest(BaseModel):
    query: str

@app.post("/rank")
def rank_entities(req: RankRequest):
    try:
        rankings, explanation = run_pipeline(req.query)
        return {
            "success": True,
            "rankings": rankings,
            "explanation": explanation
        }
    except Exception as e:
        # 🔥 CRITICAL: never let FastAPI return non-JSON
        print("PIPELINE ERROR:")
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e),
            "rankings": [],
            "explanation": {
                "summary": "Ranking failed",
                "top_drivers": [],
                "confidence_interpretation": "Internal error"
            }
        }

@app.get("/health")
def health():
    return {"status": "ok"}
