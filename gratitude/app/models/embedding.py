from sqlalchemy import Column, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class NarrativeEmbedding(Base):
    __tablename__ = "narrative_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    narrative_id = Column(UUID(as_uuid=True), nullable=False)
    embedding = Column(JSON, nullable=False)
