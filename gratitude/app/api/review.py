from fastapi import APIRouter, HTTPException
from app.services.review_service import submit_review

router = APIRouter()

@router.post("/submit")
def submit(payload: dict):
    try:
        review_id = submit_review(
            entity_id=payload["entity_id"],
            action=payload["action"],
            notes=payload.get("notes"),
            metadata=payload.get("metadata")
        )
        return {"review_id": str(review_id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
