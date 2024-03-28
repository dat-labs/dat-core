"""create workspaces table

Revision ID: 442e4a7bac57
Revises: 15a8511a33ff
Create Date: 2024-03-15 17:42:24.922875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from alembic_migrations.utils.database_utils import (
    create_trigger,
    create_trigger_function,
    drop_trigger,
    drop_trigger_function
)


# revision identifiers, used by Alembic.
revision: str = '442e4a7bac57'
down_revision: Union[str, None] = '15a8511a33ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'workspaces'


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.String(36), nullable=False,
                  primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', name='workspaces_status_enum'),
                  server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime)
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
    op.execute('DROP TYPE workspaces_status_enum')
