"""create table users

Revision ID: e8d3acf76fd5
Revises: 442e4a7bac57
Create Date: 2024-03-15 18:05:12.349211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8d3acf76fd5'
down_revision: Union[str, None] = '442e4a7bac57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True)
    )


def downgrade() -> None:
    op.drop_table('users')
