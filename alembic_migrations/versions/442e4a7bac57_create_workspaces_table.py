"""create workspaces table

Revision ID: 442e4a7bac57
Revises: 15a8511a33ff
Create Date: 2024-03-15 17:42:24.922875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = '442e4a7bac57'
down_revision: Union[str, None] = '15a8511a33ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        'workspaces',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('organization_id', sa.String(255), sa.ForeignKey('organizations.id')),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', name='workspaces_status_enum'), server_default='active'),
        sa.Column('created_at', sa.DateTime, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=func.now()),  # Adding onupdate attribute
    )

    # Create the trigger function
    op.execute(f'''
        CREATE OR REPLACE FUNCTION update_workspaces_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    ''')

    # Create the trigger
    op.execute(f'''
        CREATE TRIGGER trigger_update_workspaces_updated_at
        BEFORE UPDATE ON workspaces
        FOR EACH ROW
        EXECUTE FUNCTION update_workspaces_updated_at();
    ''')


def downgrade() -> None:
    # Drop the trigger
    op.execute(f'DROP TRIGGER IF EXISTS trigger_update_workspaces_updated_at ON workspaces')

    # Drop the trigger function
    op.execute(f'DROP FUNCTION IF EXISTS update_workspaces_updated_at')

    # Drop the table
    op.drop_table('workspaces')

    op.execute('DROP TYPE workspaces_status_enum')