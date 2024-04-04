"""Add connection_run_logs table

Revision ID: e0702c8ef408
Revises: 1d16ab0e4012
Create Date: 2024-03-22 13:15:38.838145

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

TABLE_NAME = 'connection_run_logs'

# revision identifiers, used by Alembic.
revision: str = 'e0702c8ef408'
down_revision: Union[str, None] = '1d16ab0e4012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        sa.Column('id', sa.String(36), primary_key=True,
                  nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column('connection_id', sa.String(36), sa.ForeignKey(
            'connections.id'), nullable=False),
        sa.Column('level', sa.Enum(
            'FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG',
            'TRACE', name=f'{TABLE_NAME}_loglevel_enum'), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('stack_trace', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
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
    op.execute(f'DROP TYPE {TABLE_NAME}_loglevel_enum')
