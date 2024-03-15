"""create table connections

Revision ID: 25804ddf006a
Revises: 279690c42486
Create Date: 2024-03-15 18:11:35.127178

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '25804ddf006a'
down_revision: Union[str, None] = '279690c42486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create connections table
    op.create_table(
        'connections',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('source_instance_id', sa.String(36),
                  sa.ForeignKey('actor_instances.id'), nullable=False),
        sa.Column('generator_instance_id', sa.String(36),
                  sa.ForeignKey('actor_instances.id'), nullable=False),
        sa.Column('destination_instance_id', sa.String(36),
                  sa.ForeignKey('actor_instances.id'), nullable=False),
        sa.Column('configuration', sa.JSON),
        sa.Column('catalog', sa.JSON),
        sa.Column('cron_string', sa.String(255)),
        sa.Column('status', sa.Enum('active', 'inactive',
                  name='connection_status_enum'), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime,
                  server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('connections')
    op.execute('DROP TYPE connection_status_enum')
