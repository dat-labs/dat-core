from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, text
from sqlalchemy.sql import func
from dat_core.db_models import Base


class Connection(Base):
    __tablename__ = 'connections'

    id = Column(String(36), primary_key=True,
                   nullable=False, server_default=text("uuid_generate_v4()"))
    name = Column(String(255))
    source_instance_id = Column(String(36), ForeignKey('actor_instances.id'), nullable=False)
    generator_instance_id = Column(String(36), ForeignKey('actor_instances.id'), nullable=False)
    destination_instance_id = Column(String(36), ForeignKey('actor_instances.id'), nullable=False)
    configuration = Column(JSON)
    catalog = Column(JSON)
    cron_string = Column(String(255))
    status = Column(Enum('active', 'inactive', name='connection_status_enum'), server_default='active', nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


    def __repr__(self):
        return f"<Connection(id='{self.id}', name='{self.name}', status='{self.status}')>"
