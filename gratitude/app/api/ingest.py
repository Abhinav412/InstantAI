from fastapi import APIRouter
from app.services.ingestion_service import ingest_message

router = APIRouter()

@router.post("/ingest")
async def ingest(payload: dict):
    return await ingest_message(payload)
