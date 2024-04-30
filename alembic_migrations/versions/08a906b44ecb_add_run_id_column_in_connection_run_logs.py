"""Add run_id column in connection run logs

Revision ID: 08a906b44ecb
Revises: 252d37bbf32c
Create Date: 2024-04-30 10:26:42.224437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

TABLE_NAME = 'connection_run_logs'

# revision identifiers, used by Alembic.
revision: str = '08a906b44ecb'
down_revision: Union[str, None] = '252d37bbf32c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(TABLE_NAME, column=sa.Column(
        'run_id', sa.String(36),
        nullable=False,
        server_default=sa.text("uuid_generate_v4()")
    ))


def downgrade() -> None:
    op.drop_column(TABLE_NAME, column_name='run_id')
