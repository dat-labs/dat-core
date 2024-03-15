"""create table actor_instances

Revision ID: 279690c42486
Revises: 42214da370a1
Create Date: 2024-03-15 18:11:06.801519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '279690c42486'
down_revision: Union[str, None] = '42214da370a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create actor_instances table
    op.create_table(
        'actor_instances',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey(
            'workspaces.id'), nullable=False),
        sa.Column('actor_id', sa.String(36), sa.ForeignKey(
            'actors.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey(
            'users.id'), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('configuration', sa.JSON),
        sa.Column('actor_type', sa.Enum(
            'source', 'destination', 'generator', name='actor_type_enum')),
        sa.Column('status', sa.Enum(
            'active', 'inactive', name='actor_instances_status_enum'), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime,
                  server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('actor_instances')
    op.execute('DROP TYPE actor_instances_status_enum')
