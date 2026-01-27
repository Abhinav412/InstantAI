from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_text = Column(Text, nullable=False)
    source = Column(String, nullable=False)
    language = Column(String, nullable=False)
    extra_metadata = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
