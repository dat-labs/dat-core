"""create table user_workspaces

Revision ID: db690d4218ea
Revises: e8d3acf76fd5
Create Date: 2024-03-15 18:09:38.646937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db690d4218ea'
down_revision: Union[str, None] = 'e8d3acf76fd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workspace_users table
    op.create_table(
        'workspace_users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workspace_id', sa.String(36), sa.ForeignKey(
            'workspaces.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey(
            'users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime,
                  server_default=sa.func.now(), onupdate=sa.func.now())
    )


def downgrade() -> None:
    op.drop_table('workspace_users')
