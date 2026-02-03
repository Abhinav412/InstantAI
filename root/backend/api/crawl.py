from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from web_ingestion.orchestrator import run_web_ingestion
from dkl.chatbot_modes import ChatbotMode

router = APIRouter(prefix="/crawl", tags=["Web Ingestion"])


class CrawlRequest(BaseModel):
    query: str


@router.post("")
def crawl_web(req: CrawlRequest):
    if not req.query or len(req.query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Invalid query")

    try:
        result = run_web_ingestion(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    knowledge_state = result["knowledge_index"]["knowledge_state"]

    # 🔑 Derive chatbot mode safely
    if knowledge_state == "READY":
        chatbot_mode = ChatbotMode.FULL_ANSWER
    else:
        chatbot_mode = ChatbotMode.CLARIFICATION_ONLY

    return {
        "status": "completed",
        "query": req.query,
        "knowledge_state": knowledge_state,
        "chatbot_mode": chatbot_mode,
        "message": (
            "Web ingestion completed"
            if knowledge_state == "READY"
            else "More information required before ranking"
        )
    }
