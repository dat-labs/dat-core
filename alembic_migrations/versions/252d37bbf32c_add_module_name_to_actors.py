"""add module_name to actors

Revision ID: 252d37bbf32c
Revises: dbd243dc3829
Create Date: 2024-04-02 18:19:31.280066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '252d37bbf32c'
down_revision: Union[str, None] = 'dbd243dc3829'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'actors'

def upgrade() -> None:
    op.add_column(TABLE_NAME, sa.Column('module_name', sa.String(255), nullable=False, server_default="google_drive"))


def downgrade() -> None:
    op.drop_column(TABLE_NAME, 'module_name')
