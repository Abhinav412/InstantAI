from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.chat_runtime import run_chat_runtime

router = APIRouter(prefix="/chat/web", tags=["Chat (Web)"])


class WebChatRequest(BaseModel):
    user_query: str
    knowledge_index: dict
    allowed_metrics: list[str]
    blocked_metrics: list[str]
    low_trust_present: bool = True
    dataset_preview: list[dict]


@router.post("")
def chat_with_web(req: WebChatRequest):
    if not req.user_query or len(req.user_query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Invalid query")

    return run_chat_runtime(
        user_query=req.user_query,
        knowledge_index=req.knowledge_index,
        allowed_metrics=req.allowed_metrics,
        blocked_metrics=req.blocked_metrics,
        low_trust_present=req.low_trust_present,
        dataset_preview=req.dataset_preview
    )
