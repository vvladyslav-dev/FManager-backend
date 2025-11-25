"""add super admin and approval fields

Revision ID: add_super_admin_approval
Revises: c725450c5b74
Create Date: 2025-01-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_super_admin_approval'
down_revision: Union[str, None] = 'c725450c5b74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_super_admin column
    op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add is_approved column with default True for existing users
    op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='true'))
    
    # For existing admins, set is_approved to True (they were already approved)
    # For new admins registered after this migration, is_approved will be False by default in the application logic


def downgrade() -> None:
    op.drop_column('users', 'is_approved')
    op.drop_column('users', 'is_super_admin')


