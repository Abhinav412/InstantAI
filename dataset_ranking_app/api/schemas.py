from typing import List, Dict
from pydantic import BaseModel


class RankingRequest(BaseModel):
    query: str


class MetricBreakdown(BaseModel):
    metric: str
    contribution: float


class RankedEntityResponse(BaseModel):
    entity: str
    score: float
    breakdown: Dict[str, float]


class RankingResponse(BaseModel):
    rankings: List[RankedEntityResponse]
    explanation: Dict
