from app.db.session import get_session
from app.models.entity import GratitudeEntity
from app.models.entity_resolution_state import EntityResolutionState


def detect_merge_candidates():
    # 1️⃣ Fetch entity IDs only (short session)
    with get_session() as session:
        entity_ids = [e.id for e in session.query(GratitudeEntity.id).all()]

    # 2️⃣ Compare pairs with isolated transactions
    for i, e1_id in enumerate(entity_ids):
        with get_session() as session:
            e1 = session.get(GratitudeEntity, e1_id)

            for e2_id in entity_ids[i + 1:]:
                e2 = session.get(GratitudeEntity, e2_id)

                score = _entity_similarity(e1, e2)

                if score < 0.85:
                    continue

                state = (
                    session.query(EntityResolutionState)
                    .filter_by(
                        entity_id=e1.id,
                        status="merge_candidate",
                    )
                    .first()
                )

                signals = {
                    "candidate_with": str(e2.id),
                    "similarity_score": score,
                }

                if state:
                    state.signals = signals
                else:
                    session.add(
                        EntityResolutionState(
                            entity_id=e1.id,
                            status="merge_candidate",
                            signals=signals,
                        )
                    )


def _entity_similarity(e1, e2):
    p1 = e1.canonical_profile or {}
    p2 = e2.canonical_profile or {}

    overlap = 0.0

    if p1.get("location") and p1.get("location") == p2.get("location"):
        overlap += 0.4

    overlap += 0.1 * len(
        set(p1.get("descriptors", [])) &
        set(p2.get("descriptors", []))
    )

    return round(min(overlap, 1.0), 2)
