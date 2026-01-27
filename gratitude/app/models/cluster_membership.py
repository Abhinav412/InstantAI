from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class ClusterMembership(Base):
    __tablename__ = "cluster_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), nullable=False)
    narrative_id = Column(UUID(as_uuid=True), nullable=False)
