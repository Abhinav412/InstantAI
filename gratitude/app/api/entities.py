from fastapi import APIRouter
from app.services.entity_resolution_service import resolve_entities

router = APIRouter()

@router.post("/resolve")
def resolve():
    resolve_entities()
    return {"status": "entities resolved"}
