from app.db.session import get_session
from app.models.review_action import ReviewAction
from app.models.entity_resolution_state import EntityResolutionState
from uuid import UUID

VALID_ACTIONS = {
    "approve_split",
    "reject_split",
    "approve_merge",
    "reject_merge",
    "confirm_entity",
}


def submit_review(entity_id, action, notes=None, metadata=None):
    if action not in VALID_ACTIONS:
        raise ValueError("Invalid review action")

    # 🔒 Defensive UUID validation
    try:
        entity_id = UUID(str(entity_id))
    except Exception:
        raise ValueError("Invalid entity_id")

    with get_session() as session:
        with session.no_autoflush:
            review = ReviewAction(
                entity_id=entity_id,
                action=action,
                notes=notes,
                review_metadata=metadata or {},
            )
            session.add(review)

            # Resolution rule:
            # once a human confirms/rejects → remove detection state
            if action in {
                "confirm_entity",
                "reject_split",
                "reject_merge",
            }:
                session.query(EntityResolutionState).filter(
                    EntityResolutionState.entity_id == entity_id
                ).delete(synchronize_session=False)

        session.flush()
        review_id = review.id

    return str(review_id)
