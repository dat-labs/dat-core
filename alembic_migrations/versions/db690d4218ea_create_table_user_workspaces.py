"""create table user_workspaces

Revision ID: db690d4218ea
Revises: e8d3acf76fd5
Create Date: 2024-03-15 18:09:38.646937

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
revision: str = 'db690d4218ea'
down_revision: Union[str, None] = 'e8d3acf76fd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'workspace_users'

def upgrade() -> None:
    # Create workspace_users table
    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey(
            'workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey(
            'users.id'), nullable=False),
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
