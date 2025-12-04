"""add avatar_url to users

Revision ID: add_avatar_url_20251204
Revises: 87938488130b_removed_is_active
Create Date: 2025-12-04
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_avatar_url_20251204'
# Chain to the latest head at the time (notification channel enum update)
down_revision = '31c7e164ce85'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(length=1000), nullable=True))


def downgrade():
    op.drop_column('users', 'avatar_url')
