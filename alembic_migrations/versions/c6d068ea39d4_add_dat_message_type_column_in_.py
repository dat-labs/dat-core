"""Add dat message type column in connection_run_logs

Revision ID: c6d068ea39d4
Revises: 08a906b44ecb
Create Date: 2024-04-30 11:28:38.455448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

TABLE_NAME = 'connection_run_logs'

# revision identifiers, used by Alembic.
revision: str = 'c6d068ea39d4'
down_revision: Union[str, None] = '08a906b44ecb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE connection_run_logs_message_type_enum as ENUM ('STATE', 'LOG', 'SPEC', 'CONNECTION_STATUS', 'CATALOG', 'TRACE')")
    op.add_column(TABLE_NAME, column=sa.Column(
        'message_type', sa.Enum(
            name='connection_run_logs_message_type_enum'),
            nullable=False
    ))


def downgrade() -> None:
    op.drop_column(TABLE_NAME, column_name='message_type')
    op.execute('DROP TYPE connection_run_logs_message_type_enum')