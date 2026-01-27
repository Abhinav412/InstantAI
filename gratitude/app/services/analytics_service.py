from sqlalchemy import func, cast, Text
from app.db.session import get_session
from app.models.narrative import Narrative
from app.models.cluster import SemanticCluster
from app.models.entity import GratitudeEntity
from app.models.cluster_membership import ClusterMembership


def top_entities(limit=10):
    with get_session() as session:
        rows = (
            session.query(
                GratitudeEntity.id.label("entity_id"),
                GratitudeEntity.canonical_profile,
                func.count(Narrative.id).label("story_count"),
                func.avg(Narrative.sentiment_score).label("avg_sentiment"),
            )
            .join(SemanticCluster, SemanticCluster.entity_id == GratitudeEntity.id)
            .join(ClusterMembership, ClusterMembership.cluster_id == SemanticCluster.id)
            .join(Narrative, Narrative.id == ClusterMembership.narrative_id)
            .group_by(GratitudeEntity.id)  # ✅ DO NOT group by JSON
            .order_by(func.count(Narrative.id).desc())
            .limit(limit)
            .all()
        )

    return [
        {
            "entity_id": str(r.entity_id),
            "canonical_profile": r.canonical_profile,
            "story_count": int(r.story_count),
            "avg_sentiment": float(r.avg_sentiment)
            if r.avg_sentiment is not None
            else None,
        }
        for r in rows
    ]


def top_locations(limit=10):
    with get_session() as session:
        rows = (
            session.query(
                Narrative.location_context.label("location"),
                func.count(Narrative.id).label("count"),
            )
            .filter(Narrative.location_context.isnot(None))
            .group_by(Narrative.location_context)
            .order_by(func.count(Narrative.id).desc())
            .limit(limit)
            .all()
        )

    return [
        {
            "location": r.location,
            "count": int(r.count),
        }
        for r in rows
    ]


def top_actions(limit=10):
    with get_session() as session:
        rows = (
            session.query(
                cast(Narrative.actions, Text).label("actions"),
                func.count(Narrative.id).label("count"),
            )
            .filter(Narrative.actions.isnot(None))
            .group_by(cast(Narrative.actions, Text))
            .order_by(func.count(Narrative.id).desc())
            .limit(limit)
            .all()
        )

    return [
        {
            "actions": r.actions,
            "count": int(r.count),
        }
        for r in rows
    ]
