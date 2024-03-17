"""create table users

Revision ID: e8d3acf76fd5
Revises: 442e4a7bac57
Create Date: 2024-03-15 18:05:12.349211

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
revision: str = 'e8d3acf76fd5'
down_revision: Union[str, None] = '442e4a7bac57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'users'

def upgrade() -> None:
    # Create users table
    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now())
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
