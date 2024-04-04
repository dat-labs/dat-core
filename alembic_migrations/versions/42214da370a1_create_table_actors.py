"""create table actors

Revision ID: 42214da370a1
Revises: db690d4218ea
Create Date: 2024-03-15 18:10:37.987740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_migrations.utils.database_utils import (
    create_trigger,
    create_trigger_function,
    drop_trigger,
    drop_trigger_function
)


# revision identifiers, used by Alembic.
revision: str = '42214da370a1'
down_revision: Union[str, None] = 'db690d4218ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'actors'

def upgrade() -> None:
    # Create actors table
    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.String(36), primary_key=True,
                  nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('icon', sa.String(255)),
        sa.Column('actor_type', sa.Enum(
            'source', 'destination', 'generator', name='actor_type_enum')),
        sa.Column('status', sa.Enum(
            'active', 'inactive', name='actor_status_enum'),
            server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime,
                  server_default=sa.func.now())
    )

    # Create the trigger function
    op.execute(create_trigger_function(TABLE_NAME, "updated_at"))

    # Create the trigger
    op.execute(create_trigger(TABLE_NAME, "updated_at"))

def downgrade() -> None:
    # Drop the trigger
    op.execute(drop_trigger(TABLE_NAME, "updated_at"))
    # Drop the trigger function
    op.execute(drop_trigger_function(TABLE_NAME, "updated_at"))
    # Drop the table
    op.drop_table(TABLE_NAME)
    # Drop the enum types
    op.execute('DROP TYPE actor_type_enum')
    op.execute('DROP TYPE actor_status_enum')
