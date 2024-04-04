"""add columns namespace_format, prefix, schedule, and schedule_type to connections

Revision ID: dbd243dc3829
Revises: b53fe61c64f1
Create Date: 2024-03-27 13:51:59.035526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbd243dc3829'
down_revision: Union[str, None] = 'b53fe61c64f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'connections'

def upgrade() -> None:
    #operations related to namespace_format column
    op.add_column(TABLE_NAME, sa.Column('namespace_format', sa.String(255), nullable=False, server_default="${SOURCE_NAMESPACE}"))

    op.add_column(TABLE_NAME, sa.Column('prefix', sa.String(255), nullable=True))
    op.add_column(TABLE_NAME, sa.Column('schedule', sa.JSON, nullable=True))

    #operations related to schedule_type column
    op.execute('CREATE TYPE connections_schedule_type_enum AS ENUM (\'manual\', \'cron\')')
    op.add_column(TABLE_NAME, sa.Column('schedule_type', sa.Enum('manual', 'cron', name='connections_schedule_type_enum'), nullable=False, server_default="manual"))

def downgrade() -> None:
    op.drop_column(TABLE_NAME, 'namespace_format')
    op.drop_column(TABLE_NAME, 'prefix')
    op.drop_column(TABLE_NAME, 'schedule')
    op.drop_column(TABLE_NAME, 'schedule_type')
    op.execute('DROP TYPE connections_schedule_type_enum')
