"""create table connections

Revision ID: 25804ddf006a
Revises: 279690c42486
Create Date: 2024-03-15 18:11:35.127178

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
revision: str = '25804ddf006a'
down_revision: Union[str, None] = '279690c42486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'connections'

def upgrade() -> None:
    # Create connections table
    op.create_table(
        TABLE_NAME,
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
    # Drop the ENUM type
    op.execute('DROP TYPE connection_status_enum')

