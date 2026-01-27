from fastapi import APIRouter
from app.services.entity_merge_service import detect_merge_candidates
from app.services.entity_split_service import detect_split_candidates

router = APIRouter()

@router.post("/detect")
def detect():
    detect_merge_candidates()
    detect_split_candidates()
    return {"status": "detection complete"}
