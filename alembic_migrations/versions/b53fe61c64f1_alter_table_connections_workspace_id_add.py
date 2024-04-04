"""alter table connections workspace_id add

Revision ID: b53fe61c64f1
Revises: e0702c8ef408
Create Date: 2024-03-27 01:33:26.619748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b53fe61c64f1'
down_revision: Union[str, None] = 'e0702c8ef408'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_NAME = 'connections'
COLUMN_NAME = 'workspace_id'

def upgrade() -> None:
    op.add_column(TABLE_NAME, sa.Column(COLUMN_NAME, sa.String(36), sa.ForeignKey('workspaces.id'), nullable=False))


def downgrade() -> None:
    op.drop_column(TABLE_NAME, COLUMN_NAME)
