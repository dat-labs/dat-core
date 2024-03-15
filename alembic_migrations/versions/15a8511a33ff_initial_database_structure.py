"""initial database structure

Revision ID: 15a8511a33ff
Revises: 
Create Date: 2024-03-11 19:28:18.362236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '15a8511a33ff'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'organizations',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', name='organizations_status_enum'), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=func.now()),
    )
    


def downgrade() -> None:
    op.drop_table('organizations')
    op.execute('DROP TYPE organizations_status_enum')
