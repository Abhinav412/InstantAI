from sqlalchemy import Column, String, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Narrative(Base):
    __tablename__ = "narratives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), nullable=False)
    entity_type = Column(String)
    role = Column(String)
    actions = Column(JSON)
    descriptors = Column(JSON)
    time_context = Column(String)
    location_context = Column(String)
    sentiment_score = Column(Float)
