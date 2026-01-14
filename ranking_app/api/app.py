from fastapi import FastAPI
from pydantic import BaseModel
from pipeline.orchestrator import run_pipeline

app = FastAPI(title="Agentic Ranking Engine")

class RankRequest(BaseModel):
    query: str

class RankResponse(BaseModel):
    rankings: list
    explanation: dict

@app.post("/rank", response_model=RankResponse)
def rank_entities(req: RankRequest):
    rankings, explanation = run_pipeline(req.query)
    return {
        "rankings": rankings,
        "explanation": explanation
    }
