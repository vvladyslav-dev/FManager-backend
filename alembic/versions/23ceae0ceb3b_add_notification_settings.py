"""add_notification_settings

Revision ID: 23ceae0ceb3b
Revises: add_super_admin_approval
Create Date: 2025-12-03 16:14:10.191481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23ceae0ceb3b'
down_revision: Union[str, None] = 'add_super_admin_approval'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification settings columns to users table
    op.add_column('users', sa.Column('telegram_chat_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('telegram_notifications_enabled', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('users', sa.Column('notification_preferences', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove notification settings columns from users table
    op.drop_column('users', 'notification_preferences')
    op.drop_column('users', 'email_notifications_enabled')
    op.drop_column('users', 'telegram_notifications_enabled')
    op.drop_column('users', 'telegram_chat_id')
