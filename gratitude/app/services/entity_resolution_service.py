from collections import Counter
from app.db.session import get_session
from app.models.cluster import SemanticCluster
from app.models.cluster_membership import ClusterMembership
from app.models.narrative import Narrative
from app.models.entity import GratitudeEntity


def resolve_entities():
    # 1️⃣ Fetch unresolved clusters (short session)
    with get_session() as session:
        cluster_ids = [
            c.id
            for c in session.query(SemanticCluster.id)
            .filter(SemanticCluster.entity_id.is_(None))
            .all()
        ]

    # 2️⃣ Resolve each cluster independently (isolated transactions)
    for cluster_id in cluster_ids:
        with get_session() as session:
            cluster = session.get(SemanticCluster, cluster_id)

            narratives = (
                session.query(Narrative)
                .join(
                    ClusterMembership,
                    ClusterMembership.narrative_id == Narrative.id,
                )
                .filter(ClusterMembership.cluster_id == cluster.id)
                .all()
            )

            if not narratives:
                continue

            entity = _create_entity_from_narratives(narratives)

            session.add(entity)
            session.flush()

            cluster.entity_id = entity.id
            cluster.confidence = entity.confidence_score


def _create_entity_from_narratives(narratives):
    roles = Counter(n.role for n in narratives if n.role)
    locations = Counter(
        n.location_context for n in narratives if n.location_context
    )
    descriptors = Counter(
        d for n in narratives for d in (n.descriptors or [])
    )

    canonical_profile = {
        "entity_type": narratives[0].entity_type,
        "role": roles.most_common(1)[0][0] if roles else None,
        "location": locations.most_common(1)[0][0] if locations else None,
        "descriptors": [d for d, _ in descriptors.most_common(5)],
        "narrative_count": len(narratives),
    }

    confidence = _compute_confidence(narratives)

    return GratitudeEntity(
        entity_type=canonical_profile["entity_type"],
        canonical_profile=canonical_profile,
        confidence_score=confidence,
    )


def _compute_confidence(narratives):
    base = min(0.6 + 0.1 * len(narratives), 0.9)

    roles = {n.role for n in narratives if n.role}
    locations = {n.location_context for n in narratives if n.location_context}

    if len(roles) <= 1:
        base += 0.05
    if len(locations) <= 1:
        base += 0.05

    return round(min(base, 0.99), 2)
