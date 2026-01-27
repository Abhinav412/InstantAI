from app.db.session import get_session
from app.models.narrative import Narrative
from app.models.cluster import SemanticCluster
from app.models.entity import GratitudeEntity
from app.models.cluster_membership import ClusterMembership
from sqlalchemy import cast, Text


def search_gratitude(
    location=None,
    role=None,
    action=None,
    entity_type=None,
):
    with get_session() as session:
        query = (
            session.query(
                GratitudeEntity.id.label("entity_id"),
                GratitudeEntity.canonical_profile,
                Narrative.id.label("narrative_id"),
                Narrative.actions,
                Narrative.descriptors,
                Narrative.location_context,
                Narrative.sentiment_score,
            )
            .join(
                SemanticCluster,
                SemanticCluster.entity_id == GratitudeEntity.id,
            )
            .join(
                ClusterMembership,
                ClusterMembership.cluster_id == SemanticCluster.id,
            )
            .join(
                Narrative,
                Narrative.id == ClusterMembership.narrative_id,
            )
        )

        if location:
            query = query.filter(
                Narrative.location_context.ilike(f"%{location}%")
            )

        if role:
            query = query.filter(Narrative.role == role)

        if action:
            # ✅ Correct JSON search for array elements
            query = query.filter(
                cast(Narrative.actions, Text).ilike(f'%"{action}"%')
            )

        if entity_type:
            query = query.filter(
                GratitudeEntity.canonical_profile["entity_type"].astext
                == entity_type
            )

        results = query.all()

    # 🔁 Post-process outside session
    response = {}
    for row in results:
        eid = str(row.entity_id)
        response.setdefault(
            eid,
            {
                "entity_id": eid,
                "canonical_profile": row.canonical_profile,
                "stories": [],
            },
        )

        response[eid]["stories"].append(
            {
                "narrative_id": str(row.narrative_id),
                "actions": row.actions,
                "descriptors": row.descriptors,
                "location": row.location_context,
                "sentiment": row.sentiment_score,
            }
        )

    return list(response.values())
