from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class GratitudeEntity(Base):
    __tablename__ = "gratitude_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String)
    canonical_profile = Column(JSON)
    confidence_score = Column(Float)
