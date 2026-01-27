from collections import Counter
from app.db.session import get_session
from app.models.entity import GratitudeEntity
from app.models.entity_resolution_state import EntityResolutionState
from app.models.cluster import SemanticCluster
from app.models.cluster_membership import ClusterMembership
from app.models.narrative import Narrative


def detect_split_candidates():
    # 1️⃣ Fetch entity IDs only (short session)
    with get_session() as session:
        entity_ids = [e.id for e in session.query(GratitudeEntity.id).all()]

    # 2️⃣ Process each entity in isolation
    for entity_id in entity_ids:
        with get_session() as session:
            entity = session.get(GratitudeEntity, entity_id)

            clusters = (
                session.query(SemanticCluster.id)
                .filter(SemanticCluster.entity_id == entity.id)
                .all()
            )

            if not clusters:
                continue

            roles = Counter()
            locations = Counter()

            for (cluster_id,) in clusters:
                narratives = (
                    session.query(Narrative)
                    .join(
                        ClusterMembership,
                        ClusterMembership.narrative_id == Narrative.id,
                    )
                    .filter(ClusterMembership.cluster_id == cluster_id)
                    .all()
                )

                for n in narratives:
                    if n.role:
                        roles[n.role] += 1
                    if n.location_context:
                        locations[n.location_context] += 1

            if len(roles) <= 1 and len(locations) <= 1:
                continue

            signals = {
                "roles": dict(roles),
                "locations": dict(locations),
            }

            state = (
                session.query(EntityResolutionState)
                .filter_by(
                    entity_id=entity.id,
                    status="split_candidate",
                )
                .first()
            )

            if state:
                state.signals = signals
            else:
                session.add(
                    EntityResolutionState(
                        entity_id=entity.id,
                        status="split_candidate",
                        signals=signals,
                    )
                )
