"""create table actors

Revision ID: 42214da370a1
Revises: db690d4218ea
Create Date: 2024-03-15 18:10:37.987740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42214da370a1'
down_revision: Union[str, None] = 'db690d4218ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create actors table
    op.create_table(
        'actors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('icon', sa.String(255)),
        sa.Column('actor_type', sa.Enum(
            'source', 'destination', 'generator', name='actor_type_enum')),
        sa.Column('status', sa.Enum(
            'active', 'inactive', name='actor_status_enum'), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime,
                  server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('actors')
    op.execute('DROP TYPE actor_type_enum')
    op.execute('DROP TYPE actor_status_enum')
