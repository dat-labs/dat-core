from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db_models import Base
from .actor_instances import ActorInstance

class Workspace(Base):
    __tablename__ = 'workspaces'

    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False)
    # Assuming it's a string, change data type if necessary
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Define relationship with the ActorInstance model
    actor_instances = relationship(ActorInstance, back_populates="workspace")

    def __repr__(self):
        return f"<Workspace(id='{self.id}', name='{self.name}', status='{self.status}')>"
