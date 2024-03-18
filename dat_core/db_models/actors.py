from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from dat_core.db_models import Base
from dat_core.db_models.actor_instances import ActorInstance


class Actor(Base):
    __tablename__ = 'actors'

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    icon = Column(String(255))
    actor_type = Column(Enum('source', 'destination',
                        'generator', name='actor_type_enum'))
    status = Column(Enum('active', 'inactive', name='actor_status_enum'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # relationships
    actor_instances = relationship(ActorInstance, backref="actor")

    def __repr__(self):
        return f"<Actor(id='{self.id}', name='{self.name}', actor_type='{self.actor_type}', status='{self.status}')>"
