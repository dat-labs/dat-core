"""drop column level from connection run logs

Revision ID: 04274709cf77
Revises: c6d068ea39d4
Create Date: 2024-04-30 12:23:17.249580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

TABLE_NAME = 'connection_run_logs'

# revision identifiers, used by Alembic.
revision: str = '04274709cf77'
down_revision: Union[str, None] = 'c6d068ea39d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column(TABLE_NAME, 'level')


def downgrade() -> None:
    op.add_column(
        TABLE_NAME,
        column=sa.Column('level', sa.Enum(
            'FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG',
            'TRACE', name=f'{TABLE_NAME}_loglevel_enum'), nullable=False)
    )
    
