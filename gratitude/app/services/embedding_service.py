from sentence_transformers import SentenceTransformer
from app.db.session import get_session
from app.models.narrative import Narrative
from app.models.embedding import NarrativeEmbedding
from app.services.clustering_service import assign_cluster

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_narrative(narrative_id):
    # 1️⃣ Load narrative inside active session
    with get_session() as session:
        narrative = session.get(Narrative, narrative_id)

        if not narrative:
            return

        text_parts = []

        if narrative.actions:
            text_parts.extend(narrative.actions)
        if narrative.descriptors:
            text_parts.extend(narrative.descriptors)
        if narrative.location_context:
            text_parts.append(narrative.location_context)

        text = " ".join(text_parts).strip()

        if not text:
            return

    # 2️⃣ Encode outside DB session
    vector = model.encode(text).tolist()

    # 3️⃣ Persist embedding
    with get_session() as session:
        session.add(
            NarrativeEmbedding(
                narrative_id=narrative_id,
                embedding=vector,
            )
        )
        session.flush()

    # 4️⃣ Cluster
    assign_cluster(vector, narrative_id)
