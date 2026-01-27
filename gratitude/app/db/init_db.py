from app.db.session import engine
from app.db.base import Base

from app.models.message import Message
from app.models.narrative import Narrative
from app.models.cluster import SemanticCluster
from app.models.entity import GratitudeEntity
from app.models.embedding import NarrativeEmbedding
from app.models.cluster_membership import ClusterMembership
from app.models.entity_resolution_state import EntityResolutionState
from app.models.review_action import ReviewAction

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
