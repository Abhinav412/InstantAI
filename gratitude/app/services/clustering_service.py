import numpy as np
import uuid
from app.core.vector_store import vector_store
from app.models.cluster import SemanticCluster
from app.models.cluster_membership import ClusterMembership
from app.db.session import get_session

TOP_K = 5
ATTACH_THRESHOLD = 0.78


def assign_cluster(vector: list[float], narrative_id):
    with get_session() as session:

        if session.query(SemanticCluster).count() == 0:
            cluster_id = uuid.uuid4()
            _create_cluster(session, cluster_id, vector, narrative_id)
            return cluster_id

        vec = np.array([vector]).astype("float32")
        scores, indices = vector_store.index.search(vec, TOP_K)

        best_score = scores[0][0]

        if best_score >= ATTACH_THRESHOLD:
            cluster = session.query(SemanticCluster).first()
            session.add(
                ClusterMembership(
                    cluster_id=cluster.id,
                    narrative_id=narrative_id
                )
            )
            session.commit()
            return cluster.id

        cluster_id = uuid.uuid4()
        _create_cluster(session, cluster_id, vector, narrative_id)
        return cluster_id


def _create_cluster(session, cluster_id, vector, narrative_id):
    cluster = SemanticCluster(
        id=cluster_id,
        centroid_vector=vector,
        summary={},
        confidence=0.5
    )
    session.add(cluster)

    session.add(
        ClusterMembership(
            cluster_id=cluster_id,
            narrative_id=narrative_id
        )
    )

    # ✅ FAISS only receives vectors
    vector_store.add(vector)

