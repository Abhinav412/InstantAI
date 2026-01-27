from sqlalchemy import Column, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class SemanticCluster(Base):
    __tablename__ = "semantic_clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centroid_vector = Column(JSON)
    summary = Column(JSON)
    confidence = Column(Float)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
