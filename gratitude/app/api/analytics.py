from fastapi import APIRouter
from app.services.analytics_service import (
    top_entities,
    top_locations,
    top_actions
)

router = APIRouter()

@router.get("/top-entities")
def entities(limit: int = 10):
    return {"results": top_entities(limit)}

@router.get("/top-locations")
def locations(limit: int = 10):
    return {"results": top_locations(limit)}

@router.get("/top-actions")
def actions(limit: int = 10):
    return {"results": top_actions(limit)}
