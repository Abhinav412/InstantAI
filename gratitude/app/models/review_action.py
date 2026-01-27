from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class ReviewAction(Base):
    __tablename__ = "review_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String)
    notes = Column(String)
    review_metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
