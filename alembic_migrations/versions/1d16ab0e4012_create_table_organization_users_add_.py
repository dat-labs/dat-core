"""add column password_hash to users

Revision ID: 1d16ab0e4012
Revises: 25804ddf006a
Create Date: 2024-03-19 17:51:24.915675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d16ab0e4012'
down_revision: Union[str, None] = '25804ddf006a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "users"
COLUMN_NAME = "password_hash"


def upgrade() -> None:
    op.add_column(TABLE_NAME, sa.Column(COLUMN_NAME, sa.String(255), nullable=False, default="hash"))


def downgrade() -> None:
    op.drop_column(TABLE_NAME, COLUMN_NAME)
