from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from db_models import Base


class ActorInstance(Base):
    __tablename__ = 'actor_instances'

    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey(
        'workspaces.id'), nullable=False)
    actor_id = Column(String(36), ForeignKey('actors.id'), nullable=False)
    name = Column(String(255))
    configuration = Column(JSON)
    # Assuming it's a string, change data type if necessary
    actor_type = Column(String(50))
    user_id = Column(String(50))
    # Assuming it's a string, change data type if necessary
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Define relationship with the Workspace model
    workspace = relationship('Workspace', back_populates="actor_instances")

    # Define relationship with the Actor model
    # actor = relationship("Actor", back_populates="actor_instances")

    def __repr__(self):
        return f"<ActorInstance(id='{self.id}', name='{self.name}', actor_type='{self.actor_type}', status='{self.status}')>"
