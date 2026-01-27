from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class EntityResolutionState(Base):
    __tablename__ = "entity_resolution_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String)  # stable | merge_candidate | split_candidate
    signals = Column(JSON)
