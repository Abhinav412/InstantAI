from fastapi import APIRouter, Query
from app.services.search_service import search_gratitude

router = APIRouter()

@router.get("/gratitude")
def search(
    location: str | None = Query(default=None),
    role: str | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None)
):
    return {
        "results": search_gratitude(
            location=location,
            role=role,
            action=action,
            entity_type=entity_type
        )
    }
